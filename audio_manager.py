import pyaudio
import wave
import asyncio
import datetime
import os
import tempfile
from config_manager import config
from openai import OpenAI

client = OpenAI(api_key=config.api_key)

class AudioManager:
    def __init__(self):
        self.CHUNK = 4096
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 1
        self.RATE = 44100
        self.RECORD_SECONDS = config.record_duration

    async def record_audio(self):
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        WAVE_OUTPUT_FILENAME = f"answer_{timestamp}.wav"

        p = pyaudio.PyAudio()

        stream = p.open(format=self.FORMAT,
                        channels=self.CHANNELS,
                        rate=self.RATE,
                        input=True,
                        frames_per_buffer=self.CHUNK)

        frames = []
        for _ in range(0, int(self.RATE / self.CHUNK * self.RECORD_SECONDS)):
            try:
                data = await asyncio.to_thread(stream.read, self.CHUNK, exception_on_overflow=False)
                frames.append(data)
            except IOError as e:
                print(f"\nWarning: {e}")

        stream.stop_stream()
        stream.close()
        p.terminate()

        audio_data = b''.join(frames)

        if config.debug:
            await asyncio.to_thread(self._save_audio_file, WAVE_OUTPUT_FILENAME, audio_data, p)
            print(f"Audio saved as {WAVE_OUTPUT_FILENAME}")

        return audio_data

    def _save_audio_file(self, filename, audio_data, p):
        with wave.open(filename, 'wb') as wf:
            wf.setnchannels(self.CHANNELS)
            wf.setsampwidth(p.get_sample_size(self.FORMAT))
            wf.setframerate(self.RATE)
            wf.writeframes(audio_data)

    async def transcribe_audio(self, audio_data):
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_audio_file:
            temp_filename = temp_audio_file.name
            
            # Write audio data to the temporary file
            await asyncio.to_thread(self._save_audio_file, temp_filename, audio_data, pyaudio.PyAudio())
            
            # Reopen the file in binary read mode
            with open(temp_filename, "rb") as audio_file:
                transcript = await asyncio.to_thread(
                    client.audio.transcriptions.create,
                    model="whisper-1", 
                    file=audio_file
                )
        
        # Remove the temporary file
        os.unlink(temp_filename)
        
        transcribed_text = transcript.text.strip()
        print(f"\nTranscribed text: '{transcribed_text}'")
        return transcribed_text

audio_manager = AudioManager()