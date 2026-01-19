#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import time
import signal
from termcolor import colored

from yandex_api import YandexSmartHomeAPI
from record_audio import ClapDetector
from calibration import CalibrationManager

class SmartLampController:
    def __init__(self):
        self.api_token = "y0__xDLjqC3BhjMgj0gkub-jhYwq63BsggL8YblL10mlsjdh7nt0KStsUr2sg"
        self.device_ids = [
            "19a27edd-f48b-43d5-9a53-5d913cd9272b",
            "72a33ab1-6a1d-4b98-a811-8a98bfeb873d", 
            "95cf0e1e-8117-4248-a87a-f7d83a1c50b1"
        ]
        
        self.yandex_api = None
        self.clap_detector = None
        self.calibration_manager = CalibrationManager()
        self.is_running = False
        
        # Обработка сигналов для корректного выхода
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Обработчик сигналов завершения"""
        print(colored("\n\nПолучен сигнал завершения. Выход из программы...", "yellow"))
        self.exit_program()
    
    def initialize(self):
        """Инициализация компонентов"""
        print(colored("=== Инициализация системы управления умными лампами ===\n", "blue", attrs=['bold']))
        
        # Инициализация API Яндекс.Дом
        try:
            self.yandex_api = YandexSmartHomeAPI(self.api_token)
            self.yandex_api.add_devices(self.device_ids)
            print()
        except Exception as e:
            print(colored(f"✗ Ошибка инициализации API: {str(e)}", "red"))
            return False
        
        # Инициализация детектора хлопков
        try:
            config = self.calibration_manager.config
            self.clap_detector = ClapDetector(
                sample_rate=config.get('sample_rate', 44100),
                chunk_size=1024
            )
            self.clap_detector.threshold = config.get('threshold', 0.3)
            self.clap_detector.clap_cooldown = config.get('clap_cooldown', 0.5)
            self.clap_detector.double_clap_window = config.get('double_clap_window', 1.0)
            
            device_id = config.get('device_id')
            if device_id is not None:
                self.clap_detector.set_microphone(device_id)
            else:
                print(colored("⚠ Микрофон не настроен. Требуется калибровка.", "yellow"))
        except Exception as e:
            print(colored(f"✗ Ошибка инициализации детектора хлопков: {str(e)}", "red"))
            return False
        
        print(colored("✅ Система успешно инициализирована!\n", "green", attrs=['bold']))
        return True
    
    def on_double_clap(self):
        """Обработчик двойного хлопка"""
        timestamp = time.strftime("%H:%M:%S")
        print(colored(f"🎉 [{timestamp}] Двойной хлопок обнаружен! Переключение ламп...", "green", attrs=['bold']))
        
        try:
            self.yandex_api.toggle_all_devices()
        except Exception as e:
            print(colored(f"✗ Ошибка переключения ламп: {str(e)}", "red"))
    
    def show_menu(self):
        """Отображение главного меню"""
        print(colored("\n" + "="*50, "blue"))
        print(colored("=== Управление умными лампами ===", "blue", attrs=['bold']))
        print(colored("="*50, "blue"))
        print(colored("1.", "cyan"), colored("Начать мониторинг хлопков", "white"))
        print(colored("2.", "cyan"), colored("Калибровка микрофона", "white"))
        print(colored("3.", "cyan"), colored("Выбрать микрофон", "white"))
        print(colored("4.", "cyan"), colored("Настройки", "white"))
        print(colored("5.", "cyan"), colored("Проверить лампы", "white"))
        print(colored("6.", "cyan"), colored("Информация о системе", "white"))
        print(colored("0.", "cyan"), colored("Выход", "white"))
        print(colored("="*50, "blue"))
    
    def select_microphone(self):
        """Выбор микрофона"""
        print(colored("\n=== Выбор микрофона ===", "blue", attrs=['bold']))
        
        devices = self.clap_detector.find_best_microphone()
        if not devices:
            print(colored("✗ Микрофоны не найдены", "red"))
            return
        
        print(colored("\nДоступные микрофоны:", "cyan"))
        for i, dev in enumerate(devices):
            current_marker = " ← ТЕКУЩИЙ" if dev['id'] == self.calibration_manager.config.get('device_id') else ""
            print(colored(f"  {i+1}. [{dev['id']}] {dev['name']} ({dev['channels']} каналов){current_marker}", "white"))
        
        try:
            choice = input(colored("\nВыберите номер микрофона (0 для отмены): ", "yellow")).strip()
            if choice == "0":
                return
            elif choice.isdigit() and 1 <= int(choice) <= len(devices):
                device_id = devices[int(choice) - 1]['id']
                if self.clap_detector.set_microphone(device_id):
                    self.calibration_manager.config['device_id'] = device_id
                    self.calibration_manager.save_config()
                    print(colored("✓ Микрофон успешно выбран и сохранен", "green"))
            else:
                print(colored("Неверный выбор", "red"))
        except KeyboardInterrupt:
            print(colored("\nОтмена выбора микрофона", "yellow"))
    
    def start_monitoring(self):
        """Запуск мониторинга хлопков"""
        if self.calibration_manager.config.get('device_id') is None:
            print(colored("⚠ Микрофон не выбран. Пожалуйста, выберите микрофон (пункт 3) или пройдите калибровку (пункт 2).", "yellow"))
            return
        
        print(colored("\n=== Мониторинг хлопков ===", "blue", attrs=['bold']))
        print(colored("🎤 Ожидание двойного хлопка...", "green"))
        print(colored("Нажмите Ctrl+C для возврата в меню\n", "yellow"))
        
        try:
            self.is_running = True
            self.clap_detector.on_double_clap = self.on_double_clap
            self.clap_detector.start_detection()
        except KeyboardInterrupt:
            print(colored("\n⏹ Мониторинг остановлен", "yellow"))
            self.is_running = False
        except Exception as e:
            print(colored(f"✗ Ошибка мониторинга: {str(e)}", "red"))
            self.is_running = False
    
    def test_lamps(self):
        """Тестирование подключения к лампам"""
        print(colored("\n=== Тестирование ламп ===", "blue", attrs=['bold']))
        try:
            for device_id in self.device_ids:
                state = self.yandex_api.get_device_state(device_id)
                status = colored("ВКЛЮЧЕНА", "green") if state else colored("ВЫКЛЮЧЕНА", "red")
                print(colored(f"  • Устройство {device_id[:8]}...: {status}", "white"))
        except Exception as e:
            print(colored(f"✗ Ошибка тестирования: {str(e)}", "red"))
    
    def show_settings(self):
        """Отображение и изменение настроек"""
        while True:
            print(colored("\n=== Настройки ===", "blue", attrs=['bold']))
            self.calibration_manager.show_current_settings()
            
            print(colored("1.", "cyan"), colored("Изменить порог чувствительности", "white"))
            print(colored("2.", "cyan"), colored("Изменить паузу между хлопками", "white"))
            print(colored("3.", "cyan"), colored("Изменить окно двойного хлопка", "white"))
            print(colored("0.", "cyan"), colored("Назад", "white"))
            
            try:
                choice = input(colored("\nВыберите действие: ", "yellow")).strip()
                
                if choice == "1":
                    current = self.calibration_manager.config.get('threshold', 0.3)
                    new_val = input(colored(f"Новый порог [{current}]: ", "yellow")).strip()
                    if new_val:
                        self.calibration_manager.config['threshold'] = float(new_val)
                        self.clap_detector.threshold = float(new_val)
                        self.calibration_manager.save_config()
                
                elif choice == "2":
                    current = self.calibration_manager.config.get('clap_cooldown', 0.5)
                    new_val = input(colored(f"Новая пауза (сек) [{current}]: ", "yellow")).strip()
                    if new_val:
                        self.calibration_manager.config['clap_cooldown'] = float(new_val)
                        self.clap_detector.clap_cooldown = float(new_val)
                        self.calibration_manager.save_config()
                
                elif choice == "3":
                    current = self.calibration_manager.config.get('double_clap_window', 1.0)
                    new_val = input(colored(f"Новое окно (сек) [{current}]: ", "yellow")).strip()
                    if new_val:
                        self.calibration_manager.config['double_clap_window'] = float(new_val)
                        self.clap_detector.double_clap_window = float(new_val)
                        self.calibration_manager.save_config()
                
                elif choice == "0":
                    break
                
                else:
                    print(colored("Неверный выбор", "red"))
            
            except ValueError:
                print(colored("Неверное значение", "red"))
            except KeyboardInterrupt:
                print(colored("\nОтмена", "yellow"))
                break
    
    def show_system_info(self):
        """Отображение информации о системе"""
        print(colored("\n=== Информация о системе ===", "blue", attrs=['bold']))
        print(colored(f"Python версия: {sys.version}", "white"))
        print(colored(f"API Яндекс.Дом: {'Подключен' if self.yandex_api else 'Не подключен'}", "green" if self.yandex_api else "red"))
        print(colored(f"Количество ламп: {len(self.device_ids)}", "white"))
        print(colored(f"Мониторинг: {'Активен' if self.is_running else 'Неактивен'}", "cyan" if self.is_running else "white"))
        
        if self.clap_detector:
            print(colored(f"Частота дискретизации: {self.clap_detector.sample_rate} Гц", "white"))
            print(colored(f"Размер блока: {self.clap_detector.chunk_size} samples", "white"))
    
    def exit_program(self):
        """Выход из программы"""
        print(colored("\n🚪 Выход из программы...", "yellow"))
        if self.is_running:
            self.is_running = False
            if self.clap_detector:
                self.clap_detector.stop_detection()
        sys.exit(0)
    
    def run(self):
        """Запуск главного цикла программы"""
        if not self.initialize():
            print(colored("✗ Не удалось инициализировать систему. Выход.", "red"))
            return 1
        
        try:
            while True:
                self.show_menu()
                
                try:
                    choice = input(colored("\nВыберите действие (0-6): ", "yellow", attrs=['bold'])).strip()
                    
                    if choice == "1":
                        self.start_monitoring()
                    elif choice == "2":
                        self.calibration_manager.run_calibration()
                    elif choice == "3":
                        self.select_microphone()
                    elif choice == "4":
                        self.show_settings()
                    elif choice == "5":
                        self.test_lamps()
                    elif choice == "6":
                        self.show_system_info()
                    elif choice == "0":
                        self.exit_program()
                    else:
                        print(colored("Неверный выбор. Попробуйте снова.", "red"))
                
                except KeyboardInterrupt:
                    print(colored("\n\nПринудительный выход...", "yellow"))
                    self.exit_program()
                except Exception as e:
                    print(colored(f"✗ Ошибка: {str(e)}", "red"))
        
        except Exception as e:
            print(colored(f"✗ Критическая ошибка: {str(e)}", "red"))
            return 1

if __name__ == "__main__":
    controller = SmartLampController()
    sys.exit(controller.run())