import pyaudio
import webrtcvad
import struct

# Audio settings
sample_rate = 16000
frame_duration = 30  # ms
frame_size = int(sample_rate * frame_duration / 1000)  # samples per frame
frame_bytes = frame_size * 2  # 2 bytes per sample (16-bit audio)

# Initialize PyAudio
pa = pyaudio.PyAudio()
stream = pa.open(format=pyaudio.paInt16,
                 channels=1,
                 rate=sample_rate,
                 input=True,
                 frames_per_buffer=frame_size)

# Initialize VAD
vad = webrtcvad.Vad()
vad.set_mode(3)  # 0 = aggressive (detect more), 3 = relaxed

print("Listening for speech... (Press Ctrl+C to stop)")

try:
    while True:
        audio = stream.read(frame_size, exception_on_overflow=False)
        is_speech = vad.is_speech(audio, sample_rate)

        if is_speech:
            print("Speech detected.")
        else:
            print("Silence.")

except KeyboardInterrupt:
    print("Stopped.")

finally:
    stream.stop_stream()
    stream.close()
    pa.terminate()