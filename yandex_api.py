from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Optional

import requests


@dataclass(frozen=True)
class YandexDeviceState:
    device_id: str
    is_on: Optional[bool]


class YandexSmartHomeClient:
    """Минимальный клиент для REST API Яндекс.Дом (Smart Home)."""

    def __init__(
        self,
        token: str,
        *,
        base_url: str = "https://api.iot.yandex.net/v1.0",
        timeout_sec: float = 10.0,
        logger: Optional[logging.Logger] = None,
    ) -> None:
        if not token or not token.strip():
            raise ValueError("Не задан OAuth-токен для Яндекс.Дома")

        self._token = token.strip()
        self._base_url = base_url.rstrip("/")
        self._timeout_sec = timeout_sec
        self._log = logger or logging.getLogger(__name__)

    @property
    def _headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self._token}",
            "Content-Type": "application/json",
        }

    def get_user_info(self) -> Dict[str, Any]:
        url = f"{self._base_url}/user/info"
        self._log.debug("GET %s", url)
        resp = requests.get(url, headers=self._headers, timeout=self._timeout_sec)
        resp.raise_for_status()
        data: Dict[str, Any] = resp.json()
        return data

    def get_devices_states(self, device_ids: Iterable[str]) -> List[YandexDeviceState]:
        wanted = set(device_ids)
        data = self.get_user_info()
        devices: List[Dict[str, Any]] = data.get("devices", [])

        by_id: Dict[str, Dict[str, Any]] = {d.get("id"): d for d in devices if d.get("id")}

        states: List[YandexDeviceState] = []
        for device_id in wanted:
            device = by_id.get(device_id)
            if not device:
                states.append(YandexDeviceState(device_id=device_id, is_on=None))
                continue

            is_on = self._extract_on_off(device)
            states.append(YandexDeviceState(device_id=device_id, is_on=is_on))
        return states

    def _extract_on_off(self, device: Dict[str, Any]) -> Optional[bool]:
        capabilities = device.get("capabilities", [])
        for cap in capabilities:
            if cap.get("type") != "devices.capabilities.on_off":
                continue

            state = cap.get("state") or {}
            if state.get("instance") == "on":
                value = state.get("value")
                if isinstance(value, bool):
                    return value
        return None

    def set_devices_on_off(self, device_ids: Iterable[str], *, on: bool) -> Dict[str, Any]:
        url = f"{self._base_url}/devices/actions"

        devices_payload = []
        for device_id in device_ids:
            devices_payload.append(
                {
                    "id": device_id,
                    "actions": [
                        {
                            "type": "devices.capabilities.on_off",
                            "state": {"instance": "on", "value": bool(on)},
                        }
                    ],
                }
            )

        payload: Dict[str, Any] = {"devices": devices_payload}
        self._log.info("Отправка команды: on=%s для устройств: %s", on, ", ".join(device_ids))
        self._log.debug("POST %s payload=%s", url, payload)

        resp = requests.post(url, headers=self._headers, json=payload, timeout=self._timeout_sec)
        resp.raise_for_status()
        data: Dict[str, Any] = resp.json()
        return data

    def toggle_devices_all_together(self, device_ids: Iterable[str]) -> bool:
        """Toggle (все вместе): если ВСЕ включены → выключить, иначе → включить."""

        ids = list(device_ids)
        states = self.get_devices_states(ids)
        known = [s.is_on for s in states if s.is_on is not None]

        if known and all(known):
            new_state = False
        else:
            new_state = True

        unknown = [s.device_id for s in states if s.is_on is None]
        if unknown:
            self._log.warning(
                "Не удалось определить текущее состояние некоторых устройств (будет применено общее состояние %s): %s",
                new_state,
                ", ".join(unknown),
            )

        self.set_devices_on_off(ids, on=new_state)
        return new_state
