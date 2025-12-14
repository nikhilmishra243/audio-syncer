#!/bin/bash
# Linux Audio Setup Helper Script
# Helps configure PulseAudio/PipeWire for system audio capture

echo "============================================================"
echo "  Linux Audio Setup Helper"
echo "============================================================"
echo ""

# Detect audio system
echo "🔍 Detecting audio system..."
echo ""

if systemctl --user is-active --quiet pipewire; then
    AUDIO_SYSTEM="PipeWire"
    echo "✅ PipeWire detected (modern)"
elif systemctl --user is-active --quiet pulseaudio; then
    AUDIO_SYSTEM="PulseAudio"
    echo "✅ PulseAudio detected"
else
    echo "⚠️  No audio system detected"
    AUDIO_SYSTEM="Unknown"
fi

echo "   Audio System: $AUDIO_SYSTEM"
echo ""

# Check if pactl is installed
echo "🔍 Checking for pactl..."
if command -v pactl &> /dev/null; then
    echo "✅ pactl is installed"
    PACTL_INSTALLED=true
else
    echo "❌ pactl is NOT installed"
    PACTL_INSTALLED=false
    echo ""
    echo "📦 Install pactl with:"

    if [ -f /etc/debian_version ]; then
        echo "   sudo apt-get install pulseaudio-utils"
    elif [ -f /etc/fedora-release ]; then
        echo "   sudo dnf install pulseaudio-utils"
    elif [ -f /etc/arch-release ]; then
        echo "   sudo pacman -S pulseaudio"
    else
        echo "   Install pulseaudio-utils for your distribution"
    fi
fi

echo ""
echo "------------------------------------------------------------"
echo ""

# List current sources if pactl is available
if [ "$PACTL_INSTALLED" = true ]; then
    echo "📋 Available audio sources:"
    echo ""
    pactl list short sources
    echo ""

    # Check for monitor devices
    MONITOR_COUNT=$(pactl list short sources | grep -i monitor | wc -l)

    if [ $MONITOR_COUNT -gt 0 ]; then
        echo "✅ Found $MONITOR_COUNT monitor device(s)"
        echo ""
        echo "Monitor devices:"
        pactl list short sources | grep -i monitor
        echo ""
        echo "✅ System audio capture should work!"
    else
        echo "❌ No monitor devices found"
        echo ""
        echo "💡 Solution: Enable loopback module"
        echo ""
        read -p "Enable PulseAudio loopback module now? (y/n): " -n 1 -r
        echo

        if [[ $REPLY =~ ^[Yy]$ ]]; then
            echo ""
            echo "🔧 Loading loopback module..."
            pactl load-module module-loopback

            if [ $? -eq 0 ]; then
                echo "✅ Loopback module loaded successfully!"
                echo ""
                echo "Updated audio sources:"
                pactl list short sources
            else
                echo "❌ Failed to load loopback module"
            fi
        fi
    fi
else
    echo "⚠️  Cannot list devices without pactl"
    echo "   Install pulseaudio-utils first"
fi

echo ""
echo "------------------------------------------------------------"
echo ""

# Provide additional troubleshooting
echo "📚 Troubleshooting Tips:"
echo ""
echo "1. Restart audio service:"
if [ "$AUDIO_SYSTEM" = "PipeWire" ]; then
    echo "   systemctl --user restart pipewire pipewire-pulse"
elif [ "$AUDIO_SYSTEM" = "PulseAudio" ]; then
    echo "   systemctl --user restart pulseaudio"
fi
echo ""
echo "2. Check audio service status:"
if [ "$AUDIO_SYSTEM" = "PipeWire" ]; then
    echo "   systemctl --user status pipewire"
elif [ "$AUDIO_SYSTEM" = "PulseAudio" ]; then
    echo "   systemctl --user status pulseaudio"
fi
echo ""
echo "3. List available devices in Python:"
echo "   python3 select_device.py"
echo ""
echo "4. Test microphone access:"
echo "   arecord -l"
echo ""
echo "============================================================"
echo ""
echo "After fixing the audio setup, run:"
echo "   ./start-server.sh"
echo ""
echo "============================================================"