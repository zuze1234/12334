# 🚀 Quick Start Guide

Get up and running in 5 minutes!

## Prerequisites

- Python 3.8+ installed
- Working microphone
- Yandex OAuth token

## Installation Steps

### 1. Clone/Download Project
```bash
git clone <repository-url>
cd clap-detection
```

### 2. Install Dependencies

**Linux/macOS:**
```bash
./setup.sh
```

**Windows:**
```cmd
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configure

Copy `.env.example` to `.env` and add your Yandex token:

```bash
cp .env.example .env
nano .env  # or use your favorite editor
```

Add your token:
```
YANDEX_TOKEN=your_actual_token_here
```

### 4. Run

**Linux/macOS:**
```bash
source venv/bin/activate
python main.py
```

**Windows:**
```cmd
venv\Scripts\activate
python main.py
```

### 5. Open Browser

Navigate to: **http://localhost:5000**

## First Time Setup

1. **Select Microphone**: Choose from dropdown
2. **Calibrate**: Click "Start Calibration", clap 3-4 times
3. **Apply**: Click "Apply Suggested Threshold"
4. **Save**: Click "Save Settings"
5. **Start**: Click "▶️ Start Listening"
6. **Test**: Try a double-clap!

## Troubleshooting

### No audio detected?
- Check microphone permissions
- Try different microphone from dropdown
- Increase volume

### False positives?
- Increase sensitivity threshold (make it less sensitive)
- Recalibrate in quieter environment

### Yandex not connecting?
- Verify token in `.env` file
- Check internet connection
- Verify device IDs in config

## Getting Yandex Token

1. Visit: https://oauth.yandex.ru/
2. Create application
3. Request Smart Home API access
4. Get OAuth token
5. Add to `.env` file

## Need Help?

See the full [README.md](README.md) for detailed documentation.

---

**Happy clapping! 👏**
