# Acoustic printer monitor

A 3D printer makes different sounds as its motors move and its nozzle works. This program listens to those sounds and checks for a strong frequency above a set limit. It can also send a stop command to the printer.

## How it works

The program records five seconds of audio at a time. It uses a Fast Fourier Transform, or FFT, to find the strongest frequency in that recording. A frequency describes how fast a sound wave repeats and is measured in hertz, written as Hz.

The default limit is 2500 Hz. If the strongest frequency goes above that limit, the program reports it and stops listening. If you turn on `--arm-stop`, it also sends `M112` over a serial connection. Compatible printer firmware treats that command as an emergency stop.

You can use a microphone or replay a WAV file. Replaying a file lets you check the program without connecting a printer.

## What to keep in mind

The frequency limit is a basic rule. It has not been trained to tell a printer failure apart from normal sounds. Room noise and normal printer movement can trigger it. The five-second recording window also means a problem may take several seconds to be reported.

The serial stop has not been tested on a physical printer. It needs firmware that supports the command. Opening a serial connection can reset some controllers.

## Try it

Use Python 3.11 or newer. Open a terminal in this project's folder and create a virtual environment. This keeps its packages separate from your other Python projects.

```sh
python -m venv .venv
```

On Windows, activate it with this command.

```sh
.venv\Scripts\activate
```

On macOS or Linux, use this command instead.

```sh
source .venv/bin/activate
```

Then install the packages the project needs.

```sh
python -m pip install -r requirements.txt
```

```sh
python sample_audio.py
python monitor.py --wav sample.wav
```

The sample file plays 600 Hz for five seconds and then 3200 Hz for five seconds. The second sound should pass the default limit.

For live audio, install the extra microphone package.

```sh
python -m pip install -r requirements-live.txt
python monitor.py --device 0
```

`--device` chooses the microphone by its device number. If you leave it out, the program uses the default microphone. PyAudio needs PortAudio, so some Linux systems also need the PortAudio development package.

To enable the printer stop, choose the correct serial port and add `--arm-stop`.

```sh
python monitor.py --device 0 --arm-stop --port COM3
```

You can change the frequency limit with `--threshold` and the recording length with `--seconds`. Use `--help` to see the other options.

## Tests

```sh
python -m pip install -r requirements-dev.txt
python -m pytest -q
```

The tests check known tones, silence, WAV playback, and the exact stop command using a fake serial connection. They do not test a physical printer.
