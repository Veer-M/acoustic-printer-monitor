# Acoustic printer monitor

This listens to a printer or replays a WAV recording and reports the strongest audio frequency. It can send an emergency-stop command when that frequency passes a chosen threshold.

## Run it

Use Python 3.11 or newer. Run these commands from this repository's folder.

```sh
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS / Linux:
# source .venv/bin/activate
python -m pip install -r requirements.txt
```

```sh
python sample_audio.py
python monitor.py --wav sample.wav
# Live microphone (install requirements-live.txt first):
python monitor.py --device 0
python monitor.py --device 0 --arm-stop --port COM3
```

## How it works and current limits

The 2500 Hz cutoff is a simple configurable rule, not a trained failure detector. Normal printer sounds and room noise can trigger it. Five-second windows also add detection delay. The serial stop needs compatible firmware and has not been tested on a physical printer. Opening some serial ports can reset their controller. Choose a microphone index explicitly to select a USB microphone; the default device is otherwise used.

## Tests

```sh
python -m pip install -r requirements-dev.txt
python -m pytest -q
```

Tests cover known tones, silence, WAV replay, and the exact serial command using a fake connection. Physical printer behavior has not been tested.

For microphone use, install `python -m pip install -r requirements-live.txt`. PyAudio needs PortAudio; on some Linux systems install the PortAudio development package first. Use `--help` for all options.
