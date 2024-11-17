import tkinter as tk
from tkinter import ttk
from dnd_session_recorder.audio.capture import AudioCaptureManager

class RecordingWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("D&D Session Recorder")
        self.audio_manager = AudioCaptureManager()
        
        # Create main frame
        self.main_frame = ttk.Frame(root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Input device selection
        self.input_devices = self.audio_manager.get_input_devices()
        self.input_device_var = tk.StringVar()
        
        ttk.Label(self.main_frame, text="Select Microphone:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.input_combo = ttk.Combobox(
            self.main_frame, 
            textvariable=self.input_device_var,
            values=[device['name'] for device in self.input_devices]
        )
        self.input_combo.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5)
        if self.input_devices:
            self.input_combo.set(self.input_devices[0]['name'])

        # Output device selection
        self.output_devices = self.audio_manager.get_output_devices()
        self.output_device_var = tk.StringVar()
        
        ttk.Label(self.main_frame, text="Select System Audio:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.output_combo = ttk.Combobox(
            self.main_frame, 
            textvariable=self.output_device_var,
            values=[device['name'] for device in self.output_devices]
        )
        self.output_combo.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5)
        if self.output_devices:
            self.output_combo.set(self.output_devices[0]['name'])
            
        # Status label
        self.status_var = tk.StringVar(value="Ready to record")
        self.status_label = ttk.Label(
            self.main_frame, 
            textvariable=self.status_var,
            foreground="green"
        )
        self.status_label.grid(row=2, column=0, columnspan=2, pady=10)
        
        # Record button
        self.record_button = ttk.Button(
            self.main_frame,
            text="Start Recording",
            command=self.toggle_recording
        )
        self.record_button.grid(row=3, column=0, columnspan=2, pady=10)
        
        # Add some padding around all widgets
        for child in self.main_frame.winfo_children():
            child.grid_configure(padx=5)

    def toggle_recording(self):
        if not self.audio_manager.recording:
            # Get selected input device
            selected_input_name = self.input_device_var.get()
            selected_input = next(
                (device for device in self.input_devices if device['name'] == selected_input_name),
                None
            )
            
            # Get selected output device
            selected_output_name = self.output_device_var.get()
            selected_output = next(
                (device for device in self.output_devices if device['name'] == selected_output_name),
                None
            )
            
            if selected_input and selected_output:
                try:
                    self.audio_manager.start_recording(
                        input_device_index=selected_input['index'],
                        output_device_index=selected_output['index']
                    )
                    self.status_var.set("Recording...")
                    self.record_button.configure(text="Stop Recording")
                    self.input_combo.configure(state="disabled")
                    self.output_combo.configure(state="disabled")
                except Exception as e:
                    self.status_var.set(f"Recording error: {str(e)}")
            else:
                self.status_var.set("Please select both input and output devices")
        else:
            try:
                self.audio_manager.stop_recording()
                self.status_var.set("Recording saved")
                self.record_button.configure(text="Start Recording")
                self.input_combo.configure(state="normal")
                self.output_combo.configure(state="normal")
            except Exception as e:
                self.status_var.set(f"Error stopping recording: {str(e)}")

    def __del__(self):
        """Cleanup when the window is closed."""
        if hasattr(self, 'audio_manager'):
            if self.audio_manager.recording:
                self.audio_manager.stop_recording()