import speech_recognition as sr
import time

WAKE_WORD = "saara"  # Change this to your preferred wake word
recognizer = sr.Recognizer()

def listen_for_wake_word():
    """Passively listens in the background for the wake word."""
    with sr.Microphone() as source:
        print(f"\nListening for wake word '{WAKE_WORD}'...")
        recognizer.adjust_for_ambient_noise(source, duration=0.5)
        try:
            # Use a faster, less accurate model for quick wake word detection
            # Timeout helps the loop not get stuck
            audio = recognizer.listen(source, timeout=10, phrase_time_limit=2)
            text = recognizer.recognize_whisper(audio, language="english", model="tiny.en")
            print(f"Heard: '{text.lower().strip()}'")
            if WAKE_WORD in text.lower().strip():
                return True
        except sr.UnknownValueError:
            # This is expected when there's silence or background noise
            pass
        except sr.WaitTimeoutError:
            # This is also expected, just means no speech was detected
            pass
        except Exception as e:
            print(f"An error occurred during wake word detection: {e}")
            
    return False

def listen_for_command():
    """Activates after the wake word and listens for a full command."""
    with sr.Microphone() as source:
        print("\nWake word detected! Listening for command...")
        time.sleep(0.5)
        recognizer.adjust_for_ambient_noise(source, duration=0.5)
        try:
            # Use a more accurate model for understanding the command
            audio = recognizer.listen(source, timeout=10, phrase_time_limit=15)
            print("Recognizing command with Whisper...")
            command = recognizer.recognize_whisper(audio, language="english", model="base.en")
            print(f"You said: {command}")
            return command.lower()
        except sr.UnknownValueError:
            print("Could not understand the command.")
        except Exception as e:
            print(f"An error occurred during command listening: {e}")
            
    return None