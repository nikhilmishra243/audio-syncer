# launcher.py - Control panel for audio streaming server
import subprocess
import signal
import os
import sys
from flask import Flask, send_from_directory, jsonify
import psutil
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [%(funcName)s] %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
server_process = None

# Configuration
CONTROL_PORT = 5000       # Launcher control panel port
STREAM_PORT = 5001        # Audio streaming server port
GITHUB_URL = "https://github.com/nikhilmishra243"  # Replace with your GitHub
LINKEDIN_URL = "https://www.linkedin.com/in/nikhil-mishra-0039881a1"  # Replace with your LinkedIn

def get_local_ip():
    """Get local IP address"""
    import socket
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"

LOCAL_IP = get_local_ip()

def is_server_running():
    """Check if audio server is running"""
    global server_process

    if server_process and server_process.poll() is None:
        return True

    # Check if process is running by port
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            cmdline = proc.info['cmdline']
            if cmdline and 'server.py' in ' '.join(cmdline):
                server_process = proc
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    return False

# ================== ADMIN ROUTES ==================
@app.route('/admin')
def admin_panel():
    """Serve admin control panel"""
    logger.info("[admin_panel] Serving admin.html")
    return send_from_directory('../web', 'admin.html')

@app.route('/api/admin/start', methods=['POST'])
def start_server():
    """Start the audio streaming server"""
    global server_process

    logger.info("[start_server] Attempting to start audio server")

    if is_server_running():
        logger.warning("[start_server] Server already running")
        return jsonify({
            'success': False,
            'message': 'Server is already running'
        })

    try:
        # Start server.py as subprocess - path relative to src/
        server_process = subprocess.Popen(
            [sys.executable, 'server.py'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            stdin=subprocess.PIPE,
            cwd=os.path.dirname(os.path.abspath(__file__))  # Run in src/ directory
        )

        logger.info(f"[start_server] Audio server started with PID: {server_process.pid}")

        return jsonify({
            'success': True,
            'message': 'Audio server started successfully',
            'pid': server_process.pid,
            'stream_url': f'http://{LOCAL_IP}:{STREAM_PORT}/stream'
        })

    except Exception as e:
        logger.error(f"[start_server] Failed to start server: {e}")
        return jsonify({
            'success': False,
            'message': f'Failed to start server: {str(e)}'
        })

@app.route('/api/admin/stop', methods=['POST'])
def stop_server():
    """Stop the audio streaming server"""
    global server_process

    logger.info("[stop_server] Attempting to stop audio server")

    if not is_server_running():
        logger.warning("[stop_server] No server running")
        return jsonify({
            'success': False,
            'message': 'Server is not running'
        })

    try:
        if server_process:
            # Terminate the process
            server_process.terminate()
            try:
                server_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                server_process.kill()
                server_process.wait()

            logger.info("[stop_server] Audio server stopped successfully")

        # Also kill any orphaned server.py processes
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                cmdline = proc.info['cmdline']
                if cmdline and 'server.py' in ' '.join(cmdline):
                    proc.terminate()
                    logger.info(f"[stop_server] Terminated orphaned process PID: {proc.pid}")
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        server_process = None

        return jsonify({
            'success': True,
            'message': 'Audio server stopped successfully'
        })

    except Exception as e:
        logger.error(f"[stop_server] Failed to stop server: {e}")
        return jsonify({
            'success': False,
            'message': f'Failed to stop server: {str(e)}'
        })

@app.route('/api/admin/status')
def admin_status():
    """Get server status for admin"""
    running = is_server_running()

    status = {
        'running': running,
        'stream_url': f'http://{LOCAL_IP}:{STREAM_PORT}/stream' if running else None,
        'user_page_url': f'http://{LOCAL_IP}:{CONTROL_PORT}',
        'pid': server_process.pid if server_process and running else None
    }

    logger.info(f"[admin_status] Server status: {'Running' if running else 'Stopped'}")
    return jsonify(status)

# ================== USER ROUTES ==================
@app.route('/')
def user_landing():
    """Serve user landing page"""
    logger.info("[user_landing] Serving landing.html")
    return send_from_directory('../web', 'landing.html')

@app.route('/stream')
def stream_redirect():
    """Redirect to streaming server"""
    if is_server_running():
        # Redirect to actual streaming server
        from flask import redirect
        stream_url = f'http://{LOCAL_IP}:{STREAM_PORT}/stream'
        logger.info(f"[stream_redirect] Redirecting to {stream_url}")
        return redirect(stream_url)
    else:
        logger.warning("[stream_redirect] Server not running")
        return jsonify({
            'error': 'Streaming server is not running',
            'message': 'Please ask the administrator to start the server'
        }), 503

@app.route('/api/user/status')
def user_status():
    """Get server status for users"""
    running = is_server_running()

    status = {
        'online': running,
        'message': 'Server is online and ready to stream!' if running else 'Server is currently offline',
        'stream_url': f'http://{LOCAL_IP}:{STREAM_PORT}/stream' if running else None
    }

    return jsonify(status)

# ================== DEVELOPER INFO ==================
@app.route('/api/developer')
def developer_info():
    """Get developer information"""
    return jsonify({
        'name': 'Nikhil Mishra',
        'role': 'Software Developer',
        'github': GITHUB_URL,
        'linkedin': LINKEDIN_URL
    })

# ================== MAIN ==================
if __name__ == '__main__':
    print("\n" + "="*70)
    print("  AUDIO STREAMING CONTROL PANEL")
    print("="*70)
    print(f"  🔧 Admin Panel: http://{LOCAL_IP}:{CONTROL_PORT}/admin")
    print(f"  👥 User Page:   http://{LOCAL_IP}:{CONTROL_PORT}")
    print(f"  🎵 Stream URL:  http://{LOCAL_IP}:{STREAM_PORT}/stream (when started)")
    print("="*70)
    print("  Control the audio streaming server from admin panel")
    print("  Users can check status and connect from user page")
    print("="*70 + "\n")

    try:
        app.run(host='0.0.0.0', port=CONTROL_PORT, debug=False)
    except KeyboardInterrupt:
        logger.info("[main] Shutting down...")
        if is_server_running():
            stop_server()
        print("\nControl panel stopped.")
    except Exception as e:
        logger.error(f"[main] Fatal error: {e}")
        sys.exit(1)