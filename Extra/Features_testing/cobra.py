import pvcobra
import pyaudio
import struct
import sys
from dotenv import dotenv_values

def main():
    config = dotenv_values(".env")
    cobra = pvcobra.create(access_key=config["PICO-API"])

    pa = pyaudio.PyAudio()
    stream = pa.open(
        rate=cobra.sample_rate,
        channels=1,
        format=pyaudio.paInt16,
        input=True,
        frames_per_buffer=cobra.frame_length
    )

    print("Listening for voice activity...")
    count = 30
    try:
        while True:
            pcm = stream.read(cobra.frame_length, exception_on_overflow=False)
            pcm = struct.unpack_from("h" * cobra.frame_length, pcm)

            voice_probability = cobra.process(pcm)

            if voice_probability > 0.3:
                count = 30
                print(f"Voice detected ({voice_probability:.2f})")
            else:
                count -= 1
                if count < 0:
                    print("Exiting...")
                    stream.stop_stream()
                    stream.close()
                    pa.terminate()
                    cobra.delete()
                    sys.exit(0)
                print(f"Silence ({voice_probability:.2f})")

    except KeyboardInterrupt:
        print("Exiting...")

    finally:
        stream.stop_stream()
        stream.close()
        pa.terminate()
        cobra.delete()

if __name__ == "__main__":
    main()