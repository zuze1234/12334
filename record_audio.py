from __future__ import annotations

import logging
import threading
import time
from dataclasses import dataclass
from typing import Callable, List, Optional

import numpy as np
import sounddevice as sd


@dataclass(frozen=True)
class InputDevice:
    index: int
    name: str
    max_input_channels: int
    default_samplerate: float


def list_input_devices() -> List[InputDevice]:
    devices = sd.query_devices()
    result: List[InputDevice] = []
    for idx, dev in enumerate(devices):
        if int(dev.get("max_input_channels", 0)) <= 0:
            continue
        result.append(
            InputDevice(
                index=idx,
                name=str(dev.get("name")),
                max_input_channels=int(dev.get("max_input_channels", 0)),
                default_samplerate=float(dev.get("default_samplerate", 44100.0)),
            )
        )
    return result


class ClapDetector:
    """Детектор двойного хлопка на основе порога амплитуды."""

    def __init__(
        self,
        *,
        threshold: float,
        on_double_clap: Callable[[], None],
        device: Optional[int] = None,
        samplerate: int = 44100,
        blocksize: int = 2048,
        min_interval_sec: float = 0.15,
        max_interval_sec: float = 0.8,
        cooldown_sec: float = 1.0,
        min_time_between_claps_sec: float = 0.12,
        highpass_hz: float = 800.0,
        logger: Optional[logging.Logger] = None,
    ) -> None:
        self.threshold = float(threshold)
        self.on_double_clap = on_double_clap

        self.device = device
        self.samplerate = int(samplerate)
        self.blocksize = int(blocksize)

        self.min_interval_sec = float(min_interval_sec)
        self.max_interval_sec = float(max_interval_sec)
        self.cooldown_sec = float(cooldown_sec)
        self.min_time_between_claps_sec = float(min_time_between_claps_sec)

        self.highpass_hz = float(highpass_hz)
        self._hp_alpha = self._calc_highpass_alpha(self.highpass_hz, self.samplerate)
        self._hp_prev_x: float = 0.0
        self._hp_prev_y: float = 0.0

        self._log = logger or logging.getLogger(__name__)

        self._stream: Optional[sd.InputStream] = None
        self._lock = threading.Lock()

        self._last_clap_ts: Optional[float] = None
        self._last_clap_peak_ts: float = 0.0
        self._last_trigger_ts: float = 0.0

    def start(self) -> None:
        if self._stream is not None:
            return

        self._log.info(
            "Запуск мониторинга микрофона: device=%s, samplerate=%s, threshold=%.5f",
            self.device,
            self.samplerate,
            self.threshold,
        )

        self._stream = sd.InputStream(
            device=self.device,
            channels=1,
            samplerate=self.samplerate,
            blocksize=self.blocksize,
            dtype="float32",
            callback=self._callback,
        )
        self._stream.start()

    def stop(self) -> None:
        if self._stream is None:
            return

        self._log.info("Остановка мониторинга микрофона")
        try:
            self._stream.stop()
        finally:
            self._stream.close()
            self._stream = None

    def _callback(self, indata: np.ndarray, frames: int, time_info, status) -> None:  # noqa: ANN001
        if status:
            self._log.debug("Статус аудиопотока: %s", status)

        if indata.size == 0:
            return

        samples = indata[:, 0]
        samples = self._highpass(samples)

        peak = float(np.max(np.abs(samples)))
        now = time.monotonic()

        if peak < self.threshold:
            return

        with self._lock:
            if now - self._last_clap_peak_ts < self.min_time_between_claps_sec:
                return
            self._last_clap_peak_ts = now

        self._register_clap(now, peak)

    def _register_clap(self, ts: float, peak: float) -> None:
        with self._lock:
            if ts - self._last_trigger_ts < self.cooldown_sec:
                self._log.debug("Хлопок проигнорирован (cooldown)")
                return

            if self._last_clap_ts is None:
                self._last_clap_ts = ts
                self._log.info("Хлопок 1/2 (peak=%.4f)", peak)
                return

            dt = ts - self._last_clap_ts

            if dt < self.min_interval_sec:
                self._log.debug("Слишком быстро для двойного хлопка: %.3f сек", dt)
                return

            if dt <= self.max_interval_sec:
                self._log.info("Двойной хлопок обнаружен (интервал %.3f сек)", dt)
                self._last_clap_ts = None
                self._last_trigger_ts = ts

                threading.Thread(target=self._safe_fire_double_clap, daemon=True).start()
                return

            self._log.debug("Слишком медленно, считаем хлопок новым первым: %.3f сек", dt)
            self._last_clap_ts = ts

    def _safe_fire_double_clap(self) -> None:
        try:
            self.on_double_clap()
        except Exception:
            self._log.exception("Ошибка обработки события двойного хлопка")

    def _highpass(self, x: np.ndarray) -> np.ndarray:
        # Однополюсный high-pass фильтр, быстрый и достаточный для уменьшения НЧ шума.
        y = np.empty_like(x)
        alpha = self._hp_alpha

        prev_x = self._hp_prev_x
        prev_y = self._hp_prev_y

        for i in range(x.shape[0]):
            xi = float(x[i])
            yi = alpha * (prev_y + xi - prev_x)
            y[i] = yi
            prev_x = xi
            prev_y = yi

        self._hp_prev_x = prev_x
        self._hp_prev_y = prev_y

        return y

    @staticmethod
    def _calc_highpass_alpha(cutoff_hz: float, samplerate: int) -> float:
        if cutoff_hz <= 0:
            return 1.0
        dt = 1.0 / float(samplerate)
        rc = 1.0 / (2.0 * np.pi * float(cutoff_hz))
        return rc / (rc + dt)
