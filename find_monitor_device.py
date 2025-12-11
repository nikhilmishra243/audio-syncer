#!/usr/bin/env python3
"""
Find the correct device ID for capturing system audio
Maps pactl monitor sources to sounddevice IDs
"""

import subprocess
import sounddevice as sd
import sys
import json

def get_pactl_monitors():
    """Get monitor sources from pactl"""
    try:
        result = subprocess.run(
            ['pactl', 'list', 'short', 'sources'],
            capture_output=True,
            text=True,
            timeout=5
        )

        if result.returncode != 0:
            return []

        monitors = []
        for line in result.stdout.strip().split('\n'):
            parts = line.split('\t')
            if len(parts) >= 2:
                source_id = parts[0]
                source_name = parts[1]
                status = parts[-1] if len(parts) > 3 else "UNKNOWN"

                # Get ALL sources (monitors, loopback, etc)
                if '.monitor' in source_name.lower() or 'loopback' in source_name.lower():
                    monitors.append({
                        'pactl_id': source_id,
                        'pactl_name': source_name,
                        'status': status
                    })

        return monitors
    except Exception as e:
        print(f"Error getting pactl monitors: {e}")
        return []

def get_sounddevice_inputs():
    """Get input devices from sounddevice"""
    try:
        devs = sd.query_devices()
        inputs = []

        for i, dev in enumerate(devs):
            if dev['max_input_channels'] >= 2:
                inputs.append({
                    'id': i,
                    'name': dev['name'],
                    'channels': dev['max_input_channels']
                })

        return inputs
    except Exception as e:
        print(f"Error getting sounddevice inputs: {e}")
        return []

def find_best_device():
    """Find the best device for capturing system audio"""
    print("\n" + "="*70)
    print("  Finding Best Capture Device")
    print("="*70 + "\n")

    pactl_monitors = get_pactl_monitors()
    sd_inputs = get_sounddevice_inputs()

    print("📋 PulseAudio/PipeWire Monitor Sources:")
    for mon in pactl_monitors:
        status_icon = "✅" if mon['status'] == 'RUNNING' else "💤"
        print(f"   {status_icon} [{mon['pactl_id']}] {mon['pactl_name']} [{mon['status']}]")

    print("\n📋 sounddevice Input Devices:")
    for inp in sd_inputs:
        print(f"   [{inp['id']}] {inp['name']} ({inp['channels']} ch)")

    print("\n🔍 Analyzing matches...\n")

    # Strategy 1: Look for pulse device with RUNNING monitors
    running_monitors = [m for m in pactl_monitors if m['status'] == 'RUNNING']

    for inp in sd_inputs:
        if inp['name'].lower() == 'pulse' and running_monitors:
            print(f"✅ Found Pulse Device with RUNNING monitor!")
            print(f"   Device ID: {inp['id']}")
            print(f"   Name: {inp['name']}")
            print(f"   Will auto-route from: {running_monitors[0]['pactl_name']}")
            return inp['id'], inp['name'], 'pulse-monitor'

    # Strategy 2: Look for default device with monitors
    for inp in sd_inputs:
        if inp['name'].lower() == 'default' and pactl_monitors:
            print(f"✅ Found Default Device with monitors!")
            print(f"   Device ID: {inp['id']}")
            print(f"   Name: {inp['name']}")
            if running_monitors:
                print(f"   Will capture from: {running_monitors[0]['pactl_name']}")
            else:
                print(f"   Will capture from: {pactl_monitors[0]['pactl_name']}")
            return inp['id'], inp['name'], 'default-monitor'

    # Strategy 3: First pulse device
    for inp in sd_inputs:
        if inp['name'].lower() == 'pulse':
            print(f"⚠️  Found Pulse Device (no RUNNING monitors)")
            print(f"   Device ID: {inp['id']}")
            print(f"   Name: {inp['name']}")
            return inp['id'], inp['name'], 'pulse'

    # Strategy 4: Default device
    for inp in sd_inputs:
        if inp['name'].lower() == 'default':
            print(f"⚠️  Using Default Device")
            print(f"   Device ID: {inp['id']}")
            print(f"   Name: {inp['name']}")
            return inp['id'], inp['name'], 'default'

    # Strategy 5: First device with 2+ channels
    if sd_inputs:
        inp = sd_inputs[0]
        print(f"⚠️  Using First Available Device")
        print(f"   Device ID: {inp['id']}")
        print(f"   Name: {inp['name']}")
        return inp['id'], inp['name'], 'first'

    print("❌ No suitable device found")
    return None, None, None

def save_device_config(device_id, device_name, method):
    """Save device configuration"""
    config = {
        'device_id': device_id,
        'device_name': device_name,
        'method': method,
        'note': 'Auto-detected capture device for system audio'
    }

    with open('device_config.json', 'w') as f:
        json.dump(config, f, indent=2)

    print(f"\n✅ Configuration saved to device_config.json")

def set_monitor_as_default():
    """Set monitor source as default input (KEY to capturing system audio!)"""
    try:
        # Get default sink
        result = subprocess.run(
            ['pactl', 'get-default-sink'],
            capture_output=True,
            text=True,
            timeout=5
        )

        if result.returncode != 0:
            print("⚠️  Could not get default sink")
            return False

        default_sink = result.stdout.strip()
        monitor_source = f"{default_sink}.monitor"

        print(f"\n🔧 Setting monitor as default input source...")
        print(f"   Monitor: {monitor_source}")

        # Set monitor as default source
        result = subprocess.run(
            ['pactl', 'set-default-source', monitor_source],
            capture_output=True,
            timeout=5
        )

        if result.returncode == 0:
            print(f"   ✅ Monitor is now the DEFAULT INPUT!")
            print(f"   This means 'pulse' device captures SYSTEM AUDIO, not mic")
            return True
        else:
            print(f"   ⚠️  Could not set monitor as default")
            return False

    except Exception as e:
        print(f"⚠️  Error setting default source: {e}")
        return False

def main():
    """Main"""
    print("\n" + "="*70)
    print("  System Audio Capture Device Finder")
    print("="*70)

    # CRITICAL: Set monitor as default source first!
    print("\n📋 STEP 1: Setting monitor as default input...")
    set_monitor_as_default()

    print("\n📋 STEP 2: Finding capture device...")
    device_id, device_name, method = find_best_device()

    if device_id is not None:
        save_device_config(device_id, device_name, method)

        print("\n" + "="*70)
        print("✅ Configuration complete!")
        print("="*70)
        print(f"\nDevice ID: {device_id}")
        print(f"Name: {device_name}")
        print(f"Method: {method}")

        print("\n" + "="*70)
        print("🎯 CRITICAL: Default input is now set to MONITOR")
        print("   • This captures SYSTEM AUDIO (what's playing)")
        print("   • NOT microphone input")
        print("="*70)

        print("\n📋 Next steps:")
        print("1. Test it: python3 test_audio.py")
        print("   • Play music → should show activity")
        print("   • Speak in mic → should NOT show activity")
        print("2. If test works → python3 server.py")

        print("\n💡 To switch back to microphone later:")
        print("   pactl set-default-source <your-mic-name>")

        return 0
    else:
        print("\n❌ Could not find suitable device")
        return 1

if __name__ == "__main__":
    sys.exit(main())