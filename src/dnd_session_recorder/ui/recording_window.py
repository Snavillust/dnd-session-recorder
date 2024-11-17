import tkinter as tk
from tkinter import ttk
import threading
from pathlib import Path
from dnd_session_recorder.audio.capture import AudioCapture

class RecordingUI:
    def __init__(self, root):
        self.root = root
        self.root.title("D&D Session Recorder")
        self.root.geometry("500x400")
        
        self.audio_capture = AudioCapture()
        self.recording = False
        
        self.create_widgets()
        
    def create_widgets(self):
        # Get available devices
        input_devices = self.audio_capture.list_input_devices()
        output_devices = self.audio_capture.list_output_devices()
        
        self.input_device_names = [f"{name} (ID: {id})" for id, name, _ in input_devices]
        self.output_device_names = [f"{name} (ID: {id})" for id, name, _ in output_devices]
        
        # Device selection frame
        device_frame = ttk.LabelFrame(self.root, text="Audio Device Selection", padding=10)
        device_frame.pack(fill="x", padx=10, pady=5)
        
        # Microphone input selection
        ttk.Label(device_frame, text="Microphone Input:").pack(anchor="w")
        self.mic_input = ttk.Combobox(device_frame, values=self.input_device_names, width=40)
        self.mic_input.pack(fill="x", pady=(0, 10))
        
        # Discord output selection
        ttk.Label(device_frame, text="Discord Output:").pack(anchor="w")
        self.discord_output = ttk.Combobox(device_frame, values=self.output_device_names, width=40)
        self.discord_output.pack(fill="x", pady=(0, 10))
        
        # Control frame
        control_frame = ttk.Frame(self.root, padding=10)
        control_frame.pack(fill="x", padx=10, pady=5)
        
        # Recording button
        self.record_button = ttk.Button(
            control_frame, 
            text="Start Recording", 
            command=self.toggle_recording
        )
        self.record_button.pack(fill="x", pady=5)
        
        # Status label
        self.status_label = ttk.Label(
            control_frame, 
            text="Ready to record", 
            font=("Arial", 10)
        )
        self.status_label.pack(pady=5)
        
    def get_device_id(self, selected_text):
        """Extract device ID from combobox selection."""
        if not selected_text:
            return None
        return int(selected_text.split("ID: ")[1].rstrip(")"))
        
    def toggle_recording(self):
        if not self.recording:
            # Get selected device IDs
            mic_device = self.mic_input.get()
            output_device = self.discord_output.get()
            
            if not mic_device or not output_device:
                self.status_label.config(text="Please select both input and output devices")
                return
            
            mic_id = self.get_device_id(mic_device)
            output_id = self.get_device_id(output_device)
            
            # Set devices
            self.audio_capture.set_mic_device(mic_id)
            self.audio_capture.set_output_device(output_id)
            
            # Start recording
            self.audio_capture.start_recording()
            self.recording = True
            self.record_button.config(text="Stop Recording")
            self.status_label.config(text="Recording...")
            self.mic_input.config(state="disabled")
            self.discord_output.config(state="disabled")
        else:
            # Stop recording
            output_path = self.audio_capture.stop_recording()
            self.recording = False
            self.record_button.config(text="Start Recording")
            self.status_label.config(
                text=f"Recording saved: {output_path.name}" if output_path else "Recording failed"
            )
            self.mic_input.config(state="normal")
            self.discord_output.config(state="normal")

def main():
    root = tk.Tk()
    app = RecordingUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()