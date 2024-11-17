import tkinter as tk
from src.dnd_session_recorder.ui.recording_window import RecordingWindow
import sounddevice as sd

def list_all_devices():
    """Print all audio devices for debugging."""
    print("\nAvailable Audio Devices:")
    print("-" * 50)
    devices = sd.query_devices()
    for i, device in enumerate(devices):
        print(f"Device {i}: {device['name']}")
        print(f"  Channels (in/out): {device['max_input_channels']}/{device['max_output_channels']}")
        print(f"  Sample Rate: {device['default_samplerate']}")
        if device is sd.default.device:
            print("  *DEFAULT DEVICE*")
        print("-" * 50)

def main():
    # Print device information
    print("\nDefault devices:")
    print(f"Input: {sd.default.device[0]}")
    print(f"Output: {sd.default.device[1]}")
    list_all_devices()
    
    # Start the application
    root = tk.Tk()
    app = RecordingWindow(root)
    root.mainloop()

if __name__ == "__main__":
    main()