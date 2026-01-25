import sounddevice as sd
import numpy as np
import threading
import queue
from typing import Optional
from app.config import settings
from app.core.interfaces import IAudioDetector
from app.core.schemas import AudioResult
from app.infrastructure.logger import logger

class AudioDetector(IAudioDetector):
    def __init__(self):
        self.running = False
        self.stream = None
        self.q = queue.Queue()
        self.sample_rate = settings.audio.sample_rate
        self.block_size = settings.audio.block_size
        self.threshold = settings.audio.threshold_rms
        
    def _audio_callback(self, indata, frames, time, status):
        """Callback for non-blocking audio capture"""
        if status:
            logger.warning(f"Audio status: {status}")
        self.q.put(indata.copy())

    def start(self):
        try:
            self.stream = sd.InputStream(
                callback=self._audio_callback,
                channels=1,
                samplerate=self.sample_rate,
                blocksize=self.block_size
            )
            self.stream.start()
            self.running = True
            logger.info("Audio Module Started.")
        except Exception as e:
            logger.error(f"Failed to start Audio Module: {e}")
            self.running = False

    def stop(self):
        if self.stream:
            self.stream.stop()
            self.stream.close()
        self.running = False
        logger.info("Audio Module Stopped.")

    def get_latest_sample(self) -> AudioResult:
        """
        Process the latest audio chunk from queue.
        Calculates RMS Amplitude.
        """
        if not self.running:
             return AudioResult(speech_detected=False, rms_level=0.0, decibels=-100)

        # Process all pending chunks to stay real-time
        # We only care about the max volume in the last burst
        max_rms = 0.0
        
        try:
            while True:
                data = self.q.get_nowait()
                # Calculate RMS (Root Mean Square)
                rms = np.sqrt(np.mean(data**2))
                max_rms = max(max_rms, rms)
        except queue.Empty:
            pass
            
        # Convert to dB (optional, for display)
        # Avoid log(0)
        decibels = 20 * np.log10(max_rms) if max_rms > 0 else -100
        
        is_speech = max_rms > self.threshold
        
        return AudioResult(
            speech_detected=is_speech,
            rms_level=float(max_rms),
            decibels=float(decibels)
        )
