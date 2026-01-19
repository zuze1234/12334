"""
Configuration management for Clap Detection Application
"""
import os
import json
from pathlib import Path
from typing import Dict, List, Any


class Config:
    """Configuration manager for the application"""
    
    # Default audio parameters
    DEFAULT_SAMPLE_RATE = 44100
    DEFAULT_CHUNK_SIZE = 2048
    DEFAULT_THRESHOLD = 50
    DEFAULT_MIN_CLAP_INTERVAL = 100  # milliseconds
    DEFAULT_MAX_CLAP_INTERVAL = 500  # milliseconds
    DEFAULT_CLAP_MIN_FREQ = 2000  # Hz
    DEFAULT_CLAP_MAX_FREQ = 4000  # Hz
    DEFAULT_DEBOUNCE_TIME = 1000  # milliseconds
    
    def __init__(self):
        self.config_file = Path("config.json")
        self.settings = self._load_settings()
        
    def _load_settings(self) -> Dict[str, Any]:
        """Load settings from config file or create default"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading config: {e}")
                return self._default_settings()
        return self._default_settings()
    
    def _default_settings(self) -> Dict[str, Any]:
        """Return default settings"""
        return {
            'audio': {
                'sample_rate': self.DEFAULT_SAMPLE_RATE,
                'chunk_size': self.DEFAULT_CHUNK_SIZE,
                'threshold': self.DEFAULT_THRESHOLD,
                'min_clap_interval': self.DEFAULT_MIN_CLAP_INTERVAL,
                'max_clap_interval': self.DEFAULT_MAX_CLAP_INTERVAL,
                'clap_min_freq': self.DEFAULT_CLAP_MIN_FREQ,
                'clap_max_freq': self.DEFAULT_CLAP_MAX_FREQ,
                'debounce_time': self.DEFAULT_DEBOUNCE_TIME,
                'selected_device': None
            },
            'devices': [],
            'yandex_devices': [
                '19a27edd-f48b-43d5-9a53-5d913cd9272b',
                '72a33ab1-6a1d-4b98-a811-8a98bfeb873d',
                '95cf0e1e-8117-4248-a87a-f7d83a1c50b1'
            ]
        }
    
    def save_settings(self):
        """Save settings to config file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.settings, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving config: {e}")
            return False
    
    def update_audio_settings(self, settings: Dict[str, Any]):
        """Update audio settings"""
        self.settings['audio'].update(settings)
        self.save_settings()
    
    def update_devices(self, devices: List[str]):
        """Update device list"""
        self.settings['yandex_devices'] = devices
        self.save_settings()
    
    def get_yandex_token(self) -> str:
        """Get Yandex OAuth token from environment"""
        token = os.getenv('YANDEX_TOKEN')
        if not token:
            raise ValueError("YANDEX_TOKEN not found in environment variables")
        return token
    
    def get_audio_settings(self) -> Dict[str, Any]:
        """Get audio settings"""
        return self.settings['audio']
    
    def get_yandex_devices(self) -> List[str]:
        """Get list of Yandex device IDs"""
        return self.settings['yandex_devices']
