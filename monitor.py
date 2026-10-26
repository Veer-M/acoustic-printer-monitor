import argparse
import logging
import math
import wave
import numpy as np

def dominant_frequency(samples, rate):
    samples = np.asarray(samples, dtype=float)
    if samples.ndim != 1 or len(samples) < 2 or rate <= 0:
        raise ValueError('Expected a mono sample array and a positive sample rate')
    samples = samples - samples.mean()
    if np.max(np.abs(samples)) < 1:
        return 0.0
    spectrum = np.abs(np.fft.rfft(samples * np.hanning(len(samples))))
    spectrum[0] = 0
    return float(np.fft.rfftfreq(len(samples), 1 / rate)[np.argmax(spectrum)])

def wav_windows(path, seconds=5):
    with wave.open(str(path), 'rb') as source:
        if source.getsampwidth() != 2 or source.getcomptype() != 'NONE':
            raise ValueError('Use an uncompressed 16-bit PCM WAV')
        rate = source.getframerate()
        while data := source.readframes(max(1, round(seconds * rate))):
            samples = np.frombuffer(data, dtype='<i2').reshape(-1, source.getnchannels())
            yield samples.astype(float).mean(axis=1), rate

def microphone_windows(device=None, seconds=5, rate=44100, chunk=4096):
    import pyaudio
    audio = pyaudio.PyAudio()
    stream = None
    try:
        stream = audio.open(format=pyaudio.paInt16, channels=1, rate=rate, input=True,
                            input_device_index=device, frames_per_buffer=chunk)
        while True:
            remaining = round(rate * seconds)
            parts = []
            while remaining:
                count = min(chunk, remaining)
                parts.append(stream.read(count, exception_on_overflow=False))
                remaining -= count
            yield np.frombuffer(b''.join(parts), dtype='<i2'), rate
    finally:
        if stream is not None:
            stream.stop_stream()
            stream.close()
        audio.terminate()

def emergency_stop(port, baud=115200):
    import serial
    with serial.Serial(port, baud, timeout=2, write_timeout=2) as connection:
        connection.write(b'M112\n')
        connection.flush()

def inspect(windows, threshold=2500, stop=None):
    for samples, rate in windows:
        peak = dominant_frequency(samples, rate)
        logging.info('Dominant frequency: %.1f Hz', peak)
        if peak > threshold:
            logging.error('Frequency threshold exceeded: %.1f Hz', peak)
            if stop is not None:
                stop()
            return True
    return False

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--wav')
    parser.add_argument('--device', type=int)
    parser.add_argument('--threshold', type=float, default=2500)
    parser.add_argument('--seconds', type=float, default=5)
    parser.add_argument('--port', default='COM3')
    parser.add_argument('--baud', type=int, default=115200)
    parser.add_argument('--arm-stop', action='store_true')
    args = parser.parse_args()
    if not all(math.isfinite(v) and v > 0 for v in (args.seconds, args.threshold)):
        parser.error('Seconds and threshold must be positive and finite')
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    windows = wav_windows(args.wav, args.seconds) if args.wav else microphone_windows(args.device, args.seconds)
    try:
        inspect(windows, args.threshold, (lambda: emergency_stop(args.port, args.baud)) if args.arm_stop else None)
    except KeyboardInterrupt:
        logging.info('Stopped listening')
    finally:
        windows.close()

if __name__ == '__main__':
    main()
