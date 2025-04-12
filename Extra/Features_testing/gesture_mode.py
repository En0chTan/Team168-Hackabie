import numpy as np
import sounddevice as sd
import time
from collections import deque

# Parameters
sr = 16000              # Sample rate
frame_duration = 0.02   # 20 ms
frame_samples = int(sr * frame_duration)
energy_threshold = None
spike_times = deque(maxlen=10)

def audio_callback(indata, frames, time_info, status):
    global energy_threshold

    # Calculate short-term energy of this frame
    audio_frame = indata[:, 0]
    energy = np.sum(audio_frame**2)

    # Init dynamic threshold after a few seconds
    if energy_threshold is None:
        energy_buffer.append(energy)
        if len(energy_buffer) > 50:  # ~1 sec
            mean = np.mean(energy_buffer)
            std = np.std(energy_buffer)
            energy_threshold = mean + 2 * std
        return

    if energy > energy_threshold:
        now = time.time()
        spike_times.append(now)
        print(f"Spike detected at {now:.2f}")

        # Check for 3 in succession within 2 sec
        if len(spike_times) >= 3:
            if spike_times[-1] - spike_times[-3] <= 2.0:
                print("🚨 3 cough-like spikes detected!")
                spike_times.clear()

# Rolling buffer to calculate threshold
energy_buffer = deque(maxlen=100)

# Start the stream
with sd.InputStream(callback=audio_callback, channels=1, samplerate=sr, blocksize=frame_samples):
    print("Listening for coughs... Press Ctrl+C to stop.")
    try:
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("Stopped.")