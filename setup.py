from setuptools import setup, find_packages

setup(
    name="dnd_session_recorder",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "faster-whisper",
        "pyannote-audio",
        "librosa",
        "sounddevice",
    ],
    extras_require={
        "dev": ["pytest", "pytest-cov"],
    },
)
