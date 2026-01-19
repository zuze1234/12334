# 🎵 Clap Detection - Yandex Smart Home Controller

Control your Yandex smart lamps with a simple double-clap gesture! This application uses real-time audio processing to detect double-claps and automatically toggle your Yandex smart devices.

## ✨ Features

- **Real-time Audio Detection**: Continuously monitors your microphone for clap sounds
- **Smart Double-Clap Recognition**: Uses FFT analysis and frequency filtering (2-4kHz range) to accurately detect claps
- **Yandex Smart Home Integration**: Seamlessly controls your Yandex smart lamps
- **Web-Based Interface**: Modern, responsive web UI with dark/light theme support
- **Calibration System**: Automatically determine optimal sensitivity settings
- **Configurable Settings**: Adjust sensitivity, clap intervals, and detection parameters
- **Real-time Monitoring**: Visual audio level meters and event logging
- **Multi-Device Support**: Control multiple devices simultaneously

## 🏗️ Architecture

### Backend Components

1. **audio_detector.py**: Real-time audio capture and clap detection
   - Uses `sounddevice` for audio input
   - Signal processing with `numpy` and `scipy`
   - RMS amplitude calculation
   - FFT analysis for frequency filtering
   - Peak detection algorithm

2. **yandex_api.py**: Yandex Smart Home API integration
   - Device management
   - State toggling
   - Error handling and retry logic

3. **main.py**: Flask application with WebSocket support
   - RESTful API endpoints
   - Real-time communication via Socket.IO
   - Background audio monitoring

4. **config.py**: Configuration management
   - Settings persistence
   - Environment variable handling

### Frontend

- Single-page web application
- Real-time updates via WebSocket
- Responsive design (mobile-friendly)
- Dark/light theme support

## 📋 Requirements

- Python 3.8 or higher
- Working microphone
- Yandex Smart Home account with OAuth token
- Internet connection for API calls

## 🚀 Installation

### Windows

1. **Install Python**
   - Download Python from [python.org](https://www.python.org/downloads/)
   - Make sure to check "Add Python to PATH" during installation

2. **Clone or download this repository**
   ```cmd
   git clone <repository-url>
   cd clap-detection
   ```

3. **Create virtual environment**
   ```cmd
   python -m venv venv
   venv\Scripts\activate
   ```

4. **Install dependencies**
   ```cmd
   pip install -r requirements.txt
   ```

5. **Configure environment variables**
   ```cmd
   copy .env.example .env
   notepad .env
   ```
   Add your Yandex OAuth token to the `.env` file.

6. **Run the application**
   ```cmd
   python main.py
   ```

7. **Open your browser**
   Navigate to `http://localhost:5000`

### macOS

1. **Install Python**
   ```bash
   # Using Homebrew
   brew install python@3.11
   ```

2. **Clone or download this repository**
   ```bash
   git clone <repository-url>
   cd clap-detection
   ```

3. **Run the setup script**
   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```

4. **Configure environment variables**
   ```bash
   cp .env.example .env
   nano .env
   ```
   Add your Yandex OAuth token.

5. **Activate virtual environment and run**
   ```bash
   source venv/bin/activate
   python main.py
   ```

6. **Open your browser**
   Navigate to `http://localhost:5000`

### Linux (Ubuntu/Debian)

1. **Install system dependencies**
   ```bash
   sudo apt-get update
   sudo apt-get install python3 python3-pip python3-venv portaudio19-dev
   ```

2. **Clone or download this repository**
   ```bash
   git clone <repository-url>
   cd clap-detection
   ```

3. **Run the setup script**
   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```

4. **Configure environment variables**
   ```bash
   cp .env.example .env
   nano .env
   ```
   Add your Yandex OAuth token.

5. **Activate virtual environment and run**
   ```bash
   source venv/bin/activate
   python main.py
   ```

6. **Open your browser**
   Navigate to `http://localhost:5000`

## 🔑 Getting Yandex OAuth Token

1. Go to [Yandex OAuth](https://oauth.yandex.ru/)
2. Create a new application or use existing one
3. Request access to Yandex Smart Home API
4. Get your OAuth token
5. Add it to your `.env` file:
   ```
   YANDEX_TOKEN=your_token_here
   ```

## ⚙️ Configuration

### Audio Settings

- **Sample Rate**: 44100 Hz (default)
- **Chunk Size**: 2048 samples (default)
- **Clap Frequency Range**: 2-4 kHz
- **Double-Clap Window**: 100-500ms (configurable)
- **Sensitivity Threshold**: 0-100% (adjustable via UI)

### Device Configuration

The application is pre-configured with three Yandex device IDs:
- Device 1: `19a27edd-f48b-43d5-9a53-5d913cd9272b`
- Device 2: `72a33ab1-6a1d-4b98-a811-8a98bfeb873d`
- Device 3: `95cf0e1e-8117-4248-a87a-f7d83a1c50b1`

To modify devices, edit the `config.json` file after first run or update `config.py`.

## 🎯 Usage Guide

### 1. Initial Setup

1. **Select Microphone**: Choose your input device from the dropdown
2. **Calibrate**: Click "Start Calibration" and clap a few times
3. **Apply Settings**: Click "Apply Suggested Threshold" after calibration
4. **Save Settings**: Click "Save Settings" to persist your configuration

### 2. Start Listening

1. Click the "▶️ Start Listening" button
2. The status indicator will turn green
3. Try a double-clap to test detection

### 3. Adjust Sensitivity

- Use the **Sensitivity** slider to adjust detection threshold
- Higher values = less sensitive (only loud sounds detected)
- Lower values = more sensitive (may cause false positives)

### 4. Fine-tune Intervals

- **Min Clap Interval**: Minimum time between two claps (default: 100ms)
- **Max Clap Interval**: Maximum time between two claps (default: 500ms)

### 5. Manual Control

- Use the "Toggle" buttons in the Devices panel to manually control lamps
- Useful for testing connectivity

## 📊 Monitoring

### Real-time Audio Level

- Visual bar shows current microphone input level
- Helps verify microphone is working properly

### Event Log

- Shows all detected events (claps, toggles, errors)
- Auto-scrolls to show latest events
- Can be cleared using "Clear Log" button

## 🐛 Troubleshooting

### Microphone Not Working

**Problem**: No audio level showing
- **Solution**: Check microphone permissions in your OS
- **Windows**: Settings → Privacy → Microphone
- **macOS**: System Preferences → Security & Privacy → Microphone
- **Linux**: Check ALSA/PulseAudio configuration

### False Positives

**Problem**: Lights toggle on random sounds
- **Solution**: Increase sensitivity threshold (higher value = less sensitive)
- Try recalibrating in a quieter environment
- Increase minimum clap interval

### Not Detecting Claps

**Problem**: Claps not recognized
- **Solution**: Decrease sensitivity threshold
- Ensure microphone is not too far away
- Try clapping louder or closer to microphone
- Recalibrate the system

### Yandex API Errors

**Problem**: "Yandex Disconnected" status
- **Solution**: Check your OAuth token in `.env` file
- Verify token has not expired
- Check internet connection
- Verify device IDs are correct

### Port Already in Use

**Problem**: "Port 5000 is already in use"
- **Solution**: Change port in `.env` file:
  ```
  PORT=5001
  ```
  Or kill the process using port 5000

### Python Dependencies Issues

**Problem**: Import errors or missing modules
- **Solution**: 
  ```bash
  pip install --upgrade pip
  pip install -r requirements.txt --force-reinstall
  ```

### Audio Library Issues (Linux)

**Problem**: `sounddevice` fails to initialize
- **Solution**: Install PortAudio development files
  ```bash
  sudo apt-get install portaudio19-dev python3-pyaudio
  ```

## 🔒 Security Notes

- **Never commit your `.env` file** to version control
- Keep your Yandex OAuth token secure
- The application runs on localhost by default
- For remote access, consider using a reverse proxy with HTTPS

## 🛠️ Advanced Configuration

### Changing Audio Parameters

Edit `config.py` to modify default audio parameters:

```python
DEFAULT_SAMPLE_RATE = 44100
DEFAULT_CHUNK_SIZE = 2048
DEFAULT_CLAP_MIN_FREQ = 2000  # Hz
DEFAULT_CLAP_MAX_FREQ = 4000  # Hz
```

### Adding More Devices

1. Get device IDs from Yandex Smart Home app
2. Add to `config.json`:
   ```json
   {
     "yandex_devices": [
       "device-id-1",
       "device-id-2",
       "device-id-3"
     ]
   }
   ```

### Custom Event Handlers

Modify `main.py` to add custom actions on double-clap:

```python
def on_double_clap():
    # Your custom code here
    logger.info("Double clap detected!")
    # Add additional actions
```

## 📝 API Endpoints

### REST API

- `GET /` - Serve web interface
- `GET /api/status` - Get application status
- `GET /api/devices` - Get list of Yandex devices
- `GET /api/audio-devices` - Get available audio input devices
- `POST /api/toggle` - Manually toggle a device
- `POST /api/calibrate` - Start calibration
- `GET /api/settings` - Get current settings
- `POST /api/settings` - Update settings
- `GET /api/events` - Get event history
- `POST /api/listening` - Start/stop listening

### WebSocket Events

- `connect` - Client connected
- `status` - Status update
- `audio_level` - Real-time audio level
- `clap_detected` - Clap detected event
- `device_toggled` - Device state changed
- `event` - General event notification

## 🐳 Docker Deployment (Optional)

A Docker setup is available for easy deployment:

```bash
# Build image
docker build -t clap-detection .

# Run container
docker run -d -p 5000:5000 --device /dev/snd -e YANDEX_TOKEN=your_token clap-detection
```

Note: Docker requires special configuration for audio access.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## 📄 License

This project is provided as-is for educational and personal use.

## 🙏 Acknowledgments

- Uses Yandex Smart Home API
- Built with Flask and Socket.IO
- Audio processing with NumPy and SciPy
- UI inspired by modern design principles

## 📞 Support

For issues and questions:
1. Check the Troubleshooting section
2. Review the event log in the web interface
3. Check `app.log` for detailed error messages
4. Verify your configuration in `.env` and `config.json`

## 🔄 Version History

### v1.0.0 (Initial Release)
- Real-time clap detection
- Yandex Smart Home integration
- Web-based interface
- Calibration system
- Configurable settings
- Event logging
- Dark/light theme support

---

**Enjoy controlling your smart home with claps! 👏💡**
