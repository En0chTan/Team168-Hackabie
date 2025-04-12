import numpy as np
import audioop
import pyaudio
import sys

# Assuming in_data is the raw byte string data from PyAudio callback
# Set audio parameters
WIDTH = 2  # 2 bytes for 16-bit audio
CHANNELS = 1  # Mono audio (set to 1 for mono)
RATE = 44100  # Sample rate (typically 44100 for CD-quality)

def callback(in_data, frame_count, time_info, status):
    # Convert byte data into numpy array (Mono, single channel)
    audio_data = np.frombuffer(in_data, dtype=np.int16)  # 16-bit signed integers
    
    # Calculate RMS of audio data
    rms = audioop.rms(in_data, WIDTH) / 32767  # RMS normalized to -1 to 1
    db = 20 * np.log10(rms)
    
    if db > -7:
        print("A loud sound was captured... ")
    # Optionally save or process the data here
    #wf.writeframes(in_data)  # Write the audio data to a file

    return (in_data, pyaudio.paContinue)

# Example initialization for PyAudio stream
p = pyaudio.PyAudio()
stream = p.open(format=pyaudio.paInt16,
                channels=CHANNELS,  # Set to 1 for mono audio
                rate=RATE,
                input=True,
                frames_per_buffer=1024,
                stream_callback=callback)

stream.start_stream()

# This will run the audio stream and invoke the callback function
try:
    while stream.is_active():
        pass  # The callback function will process audio continuously
except KeyboardInterrupt:
    print("Stream stopped")
    stream.stop_stream()
    stream.close()
    p.terminate()