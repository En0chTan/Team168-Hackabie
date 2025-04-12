import pvporcupine
import pyaudio
import struct
import os
import wave
import pvcobra
import time
from openai import OpenAI
import asyncio
import sys
from dotenv import dotenv_values

def main():
    config = dotenv_values(".env")
    access_key = config["PICO-API"]  # From Picovoice Console
    keyword_path = "hey_grab_ppn.ppn"
    filename = "audio/porcupine_whisper.wav"
    
    # Set your API key here
    client = OpenAI(api_key=config["OPEN-API"])

    # Async function to handle transcription
    def transcribe():
        transcript = client.audio.translations.create(
            model="whisper-1",
            file=open(filename, "rb"),
            prompt="Transcribe without translation."
        )
        print(transcript)


    cobra = pvcobra.create(access_key=access_key)
    porcupine = pvporcupine.create(
        access_key=access_key,
        keyword_paths=[keyword_path]
    )

    pa = pyaudio.PyAudio()
    audio_stream = pa.open(
        rate=porcupine.sample_rate, #16k 
        channels=1,
        format=pyaudio.paInt16,
        input=True,
        frames_per_buffer=porcupine.frame_length #512
    )


    rate = porcupine.sample_rate
    chunk = porcupine.frame_length

    while True:
        print("Listening for 'Hey Grab'...")
        record = False #As a trigger to start recording
        frames = [] #To put chunks of audio
        count = 30
        result = -1
        flag_1 = 0
        try:
            while True:
                pcm_b = audio_stream.read(porcupine.frame_length, exception_on_overflow=False)
                pcm = struct.unpack_from("h" * porcupine.frame_length, pcm_b)
                if result < 0:
                    result = porcupine.process(pcm)
                if result >= 0:
                    if flag_1 == 0:
                        print("Triggered!")
                        flag_1 = 1
                    record = True  #Start recording
                    # You can now trigger your recording logic here
                    if record:
                        voice_probability = cobra.process(pcm)
                        if voice_probability < 0.3:
                            count -= 1
                            if count <= 0:
                                wf = wave.open(filename, 'wb')
                                wf.setnchannels(1)
                                wf.setsampwidth(pa.get_sample_size(pyaudio.paInt16))
                                wf.setframerate(rate)
                                wf.writeframes(b''.join(frames))
                                wf.close()
                                print(f"Saved to {filename}")
                                transcribe()
                                break
                        else:
                            count = 30
                        frames.append(pcm_b)

        except KeyboardInterrupt:
            print("Stopping...")
            sys.exit(0)


if __name__ == "__main__":
    main()