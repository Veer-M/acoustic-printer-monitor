import numpy as np
from monitor import dominant_frequency, emergency_stop, inspect, wav_windows
import wave

def test_tones_and_silence():
    rate = 44100
    for frequency in (440, 3000):
        samples = 12000 * np.sin(2 * np.pi * frequency * np.arange(rate) / rate)
        assert abs(dominant_frequency(samples, rate) - frequency) < 2
    assert dominant_frequency(np.zeros(1000), rate) == 0

def test_stop_once_and_wav(tmp_path):
    samples = (10000 * np.sin(2 * np.pi * 3000 * np.arange(44100) / 44100)).astype('<i2')
    path = tmp_path / 'tone.wav'
    with wave.open(str(path), 'wb') as f:
        f.setparams((1, 2, 44100, 0, 'NONE', 'not compressed'))
        f.writeframes(samples.tobytes())
    calls = []
    assert inspect(wav_windows(path), stop=lambda: calls.append('stop'))
    assert calls == ['stop']

def test_firmware_command(monkeypatch):
    import serial
    class Connection:
        def __enter__(self):
            return self
        def __exit__(self, *args):
            pass
        def write(self, data):
            sent.append(data)
        def flush(self):
            sent.append('flushed')
    sent = []
    monkeypatch.setattr(serial, 'Serial', lambda *args, **kwargs: Connection())
    emergency_stop('fake-port')
    assert sent == [b'M112\n', 'flushed']
