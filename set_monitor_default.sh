#!/bin/bash
# Set Monitor Source as Default - This is the KEY to capturing system audio!

echo "============================================================"
echo "  Setting Monitor as Default Input Source"
echo "============================================================"
echo ""

# Get current default sink (audio output)
DEFAULT_SINK=$(pactl get-default-sink)

if [ -z "$DEFAULT_SINK" ]; then
    echo "❌ Could not get default sink"
    exit 1
fi

echo "✅ Current audio output: $DEFAULT_SINK"
echo ""

# Get the monitor source for this sink
MONITOR_SOURCE="${DEFAULT_SINK}.monitor"

echo "🔍 Looking for monitor: $MONITOR_SOURCE"
echo ""

# Check if this monitor exists
if pactl list short sources | grep -q "$MONITOR_SOURCE"; then
    echo "✅ Monitor source found: $MONITOR_SOURCE"
    echo ""

    # THIS IS THE KEY: Set the MONITOR as the default source!
    echo "🔧 Setting monitor as DEFAULT INPUT source..."
    pactl set-default-source "$MONITOR_SOURCE"

    if [ $? -eq 0 ]; then
        echo "✅ SUCCESS! Monitor is now the default input"
        echo ""
        echo "📋 This means:"
        echo "   • 'pulse' device will now capture from MONITOR (system audio)"
        echo "   • NOT from microphone anymore"
        echo "   • Any app using default input gets system audio"
        echo ""
    else
        echo "❌ Failed to set default source"
        exit 1
    fi
else
    echo "❌ Monitor source not found!"
    echo ""
    echo "Available sources:"
    pactl list short sources
    exit 1
fi

# Verify the change
echo "🔍 Verifying..."
NEW_DEFAULT=$(pactl get-default-source)

if [[ "$NEW_DEFAULT" == *"monitor"* ]]; then
    echo "✅ VERIFIED: Default source is now a monitor!"
    echo "   Source: $NEW_DEFAULT"
else
    echo "⚠️  Default source doesn't look like a monitor:"
    echo "   Source: $NEW_DEFAULT"
fi

echo ""
echo "============================================================"
echo "✅ Configuration Complete!"
echo "============================================================"
echo ""
echo "📋 Next steps:"
echo "   1. Test it: python3 test_audio.py"
echo "      (Play music, should show activity)"
echo "      (Speaking into mic should NOT show activity)"
echo ""
echo "   2. If test works, start server:"
echo "      python3 server.py"
echo ""
echo "============================================================"
echo ""
echo "💡 To revert to microphone later:"
echo "   pactl set-default-source <your-mic-name>"
echo ""
echo "============================================================"