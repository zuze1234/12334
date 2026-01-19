"""
Main Flask Application for Clap Detection
"""
import os
import logging
import time
from datetime import datetime
from flask import Flask, render_template, jsonify, request, send_from_directory
from flask_socketio import SocketIO, emit
from flask_cors import CORS
from dotenv import load_dotenv
import threading

from config import Config
from audio_detector import AudioDetector
from yandex_api import YandexHomeAPI

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__, static_folder='static', template_folder='templates')
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

config = Config()
yandex_api = None
audio_detector = None
event_history = []
is_listening = False


def init_yandex_api():
    """Initialize Yandex API"""
    global yandex_api
    try:
        token = config.get_yandex_token()
        yandex_api = YandexHomeAPI(token)
        logger.info("Yandex API initialized")
        return True
    except Exception as e:
        logger.error(f"Failed to initialize Yandex API: {e}")
        return False


def on_double_clap():
    """Handle double clap event"""
    logger.info("Double clap detected! Toggling devices...")
    
    add_event('double_clap', 'Double clap detected')
    
    if yandex_api:
        device_ids = config.get_yandex_devices()
        results = yandex_api.toggle_all_devices(device_ids)
        
        success_count = sum(1 for v in results.values() if v)
        add_event('toggle_devices', f'Toggled {success_count}/{len(device_ids)} devices')
        
        socketio.emit('device_toggled', {
            'timestamp': datetime.now().isoformat(),
            'results': results
        })
    else:
        add_event('error', 'Yandex API not initialized')


def add_event(event_type: str, message: str):
    """Add event to history"""
    event = {
        'type': event_type,
        'message': message,
        'timestamp': datetime.now().isoformat()
    }
    event_history.append(event)
    
    if len(event_history) > 100:
        event_history.pop(0)
    
    socketio.emit('event', event)


def audio_level_callback(level: float):
    """Callback for audio level updates"""
    socketio.emit('audio_level', {'level': float(level)})


def clap_callback(timestamp: float, level: float):
    """Callback for clap detection"""
    socketio.emit('clap_detected', {
        'timestamp': timestamp,
        'level': float(level)
    })


@app.route('/')
def index():
    """Serve main page"""
    return send_from_directory('.', 'index.html')


@app.route('/api/status')
def get_status():
    """Get application status"""
    return jsonify({
        'is_listening': is_listening,
        'yandex_connected': yandex_api is not None,
        'audio_level': audio_detector.get_current_level() if audio_detector else 0
    })


@app.route('/api/devices', methods=['GET'])
def get_devices():
    """Get list of Yandex devices"""
    if not yandex_api:
        return jsonify({'error': 'Yandex API not initialized'}), 500
    
    try:
        devices = yandex_api.get_devices(force_refresh=True)
        configured_ids = config.get_yandex_devices()
        
        filtered_devices = [d for d in devices if d['id'] in configured_ids]
        
        return jsonify({'devices': filtered_devices})
    except Exception as e:
        logger.error(f"Error fetching devices: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/audio-devices', methods=['GET'])
def get_audio_devices():
    """Get list of available audio input devices"""
    try:
        devices = AudioDetector.get_available_devices()
        return jsonify({'devices': devices})
    except Exception as e:
        logger.error(f"Error fetching audio devices: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/toggle', methods=['POST'])
def toggle_device():
    """Manually toggle a device"""
    if not yandex_api:
        return jsonify({'error': 'Yandex API not initialized'}), 500
    
    data = request.json
    device_id = data.get('device_id')
    
    if not device_id:
        return jsonify({'error': 'device_id required'}), 400
    
    try:
        success = yandex_api.toggle_device(device_id)
        add_event('manual_toggle', f'Manually toggled device {device_id}')
        return jsonify({'success': success})
    except Exception as e:
        logger.error(f"Error toggling device: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/calibrate', methods=['POST'])
def calibrate():
    """Start calibration"""
    if not audio_detector:
        return jsonify({'error': 'Audio detector not initialized'}), 500
    
    data = request.json or {}
    duration = data.get('duration', 3.0)
    
    try:
        add_event('calibration_start', f'Starting calibration for {duration}s')
        result = audio_detector.calibrate(duration)
        add_event('calibration_complete', f'Calibration complete. Suggested threshold: {result["suggested_threshold"]:.3f}')
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error during calibration: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/settings', methods=['GET', 'POST'])
def settings():
    """Get or update settings"""
    if request.method == 'GET':
        return jsonify({
            'audio': config.get_audio_settings(),
            'yandex_devices': config.get_yandex_devices()
        })
    
    elif request.method == 'POST':
        data = request.json
        
        if 'audio' in data:
            config.update_audio_settings(data['audio'])
            if audio_detector:
                audio_detector.update_config(data['audio'])
            add_event('settings_update', 'Audio settings updated')
        
        if 'yandex_devices' in data:
            config.update_devices(data['yandex_devices'])
            add_event('settings_update', 'Device list updated')
        
        return jsonify({'success': True})


@app.route('/api/events', methods=['GET'])
def get_events():
    """Get event history"""
    return jsonify({'events': event_history})


@app.route('/api/listening', methods=['POST'])
def set_listening():
    """Start/stop listening"""
    global is_listening, audio_detector
    
    data = request.json
    should_listen = data.get('listening', False)
    
    if should_listen and not is_listening:
        if not audio_detector:
            audio_detector = AudioDetector(config.get_audio_settings(), on_double_clap)
            audio_detector.register_level_callback(audio_level_callback)
            audio_detector.register_clap_callback(clap_callback)
        
        audio_detector.start()
        is_listening = True
        add_event('listening_start', 'Started listening for claps')
        
    elif not should_listen and is_listening:
        if audio_detector:
            audio_detector.stop()
        is_listening = False
        add_event('listening_stop', 'Stopped listening')
    
    return jsonify({'listening': is_listening})


@socketio.on('connect')
def handle_connect():
    """Handle WebSocket connection"""
    logger.info('Client connected')
    emit('status', {
        'is_listening': is_listening,
        'yandex_connected': yandex_api is not None
    })


@socketio.on('disconnect')
def handle_disconnect():
    """Handle WebSocket disconnection"""
    logger.info('Client disconnected')


@socketio.on('start_listening')
def handle_start_listening():
    """Handle start listening request"""
    global is_listening, audio_detector
    
    if not is_listening:
        if not audio_detector:
            audio_detector = AudioDetector(config.get_audio_settings(), on_double_clap)
            audio_detector.register_level_callback(audio_level_callback)
            audio_detector.register_clap_callback(clap_callback)
        
        audio_detector.start()
        is_listening = True
        add_event('listening_start', 'Started listening for claps')
        emit('status', {'is_listening': True}, broadcast=True)


@socketio.on('stop_listening')
def handle_stop_listening():
    """Handle stop listening request"""
    global is_listening
    
    if is_listening and audio_detector:
        audio_detector.stop()
        is_listening = False
        add_event('listening_stop', 'Stopped listening')
        emit('status', {'is_listening': False}, broadcast=True)


def main():
    """Main entry point"""
    logger.info("Starting Clap Detection Application")
    
    if not init_yandex_api():
        logger.warning("Running without Yandex API - check YANDEX_TOKEN in .env")
    
    port = int(os.getenv('PORT', 5000))
    host = os.getenv('HOST', '0.0.0.0')
    
    logger.info(f"Starting server on {host}:{port}")
    socketio.run(app, host=host, port=port, debug=False, allow_unsafe_werkzeug=True)


if __name__ == '__main__':
    main()
