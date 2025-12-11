# server.py – Cross-platform SYSTEM AUDIO capture + Low-latency streaming
import socket
import sys
import asyncio
import platform
import subprocess
import os
import json
from threading import Thread
from flask import Flask, send_from_directory, jsonify
import sounddevice as sd
import websockets
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - [%(funcName)s] %(message)s'
)
logger = logging.getLogger(__name__)

# Audio settings - Optimized for low latency
SAMPLE_RATE = 44100
CHANNELS = 2
BLOCK = 512  # Reduced from 1024 for lower latency
PORT_HTTP = 5001  # Changed from 5000 to avoid conflict with launcher.py
PORT_WS = 9000

# ------------------ HTTP SERVER ------------------
app = Flask(__name__)

@app.route('/stream')
def stream():
    """[stream] Serve streaming client"""
    logger.info("[stream] Serving client.html (streaming interface)")
    return send_from_directory('.', 'client.html')

def get_ip():
    """[get_ip] Get local IP address"""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        logger.info(f"[get_ip] Detected IP: {ip}")
        return ip
    except Exception as e:
        logger.warning(f"[get_ip] Failed to detect IP: {e}, using 127.0.0.1")
        return "127.0.0.1"
    finally:
        s.close()

HOST = get_ip()

# ------------------ PLATFORM DETECTION ------------------
def get_platform():
    """[get_platform] Detect current operating system"""
    system = platform.system()
    logger.info(f"[get_platform] Detected OS: {system}")
    return system

# ------------------ DEVICE LISTING ------------------
def list_all_devices():
    """[list_all_devices] List all available audio devices"""
    try:
        devs = sd.query_devices()
        logger.info(f"[list_all_devices] Found {len(devs)} audio devices")
        for i, d in enumerate(devs):
            logger.debug(f"[list_all_devices] Device {i}: '{d['name']}' | in:{d['max_input_channels']} out:{d['max_output_channels']}")
        return devs
    except Exception as e:
        logger.error(f"[list_all_devices] Error listing devices: {e}")
        return []

# ------------------ WINDOWS AUDIO SETUP ------------------
def setup_windows_audio():
    """[setup_windows_audio] Setup SYSTEM AUDIO capture for Windows using WASAPI loopback"""
    logger.info("[setup_windows_audio] Setting up Windows WASAPI loopback (SYSTEM AUDIO)")

    devs = list_all_devices()
    if not devs:
        return None

    # Try WASAPI loopback on output devices - THIS CAPTURES SYSTEM AUDIO, NOT MIC
    out_candidates = [i for i, d in enumerate(devs) if d['max_output_channels'] > 0]

    for idx in out_candidates:
        try:
            logger.info(f"[setup_windows_audio] Trying WASAPI loopback on device {idx}: {devs[idx]['name']}")
            ws = sd.WasapiSettings(loopback=True)
            stream = sd.InputStream(
                device=idx,
                samplerate=SAMPLE_RATE,
                channels=CHANNELS,
                blocksize=BLOCK,
                dtype="int16",
                extra_settings=ws
            )
            stream.start()
            logger.info(f"[setup_windows_audio] ✅ Capturing SYSTEM AUDIO from device {idx}")
            return stream
        except Exception as e:
            logger.debug(f"[setup_windows_audio] WASAPI failed on device {idx}: {e}")
            continue

    # Fallback to Stereo Mix
    logger.info("[setup_windows_audio] WASAPI failed, trying Stereo Mix")
    stereo_candidates = [i for i, d in enumerate(devs) if "stereo" in d['name'].lower()]

    for idx in stereo_candidates:
        try:
            logger.info(f"[setup_windows_audio] Trying Stereo Mix on device {idx}")
            stream = sd.InputStream(
                device=idx,
                samplerate=SAMPLE_RATE,
                channels=CHANNELS,
                blocksize=BLOCK,
                dtype="int16"
            )
            stream.start()
            logger.info(f"[setup_windows_audio] ✅ Capturing from Stereo Mix")
            return stream
        except Exception as e:
            logger.debug(f"[setup_windows_audio] Stereo Mix failed: {e}")
            continue

    logger.error("[setup_windows_audio] No audio source found")
    return None

# ------------------ LINUX AUDIO SETUP ------------------
def load_audio_config():
    """[load_audio_config] Load audio configuration"""
    try:
        # Try device_config.json first (from find_monitor_device.py)
        if os.path.exists('device_config.json'):
            with open('device_config.json', 'r') as f:
                config = json.load(f)
                logger.info(f"[load_audio_config] Loaded device config: ID={config.get('device_id')}, Name={config.get('device_name')}")
                return config

        # Fallback to audio_config.json (from select_audio_source.py)
        if os.path.exists('audio_config.json'):
            with open('audio_config.json', 'r') as f:
                config = json.load(f)
                logger.info(f"[load_audio_config] Loaded audio config: {config.get('sounddevice_id', 'N/A')}")
                return config
    except Exception as e:
        logger.warning(f"[load_audio_config] Failed to load config: {e}")
    return None

def get_monitor_sources_via_pactl():
    """[get_monitor_sources_via_pactl] Find ALL monitor sources (SYSTEM AUDIO) via pactl"""
    try:
        result = subprocess.run(
            ['pactl', 'list', 'short', 'sources'],
            capture_output=True,
            text=True,
            timeout=5
        )

        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            monitors = []

            for line in lines:
                # ONLY get MONITOR sources (these capture system audio playback)
                if '.monitor' in line.lower():
                    parts = line.split()
                    if len(parts) >= 2:
                        source_name = parts[1]
                        status = parts[-1] if len(parts) > 4 else "UNKNOWN"
                        monitors.append({
                            'name': source_name,
                            'status': status
                        })
                        logger.info(f"[get_monitor_sources_via_pactl] Found monitor: {source_name} [{status}]")

            return monitors

        logger.warning("[get_monitor_sources_via_pactl] pactl failed")
    except FileNotFoundError:
        logger.warning("[get_monitor_sources_via_pactl] pactl not found")
    except Exception as e:
        logger.error(f"[get_monitor_sources_via_pactl] Error: {e}")

    return []

def setup_linux_audio():
    """[setup_linux_audio] Setup SYSTEM AUDIO capture for Linux (NOT microphone)"""
    logger.info("[setup_linux_audio] Setting up Linux SYSTEM AUDIO capture (monitors only)")

    # Priority 1: Use device_config.json (from find_monitor_device.py)
    config = load_audio_config()
    if config and 'device_id' in config:
        device_id = config['device_id']
        device_name = config.get('device_name', 'unknown')
        method = config.get('method', 'unknown')
        logger.info(f"[setup_linux_audio] Using device config: ID={device_id}, Name={device_name}, Method={method}")

        try:
            stream = sd.InputStream(
                device=device_id,
                samplerate=SAMPLE_RATE,
                channels=CHANNELS,
                blocksize=BLOCK,
                dtype="int16"
            )
            stream.start()
            logger.info(f"[setup_linux_audio] ✅ Capturing SYSTEM AUDIO via device {device_id} ({device_name})")
            return stream
        except Exception as e:
            logger.error(f"[setup_linux_audio] Failed with device config: {e}")

    # Priority 2: Use sounddevice ID from audio_config.json
    if config and config.get('use_pulse_device') and 'sounddevice_id' in config:
        device_id = config['sounddevice_id']
        device_name = config.get('sounddevice_name', 'pulse')
        logger.info(f"[setup_linux_audio] Using audio config device: {device_id} ({device_name})")

        try:
            stream = sd.InputStream(
                device=device_id,
                samplerate=SAMPLE_RATE,
                channels=CHANNELS,
                blocksize=BLOCK,
                dtype="int16"
            )
            stream.start()
            logger.info(f"[setup_linux_audio] ✅ Capturing SYSTEM AUDIO via device {device_id}")
            return stream
        except Exception as e:
            logger.error(f"[setup_linux_audio] Failed with audio config: {e}")

    # Priority 3: Get all monitor sources via pactl
    monitors = get_monitor_sources_via_pactl()

    if monitors:
        # Try RUNNING monitors first
        for monitor in monitors:
            if monitor['status'] == 'RUNNING':
                try:
                    logger.info(f"[setup_linux_audio] Trying RUNNING monitor: {monitor['name']}")
                    stream = sd.InputStream(
                        device=monitor['name'],
                        samplerate=SAMPLE_RATE,
                        channels=CHANNELS,
                        blocksize=BLOCK,
                        dtype="int16"
                    )
                    stream.start()
                    logger.info(f"[setup_linux_audio] ✅ Capturing SYSTEM AUDIO from RUNNING monitor")
                    return stream
                except Exception as e:
                    logger.debug(f"[setup_linux_audio] Failed on {monitor['name']}: {e}")

        # Try any monitor
        for monitor in monitors:
            try:
                logger.info(f"[setup_linux_audio] Trying monitor: {monitor['name']}")
                stream = sd.InputStream(
                    device=monitor['name'],
                    samplerate=SAMPLE_RATE,
                    channels=CHANNELS,
                    blocksize=BLOCK,
                    dtype="int16"
                )
                stream.start()
                logger.info(f"[setup_linux_audio] ✅ Capturing SYSTEM AUDIO from monitor")
                return stream
            except Exception as e:
                logger.debug(f"[setup_linux_audio] Failed: {e}")

    # Priority 4: Try 'pulse' and 'default' devices specifically (PipeWire compatibility)
    logger.info("[setup_linux_audio] Trying PipeWire/PulseAudio compatibility devices...")
    devs = list_all_devices()

    for i, d in enumerate(devs):
        device_name_lower = d['name'].lower()
        if device_name_lower in ['pulse', 'default'] and d['max_input_channels'] >= CHANNELS:
            try:
                logger.info(f"[setup_linux_audio] Trying {d['name']} device {i}")
                stream = sd.InputStream(
                    device=i,
                    samplerate=SAMPLE_RATE,
                    channels=CHANNELS,
                    blocksize=BLOCK,
                    dtype="int16"
                )
                stream.start()
                logger.info(f"[setup_linux_audio] ✅ Successfully initialized on device {i}")
                return stream
            except Exception as e:
                logger.debug(f"[setup_linux_audio] Failed on device {i}: {e}")
                continue

    # Priority 5: Search devices by name for 'monitor'
    logger.info("[setup_linux_audio] Searching sounddevice list for monitors...")
    for i, d in enumerate(devs):
        if 'monitor' in d['name'].lower() and d['max_input_channels'] >= CHANNELS:
            try:
                logger.info(f"[setup_linux_audio] Trying device {i}: {d['name']}")
                stream = sd.InputStream(
                    device=i,
                    samplerate=SAMPLE_RATE,
                    channels=CHANNELS,
                    blocksize=BLOCK,
                    dtype="int16"
                )
                stream.start()
                logger.info(f"[setup_linux_audio] ✅ Capturing SYSTEM AUDIO from device {i}")
                return stream
            except Exception as e:
                logger.debug(f"[setup_linux_audio] Failed on device {i}: {e}")

    logger.error("[setup_linux_audio] No monitor sources found")
    return None

# ------------------ MACOS AUDIO SETUP ------------------
def setup_macos_audio():
    """[setup_macos_audio] Setup SYSTEM AUDIO capture for macOS"""
    logger.info("[setup_macos_audio] Setting up macOS SYSTEM AUDIO capture")

    devs = list_all_devices()
    if not devs:
        return None

    # Look for BlackHole or loopback devices
    loopback_keywords = ['blackhole', 'loopback', 'soundflower', 'aggregate']

    for i, d in enumerate(devs):
        device_name_lower = d['name'].lower()
        if any(keyword in device_name_lower for keyword in loopback_keywords):
            if d['max_input_channels'] >= CHANNELS:
                try:
                    logger.info(f"[setup_macos_audio] Trying loopback device {i}: {d['name']}")
                    stream = sd.InputStream(
                        device=i,
                        samplerate=SAMPLE_RATE,
                        channels=CHANNELS,
                        blocksize=BLOCK,
                        dtype="int16"
                    )
                    stream.start()
                    logger.info(f"[setup_macos_audio] ✅ Capturing SYSTEM AUDIO from device {i}")
                    return stream
                except Exception as e:
                    logger.debug(f"[setup_macos_audio] Failed on device {i}: {e}")

    logger.error("[setup_macos_audio] No loopback device found")
    return None

# ------------------ UNIFIED AUDIO SETUP ------------------
def setup_audio_capture():
    """[setup_audio_capture] Setup SYSTEM AUDIO capture based on platform"""
    current_platform = get_platform()

    if current_platform == "Windows":
        return setup_windows_audio()
    elif current_platform == "Linux":
        return setup_linux_audio()
    elif current_platform == "Darwin":
        return setup_macos_audio()
    else:
        logger.error(f"[setup_audio_capture] Unsupported platform: {current_platform}")
        return None

# Initialize audio stream
logger.info("[main] ==============================================")
logger.info("[main] Starting SYSTEM AUDIO capture initialization")
logger.info("[main] (This captures playback audio, NOT microphone)")
logger.info("[main] ==============================================")

stream = setup_audio_capture()

if not stream:
    logger.error("[main] Failed to initialize SYSTEM AUDIO capture")
    print("\n" + "="*70)
    print("ERROR: Cannot capture SYSTEM AUDIO!")
    print("="*70)

    current_platform = get_platform()

    if current_platform == "Windows":
        print("\n🪟 Windows Setup:")
        print("Enable WASAPI Loopback or Stereo Mix to capture system audio")
        print("1. Right-click speaker icon → Sounds → Recording tab")
        print("2. Enable 'Stereo Mix' (this captures what you hear)")
        print("3. Or update audio drivers for WASAPI loopback")

    elif current_platform == "Linux":
        print("\n🐧 Linux Setup:")
        print("You need a MONITOR source (captures system audio playback)")
        print("\n✨ RECOMMENDED: Run these commands in order:")
        print("  1. ./simple_setup.sh")
        print("     (Sets monitor as default input)")
        print("  2. python3 find_monitor_device.py")
        print("     (Finds correct device)")
        print("  3. python3 test_audio.py")
        print("     (Test with music playing)")
        print("\nOR check manually:")
        print("  pactl list short sources | grep monitor")
        print("\n💡 The monitor captures what's PLAYING, not microphone!")

    elif current_platform == "Darwin":
        print("\n🍎 macOS Setup:")
        print("1. Install BlackHole: https://github.com/ExistentialAudio/BlackHole")
        print("2. Create Multi-Output Device in Audio MIDI Setup")
        print("3. Route system audio through BlackHole")

    print("="*70 + "\n")
    sys.exit(1)

logger.info("[main] ✅ SYSTEM AUDIO capture initialized")

# ------------------ LOW-LATENCY STREAMING ------------------
clients = set()

async def audio_broadcast():
    """[audio_broadcast] Low-latency audio broadcast"""
    logger.info("[audio_broadcast] Starting low-latency audio broadcast")

    while True:
        try:
            frames, overflowed = stream.read(BLOCK)
            if overflowed:
                logger.warning("[audio_broadcast] Audio buffer overflow - reduce load")

            raw = frames.tobytes()

            # Send to all clients without delay
            disconnected = []
            for ws in list(clients):
                try:
                    await ws.send(raw)
                except Exception:
                    disconnected.append(ws)

            # Clean up disconnected clients
            for ws in disconnected:
                clients.discard(ws)

            # Minimal sleep for event loop
            await asyncio.sleep(0)

        except Exception as e:
            logger.error(f"[audio_broadcast] Error: {e}")
            await asyncio.sleep(0.01)

async def ws_handler(websocket):
    """[ws_handler] Handle WebSocket connections"""
    client_addr = websocket.remote_address
    clients.add(websocket)
    logger.info(f"[ws_handler] Client connected: {client_addr} (Total: {len(clients)})")

    try:
        await asyncio.Future()
    except Exception:
        pass
    finally:
        clients.discard(websocket)
        logger.info(f"[ws_handler] Client disconnected: {client_addr} (Total: {len(clients)})")

async def ws_main():
    """[ws_main] Start WebSocket server"""
    logger.info(f"[ws_main] WebSocket server at ws://{HOST}:{PORT_WS}")
    server = await websockets.serve(
        ws_handler,
        "0.0.0.0",
        PORT_WS,
        max_size=None,
        ping_interval=None,  # Disable ping for lower latency
        ping_timeout=None
    )
    logger.info("[ws_main] WebSocket server started")
    await asyncio.gather(asyncio.Future(), audio_broadcast())

def http_start():
    """[http_start] Start HTTP server"""
    logger.info(f"[http_start] HTTP server at http://{HOST}:{PORT_HTTP}")
    app.run(host="0.0.0.0", port=PORT_HTTP, debug=False)

# ------------------ START ------------------
if __name__ == "__main__":
    print("\n" + "="*70)
    print("  AUDIO STREAMING SERVER")
    print("="*70)
    print(f"  Platform: {get_platform()}")
    print(f"  Capturing: SYSTEM AUDIO (what you hear, not microphone)")
    print(f"  Latency: ~100-200ms optimized")
    print("="*70)
    print(f"  🎵 Stream Player:")
    print(f"     http://{HOST}:{PORT_HTTP}/stream")
    print(f"  🔌 WebSocket:")
    print(f"     ws://{HOST}:{PORT_WS}")
    print("="*70)
    print("  This server is managed by launcher.py")
    print("  Press Ctrl+C to stop")
    print("="*70 + "\n")

    try:
        Thread(target=http_start, daemon=True).start()
        asyncio.run(ws_main())
    except KeyboardInterrupt:
        logger.info("[main] Server stopped by user")
        print("\nServer stopped.")
    except Exception as e:
        logger.error(f"[main] Fatal error: {e}")
        sys.exit(1)