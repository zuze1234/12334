#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np
import sounddevice as sd
import threading
import time
from scipy import signal
from termcolor import colored

class ClapDetector:
    def __init__(self, sample_rate=44100, chunk_size=1024):
        self.sample_rate = sample_rate
        self.chunk_size = chunk_size
        self.threshold = 0.3  # Порог громкости для хлопка
        self.clap_cooldown = 0.5  # Минимальное время между хлопками
        self.double_clap_window = 1.0  # Максимальное время между хлопками для двойного
        self.is_running = False
        self.audio_thread = None
        
        # Для детекции двойного хлопка
        self.last_clap_time = 0
        self.clap_count = 0
        
        # Характеристики частот хлопка
        self.clap_freq_min = 2000  # Минимальная частота хлопка (Гц)
        self.clap_freq_max = 8000  # Максимальная частота хлопка (Гц)
        
    def find_best_microphone(self):
        """Поиск доступных микрофонов"""
        try:
            devices = sd.query_devices()
            input_devices = []
            
            for i, device in enumerate(devices):
                if device['max_input_channels'] > 0:
                    input_devices.append({
                        'id': i,
                        'name': device['name'],
                        'channels': device['max_input_channels'],
                        'default_samplerate': device['default_samplerate']
                    })
            
            return input_devices
        except Exception as e:
            print(colored(f"✗ Ошибка поиска микрофонов: {str(e)}", "red"))
            return []
    
    def set_microphone(self, device_id):
        """Установка микрофона по ID"""
        try:
            sd.default.device = device_id
            device_info = sd.query_devices(device_id)
            print(colored(f"✓ Выбран микрофон: {device_info['name']}", "green"))
            return True
        except Exception as e:
            print(colored(f"✗ Ошибка установки микрофона: {str(e)}", "red"))
            return False
    
    def is_clap_sound(self, audio_chunk):
        """Анализ аудио-фрагмента на наличие характеристик хлопка"""
        # Вычисление уровня громкости
        rms = np.sqrt(np.mean(audio_chunk**2))
        
        if rms < self.threshold:
            return False
        
        # Анализ частотного спектра
        fft = np.fft.fft(audio_chunk)
        frequencies = np.fft.fftfreq(len(audio_chunk), 1/self.sample_rate)
        magnitude = np.abs(fft)
        
        # Фильтрация частот в диапазоне хлопка
        freq_mask = (frequencies >= self.clap_freq_min) & (frequencies <= self.clap_freq_max)
        clap_energy = np.sum(magnitude[freq_mask])
        total_energy = np.sum(magnitude)
        
        # Хлопок должен иметь значительную энергию в высокочастотном диапазоне
        if total_energy > 0 and (clap_energy / total_energy) > 0.4:
            return True
        
        return False
    
    def calibrate_threshold(self, duration=5):
        """Калибровка порога чувствительности"""
        print(colored(f"\n🔊 Калибровка микрофона в течение {duration} секунд...", "yellow"))
        print(colored("Сделайте несколько хлопков для автоматической настройки", "yellow"))
        
        try:
            # Запись фонового шума и хлопков
            audio_data = sd.rec(
                int(duration * self.sample_rate),
                samplerate=self.sample_rate,
                channels=1,
                dtype='float32'
            )
            sd.wait()
            
            # Анализ уровней громкости
            rms_levels = []
            chunk_samples = int(self.sample_rate * 0.1)  # 100ms блоки
            
            for i in range(0, len(audio_data) - chunk_samples, chunk_samples):
                chunk = audio_data[i:i + chunk_samples].flatten()
                rms = np.sqrt(np.mean(chunk**2))
                rms_levels.append(rms)
            
            if rms_levels:
                background_noise = np.percentile(rms_levels, 20)
                average_level = np.median(rms_levels)
                peak_level = np.max(rms_levels)
                
                # Установка порога между средним уровнем и пиком
                new_threshold = average_level + (peak_level - average_level) * 0.6
                self.threshold = max(new_threshold, background_noise * 3)
                
                print(colored(f"✓ Калибровка завершена", "green"))
                print(colored(f"  Фоновый шум: {background_noise:.4f}", "blue"))
                print(colored(f"  Средний уровень: {average_level:.4f}", "blue"))
                print(colored(f"  Пиковый уровень: {peak_level:.4f}", "blue"))
                print(colored(f"  Установлен порог: {self.threshold:.4f}", "green"))
                
                return self.threshold
            
        except Exception as e:
            print(colored(f"✗ Ошибка калибровки: {str(e)}", "red"))
        
        return self.threshold
    
    def _audio_callback(self, indata, frames, time_info, status):
        """Обработка аудио-данных в реальном времени"""
        if status:
            print(colored(f"⚠ Предупреждение аудио: {status}", "yellow"))
        
        # Анализ аудио-фрагмента
        audio_chunk = indata[:, 0]
        
        if self.is_clap_sound(audio_chunk):
            current_time = time.time()
            time_since_last_clap = current_time - self.last_clap_time
            
            if time_since_last_clap > self.clap_cooldown:
                self.clap_count += 1
                self.last_clap_time = current_time
                
                if self.clap_count == 1:
                    print(colored("👏 Обнаружен одиночный хлопок!", "cyan"), end="", flush=True)
                elif self.clap_count == 2:
                    time_between_claps = current_time - self.last_clap_time + self.clap_cooldown
                    if time_between_claps <= self.double_clap_window:
                        print(colored("\n👏👏 ДВОЙНОЙ ХЛОПОК ОБНАРУЖЕН! Выполняется действие...", "green", attrs=['bold']))
                        self.on_double_clap()
                        self.clap_count = 0
                    else:
                        self.clap_count = 1
                        print(colored("\n👏 Обнаружен одиночный хлопок!", "cyan"), end="", flush=True)
    
    def on_double_clap(self):
        """Обработчик двойного хлопка (можно переопределить)"""
        pass
    
    def start_detection(self, callback=None):
        """Запуск детекции хлопков"""
        if callback:
            self.on_double_clap = callback
        
        self.is_running = True
        self.clap_count = 0
        self.last_clap_time = 0
        
        try:
            print(colored(f"\n🎤 Начало мониторинга хлопков...", "blue"))
            print(colored("Порог чувствительности: {:.4f}".format(self.threshold), "blue"))
            print(colored("Сделайте двойной хлопок для управления лампами\n", "yellow"))
            
            with sd.InputStream(
                callback=self._audio_callback,
                channels=1,
                samplerate=self.sample_rate,
                blocksize=self.chunk_size
            ):
                while self.is_running:
                    time.sleep(0.1)
        
        except Exception as e:
            print(colored(f"✗ Ошибка при записи аудио: {str(e)}", "red"))
        
        print(colored("\n🛑 Мониторинг остановлен", "yellow"))
    
    def stop_detection(self):
        """Остановка детекции хлопков"""
        self.is_running = False
        if self.audio_thread and self.audio_thread.is_alive():
            self.audio_thread.join()

# Функция для тестирования детекции
if __name__ == "__main__":
    detector = ClapDetector()
    
    # Вывод доступных микрофонов
    devices = detector.find_best_microphone()
    if devices:
        print(colored("\nДоступные микрофоны:", "blue"))
        for dev in devices:
            print(colored(f"  [{dev['id']}] {dev['name']} ({dev['channels']} каналов)", "white"))
        
        # Использование первого доступного микрофона
        detector.set_microphone(devices[0]['id'])
        
        # Тестовый callback
        def test_callback():
            print(colored("🎉 Двойной хлопок обнаружен в тестовом режиме!", "green", attrs=['bold']))
        
        # Запуск детекции на 30 секунд
        try:
            detector.start_detection(callback=test_callback)
        except KeyboardInterrupt:
            detector.stop_detection()
    else:
        print(colored("✗ Микрофоны не найдены", "red"))