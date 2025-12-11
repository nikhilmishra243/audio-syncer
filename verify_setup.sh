#!/bin/bash
# Verify Audio Setup - Check what's being captured

echo "============================================================"
echo "  Audio Setup Verification"
echo "============================================================"
echo ""

echo "🔍 Checking default audio sources..."
echo ""

# Get default sink (output)
DEFAULT_SINK=$(pactl get-default-sink)
echo "✅ Default OUTPUT (sink):"
echo "   $DEFAULT_SINK"
echo ""

# Get default source (input)
DEFAULT_SOURCE=$(pactl get-default-source)
echo "🎯 Default INPUT (source):"
echo "   $DEFAULT_SOURCE"
echo ""

# Check if default source is a monitor
if [[ "$DEFAULT_SOURCE" == *"monitor"* ]]; then
    echo "✅ CORRECT: Default input is a MONITOR"
    echo "   → Will capture SYSTEM AUDIO"
else
    echo "❌ PROBLEM: Default input is NOT a monitor"
    echo "   → Will capture MICROPHONE"
    echo ""
    echo "🔧 FIX IT:"
    echo "   ./set_monitor_default.sh"
    echo "   OR"
    echo "   python3 find_monitor_device.py"
fi

echo ""
echo "============================================================"
echo "📋 Available Sources (what can be captured):"
echo "============================================================"
echo ""

pactl list short sources | nl -w2 -s'. '

echo ""
echo "============================================================"
echo "💡 Legend:"
echo "   • Sources with '.monitor' → capture system audio output"
echo "   • Sources without '.monitor' → capture microphone input"
echo "============================================================"