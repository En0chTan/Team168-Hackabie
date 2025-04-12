import pyaudio
import wave
import librosa
import librosa.display
import matplotlib.pyplot as plt
import numpy as np
from scipy.signal import find_peaks
import keyboard

# Settings
filename = "audio/audio_analysis.wav"
duration = 5  # seconds
rate = 44100
channels = 1
format = pyaudio.paInt16
chunk = 1024


def record_audio():
    duration = int(input("Enter seconds: "))
    audio = pyaudio.PyAudio()

    stream = audio.open(format=format,
                        channels=channels,
                        rate=rate,
                        input=True,
                        frames_per_buffer=chunk)

    print(f"Recording for {duration} seconds...")
    frames = []

    for _ in range(0, int(rate / chunk * duration)):
        data = stream.read(chunk)
        frames.append(data)

    print("Recording complete.")

    stream.stop_stream()
    stream.close()
    audio.terminate()

    with wave.open("audio/audio_analysis.wav", 'wb') as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(audio.get_sample_size(format))
        wf.setframerate(rate)
        wf.writeframes(b''.join(frames))

    print(f"Saved to audio/audio_analysis.wav")

def choose_file():
    global filename
    print("Pick a file: ")
    print("(1) audio_analysis.wav")
    print("(2) spike.wav")
    choice = input("Number: ")
    if choice == "1":
        filename = "audio/audio_analysis.wav"
    else:
        filename = "audio/Spike.wav"
        
def plot_waveform():
    choose_file()
    try:
        y, sr = librosa.load(filename, sr=None)
        plt.figure(figsize=(10, 3))
        librosa.display.waveshow(y, sr=sr)
        plt.axhline(np.mean(y), color='red', linestyle='--', label='Average (center line)')
        plt.title("Waveform")
        plt.xlabel("Time (s)")
        plt.ylabel("Amplitude")
        plt.tight_layout()
        plt.show()
    except FileNotFoundError:
        print("No audio file found. Please record first.")


def plot_spectrogram():
    choose_file()
    try:
        y, sr = librosa.load(filename, sr=None)
        S = librosa.stft(y)
        S_db = librosa.amplitude_to_db(abs(S))

        plt.figure(figsize=(10, 4))
        librosa.display.specshow(S_db, sr=sr, x_axis='time', y_axis='hz')
        plt.colorbar(format='%+2.0f dB')
        plt.title("Spectrogram (dB)")
        plt.tight_layout()
        plt.show()
    except FileNotFoundError:
        print("No audio file found. Please record first.")

def smooth_signal(y, window_size=101):
    """Apply simple moving average to smooth signal"""
    window = np.ones(window_size) / window_size
    return np.convolve(np.abs(y), window, mode='same')

def any_spikes():
    choose_file()
    y, sr = librosa.load(filename)

    # Optional: normalize
    y = y / np.max(np.abs(y))

    # Compute mean and threshold
    avg_amp = np.mean(np.abs(y))     # baseline activity
    threshold = 0.45            # tune this — 0.2~0.4 works well for loud spikes

    # Find where it's "spikey"
    spikes = np.where(np.abs(y) > threshold)[0]

    print(f"Found {len(spikes)} spike samples")

    # Find peak frames, distance prevents too-close clustering
    peak_idxs, _ = find_peaks(np.abs(y), height=threshold, distance=sr//18,prominence = 0.01)  # e.g., 100ms apart

    print(f"Found {len(peak_idxs)} major peaks")

    # Visualize
    import matplotlib.pyplot as plt

    plt.figure(figsize=(10, 3))
    librosa.display.waveshow(y, sr=sr)
    plt.plot(peak_idxs / sr, y[peak_idxs], 'rx', label="Spikes")
    plt.axhline(threshold, color='red', linestyle='--', label='Threshold')
    plt.title("Detected Spikes")
    plt.legend()
    plt.tight_layout()
    plt.show()
    
def set_spike():
    audio = pyaudio.PyAudio()

    print("Press [SPACE] to start recording...")

    # Wait for spacebar
    keyboard.wait('space')
    print("Recording... Press [X] to stop.")

    stream = audio.open(format=format,
                        channels=channels,
                        rate=rate,
                        input=True,
                        frames_per_buffer=chunk)

    frames = []

    # Record until 'x' is pressed
    while True:
        if keyboard.is_pressed('x'):
            print("Stopping...")
            break
        data = stream.read(chunk)
        frames.append(data)

    stream.stop_stream()
    stream.close()
    audio.terminate()

    # Save
    with wave.open("audio/Spike.wav", 'wb') as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(audio.get_sample_size(format))
        wf.setframerate(rate)
        wf.writeframes(b''.join(frames))

    print(f"Saved to {filename}")

def main():
    while True:
        print("\n🎧 Welcome to Audio Analysis Tool!")
        print("(1) Record Audio")
        print("(2) Show Waveform")
        print("(3) Show Spectrogram")
        print("(4) Show Spikes count")
        print("(5) Good bye")
        print("(6) Set spike")

        choice = input("Enter number: ")

        if choice == '1':
            record_audio()
        elif choice == '2':
            plot_waveform()
        elif choice == '3':
            plot_spectrogram()
        elif choice == '4':
            any_spikes()
        elif choice == '5':
            print("Goodbye!")
            break
        elif choice == '6':
            set_spike()
        else:
            print("Invalid option, try again.")


if __name__ == "__main__":
    main()