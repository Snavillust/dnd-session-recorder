import pytest
from pathlib import Path
from dnd_session_recorder.audio.capture import AudioCapture
import time

def test_audio_capture_initialization():
    capture = AudioCapture()
    assert not capture.is_recording()
    assert capture.sample_rate == 44100
    assert capture.channels == 2
    
def test_list_devices():
    devices = AudioCapture.list_devices()
    assert isinstance(devices, list)
    assert all(isinstance(d, tuple) and len(d) == 4 for d in devices)
    
def test_set_device():
    capture = AudioCapture()
    devices = AudioCapture.list_devices()
    if devices:  # Only test if we have audio devices
        capture.set_device(devices[0][0])
        assert capture.device_id == devices[0][0]
        
def test_set_invalid_device():
    capture = AudioCapture()
    with pytest.raises(ValueError):
        capture.set_device(-1)

@pytest.mark.skip(reason="Manual test - requires audio input")
def test_recording_workflow():
    capture = AudioCapture()
    devices = AudioCapture.list_devices()
    if not devices:
        pytest.skip("No audio devices available")
        
    # Set up recording device
    capture.set_device(devices[0][0])
    
    # Start recording
    capture.start_recording()
    assert capture.is_recording()
    
    # Record for 3 seconds
    time.sleep(3)
    
    # Stop recording
    output_path = capture.stop_recording()
    assert not capture.is_recording()
    assert output_path.exists()
    assert output_path.suffix == '.wav'