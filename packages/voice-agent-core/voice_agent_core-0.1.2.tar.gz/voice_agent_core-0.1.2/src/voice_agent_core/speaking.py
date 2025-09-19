import requests
import io
import base64  # <-- Import the base64 library
import pyttsx3   # <-- Import the fallback TTS
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
        
        # 1. Make the POST request to your TTS API
        response = requests.post(TTS_ENDPOINT_URL, json={'text': text}, timeout=20)
        response.raise_for_status()  # Raise an error for bad status codes (4xx or 5xx)

        # 2. Parse the JSON response from the server
        json_response = response.json()
        
        # 3. Check if the 'audio' key exists and decode the base64 string
        if 'audio' in json_response and json_response['audio']:
            audio_base64 = json_response['audio']
            audio_data = base64.b64decode(audio_base64)
            
            # 4. Load the decoded audio data from memory and play it
            audio_segment = AudioSegment.from_file(io.BytesIO(audio_data))
            play(audio_segment)
        else:
            # The server responded but didn't provide audio data
            print("TTS API response did not contain audio data.")
            speak_with_fallback(text)
            
    except requests.exceptions.RequestException as e:
        print(f"Error connecting to TTS API: {e}")
        speak_with_fallback(text)
    except (KeyError, base64.binascii.Error, Exception) as e:
        # This will catch errors from JSON parsing, base64 decoding, or pydub playback
        print(f"An error occurred processing TTS audio: {e}")
        speak_with_fallback(text)