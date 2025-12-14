#!/bin/bash
# Cross-Platform Audio Streamer Launcher with Auto-Restart
# Works on Linux and macOS
# This script runs server.py directly (not via launcher.py)

echo "============================================================"
echo "    System Audio Streamer - Auto-Restart Enabled"
echo "============================================================"
echo ""

# Get script directory and project root
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/../.." && pwd )"

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3."
    exit 1
fi

echo "✅ Python 3 found"
echo ""

# Check if config exists
CONFIG_PATH="$PROJECT_ROOT/config/device_config.json"
if [ ! -f "$CONFIG_PATH" ]; then
    echo "⚠️  device_config.json not found at $CONFIG_PATH"
    echo ""
    echo "📋 First-time setup required:"
    echo "   1. Run: cd $PROJECT_ROOT/scripts/setup"
    echo "   2. Run: python3 find_monitor_device.py"
    echo "      (Finds capture device)"
    echo "   3. Run: python3 test_audio.py"
    echo "      (Test with music)"
    echo ""
    read -p "Continue anyway? (y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Verify monitor is set as default (Linux only)
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    if command -v pactl &> /dev/null; then
        DEFAULT_SOURCE=$(pactl get-default-source 2>/dev/null)
        if [[ ! "$DEFAULT_SOURCE" == *"monitor"* ]]; then
            echo "⚠️  Default input is NOT a monitor!"
            echo "   Current: $DEFAULT_SOURCE"
            echo ""
            echo "🔧 Quick fix:"
            echo "   cd $PROJECT_ROOT/scripts/setup"
            echo "   python3 find_monitor_device.py"
            echo ""
            read -p "Continue anyway? (y/n): " -n 1 -r
            echo
            if [[ ! $REPLY =~ ^[Yy]$ ]]; then
                exit 1
            fi
        else
            echo "✅ Default input is a monitor (system audio)"
            echo "   Source: $DEFAULT_SOURCE"
            echo ""
        fi
    fi
fi

echo "============================================================"
echo "  Starting Server"
echo "============================================================"
echo ""

restart_count=0

while true; do
    echo "[$(date '+%H:%M:%S')] Starting Audio Server..."
    if [ $restart_count -gt 0 ]; then
        echo "(Restart #$restart_count)"
    fi
    echo "------------------------------------------------------------"

    # Run server.py from src directory
    cd "$PROJECT_ROOT/src"
    python3 server.py
    exit_code=$?

    # If server exits cleanly (Ctrl+C), don't restart
    if [ $exit_code -eq 0 ]; then
        echo ""
        echo "============================================================"
        echo "  Server stopped cleanly. Exiting..."
        echo "============================================================"
        break
    fi

    # Server crashed, restart after delay
    restart_count=$((restart_count + 1))
    echo ""
    echo "============================================================"
    echo "  ⚠️  Server crashed (exit code: $exit_code)"
    echo "  Restarting in 3 seconds..."
    echo "============================================================"
    sleep 3
done

echo ""
echo "✅ Shutdown complete"