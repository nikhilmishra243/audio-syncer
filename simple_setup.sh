#!/bin/bash
# Simple Setup - Just the essentials, NO complications!

echo "============================================================"
echo "  Simple Audio Streaming Setup"
echo "============================================================"
echo ""

# Step 1: Set monitor as default
echo "STEP 1: Setting monitor as default input..."
echo "------------------------------------------------------------"

DEFAULT_SINK=$(pactl get-default-sink)
MONITOR_SOURCE="${DEFAULT_SINK}.monitor"

echo "Current output: $DEFAULT_SINK"
echo "Setting monitor: $MONITOR_SOURCE"
echo ""

pactl set-default-source "$MONITOR_SOURCE"

if [ $? -eq 0 ]; then
    echo "✅ Monitor set as default input"
else
    echo "❌ Failed to set monitor"
    exit 1
fi

echo ""

# Step 2: Verify
echo "STEP 2: Verifying setup..."
echo "------------------------------------------------------------"

NEW_DEFAULT=$(pactl get-default-source)

if [[ "$NEW_DEFAULT" == *"monitor"* ]]; then
    echo "✅ VERIFIED: Capturing from monitor (system audio)"
    echo "   Source: $NEW_DEFAULT"
else
    echo "❌ ERROR: Not capturing from monitor!"
    echo "   Source: $NEW_DEFAULT"
    exit 1
fi

echo ""

# Step 3: Find device
echo "STEP 3: Finding capture device..."
echo "------------------------------------------------------------"

if [ -f "find_monitor_device.py" ]; then
    python3 find_monitor_device.py
else
    echo "⚠️  find_monitor_device.py not found"
fi

echo ""
echo "============================================================"
echo "✅ Setup Complete!"
echo "============================================================"
echo ""
echo "📋 Next: Test it!"
echo "   python3 test_audio.py"
echo ""
echo "   During test:"
echo "   • Play music → should show HIGH activity (>10%)"
echo "   • Speak in mic → should show LOW/NO activity (<1%)"
echo ""
echo "If test works, start server:"
echo "   python3 server.py"
echo ""
echo "============================================================"