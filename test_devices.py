import pyaudio

def list_audio_devices():
    p = pyaudio.PyAudio()
    print("\nAvailable Audio Devices:")
    print("-" * 50)
    for i in range(p.get_device_count()):
        dev = p.get_device_info_by_index(i)
        print(f"Device {i}: {dev.get('name')}")
        print(f"  Max Input Channels: {dev.get('maxInputChannels')}")
        print(f"  Max Output Channels: {dev.get('maxOutputChannels')}")
        print(f"  Default Sample Rate: {dev.get('defaultSampleRate')}")
        print("-" * 50)
    p.terminate()

if __name__ == "__main__":
    list_audio_devices()