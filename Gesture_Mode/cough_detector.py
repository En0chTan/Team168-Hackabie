import numpy as np
import sounddevice as sd
import librosa
import queue
import threading
import audioop
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
import time

# Settings
sample_rate = 44100
chunk_duration = 0.5  # seconds
chunk_samples = int(sample_rate * chunk_duration)
audio_queue = queue.Queue()
detected_coughs = []
count = 0

# ---- 1. Analyze a Sample Cough ----
def analyze_sample_cough(file_path):
    y, sr = librosa.load(file_path, sr=sample_rate)
    y = y / np.max(np.abs(y))  # normalize

    rms = np.mean(np.square(y))
    peak = np.max(np.abs(y))
    return {
        "rms": rms,
        "peak": peak
    }

cough_stats = analyze_sample_cough("audio/Spike.wav")
print("Cough Profile:", cough_stats)

# ---- 2. Real-Time Audio Callback ----
def audio_callback(indata, frames, time, status):
    if status:
        print(status)
    audio_queue.put(indata.copy())

# ---- 3. Real-Time Cough Detection ----
def detect_coughs():
    global count
    consecutive = False
    while True:
        chunk = audio_queue.get()
        audio_data = np.frombuffer(chunk, dtype=np.int16)  # 16-bit signed integers
        
        # Calculate RMS of audio data
        rms = audioop.rms(chunk, 2) / 32767  # RMS normalized to -1 to 1
        db = 20 * np.log10(rms)
        if db > -8.2:
            if consecutive == False:
                count += 1
                consecutive = True
                print("Cough-like spike detected!")
                if count >= 3:
                    print("Gesture mode activated")
                    print("Vibrating Phone, please answer 'No' to Cancel emergency signal")
                    time.sleep(10)
                    print("Trasmitting emergency signal...")
                    time.sleep(5000)
                    break;
                detected_coughs.append(chunk)
        else:
            consecutive = False   

# ---- 4. Start Stream & Detection Thread ----
detection_thread = threading.Thread(target=detect_coughs, daemon=True)
detection_thread.start()

print("Listening for cough-like spikes... Press Ctrl+C to stop.\nStarting recording")
with sd.InputStream(callback=audio_callback, channels=1, samplerate=sample_rate, blocksize=chunk_samples):
    try:
        while True:
            sd.sleep(1000)
    except KeyboardInterrupt:
        print("Stopped.")