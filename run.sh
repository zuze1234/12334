#!/bin/bash

echo "🎵 Starting Clap Detection Application..."
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found!"
    echo "Please run ./setup.sh first"
    exit 1
fi

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "❌ .env file not found!"
    echo "Please copy .env.example to .env and add your Yandex token"
    exit 1
fi

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Check if YANDEX_TOKEN is set
if ! grep -q "YANDEX_TOKEN=.*[a-zA-Z0-9]" .env; then
    echo "⚠️  Warning: YANDEX_TOKEN may not be set in .env file"
    echo "The application will run but Yandex integration will not work"
    echo ""
fi

# Run the application
echo "🚀 Starting server..."
echo "📱 Open http://localhost:5000 in your browser"
echo ""
python main.py
