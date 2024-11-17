from setuptools import setup, find_packages

setup(
    name="dnd_session_recorder",
    version="0.1",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "sounddevice",
        "numpy",
        "scipy",
    ],
    python_requires=">=3.8",
)