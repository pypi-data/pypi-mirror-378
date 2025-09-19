# src/voice_agent_core/speaking.py

import requests
import io
import base64
import pyttsx3
from pydub import AudioSegment
from pydub.playback import play

TTS_ENDPOINT_URL = "https://sasthra.in/tts"

# Initialize the fallback engine once
try:
    fallback_engine = pyttsx3.init()
except Exception:
    fallback_engine = None

def speak_with_fallback(text):
    """A simple, local text-to-speech fallback."""
    print(f"Agent (fallback TTS): {text}")
    if fallback_engine:
        fallback_engine.say(text)
        fallback_engine.runAndWait()
    else:
        print("Fallback TTS engine not available.")


def speak(text):
    """
    Sends text to the custom TTS endpoint, decodes the response, and plays the audio.
    Falls back to a local TTS if the API fails.
    """
    try:
        print(f"Agent: {text}")
        
        response = requests.post(TTS_ENDPOINT_URL, json={'text': text}, timeout=20)
        response.raise_for_status()

        json_response = response.json()
        
        if 'audio' in json_response and json_response['audio']:
            audio_base64 = json_response['audio']
            audio_data = base64.b64decode(audio_base64)
            
            audio_segment = AudioSegment.from_file(io.BytesIO(audio_data))
            play(audio_segment)
        else:
            print("TTS API response did not contain audio data.")
            speak_with_fallback(text)
            
    except requests.exceptions.RequestException as e:
        print(f"Error connecting to TTS API: {e}")
        speak_with_fallback(text)
    except (KeyError, base64.binascii.Error, Exception) as e:
        print(f"An error occurred processing TTS audio: {e}")
        speak_with_fallback(text)