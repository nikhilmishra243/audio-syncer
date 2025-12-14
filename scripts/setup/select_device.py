#!/usr/bin/env python3
"""
Interactive device selector for manual audio device configuration
Use this when auto-detection fails
"""

import sounddevice as sd
import sys

def list_devices():
    """List all available audio devices"""
    print("\n" + "="*70)
    print("  AVAILABLE AUDIO DEVICES")
    print("="*70 + "\n")

    devices = sd.query_devices()

    print(f"{'ID':<5} {'Name':<40} {'In':<5} {'Out':<5}")
    print("-"*70)

    for i, dev in enumerate(devices):
        name = dev['name'][:38]  # Truncate long names
        in_ch = dev['max_input_channels']
        out_ch = dev['max_output_channels']
        print(f"{i:<5} {name:<40} {in_ch:<5} {out_ch:<5}")

    print("\n" + "="*70)
    return devices

def test_device(device_id, sample_rate=44100, channels=2):
    """Test if a device works"""
    print(f"\n🔍 Testing device {device_id}...")

    try:
        stream = sd.InputStream(
            device=device_id,
            samplerate=sample_rate,
            channels=channels,
            blocksize=1024,
            dtype="int16"
        )
        stream.start()

        # Try to read some data
        data, overflowed = stream.read(1024)
        stream.stop()
        stream.close()

        print(f"✅ Device {device_id} works!")
        return True

    except Exception as e:
        print(f"❌ Device {device_id} failed: {e}")
        return False

def main():
    """Main device selector"""
    print("\n" + "="*70)
    print("  AUDIO DEVICE SELECTOR")
    print("  Use this tool to manually select an audio input device")
    print("="*70)

    devices = list_devices()

    if not devices:
        print("\n❌ No audio devices found!")
        return 1

    print("\n💡 For system audio capture, look for:")
    print("   • Devices with 'monitor' in the name (Linux)")
    print("   • Devices with 'Stereo Mix' in the name (Windows)")
    print("   • Devices with 'BlackHole' or 'Loopback' in the name (macOS)")

    while True:
        print("\n" + "-"*70)
        choice = input("\nEnter device ID to test (or 'q' to quit): ").strip()

        if choice.lower() == 'q':
            print("\nExiting...")
            break

        try:
            device_id = int(choice)

            if device_id < 0 or device_id >= len(devices):
                print(f"❌ Invalid device ID. Must be between 0 and {len(devices)-1}")
                continue

            device_name = devices[device_id]['name']
            print(f"\n📋 Selected: [{device_id}] {device_name}")

            # Test the device
            if test_device(device_id):
                print("\n" + "="*70)
                print("✅ SUCCESS! This device works.")
                print("="*70)
                print("\nTo use this device, update server.py:")
                print(f"\n  stream = sd.InputStream(")
                print(f"      device={device_id},  # <-- Add this line")
                print(f"      samplerate=44100,")
                print(f"      channels=2,")
                print(f"      blocksize=1024,")
                print(f"      dtype=\"int16\"")
                print(f"  )")
                print("\nOr set as environment variable:")
                print(f"  export AUDIO_DEVICE_ID={device_id}")
                print("="*70)

        except ValueError:
            print("❌ Please enter a valid number")
        except KeyboardInterrupt:
            print("\n\nInterrupted by user.")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\nExiting...")
        sys.exit(0)