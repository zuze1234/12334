#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import time
from termcolor import colored

from yandex_api import YandexSmartHomeAPI
from record_audio import ClapDetector

def test_api():
    """Тестирование API Яндекс.Дом"""
    print(colored("\n=== Тест API Яндекс.Дом ===", "blue", attrs=['bold']))
    
    try:
        token = "y0__xDLjqC3BhjMgj0gkub-jhYwq63BsggL8YblL10mlsjdh7nt0KStsUr2sg"
        device_ids = [
            "19a27edd-f48b-43d5-9a53-5d913cd9272b",
            "72a33ab1-6a1d-4b98-a811-8a98bfeb873d",
            "95cf0e1e-8117-4248-a87a-f7d83a1c50b1"
        ]
        
        api = YandexSmartHomeAPI(token)
        api.add_devices(device_ids)
        
        print(colored("✅ API тест успешно пройден", "green"))
        return True
        
    except Exception as e:
        print(colored(f"✗ Ошибка теста API: {str(e)}", "red"))
        return False

def test_microphone():
    """Тестирование микрофона"""
    print(colored("\n=== Тест микрофона ===", "blue", attrs=['bold']))
    
    try:
        detector = ClapDetector()
        
        # Поиск микрофонов
        devices = detector.find_best_microphone()
        if not devices:
            print(colored("✗ Микрофоны не найдены", "red"))
            return False
        
        print(colored(f"✓ Найдено {len(devices)} микрофон(ов)", "green"))
        
        # Использование первого микрофона
        if detector.set_microphone(devices[0]['id']):
            print(colored("✓ Микрофон успешно инициализирован", "green"))
            
            # Краткая калибровка
            print(colored("\nБыстрая калибровка (3 секунды)...", "yellow"))
            threshold = detector.calibrate_threshold(duration=3)
            print(colored(f"✓ Порог установлен: {threshold:.4f}", "green"))
            
            return True
        else:
            print(colored("✗ Ошибка инициализации микрофона", "red"))
            return False
            
    except Exception as e:
        print(colored(f"✗ Ошибка теста микрофона: {str(e)}", "red"))
        return False

def test_clap_detection():
    """Тестирование детекции хлопков"""
    print(colored("\n=== Тест детекции хлопков ===", "blue", attrs=['bold']))
    print(colored("Тест будет работать 10 секунд", "yellow"))
    print(colored("Сделайте двойной хлопок для проверки\n", "cyan"))
    
    clap_count = 0
    
    def test_callback():
        nonlocal clap_count
        clap_count += 1
        timestamp = time.strftime("%H:%M:%S")
        print(colored(f"🎉 [{timestamp}] Двойной хлопок #{clap_count} обнаружен!", "green", attrs=['bold']))
    
    try:
        detector = ClapDetector()
        devices = detector.find_best_microphone()
        
        if devices:
            detector.set_microphone(devices[0]['id'])
            detector.calibrate_threshold(duration=3)
            
            detector.on_double_clap = test_callback
            
            # Запуск на 10 секунд
            import threading
            timer = threading.Timer(10, detector.stop_detection)
            timer.start()
            
            detector.start_detection()
            timer.cancel()
            
            if clap_count > 0:
                print(colored(f"\n✅ Тест пройден: обнаружено {clap_count} двойных хлопков", "green"))
            else:
                print(colored("\nℹ Тест завершен: хлопки не обнаружены", "yellow"))
            
            return True
        else:
            print(colored("✗ Микрофон не найден", "red"))
            return False
            
    except KeyboardInterrupt:
        print(colored("\nТест прерван", "yellow"))
        return True
    except Exception as e:
        print(colored(f"✗ Ошибка теста детекции: {str(e)}", "red"))
        return False

def full_test():
    """Полный тест системы"""
    print(colored("\n" + "="*60, "blue"))
    print(colored("=== ПОЛНЫЙ ТЕСТ СИСТЕМЫ УПРАВЛЕНИЯ ЛАМПАМИ ===", "blue", attrs=['bold']))
    print(colored("="*60, "blue"))
    
    results = []
    
    # Тест API
    results.append(("API Яндекс.Дом", test_api()))
    time.sleep(1)
    
    # Тест микрофона
    results.append(("Микрофон", test_microphone()))
    time.sleep(1)
    
    # Тест детекции (опционально)
    print(colored("\nХотите протестировать детекцию хлопков? (y/n): ", "yellow"), end="")
    try:
        choice = input().strip().lower()
        if choice == 'y':
            results.append(("Детекция хлопков", test_clap_detection()))
        else:
            results.append(("Детекция хлопков", None))
    except KeyboardInterrupt:
        print(colored("\nТест прерван", "yellow"))
        return
    
    # Итоги
    print(colored("\n" + "="*60, "blue"))
    print(colored("=== РЕЗУЛЬТАТЫ ТЕСТА ===", "blue", attrs=['bold']))
    print(colored("="*60, "blue"))
    
    for test_name, result in results:
        if result is True:
            status = colored("✅ УСПЕХ", "green", attrs=['bold'])
        elif result is False:
            status = colored("❌ ОШИБКА", "red", attrs=['bold'])
        else:
            status = colored("⏭ ПРОПУЩЕНО", "yellow")
        
        print(colored(f"{test_name:<25} {status}", "white"))
    
    print(colored("="*60, "blue"))
    
    # Общий результат
    passed = sum(1 for _, r in results if r is True)
    total = sum(1 for _, r in results if r is not None)
    
    if passed == total and total > 0:
        print(colored(f"\n🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ ({passed}/{total})!", "green", attrs=['bold']))
        print(colored("Можно запускать главное приложение: python main.py", "cyan"))
    else:
        print(colored(f"\n⚠ ТЕСТЫ ЗАВЕРШЕНЫ ({passed}/{total} успешно)", "yellow"))
        if passed < total:
            print(colored("Устраните ошибки перед запуском основного приложения", "yellow"))

if __name__ == "__main__":
    try:
        # Проверка аргументов
        if len(sys.argv) > 1 and sys.argv[1] == "--quick":
            # Быстрый тест без детекции
            print(colored("\nЗапуск быстрого теста...", "blue"))
            test_api()
            test_microphone()
        else:
            # Полный тест
            full_test()
    except KeyboardInterrupt:
        print(colored("\n\nТест прерван пользователем", "yellow"))
    except Exception as e:
        print(colored(f"\n✗ Критическая ошибка: {str(e)}", "red"))
        sys.exit(1)