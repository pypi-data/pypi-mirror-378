# src/voice_agent_core/listening.py

import speech_recognition as sr
import os
import sys
from contextlib import contextmanager

# Define a context manager to suppress ALSA warnings from PyAudio
@contextmanager
def suppress_stderr():
    # Keep the original stderr
    original_stderr = sys.stderr
    # Redirect stderr to /dev/null
    sys.stderr = open(os.devnull, 'w')
    try:
        yield
    finally:
        # Restore the original stderr
        sys.stderr.close()
        sys.stderr = original_stderr

def listen_for_wake_word():
    """Listens for the wake word 'saara' using a more accurate model."""
    recognizer = sr.Recognizer()
    wake_word = "saara" # Or your preferred wake word

    with sr.Microphone() as source:
        print(f"Adjusting for ambient noise... Please be quiet for a moment.")
        # Listen for 1 second to calibrate the energy threshold for ambient noise levels
        recognizer.adjust_for_ambient_noise(source, duration=1)
        print(f"Listening for wake word '{wake_word}'...")
        
        while True:
            try:
                # Use the context manager to hide ALSA warnings during listening
                with suppress_stderr():
                    audio = recognizer.listen(source, timeout=10, phrase_time_limit=2)

                # Use a more accurate model for better recognition
                text = recognizer.recognize_whisper(audio, language="english", model="small")
                text = text.lower().strip()
                print(f"Heard: '{text}'")

                if wake_word in text:
                    print("Wake word detected.")
                    return True
            except sr.UnknownValueError:
                # This is normal, just means silence was detected
                pass
            except sr.RequestError as e:
                print(f"Could not request results from Whisper service; {e}")
            except Exception as e:
                print(f"An error occurred during wake word detection: {e}")
                # We return False here to prevent an infinite loop on a persistent error
                return False

def listen_for_command():
    """Listens for a command after the wake word is detected."""
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening for your command...")
        recognizer.adjust_for_ambient_noise(source, duration=0.5)
        
        try:
            with suppress_stderr():
                audio = recognizer.listen(source, timeout=10, phrase_time_limit=10)
            
            # You can use a smaller model here if command recognition is easier
            command = recognizer.recognize_whisper(audio, language="english", model="base")
            print(f"Command heard: {command}")
            return command.lower()
        except sr.UnknownValueError:
            print("Sorry, I did not understand that.")
            return None
        except sr.RequestError as e:
            print(f"Whisper service error: {e}")
            return None