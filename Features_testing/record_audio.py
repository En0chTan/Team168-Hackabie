import sounddevice as sd
import soundfile as sf
import keyboard  # New import

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

sf.write("audio/record_audio.wav", my_recording, samplerate)