# src/voice_agent_core/actions.py

import pywhatkit
import webbrowser
import pyautogui
import subprocess

def play_on_youtube(query: str):
    """
    Opens YouTube and plays the given video or song query.

    Args:
        query (str): The name of the song or video to play. For example: 'lofi hip hop radio'
    """
    try:
        pywhatkit.playonyt(query)
        return f"Now playing '{query}' on YouTube."
    except Exception as e:
        return f"Sorry, I couldn't play that. Error: {e}"

def pause_or_resume():
    """
    Pauses or resumes the currently playing media by simulating a spacebar press.
    """
    pyautogui.press('space')
    return "Done."

def stop_current_task():
    """
    Stops the current task by closing the active tab in the browser (Ctrl+W).
    """
    pyautogui.hotkey('ctrl', 'w')
    return "Stopped."

def open_website(url: str):
    """
    Opens a website in the default browser given a valid URL.

    Args:
        url (str): The full URL of the website to open. Must start with http or https.
    """
    # Ensure the URL is properly formatted
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    webbrowser.open(url)
    return f"Opening {url}."

def search_google(query: str):
    """
    Searches for a query on Google.

    Args:
        query (str): The topic or question to search for on Google.
    """
    pywhatkit.search(query)
    return f"Searching Google for '{query}'."

def open_vscode():
    """
    Opens the Visual Studio Code application.
    """
    try:
        # The command to open VS Code is 'code' on most systems
        subprocess.run(['code'], check=True)
        return "Opening Visual Studio Code."
    except FileNotFoundError:
        return "I couldn't find Visual Studio Code. Is it installed and in your system's PATH?"
    except Exception as e:
        return f"An error occurred: {e}"