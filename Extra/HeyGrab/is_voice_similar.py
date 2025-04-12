from resemblyzer import VoiceEncoder, preprocess_wav
from pathlib import Path
import numpy as np
import sounddevice as sd
import soundfile as sf
import keyboard  # New import

encoder = VoiceEncoder()
samplerate = 16000
duration = 3  # seconds

#----------------Start First Recording------------------------
print("🎙️ Press SPACE to record your voice for voiceprint...")

# Wait for spacebar press
keyboard.wait("space")

print("🎤 Recording...")
my_recording = sd.rec(int(duration * samplerate), samplerate=samplerate, channels=1)
sd.wait()
print("🔇 Shut up nowww!!!!")

sf.write("1.wav", my_recording, samplerate)
fpath = Path("1.wav")
wav = preprocess_wav(fpath)

reference_embedding = encoder.embed_utterance(wav)

#----------------Start Second Recording------------------------
print("🎙️ Press SPACE to record your voice for voiceprint...")

# Wait for spacebar press
keyboard.wait("space")

print("🎤 Recording...")
my_recording = sd.rec(int(duration * samplerate), samplerate=samplerate, channels=1)
sd.wait()
print("🔇 Shut up nowww!!!!")

sf.write("2.wav", my_recording, samplerate)
fpath = Path("2.wav")
wav = preprocess_wav(fpath)

test_embedding = encoder.embed_utterance(wav)

# Compare using cosine similarity
similarity = np.dot(reference_embedding, test_embedding) / (
    np.linalg.norm(reference_embedding) * np.linalg.norm(test_embedding)
)

print(f"🎯 Similarity Score: {similarity:.3f}")
if similarity > 0.70:
    print("✅ Same speaker!")
else:
    print("❌ Different speaker.")