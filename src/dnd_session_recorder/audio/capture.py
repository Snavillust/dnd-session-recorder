import sounddevice as sd
import numpy as np
import wave
import threading
from datetime import datetime
import os
import queue

class AudioCaptureManager:
    def __init__(self):
        self.recording = False
        self.audio_queue = queue.Queue()
        self.system_queue = queue.Queue()
        self.recording_thread = None
        
    def get_input_devices(self):
        """Returns a list of available input devices."""
        devices = []
        device_list = sd.query_devices()
        for i, device in enumerate(device_list):
            if device['max_input_channels'] > 0:  # Only input devices
                devices.append({
                    'index': i,
                    'name': device['name'],
                    'channels': device['max_input_channels']
                })
        return devices

    def get_output_devices(self):
        """Returns a list of available output devices."""
        devices = []
        device_list = sd.query_devices()
        for i, device in enumerate(device_list):
            if device['max_output_channels'] > 0:  # Only output devices
                devices.append({
                    'index': i,
                    'name': device['name'],
                    'channels': device['max_output_channels']
                })
        return devices

    def record_thread(self, input_device_index, output_device_index):
        """Thread function to handle recording."""
        try:
            # Start input stream (microphone)
            mic_stream = sd.InputStream(
                device=input_device_index,
                channels=1,
                samplerate=44100,
                callback=self.audio_callback
            )
            
            # Start system audio stream
            system_stream = sd.InputStream(
                device=output_device_index,
                channels=2,
                samplerate=44100,
                callback=self.system_callback
            )
            
            with mic_stream, system_stream:
                print(f"Recording started with mic ({input_device_index}) and system audio ({output_device_index})")
                while self.recording:
                    sd.sleep(100)

        except Exception as e:
            print(f"Error in recording thread: {e}")
            self.recording = False

    def audio_callback(self, indata, frames, time, status):
        """Callback for audio recording."""
        if status:
            print(f"Audio callback status: {status}")
        if self.recording:
            self.audio_queue.put(indata.copy())

    def system_callback(self, indata, frames, time, status):
        """Callback for system audio recording."""
        if status:
            print(f"System audio callback status: {status}")
        if self.recording:
            self.system_queue.put(indata.copy())

    def start_recording(self, input_device_index=None, output_device_index=None):
        """Start recording from both microphone and system audio."""
        if self.recording:
            return

        print(f"Starting recording with input device {input_device_index} and output device {output_device_index}")
        self.recording = True
        
        # Clear queues
        while not self.audio_queue.empty():
            self.audio_queue.get()
        while not self.system_queue.empty():
            self.system_queue.get()

        # Start recording thread
        self.recording_thread = threading.Thread(
            target=self.record_thread,
            args=(input_device_index, output_device_index)
        )
        self.recording_thread.start()

    def stop_recording(self):
        """Stop recording and save the audio file."""
        if not self.recording:
            return

        print("Stopping recording")
        self.recording = False
        
        if self.recording_thread:
            self.recording_thread.join()

        # Collect recorded audio data
        mic_frames = []
        system_frames = []
        
        while not self.audio_queue.empty():
            mic_frames.append(self.audio_queue.get())
            
        while not self.system_queue.empty():
            system_frames.append(self.system_queue.get())

        # Mix audio if we have both streams
        if mic_frames and system_frames:
            mic_audio = np.concatenate(mic_frames)
            system_audio = np.concatenate(system_frames)
            
            # Convert system audio to mono if it's stereo
            if len(system_audio.shape) > 1 and system_audio.shape[1] > 1:
                system_audio = np.mean(system_audio, axis=1)
            
            # Ensure both arrays are the same length
            min_length = min(len(mic_audio), len(system_audio))
            mic_audio = mic_audio[:min_length]
            system_audio = system_audio[:min_length]
            
            # Mix the audio (adjust mixing ratio as needed)
            mixed_audio = 0.7 * mic_audio + 0.3 * system_audio
            print("Mixed audio with both microphone and system audio")
        else:
            # If we only have microphone audio
            mixed_audio = np.concatenate(mic_frames) if mic_frames else np.array([])
            print("Only microphone audio was captured")

        # Save the mixed audio
        if len(mixed_audio) > 0:
            self._save_audio(mixed_audio)
            print("Saved mixed audio file")

    def _save_audio(self, audio_data):
        """Save the recorded audio to a WAV file."""
        # Create recordings directory if it doesn't exist
        os.makedirs('recordings', exist_ok=True)
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'recordings/session_{timestamp}.wav'
        
        # Convert float32 to int16
        audio_data = np.int16(audio_data * 32767)
        
        # Save the file
        with wave.open(filename, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(44100)
            wf.writeframes(audio_data.tobytes())
        print(f"Saved audio to: {filename}")

    def __del__(self):
        """Cleanup when the object is destroyed."""
        if self.recording:
            self.stop_recording()