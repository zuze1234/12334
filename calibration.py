#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import os
from record_audio import ClapDetector
from termcolor import colored

class CalibrationManager:
    def __init__(self, config_file='config.json'):
        self.config_file = config_file
        self.config = self.load_config()
    
    def load_config(self):
        """Загрузка конфигурации"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(colored(f"⚠ Ошибка загрузки конфигурации: {str(e)}", "yellow"))
        
        return {
            "threshold": 0.3,
            "device_id": None,
            "sample_rate": 44100,
            "clap_cooldown": 0.5,
            "double_clap_window": 1.0
        }
    
    def save_config(self):
        """Сохранение конфигурации"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            print(colored("✓ Конфигурация сохранена", "green"))
        except Exception as e:
            print(colored(f"✗ Ошибка сохранения конфигурации: {str(e)}", "red"))
    
    def run_calibration(self):
        """Запуск процесса калибровки"""
        print(colored("\n=== Калибровка микрофона ===", "blue", attrs=['bold']))
        
        detector = ClapDetector(
            sample_rate=self.config['sample_rate'],
            chunk_size=1024
        )
        
        # Выбор микрофона
        devices = detector.find_best_microphone()
        if not devices:
            print(colored("✗ Микрофоны не найдены", "red"))
            return False
        
        print(colored("\nДоступные микрофоны:", "cyan"))
        for i, dev in enumerate(devices):
            marker = " ← ТЕКУЩИЙ" if dev['id'] == self.config.get('device_id') else ""
            print(colored(f"  {i+1}. [{dev['id']}] {dev['name']} ({dev['channels']} каналов){marker}", "white"))
        
        # Выбор микрофона
        while True:
            try:
                choice = input(colored("\nВыберите номер микрофона (Enter для текущего): ", "yellow")).strip()
                if not choice and self.config.get('device_id') is not None:
                    device_id = self.config['device_id']
                    break
                elif choice.isdigit() and 1 <= int(choice) <= len(devices):
                    device_id = devices[int(choice) - 1]['id']
                    self.config['device_id'] = device_id
                    break
                else:
                    print(colored("Неверный выбор. Попробуйте снова.", "red"))
            except KeyboardInterrupt:
                print(colored("\nКалибровка прервана", "yellow"))
                return False
        
        if not detector.set_microphone(device_id):
            return False
        
        # Калибровка порога
        print(colored("\n🔊 Начало калибровки...", "yellow"))
        print(colored("1. Будет записано 5 секунд аудио", "blue"))
        print(colored("2. Оставайтесь в тишине первые 2 секунды", "blue"))
        print(colored("3. Сделайте 2-3 хлопка в последние 3 секунды", "blue"))
        print(colored("\nНажмите Enter для начала калибровки...", "green"))
        input()
        
        threshold = detector.calibrate_threshold(duration=5)
        self.config['threshold'] = threshold
        
        # Тестирование калибровки
        print(colored("\n🎯 Тестирование калибровки...", "yellow"))
        print(colored("Сделайте двойной хлопок для проверки", "blue"))
        print(colored("Нажмите Ctrl+C для завершения теста\n", "blue"))
        
        test_count = 0
        def test_callback():
            nonlocal test_count
            test_count += 1
            print(colored(f"🎉 Двойной хлопок #{test_count} обнаружен!", "green"))
        
        try:
            detector.on_double_clap = test_callback
            detector.start_detection()
        except KeyboardInterrupt:
            detector.stop_detection()
        
        print(colored(f"\n✓ Обнаружено {test_count} двойных хлопков", "green"))
        
        # Настройка параметров
        print(colored("\n=== Настройка параметров ===", "blue", attrs=['bold']))
        
        # Пауза между хлопками
        try:
            current_cooldown = self.config.get('clap_cooldown', 0.5)
            new_cooldown = input(colored(f"Пауза между хлопками (сек) [{current_cooldown}]: ", "yellow")).strip()
            if new_cooldown:
                self.config['clap_cooldown'] = float(new_cooldown)
        except ValueError:
            print(colored("Неверное значение, оставлено по умолчанию", "yellow"))
        
        # Окно для двойного хлопка
        try:
            current_window = self.config.get('double_clap_window', 1.0)
            new_window = input(colored(f"Окно для двойного хлопка (сек) [{current_window}]: ", "yellow")).strip()
            if new_window:
                self.config['double_clap_window'] = float(new_window)
        except ValueError:
            print(colored("Неверное значение, оставлено по умолчанию", "yellow"))
        
        # Сохранение конфигурации
        self.save_config()
        
        print(colored("\n✅ Калибровка успешно завершена!", "green", attrs=['bold']))
        return True
    
    def show_current_settings(self):
        """Показ текущих настроек"""
        print(colored("\n=== Текущие настройки ===", "blue", attrs=['bold']))
        print(colored(f"Порог чувствительности: {self.config.get('threshold', 0.3):.4f}", "white"))
        print(colored(f"Пауза между хлопками: {self.config.get('clap_cooldown', 0.5)} сек", "white"))
        print(colored(f"Окно двойного хлопка: {self.config.get('double_clap_window', 1.0)} сек", "white"))
        
        device_id = self.config.get('device_id')
        if device_id is not None:
            try:
                device_info = sd.query_devices(device_id)
                print(colored(f"Микрофон: {device_info['name']}", "white"))
            except:
                print(colored(f"Микрофон: ID {device_id} (не найден)", "yellow"))
        else:
            print(colored("Микрофон: не выбран", "yellow"))
        
        print()

if __name__ == "__main__":
    calibrator = CalibrationManager()
    
    try:
        calibrator.run_calibration()
    except KeyboardInterrupt:
        print(colored("\n\nКалибровка прервана пользователем", "yellow"))