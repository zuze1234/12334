#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json
import time
from termcolor import colored

class YandexSmartHomeAPI:
    def __init__(self, token):
        self.token = token
        self.base_url = "https://api.iot.yandex.net/v1.0"
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        self.device_ids = []
        self._test_connection()
    
    def _test_connection(self):
        """Проверка подключения к API Яндекс.Дом"""
        try:
            response = requests.get(
                f"{self.base_url}/user/info",
                headers=self.headers,
                timeout=10
            )
            if response.status_code == 200:
                print(colored("✓ Успешное подключение к API Яндекс.Дом", "green"))
            else:
                print(colored(f"✗ Ошибка подключения к API: {response.status_code}", "red"))
                print(colored(f"Ответ: {response.text}", "yellow"))
        except Exception as e:
            print(colored(f"✗ Ошибка сети: {str(e)}", "red"))
    
    def add_devices(self, device_ids):
        """Добавление списка устройств для управления"""
        self.device_ids = device_ids
        print(colored(f"✓ Добавлено {len(device_ids)} устройств", "blue"))
        
        # Проверка доступности устройств
        for device_id in device_ids:
            self._check_device(device_id)
    
    def _check_device(self, device_id):
        """Проверка доступности конкретного устройства"""
        try:
            response = requests.get(
                f"{self.base_url}/devices/{device_id}",
                headers=self.headers,
                timeout=5
            )
            if response.status_code == 200:
                device_info = response.json()
                device_name = device_info.get("name", "Неизвестное устройство")
                print(colored(f"  • {device_name} ({device_id[:8]}...) - доступен", "green"))
            else:
                print(colored(f"  • Устройство {device_id[:8]}... - недоступно", "yellow"))
        except Exception as e:
            print(colored(f"  • Ошибка проверки устройства: {str(e)}", "red"))
    
    def get_device_state(self, device_id):
        """Получение текущего состояния устройства"""
        try:
            response = requests.get(
                f"{self.base_url}/devices/{device_id}",
                headers=self.headers,
                timeout=5
            )
            if response.status_code == 200:
                device_info = response.json()
                capabilities = device_info.get("capabilities", [])
                for cap in capabilities:
                    if cap.get("type") == "devices.capabilities.on_off":
                        return cap.get("state", {}).get("value", False)
            return False
        except Exception as e:
            print(colored(f"✗ Ошибка получения состояния: {str(e)}", "red"))
            return False
    
    def toggle_device(self, device_id):
        """Переключение состояния устройства (вкл/выкл)"""
        current_state = self.get_device_state(device_id)
        new_state = not current_state
        
        payload = {
            "devices": [{
                "id": device_id,
                "actions": [{
                    "type": "devices.capabilities.on_off",
                    "state": {
                        "instance": "on",
                        "value": new_state
                    }
                }]
            }]
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/devices/actions",
                headers=self.headers,
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                action_result = response.json()
                if action_result.get("status") == "DONE":
                    print(colored(f"✓ Устройство {device_id[:8]}... {'включено' if new_state else 'выключено'}", "green"))
                    return True
                else:
                    print(colored(f"✗ Ошибка выполнения действия: {action_result}", "red"))
                    return False
            else:
                print(colored(f"✗ HTTP ошибка: {response.status_code}", "red"))
                print(colored(f"Ответ: {response.text}", "yellow"))
                return False
                
        except Exception as e:
            print(colored(f"✗ Ошибка управления устройством: {str(e)}", "red"))
            return False
    
    def toggle_all_devices(self):
        """Одновременное переключение всех устройств"""
        print(colored("\n🔄 Переключение всех ламп...", "cyan"))
        success_count = 0
        
        for device_id in self.device_ids:
            if self.toggle_device(device_id):
                success_count += 1
            time.sleep(0.5)  # Небольшая задержка между запросами
        
        print(colored(f"✓ Успешно переключено {success_count}/{len(self.device_ids)} устройств\n", "green"))
        return success_count == len(self.device_ids)