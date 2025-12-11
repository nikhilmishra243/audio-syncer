# 🎵 Cross-Platform System Audio Streamer

**Stream whatever is PLAYING on your computer (music, videos, games) to any device over LAN with admin control panel!**

> ⚡ **Key Point**: This captures **SYSTEM AUDIO** (what you hear through speakers/headphones), **NOT** microphone input!

## ✨ Features

* **🎵 System Audio Streaming** - Captures what's playing (Spotify, YouTube, games, etc.)
* **🎛️ Admin Control Panel** - Start/stop server with beautiful web interface
* **👥 User Landing Page** - Easy access for end users with status indicators
* **📱 Browser-Based** - No apps needed on receiving devices
* **⚡ Low Latency** - Optimized for ~100-200ms delay
* **🌐 Cross-Platform** - Windows, Linux, macOS support
* **🔀 Multi-Device** - Stream to unlimited devices simultaneously
* **🎛️ Output Selection** - Choose which audio output to capture (speakers/headphones)
* **💪 Production Ready** - Auto-restart and robust error handling

---

## 📋 Platform Support

| Platform | Audio Capture Method | Status |
|----------|---------------------|---------|
| **Windows** | WASAPI Loopback / Stereo Mix | ✅ Fully Supported |
| **Linux** | PulseAudio / PipeWire Monitor | ✅ Fully Supported |
| **macOS** | BlackHole / Loopback | ✅ Fully Supported |

---

## 🚀 Quick Start (4 Steps!)

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Choose Audio Source (IMPORTANT!)
```bash
python3 select_audio_source.py
```
This shows your audio outputs (speakers, headphones, etc.) and lets you choose which one to capture.

### Step 3: Start Control Panel
```bash
python3 launcher.py
```

You'll see:
```
====================================================================
  AUDIO STREAMING CONTROL PANEL
====================================================================
  🔧 Admin Panel: http://192.168.1.109:5000/admin
  👥 User Page:   http://192.168.1.109:5000
  🎵 Stream URL:  http://192.168.1.109:5001/stream (when started)
====================================================================
```

### Step 4: Start Streaming

**As Admin:**
1. Open `http://YOUR-IP:5000/admin`
2. Click **"Start Server"**
3. Share user page URL with others

**As User:**
1. Open `http://YOUR-IP:5000`
2. Click **"Start Streaming"**
3. Enjoy the audio! 🎵

---

## 💡 Understanding System Audio vs Microphone

**This tool captures SYSTEM AUDIO:**
- ✅ Music playing in Spotify
- ✅ YouTube videos
- ✅ Game sounds
- ✅ Any audio from any app

**NOT microphone:**
- ❌ Your voice
- ❌ Ambient room sounds

Think of it as "capturing what's coming OUT of your speakers/headphones", not what's going IN through a mic.

---

## 🎯 System Architecture

### Three-Tier Interface

```
┌─────────────────────────────────┐
│     ADMIN CONTROL PANEL         │
│     http://IP:5000/admin        │
│  ✅ Start/Stop Server           │
│  ✅ Server Status               │
│  ✅ Developer Info              │
└────────────┬────────────────────┘
             │
             │ Controls
             ↓
┌─────────────────────────────────┐
│     AUDIO STREAMING SERVER      │
│     http://IP:5001/stream       │
│  🎵 System Audio Capture        │
│  🔌 WebSocket (Port 9000)       │
└────────────┬────────────────────┘
             │
             │ Streams to
             ↓
┌─────────────────────────────────┐
│     USER LANDING PAGE           │
│     http://IP:5000              │
│  📱 Status Indicator            │
│  🎵 Start Streaming Button      │
└─────────────────────────────────┘
```

### Port Architecture

| Service | Port | Purpose |
|---------|------|---------|
| **Control Panel** | 5000 | Admin panel + User landing page |
| **Streaming Server** | 5001 | Audio stream player (client.html) |
| **WebSocket** | 9000 | Real-time audio data stream |

---

## 🎛️ Interface Overview

### 1. Admin Control Panel (`/admin`)

**Purpose:** Manage the audio streaming server

**Features:**
- ✅ One-click Start/Stop server
- ✅ Real-time server status (Online/Offline)
- ✅ Stream URL display when active
- ✅ User page URL for sharing
- ✅ Developer profile with GitHub/LinkedIn links
- ✅ Beautiful glassmorphism UI with animations

**Who uses it:** System administrator

**Access:** `http://YOUR-IP:5000/admin`

### 2. User Landing Page (`/`)

**Purpose:** Entry point for end users

**Features:**
- ✅ Clean, simple interface
- ✅ Server status indicator (Green = Online, Red = Offline)
- ✅ "Start Streaming" button
- ✅ Auto-refreshes status every 3 seconds
- ✅ Redirects to stream player when clicked
- ✅ Feature highlights (Quality, Latency, Multi-device)
- ✅ Mobile responsive design

**Who uses it:** End users

**Access:** `http://YOUR-IP:5000`

### 3. Stream Player (`/stream`)

**Purpose:** Actual audio playback interface

**Features:**
- ✅ Play/Pause controls
- ✅ Real-time audio streaming via WebSocket
- ✅ Connection status display
- ✅ Visual audio indicators
- ✅ Low-latency playback (~100-200ms)

**Who uses it:** Anyone listening to the stream

**Access:** `http://YOUR-IP:5001/stream`

---

## 📋 Usage Workflow

### For Administrators

1. **Start the control panel:**
   ```bash
   python3 launcher.py
   ```

2. **Open admin panel:**
   ```
   http://YOUR-IP:5000/admin
   ```

3. **Click "Start Server":**
   - Audio streaming server launches automatically
   - Status changes to "Server Online" (green)
   - Stream URLs become available

4. **Share the user page URL:**
   ```
   http://YOUR-IP:5000
   ```
   Send this link to users who want to listen

5. **When done, click "Stop Server":**
   - Streaming stops
   - All resources released
   - Status changes to "Server Offline"

### For End Users

1. **Open the user page:**
   ```
   http://YOUR-IP:5000
   ```

2. **Check server status:**
   - 🟢 Green = Server Online (ready to stream)
   - 🔴 Red = Server Offline (wait for admin)
   - Status auto-refreshes every 3 seconds

3. **Click "Start Streaming":**
   - Automatically redirects to stream player
   - Player opens at `http://YOUR-IP:5001/stream`

4. **Click "Play Stream" in the player:**
   - WebSocket connection establishes
   - Audio starts streaming!

5. **Play music on server computer:**
   - Any audio (Spotify, YouTube, games) streams to all connected devices
   - Enjoy low-latency audio! 🎵

---

## 🔧 Installation & Setup

### 1. Install Python Dependencies

```bash
pip install -r requirements.txt
```

**Required packages:**
- flask
- sounddevice
- websockets
- psutil

**Platform-specific dependencies:**

<details>
<summary><b>Linux (Ubuntu/Debian)</b></summary>

```bash
# Install PortAudio development files
sudo apt-get update
sudo apt-get install portaudio19-dev python3-pyaudio

# Ensure PulseAudio/PipeWire is running
systemctl --user status pulseaudio
# or
systemctl --user status pipewire
```
</details>

<details>
<summary><b>Linux (Fedora/RHEL)</b></summary>

```bash
sudo dnf install portaudio-devel python3-devel
```
</details>

<details>
<summary><b>Linux (Arch)</b></summary>

```bash
sudo pacman -S portaudio python-pyaudio
```
</details>

<details>
<summary><b>macOS</b></summary>

```bash
# Usually works out of the box, but if needed:
brew install portaudio
```
</details>

### 2. Platform-Specific Audio Setup

<details>
<summary><b>🪟 Windows Setup</b></summary>

**Option 1: WASAPI Loopback (Recommended)**
- Works automatically if you have an audio output device
- No additional setup needed!

**Option 2: Stereo Mix (Fallback)**
1. Right-click the **speaker icon** in taskbar
2. Select **Sounds** → **Recording** tab
3. Right-click → **Show Disabled Devices**
4. Enable **Stereo Mix**
5. Set as **Default Device**

</details>

<details>
<summary><b>🐧 Linux Setup</b></summary>

**PulseAudio (Most Common)**

Check if monitor source exists:
```bash
pactl list short sources | grep monitor
```

You should see a device with "monitor" in the name (e.g., `alsa_output.pci-0000_00_1f.3.analog-stereo.monitor`)

If not found, ensure PulseAudio is running:
```bash
systemctl --user start pulseaudio
```

**PipeWire (Modern Distros)**

PipeWire provides PulseAudio compatibility, so monitor sources work the same way:
```bash
pactl list short sources | grep monitor
```

**Setup Helper (Recommended):**
```bash
# Run audio device selector
python3 select_audio_source.py

# Or use automated setup
python3 find_monitor_device.py
```

**Troubleshooting:**
```bash
# Restart audio server
systemctl --user restart pulseaudio
# or for PipeWire
systemctl --user restart pipewire pipewire-pulse
```

</details>

<details>
<summary><b>🍎 macOS Setup</b></summary>

macOS requires a virtual audio device for system audio capture.

**Option 1: BlackHole (Recommended - Free)**

1. Download from: https://github.com/ExistentialAudio/BlackHole
2. Install the 2ch version
3. Create an **Aggregate Device** in **Audio MIDI Setup**:
   - Open **Audio MIDI Setup** (Applications → Utilities)
   - Click **+** → **Create Aggregate Device**
   - Check both your **output device** and **BlackHole 2ch**
   - Ensure **Drift Correction** is enabled for BlackHole
4. Create a **Multi-Output Device**:
   - Click **+** → **Create Multi-Output Device**
   - Check your **output device** and **BlackHole 2ch**
5. Set **Multi-Output Device** as your system output in Sound preferences

**Option 2: Loopback (Commercial)**
- Purchase from: https://rogueamoeba.com/loopback/
- More user-friendly but costs ~$99

</details>

These links appear in the footer of the admin control panel.

---

## 🛠️ Configuration

### Port Configuration

In `launcher.py`:
```python
CONTROL_PORT = 5000  # Control panel (admin + user pages)
STREAM_PORT = 5001   # Audio streaming server
```

In `server.py`:
```python
SAMPLE_RATE = 44100  # Audio sample rate (Hz)
CHANNELS = 2         # Stereo (2) or Mono (1)
BLOCK = 512          # Buffer size (lower = less latency)
PORT_HTTP = 5001     # Must match STREAM_PORT in launcher.py
PORT_WS = 9000       # WebSocket port
```

### Latency Tuning

Adjust `BLOCK` size in `server.py` for latency vs stability trade-off:

```python
BLOCK = 256   # Lower latency (~100ms), higher CPU usage
BLOCK = 512   # Balanced (default, ~150ms)
BLOCK = 1024  # Higher latency (~200ms), lower CPU usage
```

**Note:** Network latency adds 50-100ms regardless of buffer size.

---

## 🔧 Troubleshooting

### 🎤 "It's capturing my microphone, not system audio!"

**This is the #1 issue - here's how to fix it:**

1. **Run the audio source selector:**
   ```bash
   python3 select_audio_source.py
   ```

2. **Look for devices with "Monitor" status:**
   ```
   ID   Description                  Status     Monitor
   0    Built-in Speakers            RUNNING    ✅ ACTIVE
   1    Headphones                   IDLE       ✅ Ready
   ```

3. **Select the output device where audio is PLAYING**

4. **Test it:**
   ```bash
   python3 test_audio.py
   ```
   Play some music and watch if the meter shows activity.

5. **If still wrong:**
   - Linux: Check `pactl list short sources | grep monitor`
   - You should see `.monitor` devices
   - If none, restart audio: `systemctl --user restart pipewire`

### "Failed to start server" in Admin Panel

**Possible causes:**

1. **Port already in use:**
   ```bash
   # Check if port 5001 is available
   sudo lsof -i :5001
   
   # Kill process if needed
   sudo kill -9 <PID>
   ```

2. **Audio device not configured:**
   ```bash
   # Run device configuration
   python3 find_monitor_device.py
   ```

3. **Python dependencies missing:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Check launcher.py console output for detailed error messages**

### 404 Error on /stream

**Solution:**
- Ensure you clicked **"Start Server"** in admin panel first
- Check if `server.py` is running: `ps aux | grep server.py`
- Verify ports 5001 and 9000 are not blocked by firewall

### "Server Offline" on User Page

**Solution:**
- Admin needs to start the server from admin panel (`http://IP:5000/admin`)
- Check admin panel shows "Server Online" status
- Verify `launcher.py` is running

### Connection Errors in Stream Player

**Firewall Configuration:**

```bash
# Windows
netsh advfirewall firewall add rule name="Audio Streamer Control" dir=in action=allow protocol=TCP localport=5000
netsh advfirewall firewall add rule name="Audio Streamer Server" dir=in action=allow protocol=TCP localport=5001,9000

# Linux (ufw)
sudo ufw allow 5000/tcp
sudo ufw allow 5001/tcp
sudo ufw allow 9000/tcp

# Linux (firewalld)
sudo firewall-cmd --permanent --add-port=5000/tcp
sudo firewall-cmd --permanent --add-port=5001/tcp
sudo firewall-cmd --permanent --add-port=9000/tcp
sudo firewall-cmd --reload

# macOS
# Usually works without firewall changes, but check:
# System Preferences → Security & Privacy → Firewall
```

### Audio Quality Issues

- Increase `BLOCK` size in `server.py` for more stability
- Check network bandwidth (use 5GHz WiFi or wired connection)
- Reduce number of connected clients
- Close bandwidth-heavy applications on server

### High Latency (>500ms delay)

**Current optimized latency: ~100-200ms**

If experiencing higher latency:
1. **Network**: Use wired connection or 5GHz WiFi
2. **Server**: Reduce `BLOCK = 512` to `BLOCK = 256` in server.py
3. **Client**: Close other browser tabs
4. **System**: Close resource-heavy applications

### Admin Panel Not Loading

**Check:**
1. Is `launcher.py` running?
2. Can you access `http://localhost:5000/admin` on the server?
3. Are files `admin.html` and `landing.html` in the same directory?
4. Check console output for errors

### WebSocket Connection Failed

**Verify:**
1. Server is running (check admin panel status)
2. Port 9000 is not blocked:
   ```bash
   sudo lsof -i :9000
   ```
3. Browser console for specific error messages (F12 → Console)

---

## 📁 File Structure

```
.
├── launcher.py             # Control panel server (MAIN - run this!)
├── server.py              # Audio streaming server (managed by launcher)
├── admin.html             # Admin control panel UI
├── landing.html           # User landing page
├── client.html            # Audio stream player interface
├── select_audio_source.py # Audio device selector
├── find_monitor_device.py # Auto-detect monitor source (Linux)
├── test_audio.py          # Audio capture tester
├── requirements.txt       # Python dependencies
├── README.md              # This file
└── LICENSE                # MIT License
```

---

## 🔬 Technical Details

### Architecture Flow

```
┌─────────────────────────────────────────────────────────────┐
│                    launcher.py                              │
│           Control Panel Server (Port 5000)                  │
│  ┌──────────────────┐         ┌─────────────────┐           │
│  │  Admin Panel     │         │  User Landing   │           │
│  │  /admin          │         │  /              │           │
│  │  - Start Server  │         │  - Status Check │           │
│  │  - Stop Server   │         │  - Redirect     │           │
│  │  - Status        │         │  - Auto-refresh │           │
│  └────────┬─────────┘         └─────────────────┘           │
│           │ Manages                                         │
└───────────┼─────────────────────────────────────────────────┘
            │
            ▼
┌─────────────────────────────────────────────────────────────┐
│                      server.py                              │
│            Audio Streaming Server (Port 5001)               │
│                                                             │
│  ┌─────────────────────────────────────────────────┐        │
│  │             System Audio Capture                │        │
│  │   WASAPI / PulseAudio Monitor / BlackHole       │        │
│  └───────────────────┬─────────────────────────────┘        │
│                      │                                      │
│                      ▼                                      │
│  ┌─────────────────────────────────────────────────┐        │
│  │          WebSocket Broadcast (Port 9000)        │        │
│  │       Real-time PCM Audio Stream                │        │
│  └───────────────────┬─────────────────────────────┘        │
│                      │                                      │
│                      ▼                                      │
│  ┌─────────────────────────────────────────────────┐        │
│  │         HTTP Server (Port 5001)                 │        │
│  │           Serves client.html                    │        │
│  └─────────────────────────────────────────────────┘        │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│                  client.html (Browsers)                     │
│              WebAudio API Decoder & Player                  │
│         Multiple devices can connect simultaneously         │
└─────────────────────────────────────────────────────────────┘
```

### Tech Stack

| Layer | Technology |
|-------|-----------|
| **Control Panel** | Flask, Python subprocess management, psutil |
| **Audio Capture** | sounddevice + platform-specific APIs |
| **Streaming Backend** | Python, asyncio, WebSockets |
| **Web Server** | Flask (HTTP), websockets library |
| **Frontend** | HTML5, CSS3 (Glassmorphism), JavaScript |
| **Audio Playback** | WebAudio API, WebSocket client |
| **Protocol** | Raw PCM audio over WebSocket |

### Performance Metrics

- **Latency:** ~100-200ms (network + buffer + decode)
- **Bitrate:** ~1.4 Mbps for stereo 44.1kHz 16-bit
- **CPU Usage:**
   - Control panel: <1%
   - Audio server: ~2-5% on modern systems
- **Memory:** ~50-100 MB total
- **Network:** Works on LAN, can work over WAN with port forwarding
- **Concurrent Clients:** Tested with 10+ simultaneous connections

---

## 📱 Mobile Access

All interfaces are fully responsive and work perfectly on mobile devices!

**From Phone/Tablet:**

1. **Find your server IP** from launcher output
2. **Open browser** on mobile device
3. **Navigate to:** `http://SERVER-IP:5000`
4. **Tap "Start Streaming"**
5. **Tap "Play Stream"** in the player
6. **Enjoy wireless audio!** 🎵

**Pro Tips:**
- Use 5GHz WiFi for better performance
- Keep screen on during streaming
- Add to home screen for quick access

---

## 🚀 Advanced Usage

### Running as Background Service (Linux)

Create a systemd service for auto-start:

```bash
# Create service file
sudo nano /etc/systemd/system/audio-streamer.service
```

```ini
[Unit]
Description=Audio Streaming Control Panel
After=network.target

[Service]
Type=simple
User=YOUR_USERNAME
WorkingDirectory=/path/to/audio-streamer
ExecStart=/usr/bin/python3 /path/to/audio-streamer/launcher.py
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start
sudo systemctl enable audio-streamer
sudo systemctl start audio-streamer

# Check status
sudo systemctl status audio-streamer
```

### Port Forwarding for Remote Access

To access over the internet:

1. **Configure router port forwarding:**
   - External Port 5000 → Internal IP:5000
   - External Port 5001 → Internal IP:5001
   - External Port 9000 → Internal IP:9000

2. **Find your public IP:**
   ```bash
   curl ifconfig.me
   ```

3. **Access from anywhere:**
   ```
   http://YOUR-PUBLIC-IP:5000
   ```

**Security Note:** Consider using a reverse proxy (nginx) with HTTPS for production use.

### Multi-Room Audio Setup

Run multiple streaming servers on different ports for different rooms:

1. Copy project to separate directories
2. Edit `launcher.py` in each:
   ```python
   CONTROL_PORT = 5000  # Room 1
   STREAM_PORT = 5001
   ```
   ```python
   CONTROL_PORT = 5010  # Room 2
   STREAM_PORT = 5011
   ```
3. Start each launcher separately

---

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Test on all platforms if possible
4. Submit a pull request with detailed description

**Areas for contribution:**
- Additional audio source detection methods
- UI/UX improvements
- Performance optimizations
- Documentation translations
- Mobile app development

---

## 📄 License

MIT License - See [LICENSE](LICENSE) file for details

You are free to use, modify, and distribute this software. No warranties provided.

---

## 🙏 Acknowledgments

- Original Windows-only version by the community
- Cross-platform enhancements for wider compatibility
- BlackHole audio driver for macOS support
- PulseAudio/PipeWire teams for Linux audio infrastructure
- Flask and asyncio communities
- WebAudio API for browser-based audio playback

---

## 📧 Support & Contact

**Found a bug?** Open an issue on GitHub  
**Have questions?** Start a discussion  
**Want to contribute?** Pull requests welcome!

**Developer Contact:**

<div align="left">

[![GitHub](https://img.shields.io/badge/GitHub-nikhilmishra243-181717?style=for-the-badge&logo=github&logoColor=white)](https://github.com/nikhilmishra243)

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Nikhil_Mishra-0A66C2?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/nikhil-mishra-0039881a1)

**Nikhil Mishra** - Software Developer

</div>
---

## 🆘 Common Issues Quick Reference

| Issue | Solution |
|-------|----------|
| Capturing microphone instead of system audio | Run `python3 select_audio_source.py` |
| 404 on /stream | Start server from admin panel first |
| Server won't start | Check ports 5001/9000 aren't in use |
| No audio playing | Verify server.py is actually capturing (check logs) |
| High latency | Reduce BLOCK size, use wired connection |
| Firewall blocking | Allow ports 5000, 5001, 9000 |
| Admin panel not loading | Check launcher.py is running |
| WebSocket connection failed | Verify port 9000 is open |

---

## ⭐ Show Your Support

If this project helped you stream audio seamlessly across devices, please give it a ⭐ on GitHub!

---

## 🎉 Ready to Stream!

```bash
# 1. Start the control panel
python3 launcher.py

# 2. Open admin panel
http://YOUR-IP:5000/admin

# 3. Click "Start Server"

# 4. Share with users
http://YOUR-IP:5000

# 5. Enjoy streaming! 🎵🚀
```

---

**Made with ❤️ by Nikhil for the audio streaming community**  
**Now with beautiful admin interface and user-friendly design