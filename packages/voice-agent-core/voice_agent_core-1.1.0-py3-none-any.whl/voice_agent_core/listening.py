# src/voice_agent_core/listening.py

import os
import sys
import struct
import pvporcupine
import pyaudio
import speech_recognition as sr
from contextlib import contextmanager

@contextmanager
def suppress_stderr():
    """A context manager to temporarily suppress stderr messages."""
    original_stderr = sys.stderr
    sys.stderr = open(os.devnull, 'w')
    try:
        yield
    finally:
        sys.stderr.close()
        sys.stderr = original_stderr

def listen_for_wake_word():
    """Listens for the wake word in real-time using the highly efficient Porcupine engine."""
    access_key = os.getenv("PICOVOICE_ACCESS_KEY")
    if not access_key:
        raise ValueError("PICOVOICE_ACCESS_KEY not found. Please set it in your environment variables or .env file.")

    porcupine = None
    pa = None
    audio_stream = None

    try:
        with suppress_stderr():
            porcupine = pvporcupine.create(
                access_key=access_key,
                keywords=['porcupine', 'hey siri', 'alexa', 'ok google'] 
            )
            pa = pyaudio.PyAudio()
            audio_stream = pa.open(
                rate=porcupine.sample_rate,
                channels=1,
                format=pyaudio.paInt16,
                input=True,
                frames_per_buffer=porcupine.frame_length
            )

        print("Listening for wake word ('porcupine')...")

        while True:
            pcm = audio_stream.read(porcupine.frame_length)
            pcm = struct.unpack_from("h" * porcupine.frame_length, pcm)
            keyword_index = porcupine.process(pcm)
            if keyword_index >= 0:
                print("Wake word detected!")
                return True

    except Exception as e:
        print(f"Error during wake word detection: {e}")
        return False
    finally:
        if audio_stream is not None:
            audio_stream.close()
        if pa is not None:
            pa.terminate()
        if porcupine is not None:
            porcupine.delete()

def listen_for_command():
    """Listens for a command AFTER the wake word is detected using the fast Whisper tiny.en model."""
    recognizer = sr.Recognizer()
    recognizer.pause_threshold = 2.0

    with sr.Microphone() as source:
        print("Adjusting for noise...")
        recognizer.adjust_for_ambient_noise(source, duration=0.5)
        print("Listening for command...")
        
        try:
            with suppress_stderr():
                audio = recognizer.listen(source, timeout=15, phrase_time_limit=15)
            
            print("Transcribing with 'tiny.en' model...")
            command = recognizer.recognize_whisper(audio, language="english", model="tiny.en")
            print(f"Command heard: {command}")
            return command.lower()
        except sr.UnknownValueError:
            print("Sorry, I did not understand that.")
            return None
        except sr.RequestError as e:
            print(f"Whisper service error: {e}")
            return None