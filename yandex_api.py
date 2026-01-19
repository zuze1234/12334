"""
Yandex Home API Integration
"""
import requests
import logging
import time
from typing import Dict, List, Optional, Any


logger = logging.getLogger(__name__)


class YandexHomeAPI:
    """Interface to Yandex Smart Home API"""
    
    BASE_URL = "https://api.iot.yandex.net/v1.0"
    
    def __init__(self, token: str):
        self.token = token
        self.headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        self._device_cache = {}
        self._cache_time = 0
        self._cache_duration = 60  # Cache devices for 60 seconds
    
    def get_devices(self, force_refresh: bool = False) -> List[Dict[str, Any]]:
        """Get list of all devices"""
        current_time = time.time()
        
        if not force_refresh and (current_time - self._cache_time) < self._cache_duration:
            return list(self._device_cache.values())
        
        try:
            response = requests.get(
                f"{self.BASE_URL}/user/info",
                headers=self.headers,
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            
            devices = []
            for room in data.get('rooms', []):
                for device in room.get('devices', []):
                    device_info = {
                        'id': device.get('id'),
                        'name': device.get('name'),
                        'type': device.get('type'),
                        'room': room.get('name'),
                        'capabilities': device.get('capabilities', []),
                        'properties': device.get('properties', [])
                    }
                    devices.append(device_info)
                    self._device_cache[device['id']] = device_info
            
            for device in data.get('devices', []):
                if device.get('id') not in self._device_cache:
                    device_info = {
                        'id': device.get('id'),
                        'name': device.get('name'),
                        'type': device.get('type'),
                        'room': 'Unknown',
                        'capabilities': device.get('capabilities', []),
                        'properties': device.get('properties', [])
                    }
                    devices.append(device_info)
                    self._device_cache[device['id']] = device_info
            
            self._cache_time = current_time
            logger.info(f"Retrieved {len(devices)} devices from Yandex Home")
            return devices
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching devices: {e}")
            return list(self._device_cache.values())
        except Exception as e:
            logger.error(f"Unexpected error fetching devices: {e}")
            return []
    
    def get_device_state(self, device_id: str) -> Optional[Dict[str, Any]]:
        """Get current state of a device"""
        try:
            response = requests.get(
                f"{self.BASE_URL}/devices/{device_id}",
                headers=self.headers,
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error getting device state for {device_id}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error getting device state: {e}")
            return None
    
    def toggle_device(self, device_id: str, max_retries: int = 3) -> bool:
        """Toggle device on/off state"""
        current_state = self._get_on_off_state(device_id)
        new_state = not current_state if current_state is not None else True
        
        return self.set_device_state(device_id, new_state, max_retries)
    
    def set_device_state(self, device_id: str, state: bool, max_retries: int = 3) -> bool:
        """Set device on/off state with retry logic"""
        for attempt in range(max_retries):
            try:
                payload = {
                    "devices": [{
                        "id": device_id,
                        "actions": [{
                            "type": "devices.capabilities.on_off",
                            "state": {
                                "instance": "on",
                                "value": state
                            }
                        }]
                    }]
                }
                
                response = requests.post(
                    f"{self.BASE_URL}/devices/actions",
                    headers=self.headers,
                    json=payload,
                    timeout=10
                )
                response.raise_for_status()
                
                result = response.json()
                if result.get('devices', [{}])[0].get('capabilities', [{}])[0].get('state', {}).get('action_result', {}).get('status') == 'DONE':
                    logger.info(f"Device {device_id} turned {'on' if state else 'off'}")
                    return True
                else:
                    logger.warning(f"Device action may have failed: {result}")
                    if attempt < max_retries - 1:
                        time.sleep(0.5 * (attempt + 1))
                        continue
                    return False
                    
            except requests.exceptions.RequestException as e:
                logger.error(f"Error setting device state (attempt {attempt + 1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(0.5 * (attempt + 1))
                else:
                    return False
            except Exception as e:
                logger.error(f"Unexpected error setting device state: {e}")
                return False
        
        return False
    
    def _get_on_off_state(self, device_id: str) -> Optional[bool]:
        """Get current on/off state of device"""
        device_state = self.get_device_state(device_id)
        if not device_state:
            return None
        
        for capability in device_state.get('capabilities', []):
            if capability.get('type') == 'devices.capabilities.on_off':
                return capability.get('state', {}).get('value', False)
        
        return None
    
    def toggle_all_devices(self, device_ids: List[str]) -> Dict[str, bool]:
        """Toggle multiple devices"""
        results = {}
        for device_id in device_ids:
            results[device_id] = self.toggle_device(device_id)
        return results
