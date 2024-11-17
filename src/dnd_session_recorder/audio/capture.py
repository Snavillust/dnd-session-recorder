import pyaudio
import numpy as np
import wave
from pathlib import Path
from datetime import datetime
import threading
import logging

class AudioCapture:
    """Handle audio recording from both microphone and system output."""
    
    def __init__(self):
        self.recording = False
        self.audio_data = []
        self.sample_rate = 44100
        self.channels = 2
        self.mic_device_id = None
        self.output_device_id = None
        self._recording_thread = None
        self.pa = pyaudio.PyAudio()
        
        # Set up logging
        self.logger = logging.getLogger(__name__)
    
    def list_input_devices(self):
        """List all available input (microphone) devices."""
        input_devices = []
        for i in range(self.pa.get_device_count()):
            device_info = self.pa.get_device_info_by_index(i)
            if device_info['maxInputChannels'] > 0:
                input_devices.append((
                    i,
                    device_info['name'],
                    device_info['maxInputChannels']
                ))
        return input_devices

    def list_output_devices(self):
        """List all available output devices with loopback support."""
        output_devices = []
        try:
            wasapi_info = self.pa.get_host_api_info_by_type(pyaudio.paWASAPI)
            wasapi_index = wasapi_info['index']
            
            for i in range(self.pa.get_device_count()):
                device_info = self.pa.get_device_info_by_index(i)
                if device_info['hostApi'] == wasapi_index:
                    if device_info['maxInputChannels'] == 0 and device_info['maxOutputChannels'] > 0:
                        output_devices.append((
                            i,
                            f"{device_info['name']} (System Audio)",
                            device_info['maxOutputChannels']
                        ))
            
            return output_devices
        except Exception as e:
            self.logger.error(f"Error listing output devices: {e}")
            return []
    
    def start_recording(self):
        """Start recording both microphone and system audio."""
        if self.recording:
            self.logger.warning("Recording already in progress")
            return
            
        if self.mic_device_id is None or self.output_device_id is None:
            raise ValueError("Both input and output devices must be selected")
        
        self.audio_data = []
        self.recording = True
        
        def record_thread():
            try:
                # Open streams for both microphone and system audio
                mic_stream = self.pa.open(
                    format=pyaudio.paFloat32,
                    channels=self.channels,
                    rate=self.sample_rate,
                    input=True,
                    input_device_index=self.mic_device_id,
                    frames_per_buffer=1024
                )
                
                wasapi_stream = self.pa.open(
                    format=pyaudio.paFloat32,
                    channels=self.channels,
                    rate=self.sample_rate,
                    input=True,
                    input_device_index=self.output_device_id,
                    frames_per_buffer=1024,
                    as_loopback=True  # This enables WASAPI loopback
                )
                
                while self.recording:
                    mic_data = np.frombuffer(mic_stream.read(1024, exception_on_overflow=False), dtype=np.float32)
                    system_data = np.frombuffer(wasapi_stream.read(1024, exception_on_overflow=False), dtype=np.float32)
                    
                    # Mix the audio (simple addition with clipping prevention)
                    mixed_data = np.clip(mic_data + system_data, -1.0, 1.0)
                    self.audio_data.append(mixed_data)
                
                mic_stream.stop_stream()
                wasapi_stream.stop_stream()
                mic_stream.close()
                wasapi_stream.close()
                
            except Exception as e:
                self.logger.error(f"Recording error: {e}")
                self.recording = False
        
        self._recording_thread = threading.Thread(target=record_thread)
        self._recording_thread.start()
        self.logger.info("Recording started")
    
    def stop_recording(self):
        """Stop recording and save the audio file."""
        if not self.recording:
            self.logger.warning("No recording in progress")
            return None
        
        self.recording = False
        if self._recording_thread:
            self._recording_thread.join()
        
        if not self.audio_data:
            self.logger.warning("No audio data captured")
            return None
        
        # Combine all audio chunks
        audio_data = np.concatenate(self.audio_data, axis=0)
        
        # Create filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = Path(f"recordings/session_{timestamp}.wav")
        output_path.parent.mkdir(exist_ok=True)
        
        # Save to WAV file
        with wave.open(str(output_path), 'wb') as wav_file:
            wav_file.setnchannels(self.channels)
            wav_file.setsampwidth(2)  # 16-bit audio
            wav_file.setframerate(self.sample_rate)
            wav_file.writeframes((audio_data * 32767).astype(np.int16).tobytes())
        
        self.logger.info(f"Recording saved to: {output_path}")
        return output_path
    
    def is_recording(self):
        """Check if currently recording."""
        return self.recording
    
    def set_mic_device(self, device_id):
        """Set the microphone device."""
        self.mic_device_id = device_id
        
    def set_output_device(self, device_id):
        """Set the output device."""
        self.output_device_id = device_id
        
    def __del__(self):
        """Cleanup PyAudio."""
        if hasattr(self, 'pa'):
            self.pa.terminate()