import wave
import numpy as np

# Parameters
sample_rate = 16000
duration = 1  # seconds
num_channels = 1
sampwidth = 2  # 16-bit
num_frames = duration * sample_rate

# Create silent audio data
silent_data = np.zeros(num_frames, dtype=np.int16)

# Write to a .wav file
with wave.open("/Users/natalacernikova/Downloads/aurion-stage13/aurion-backend/tests/e2e/silent.wav", "wb") as wf:
    wf.setnchannels(num_channels)
    wf.setsampwidth(sampwidth)
    wf.setframerate(sample_rate)
    wf.writeframes(silent_data.tobytes())
