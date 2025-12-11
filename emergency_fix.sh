#!/bin/bash
# Emergency Audio Fix - Safe version with limits

echo "============================================================"
echo "  🚨 EMERGENCY AUDIO FIX"
echo "============================================================"
echo ""

echo "🔧 Step 1: Checking for loopback modules..."

# Get list of loopback module IDs
LOOPBACK_IDS=$(pactl list modules short | grep module-loopback | awk '{print $1}')

if [ -z "$LOOPBACK_IDS" ]; then
    echo "   ℹ️  No loopback modules found"
else
    echo "   Found loopback module IDs: $LOOPBACK_IDS"
    echo ""
    echo "   Removing them..."

    for MODULE_ID in $LOOPBACK_IDS; do
        echo "   Removing module $MODULE_ID"
        pactl unload-module "$MODULE_ID" 2>/dev/null
        sleep 0.2
    done

    echo "   ✅ All loopback modules removed"
fi

echo ""
echo "🔧 Step 2: Restarting audio system..."
systemctl --user restart pipewire pipewire-pulse

if [ $? -eq 0 ]; then
    echo "   ✅ Audio system restarted"
else
    echo "   ⚠️  Audio restart had issues"
    echo "   Trying alternative method..."
    systemctl --user stop pipewire pipewire-pulse
    sleep 1
    systemctl --user start pipewire pipewire-pulse
fi

echo ""
echo "⏳ Waiting for audio to stabilize..."
sleep 3

echo ""
echo "🔧 Step 3: Verifying audio system..."

# Check if pipewire is running
if systemctl --user is-active --quiet pipewire; then
    echo "   ✅ PipeWire is running"
else
    echo "   ⚠️  PipeWire is not running!"
fi

# Check for any remaining loopback
REMAINING=$(pactl list modules short | grep -c module-loopback)
if [ "$REMAINING" -eq 0 ]; then
    echo "   ✅ No loopback modules present"
else
    echo "   ⚠️  Warning: $REMAINING loopback module(s) still present"
fi

echo ""
echo "============================================================"
echo "✅ Emergency fix complete!"
echo "============================================================"
echo ""
echo "🔊 Test your speakers now:"
echo "   • Open a music player"
echo "   • Play some audio"
echo "   • Verify speakers work normally"
echo ""
echo "📋 If speakers work:"
echo "   Continue with: python3 find_monitor_device.py"
echo ""
echo "📋 If speakers still don't work:"
echo "   systemctl --user restart pipewire pipewire-pulse"
echo ""
echo "📋 If nothing works:"
echo "   Reboot your computer"
echo ""
echo "============================================================"