"""
Real-time audio detection for clap events
"""
import numpy as np
import sounddevice as sd
import logging
import time
from collections import deque
from typing import Callable, Optional, Dict, Any, List
from scipy import signal
import threading


logger = logging.getLogger(__name__)


class AudioDetector:
    """Real-time audio detection with clap recognition"""
    
    def __init__(self, config: Dict[str, Any], on_double_clap: Optional[Callable] = None):
        self.sample_rate = config.get('sample_rate', 44100)
        self.chunk_size = config.get('chunk_size', 2048)
        self.threshold = config.get('threshold', 50) / 100.0
        self.min_clap_interval = config.get('min_clap_interval', 100) / 1000.0
        self.max_clap_interval = config.get('max_clap_interval', 500) / 1000.0
        self.clap_min_freq = config.get('clap_min_freq', 2000)
        self.clap_max_freq = config.get('clap_max_freq', 4000)
        self.debounce_time = config.get('debounce_time', 1000) / 1000.0
        self.selected_device = config.get('selected_device', None)
        
        self.on_double_clap = on_double_clap
        self.is_running = False
        self.stream = None
        
        self.clap_times = deque(maxlen=10)
        self.last_double_clap_time = 0
        self.current_level = 0
        self.peak_level = 0
        
        self.level_callbacks = []
        self.clap_callbacks = []
        
        self._lock = threading.Lock()
        
    def update_config(self, config: Dict[str, Any]):
        """Update detector configuration"""
        with self._lock:
            self.threshold = config.get('threshold', self.threshold * 100) / 100.0
            self.min_clap_interval = config.get('min_clap_interval', self.min_clap_interval * 1000) / 1000.0
            self.max_clap_interval = config.get('max_clap_interval', self.max_clap_interval * 1000) / 1000.0
            self.clap_min_freq = config.get('clap_min_freq', self.clap_min_freq)
            self.clap_max_freq = config.get('clap_max_freq', self.clap_max_freq)
            self.debounce_time = config.get('debounce_time', self.debounce_time * 1000) / 1000.0
            
            if 'selected_device' in config and config['selected_device'] != self.selected_device:
                self.selected_device = config['selected_device']
                if self.is_running:
                    self.stop()
                    time.sleep(0.1)
                    self.start()
    
    def register_level_callback(self, callback: Callable):
        """Register callback for audio level updates"""
        self.level_callbacks.append(callback)
    
    def register_clap_callback(self, callback: Callable):
        """Register callback for clap events"""
        self.clap_callbacks.append(callback)
    
    def _audio_callback(self, indata, frames, time_info, status):
        """Audio stream callback"""
        if status:
            logger.warning(f"Audio stream status: {status}")
        
        try:
            audio_data = indata[:, 0] if indata.ndim > 1 else indata
            
            rms = self._calculate_rms(audio_data)
            self.current_level = rms
            
            for callback in self.level_callbacks:
                try:
                    callback(rms)
                except Exception as e:
                    logger.error(f"Error in level callback: {e}")
            
            if self._is_clap(audio_data, rms):
                current_time = time.time()
                
                for callback in self.clap_callbacks:
                    try:
                        callback(current_time, rms)
                    except Exception as e:
                        logger.error(f"Error in clap callback: {e}")
                
                self._process_clap(current_time)
                
        except Exception as e:
            logger.error(f"Error in audio callback: {e}")
    
    def _calculate_rms(self, audio_data: np.ndarray) -> float:
        """Calculate RMS amplitude"""
        return np.sqrt(np.mean(audio_data**2))
    
    def _is_clap(self, audio_data: np.ndarray, rms: float) -> bool:
        """Detect if audio contains a clap sound"""
        if rms < self.threshold * 0.5:
            return False
        
        try:
            freqs, psd = signal.welch(audio_data, self.sample_rate, nperseg=min(len(audio_data), 512))
            
            clap_band_indices = np.where((freqs >= self.clap_min_freq) & (freqs <= self.clap_max_freq))[0]
            
            if len(clap_band_indices) == 0:
                return False
            
            clap_band_power = np.sum(psd[clap_band_indices])
            total_power = np.sum(psd)
            
            if total_power == 0:
                return False
            
            clap_ratio = clap_band_power / total_power
            
            is_clap = clap_ratio > 0.3 and rms > self.threshold
            
            return is_clap
            
        except Exception as e:
            logger.error(f"Error in clap detection: {e}")
            return False
    
    def _process_clap(self, current_time: float):
        """Process clap event and detect double claps"""
        with self._lock:
            if current_time - self.last_double_clap_time < self.debounce_time:
                return
            
            self.clap_times.append(current_time)
            
            if len(self.clap_times) >= 2:
                time_diff = self.clap_times[-1] - self.clap_times[-2]
                
                if self.min_clap_interval <= time_diff <= self.max_clap_interval:
                    logger.info(f"Double clap detected! Interval: {time_diff*1000:.0f}ms")
                    self.last_double_clap_time = current_time
                    
                    if self.on_double_clap:
                        try:
                            self.on_double_clap()
                        except Exception as e:
                            logger.error(f"Error in double clap callback: {e}")
    
    def start(self):
        """Start audio detection"""
        if self.is_running:
            logger.warning("Audio detector already running")
            return
        
        try:
            device_index = None
            if self.selected_device is not None:
                try:
                    device_index = int(self.selected_device)
                except (ValueError, TypeError):
                    logger.warning(f"Invalid device index: {self.selected_device}")
            
            self.stream = sd.InputStream(
                device=device_index,
                channels=1,
                samplerate=self.sample_rate,
                blocksize=self.chunk_size,
                callback=self._audio_callback
            )
            self.stream.start()
            self.is_running = True
            logger.info("Audio detector started")
            
        except Exception as e:
            logger.error(f"Error starting audio detector: {e}")
            self.is_running = False
    
    def stop(self):
        """Stop audio detection"""
        if not self.is_running:
            return
        
        try:
            if self.stream:
                self.stream.stop()
                self.stream.close()
                self.stream = None
            self.is_running = False
            logger.info("Audio detector stopped")
        except Exception as e:
            logger.error(f"Error stopping audio detector: {e}")
    
    def get_current_level(self) -> float:
        """Get current audio level"""
        return self.current_level
    
    @staticmethod
    def get_available_devices() -> List[Dict[str, Any]]:
        """Get list of available audio input devices"""
        devices = []
        try:
            device_list = sd.query_devices()
            for idx, device in enumerate(device_list):
                if device['max_input_channels'] > 0:
                    devices.append({
                        'index': idx,
                        'name': device['name'],
                        'channels': device['max_input_channels'],
                        'sample_rate': int(device['default_samplerate'])
                    })
        except Exception as e:
            logger.error(f"Error querying audio devices: {e}")
        
        return devices
    
    def calibrate(self, duration: float = 3.0) -> Dict[str, float]:
        """Run calibration to determine optimal threshold"""
        logger.info(f"Starting calibration for {duration} seconds...")
        
        levels = []
        was_running = self.is_running
        
        if not was_running:
            self.start()
        
        def collect_level(level):
            levels.append(level)
        
        self.register_level_callback(collect_level)
        
        start_time = time.time()
        while time.time() - start_time < duration:
            time.sleep(0.1)
        
        self.level_callbacks.remove(collect_level)
        
        if not was_running:
            self.stop()
        
        if levels:
            levels_array = np.array(levels)
            suggested_threshold = np.percentile(levels_array, 95)
            
            return {
                'min': float(np.min(levels_array)),
                'max': float(np.max(levels_array)),
                'mean': float(np.mean(levels_array)),
                'std': float(np.std(levels_array)),
                'suggested_threshold': float(suggested_threshold)
            }
        
        return {
            'min': 0,
            'max': 0,
            'mean': 0,
            'std': 0,
            'suggested_threshold': 0.1
        }
