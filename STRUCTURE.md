# 📁 Project Structure

Complete overview of the project file structure and organization.

```
clap-detection/
│
├── 🐍 Backend (Python)
│   ├── main.py                 # Flask application & WebSocket server
│   ├── config.py               # Configuration management
│   ├── audio_detector.py       # Audio capture & clap detection
│   └── yandex_api.py          # Yandex Smart Home API integration
│
├── 🌐 Frontend
│   └── index.html             # Single-page web application
│
├── 📦 Configuration
│   ├── requirements.txt        # Python dependencies
│   ├── .env.example           # Environment variables template
│   ├── .gitignore             # Git ignore rules
│   └── config.json            # User settings (auto-generated)
│
├── 🐳 Docker (Optional)
│   ├── Dockerfile             # Docker container definition
│   └── docker-compose.yml     # Docker Compose configuration
│
├── 🚀 Setup Scripts
│   ├── setup.sh               # Linux/macOS setup script
│   ├── setup.bat              # Windows setup script
│   ├── run.sh                 # Linux/macOS run script
│   └── run.bat                # Windows run script
│
└── 📚 Documentation
    ├── README.md              # Main documentation
    ├── QUICKSTART.md          # Quick start guide
    ├── API.md                 # API documentation
    ├── TESTING.md             # Testing guide
    └── STRUCTURE.md           # This file
```

## File Descriptions

### Backend Files

#### `main.py`
**Purpose:** Main Flask application entry point

**Key Components:**
- Flask web server
- Socket.IO WebSocket server
- REST API endpoints
- Event handling
- Background audio monitoring thread

**Dependencies:** Flask, Flask-SocketIO, Flask-CORS

---

#### `config.py`
**Purpose:** Configuration management system

**Key Components:**
- Default settings
- JSON file persistence
- Environment variable handling
- Settings validation

**Manages:**
- Audio parameters (sample rate, chunk size, thresholds)
- Device IDs
- User preferences

---

#### `audio_detector.py`
**Purpose:** Real-time audio detection and processing

**Key Components:**
- Audio input capture using sounddevice
- RMS (Root Mean Square) calculation
- FFT (Fast Fourier Transform) analysis
- Frequency filtering (2-4kHz for claps)
- Peak detection algorithm
- Double-clap timing logic
- Calibration system

**Dependencies:** sounddevice, numpy, scipy

---

#### `yandex_api.py`
**Purpose:** Yandex Smart Home API integration

**Key Components:**
- Device discovery
- State management
- Toggle operations
- Error handling
- Retry logic
- Device caching

**Dependencies:** requests

---

### Frontend Files

#### `index.html`
**Purpose:** Complete web interface

**Sections:**
1. **Status Panel**: Connection and listening state
2. **Microphone Selection**: Audio device picker
3. **Calibration Panel**: Threshold calibration tool
4. **Settings Panel**: Adjustable parameters
5. **Device Management**: Manual device control
6. **Event Log**: Real-time event history

**Features:**
- Responsive design
- Dark/light theme
- Real-time updates via WebSocket
- Interactive controls
- Visual feedback

**Dependencies:** Socket.IO client (CDN)

---

### Configuration Files

#### `requirements.txt`
Python package dependencies:
```
Flask==3.0.0              # Web framework
Flask-SocketIO==5.3.5     # WebSocket support
Flask-CORS==4.0.0         # CORS handling
python-dotenv==1.0.0      # Environment variables
sounddevice==0.4.6        # Audio capture
numpy==1.26.2             # Numerical computing
scipy==1.11.4             # Signal processing
requests==2.31.0          # HTTP requests
```

---

#### `.env.example`
Template for environment variables:
```env
YANDEX_TOKEN=your_token_here
SECRET_KEY=your_secret_key
HOST=0.0.0.0
PORT=5000
```

---

#### `.gitignore`
Excludes from version control:
- `.env` (contains secrets)
- `config.json` (user settings)
- `*.log` (log files)
- `__pycache__/` (Python cache)
- `venv/` (virtual environment)

---

#### `config.json` (Auto-generated)
Runtime settings storage:
```json
{
  "audio": {
    "sample_rate": 44100,
    "chunk_size": 2048,
    "threshold": 50,
    ...
  },
  "yandex_devices": [...]
}
```

---

### Docker Files

#### `Dockerfile`
Container definition for deployment

**Base Image:** python:3.11-slim

**Includes:**
- PortAudio libraries
- Python dependencies
- Application code

---

#### `docker-compose.yml`
Orchestration configuration

**Features:**
- Port mapping (5000:5000)
- Audio device access
- Environment variables
- Volume mounts
- Auto-restart

---

### Setup Scripts

#### `setup.sh` / `setup.bat`
Initial setup automation

**Tasks:**
1. Check Python installation
2. Create virtual environment
3. Install dependencies
4. Create `.env` from template
5. Display next steps

---

#### `run.sh` / `run.bat`
Quick start scripts

**Tasks:**
1. Verify setup
2. Activate virtual environment
3. Check configuration
4. Start application

---

### Documentation Files

#### `README.md`
Complete user documentation

**Sections:**
- Features overview
- Architecture
- Installation (Windows/macOS/Linux)
- Configuration
- Usage guide
- Troubleshooting
- API reference
- Security notes

---

#### `QUICKSTART.md`
5-minute getting started guide

**Focus:**
- Minimal steps to run
- Basic configuration
- First-time usage

---

#### `API.md`
Complete API reference

**Covers:**
- REST endpoints
- WebSocket events
- Request/response formats
- Examples in multiple languages
- Data models

---

#### `TESTING.md`
Testing guide and checklist

**Includes:**
- Manual testing procedures
- Integration tests
- Performance tests
- Troubleshooting
- Common issues

---

## Data Flow

```
┌─────────────┐
│ Microphone  │
└──────┬──────┘
       │
       v
┌────────────────┐
│ audio_detector │ ──> FFT Analysis ──> Clap Detection
└────────┬───────┘
         │
         v
    Double Clap?
         │
         v
    ┌────────┐
    │  main  │ ──> Event Logging
    └────┬───┘
         │
         v
  ┌──────────────┐
  │  yandex_api  │ ──> Toggle Devices
  └──────────────┘
         │
         v
  ┌──────────────┐
  │ Smart Lamps  │
  └──────────────┘
```

## Communication Flow

```
┌─────────┐                  ┌────────┐                 ┌──────────┐
│ Browser │ <── WebSocket ──>│  main  │<── HTTP API ──> │  Yandex  │
└─────────┘                  └────┬───┘                 └──────────┘
                                  │
                                  v
                            ┌──────────────┐
                            │audio_detector│
                            └──────────────┘
```

## Module Dependencies

```
main.py
├── config.py
├── audio_detector.py
│   ├── sounddevice
│   ├── numpy
│   └── scipy
└── yandex_api.py
    └── requests
```

## Runtime Files (Generated)

These files are created during operation:

```
├── config.json            # User settings
├── app.log               # Application logs
├── venv/                 # Virtual environment
└── __pycache__/          # Python cache
```

## Port Usage

- **5000**: HTTP server & WebSocket (default)
- Configurable via `.env` file

## Directory Permissions

### Linux/macOS
```bash
chmod +x setup.sh run.sh
```

### Windows
No special permissions needed

## File Sizes (Approximate)

```
main.py              ~8 KB
audio_detector.py    ~9 KB
yandex_api.py        ~6 KB
config.py            ~3 KB
index.html          ~30 KB
requirements.txt     <1 KB
README.md           ~12 KB
```

## Code Statistics

- **Total Lines**: ~2,000
- **Python Code**: ~800 lines
- **HTML/CSS/JS**: ~900 lines
- **Documentation**: ~1,500 lines
- **Configuration**: ~50 lines

## Technology Stack

### Backend
- **Language**: Python 3.8+
- **Framework**: Flask
- **WebSocket**: Socket.IO
- **Audio**: sounddevice + PortAudio
- **Signal Processing**: NumPy + SciPy

### Frontend
- **HTML5** + **CSS3** + **Vanilla JavaScript**
- **No build tools required**
- **CDN dependencies only**

### Infrastructure
- **Development**: Local Python server
- **Production**: Docker (optional)
- **Platform**: Cross-platform (Windows/macOS/Linux)

## Environment

### Development
```
Python 3.8+
Virtual environment (venv)
Local Flask server
```

### Production (Docker)
```
Docker container
Exposed port 5000
Volume mounts for persistence
```

## Scalability Notes

**Current Design:**
- Single-threaded audio processing
- Local audio input only
- Suitable for personal use

**Future Enhancements:**
- Multi-user support
- Remote audio streaming
- Distributed deployment
- Load balancing

## Security Considerations

**Protected:**
- OAuth tokens (via .env)
- User settings (local only)

**Not Protected:**
- No authentication on endpoints
- No HTTPS in default setup
- CORS open to all origins

**For Production:**
- Add authentication
- Enable HTTPS
- Restrict CORS
- Rate limiting
- Input validation

---

**Last Updated:** v1.0.0
