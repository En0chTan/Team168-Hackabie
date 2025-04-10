import sounddevice as sd
import numpy as np

# Settings
samplerate = 44100  # Hz
blocksize = 1024    # Samples per block
threshold_db = -20  # dBFS (probably can ask driver to set this?) like where is the phone normally located etc

def audio_callback(indata, frames, time, status):
    if status:
        print(status)
    
    mono_data = np.mean(indata, axis=1)
    rms = np.sqrt(np.mean(mono_data**2))
    if rms > 0:
        db = 20 * np.log10(rms)
    # Check threshold
    if db > threshold_db:
        print("🔊 Loud sound detected!")

# Start stream
with sd.InputStream(callback=audio_callback,
                    channels=1,
                    samplerate=samplerate,
                    blocksize=blocksize):
    print("🎧 Listening... Press Ctrl+C to stop.")
    try:
        while True:
            pass
    except KeyboardInterrupt:
        print("👋 Done.")