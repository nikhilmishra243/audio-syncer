#!/usr/bin/env python3
"""
Audio Source Selector - Choose which audio OUTPUT to capture
This captures what's PLAYING (system audio), not microphone input
"""

import subprocess
import sys
import json
import os
import sounddevice as sd

def print_header(text):
    """Print formatted header"""
    print("\n" + "="*70)
    print(f"  {text}")
    print("="*70 + "\n")

def find_pulse_device_id():
    """Find the 'pulse' device ID in sounddevice"""
    try:
        devs = sd.query_devices()
        for i, dev in enumerate(devs):
            if dev['name'].lower() == 'pulse' and dev['max_input_channels'] >= 2:
                return i, dev['name']

        # Fallback to 'default'
        for i, dev in enumerate(devs):
            if dev['name'].lower() == 'default' and dev['max_input_channels'] >= 2:
                return i, dev['name']
    except Exception as e:
        print(f"Warning: Could not find pulse device: {e}")

    return None, None

def get_audio_sinks_and_monitors():
    """Get audio outputs (sinks) and their monitors"""
    try:
        # Get all sources (including monitors)
        sources_result = subprocess.run(
            ['pactl', 'list', 'short', 'sources'],
            capture_output=True,
            text=True,
            timeout=5
        )

        # Get sink info for descriptions
        sinks_result = subprocess.run(
            ['pactl', 'list', 'sinks'],
            capture_output=True,
            text=True,
            timeout=5
        )

        if sources_result.returncode != 0:
            return []

        # Parse monitors
        monitors = {}
        for line in sources_result.stdout.strip().split('\n'):
            if '.monitor' in line:
                parts = line.split()
                if len(parts) >= 2:
                    monitor_name = parts[1]
                    status = parts[-1] if len(parts) > 3 else "UNKNOWN"
                    # Extract sink name from monitor
                    sink_name = monitor_name.replace('.monitor', '')
                    monitors[sink_name] = {
                        'monitor_name': monitor_name,
                        'status': status
                    }

        # Parse sink descriptions
        audio_outputs = []
        current_sink = {}

        for line in sinks_result.stdout.split('\n'):
            line = line.strip()

            if line.startswith('Name:'):
                if current_sink and 'name' in current_sink:
                    # Check if this sink has a monitor
                    if current_sink['name'] in monitors:
                        current_sink['monitor'] = monitors[current_sink['name']]
                        audio_outputs.append(current_sink)

                current_sink = {'name': line.split('Name:')[1].strip()}

            elif line.startswith('Description:'):
                current_sink['description'] = line.split('Description:')[1].strip()

            elif line.startswith('State:'):
                current_sink['state'] = line.split('State:')[1].strip()

        # Add last sink
        if current_sink and 'name' in current_sink:
            if current_sink['name'] in monitors:
                current_sink['monitor'] = monitors[current_sink['name']]
                audio_outputs.append(current_sink)

        return audio_outputs

    except FileNotFoundError:
        print("❌ pactl not found. Install: sudo apt-get install pulseaudio-utils")
        return []
    except Exception as e:
        print(f"❌ Error: {e}")
        return []

def display_audio_outputs(outputs):
    """Display audio outputs"""
    print_header("Available Audio Outputs (What You Can Capture)")

    print("💡 These are your audio OUTPUT devices")
    print("   Selecting one will capture what's PLAYING through it")
    print("   (Music, videos, games - NOT microphone)")
    print()

    print(f"{'ID':<4} {'Description':<40} {'Status':<12} {'Monitor':<8}")
    print("-"*70)

    for i, output in enumerate(outputs):
        desc = output.get('description', 'Unknown')[:38]
        state = output.get('state', 'UNKNOWN')

        # Check monitor status
        monitor_status = "❌"
        if 'monitor' in output:
            mon_state = output['monitor'].get('status', '')
            if mon_state == 'RUNNING':
                monitor_status = "✅ ACTIVE"
            elif mon_state == 'IDLE':
                monitor_status = "💤 IDLE"
            else:
                monitor_status = "✅ Ready"

        print(f"{i:<4} {desc:<40} {state:<12} {monitor_status:<8}")

    print("\n" + "="*70)

def save_config(output, pulse_device_id, pulse_device_name):
    """Save configuration with both pactl and sounddevice info"""
    config = {
        'sink_name': output['name'],
        'monitor_source_name': output['monitor']['monitor_name'],
        'description': output.get('description', 'Unknown'),
        # Add sounddevice-compatible device info
        'sounddevice_id': pulse_device_id,
        'sounddevice_name': pulse_device_name,
        'use_pulse_device': True  # Flag to use pulse device which auto-routes
    }

    # Ensure config directory exists
    config_dir = os.path.join('..', '..', 'config')
    os.makedirs(config_dir, exist_ok=True)

    config_path = os.path.join(config_dir, 'audio_config.json')
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)

    print(f"\n✅ Configuration saved to {config_path}")

def set_default_sink(sink_name):
    """Set the selected sink as default"""
    try:
        result = subprocess.run(
            ['pactl', 'set-default-sink', sink_name],
            capture_output=True,
            timeout=5
        )
        if result.returncode == 0:
            print(f"✅ Set as default audio output")
            return True
    except Exception as e:
        print(f"⚠️ Could not set as default: {e}")
    return False

def main():
    """Main"""
    print_header("System Audio Source Selector")
    print("🎵 Choose which audio OUTPUT to stream")
    print("   (This captures playback audio, NOT microphone)")

    # Find pulse device first
    print("\n🔍 Finding PulseAudio/PipeWire device...")
    pulse_id, pulse_name = find_pulse_device_id()

    if pulse_id is not None:
        print(f"✅ Found: Device {pulse_id} ({pulse_name})")
    else:
        print("⚠️ Could not find pulse device - may have issues")

    print("\n🔍 Scanning audio outputs...")
    outputs = get_audio_sinks_and_monitors()

    if not outputs:
        print("\n❌ No audio outputs with monitors found!")
        print("\nTroubleshooting:")
        print("1. Check audio status: systemctl --user status pipewire")
        print("2. List sources: pactl list short sources | grep monitor")
        print("3. Restart audio: systemctl --user restart pipewire pipewire-pulse")
        return 1

    display_audio_outputs(outputs)

    print("\n💡 Example:")
    print("   • Built-in Audio → Captures what plays through laptop speakers")
    print("   • Headphones → Captures what plays through headphones")
    print("   • USB Audio → Captures what plays through USB device")

    while True:
        print("\n" + "-"*70)
        choice = input("\nSelect output ID (or 'q' to quit): ").strip()

        if choice.lower() == 'q':
            return 0

        try:
            idx = int(choice)

            if idx < 0 or idx >= len(outputs):
                print(f"❌ Invalid. Must be 0-{len(outputs)-1}")
                continue

            selected = outputs[idx]

            if 'monitor' not in selected:
                print("❌ This output doesn't have a monitor!")
                continue

            print("\n" + "="*70)
            print("✅ Selected:")
            print(f"   Output: {selected.get('description', 'Unknown')}")
            print(f"   Monitor: {selected['monitor']['monitor_name']}")
            print(f"   Status: {selected['monitor'].get('status', 'UNKNOWN')}")
            print("="*70)

            # Set as default sink
            print("\n🔧 Setting up audio routing...")
            set_default_sink(selected['name'])

            # Save configuration
            save_config(selected, pulse_id, pulse_name)

            print("\n✨ Setup complete!")
            print("\n📋 Next steps:")
            print("   1. Play some audio/music")
            print("      (It will play through your selected output)")
            print("   2. Run: ../../scripts/start/start.sh")
            print("   3. Open http://YOUR-IP:5000 on another device")
            print("   4. The audio will stream to that device!")
            print("\n💡 Audio will route through PulseAudio's 'pulse' device")
            print("   which automatically captures from your selected output")

            return 0

        except ValueError:
            print("❌ Enter a valid number")
        except KeyboardInterrupt:
            print("\n\nExiting...")
            return 1

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\nExiting...")
        sys.exit(0)