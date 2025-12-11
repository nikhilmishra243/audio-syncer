#!/bin/bash
# Complete Setup - Safe version, NO LOOPS!

echo "============================================================"
echo "  System Audio Streaming Setup (Safe Mode)"
echo "============================================================"
echo ""

# Make scripts executable
chmod +x setup_loopback.sh start-server.sh 2>/dev/null

# Step 1: Quick audio check (safe, no loops)
echo "STEP 1: Checking audio system..."
echo "------------------------------------------------------------"

if [ -f "./setup_loopback.sh" ]; then
    timeout 10 ./setup_loopback.sh
    EXIT_CODE=$?

    if [ $EXIT_CODE -eq 124 ]; then
        echo ""
        echo "⚠️  Setup timed out (killed for safety)"
    elif [ $EXIT_CODE -ne 0 ]; then
        echo ""
        echo "⚠️  Setup had issues, continuing anyway..."
    fi
else
    echo "⚠️  setup_loopback.sh not found, skipping..."
fi

echo ""
sleep 1

# Step 2: Find capture device
echo ""
echo "STEP 2: Finding capture device..."
echo "------------------------------------------------------------"

if [ -f "find_monitor_device.py" ]; then
    python3 find_monitor_device.py

    if [ $? -ne 0 ]; then
        echo ""
        echo "❌ Could not find capture device"
        echo ""
        echo "📋 Manual steps:"
        echo "   1. Check: pactl list short sources | grep monitor"
        echo "   2. Restart audio: systemctl --user restart pipewire"
        exit 1
    fi
else
    echo "❌ find_monitor_device.py not found!"
    exit 1
fi

# Step 3: Test it
echo ""
echo "STEP 3: Testing audio capture..."
echo "------------------------------------------------------------"
echo ""
echo "📋 Play some music/audio on your computer"
echo "   Then press Enter when prompted..."
echo ""
sleep 2

if [ -f "test_audio.py" ]; then
    python3 test_audio.py
else
    echo "⚠️  test_audio.py not found, skipping test..."
fi

# Final instructions
echo ""
echo "============================================================"
echo "  Setup Complete!"
echo "============================================================"
echo ""
echo "📋 Next steps:"
echo ""
echo "1. If the test showed activity (>5%) → SUCCESS! ✅"
echo "   Start the server:"
echo "   ./start-server.sh"
echo "   OR"
echo "   python3 server.py"
echo ""
echo "2. If the test was silent (<1%):"
echo "   • Make sure audio was playing during the test"
echo "   • Run: python3 find_monitor_device.py"
echo "   • Run: python3 test_audio.py (with music playing)"
echo ""
echo "3. Connect from other devices:"
echo "   Open: http://YOUR-IP:5000"
echo ""
echo "============================================================"
echo ""
echo "💡 Commands:"
echo "   • Find device:  python3 find_monitor_device.py"
echo "   • Test audio:   python3 test_audio.py"
echo "   • Start server: ./start-server.sh"
echo "   • Fix audio:    ./emergency_fix.sh"
echo ""
echo "============================================================"