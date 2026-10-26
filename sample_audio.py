import wave
import numpy as np
samples = np.concatenate([12000 * np.sin(2 * np.pi * f * np.arange(44100 * 5) / 44100) for f in (600, 3200)])
with wave.open('sample.wav', 'wb') as output:
    output.setparams((1, 2, 44100, 0, 'NONE', 'not compressed'))
    output.writeframes(samples.astype('<i2').tobytes())
print('Wrote sample.wav: five seconds at 600 Hz, then five at 3200 Hz')
