#!/usr/bin/env python3
"""
Test Audio Capture - Verify you're capturing SYSTEM AUDIO, not microphone
"""

import sounddevice as sd
import numpy as np
import sys
import json
import os

def load_config():
    """Load audio configuration"""
    try:
        # Try device_config.json first
        if os.path.exists('device_config.json'):
            with open('device_config.json', 'r') as f:
                config = json.load(f)
                config['source'] = 'device_config'
                return config

        # Fallback to audio_config.json
        if os.path.exists('audio_config.json'):
            with open('audio_config.json', 'r') as f:
                config = json.load(f)
                config['source'] = 'audio_config'
                return config
    except Exception as e:
        print(f"Warning: Could not load config: {e}")
    return None

def test_audio_levels(device, duration=5):
    """Test audio levels to verify capture"""
    print(f"\n{'='*60}")
    print("🎵 Testing Audio Capture")
    print(f"{'='*60}")
    print(f"Device: {device}")
    print(f"Duration: {duration} seconds")
    print(f"{'='*60}\n")

    print("📋 Instructions:")
    print("1. PLAY SOME AUDIO on your computer")
    print("   (Open YouTube, play music, etc.)")
    print("2. Watch the level meter below")
    print("3. If you see activity → capturing SYSTEM AUDIO ✅")
    print("4. If silent → capturing wrong source ❌\n")

    input("Press Enter when audio is playing...")

    print("\n🎧 Capturing audio...\n")

    try:
        # Capture audio
        recording = sd.rec(
            int(duration * 44100),
            samplerate=44100,
            channels=2,
            dtype='int16',
            device=device
        )

        # Show live levels
        for i in range(duration):
            sd.wait(int(1000))  # Wait 1 second

            # Calculate RMS level
            chunk = recording[i*44100:(i+1)*44100]
            if len(chunk) > 0:
                rms = np.sqrt(np.mean(chunk.astype(float)**2))
                normalized = int((rms / 32768) * 50)  # Scale to 50 chars

                bar = '█' * min(normalized, 50)
                level_pct = (rms / 32768) * 100

                print(f"[{i+1}s] {bar:<50} {level_pct:.1f}%")

        print("\n" + "="*60)

        # Analyze results
        max_level = np.max(np.abs(recording))
        avg_level = np.mean(np.abs(recording))

        print(f"\n📊 Results:")
        print(f"   Max Level: {(max_level/32768)*100:.1f}%")
        print(f"   Avg Level: {(avg_level/32768)*100:.1f}%")

        if max_level > 1000:  # Threshold for detecting audio
            print("\n✅ SUCCESS! Capturing audio!")
            print("   You should hear this audio when you run the server.")
        else:
            print("\n❌ WARNING: Very low or no audio detected!")
            print("   Possible issues:")
            print("   • No audio is playing")
            print("   • Wrong device selected")
            print("   • Capturing microphone instead of system audio")
            print("\n💡 Solution:")
            print("   Run: python3 select_audio_source.py")
            print("   Select the output device where audio is playing")

        print("="*60 + "\n")

    except Exception as e:
        print(f"\n❌ Error capturing audio: {e}")
        print("\nPossible solutions:")
        print("1. Run: python3 select_audio_source.py")
        print("2. Make sure audio is playing")
        print("3. Check: pactl list short sources | grep monitor")
        return False

    return True

def main():
    """Main test function"""
    print("\n" + "="*60)
    print("  AUDIO CAPTURE TEST")
    print("  Verify you're capturing SYSTEM AUDIO (not microphone)")
    print("="*60)

    # Load configuration
    config = load_config()
    device = None

    if config:
        config_source = config.get('source', 'unknown')

        # Try device_config.json first (preferred)
        if config_source == 'device_config' and 'device_id' in config:
            device = config['device_id']
            device_name = config.get('device_name', 'Unknown')
            method = config.get('method', 'unknown')
            print(f"\n✅ Using device configuration:")
            print(f"   Device ID: {device}")
            print(f"   Name: {device_name}")
            print(f"   Method: {method}")

        # Fallback to audio_config.json
        elif config_source == 'audio_config':
            if config.get('use_pulse_device') and 'sounddevice_id' in config:
                device = config['sounddevice_id']
                desc = config.get('description', 'Unknown')
                print(f"\n✅ Using audio configuration:")
                print(f"   Output: {desc}")
                print(f"   Device ID: {device}")
            elif 'monitor_source_name' in config:
                device = config['monitor_source_name']
                desc = config.get('description', 'Unknown')
                print(f"\n✅ Using monitor configuration:")
                print(f"   Output: {desc}")
                print(f"   Monitor: {device}")

    if not device:
        print("\n⚠️  No configuration found!")
        print("   Trying to auto-detect...\n")

        # Try to find pulse device
        try:
            import sounddevice as sd
            devs = sd.query_devices()

            # Look for pulse first (best for PipeWire)
            for i, dev in enumerate(devs):
                if dev['name'].lower() == 'pulse' and dev['max_input_channels'] >= 2:
                    device = i
                    print(f"   Found 'pulse' device at ID {i}")
                    break

            # Then default
            if not device:
                for i, dev in enumerate(devs):
                    if dev['name'].lower() == 'default' and dev['max_input_channels'] >= 2:
                        device = i
                        print(f"   Found 'default' device at ID {i}")
                        break
        except Exception as e:
            print(f"   Error: {e}")

    if device is None:
        print("\n❌ Cannot determine audio device")
        print("\n📋 Fix this issue:")
        print("   1. Run: python3 find_monitor_device.py")
        print("      (Finds the right capture device)")
        print("   2. Run this test again")
        print("   3. If still failing:")
        print("      systemctl --user restart pipewire pipewire-pulse")
        return 1

    # Run test
    test_audio_levels(device, duration=5)

    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\nTest cancelled.")
        sys.exit(0)