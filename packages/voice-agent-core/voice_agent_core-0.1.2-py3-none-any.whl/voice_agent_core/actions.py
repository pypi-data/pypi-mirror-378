import webbrowser
import pywhatkit
import subprocess
import platform
import pyautogui
import time

def play_on_youtube(query):
    """Opens YouTube and plays the given video query."""
    print(f"Playing '{query}' on YouTube...")
    try:
        pywhatkit.playonyt(query)
        time.sleep(5)  # Give the browser time to open
        return f"Alright, playing {query} on YouTube."
    except Exception as e:
        print(f"Error playing on YouTube: {e}")
        return "Sorry, I couldn't play that on YouTube."

def pause_or_resume():
    """Simulates pressing the 'k' key to pause or resume media in the active window."""
    try:
        pyautogui.press('k')
        return "Done."
    except Exception as e:
        return f"Could not perform action: {e}"

def stop_current_task():
    """Simulates pressing 'ctrl+w' (or 'cmd+w' on Mac) to close the current tab."""
    try:
        if platform.system() == "Darwin":  # macOS
            pyautogui.hotkey('command', 'w')
        else:  # Windows/Linux
            pyautogui.hotkey('ctrl', 'w')
        return "Okay, I've stopped the current task."
    except Exception as e:
        return f"Could not perform action: {e}"

def open_website(url):
    """Opens a website in the default browser."""
    if not url.startswith('http'):
        url = f'https://{url}'
    print(f"Opening website: {url}")
    webbrowser.open(url)
    return f"Opening {url} now."

def search_google(query):
    """Searches for a query on Google."""
    print(f"Searching Google for '{query}'...")
    try:
        pywhatkit.search(query)
        return f"Here are the search results for {query}."
    except Exception as e:
        print(f"Error searching Google: {e}")
        return "Sorry, I ran into an error while searching Google."

def open_vscode():
    """Opens Visual Studio Code."""
    print("Opening Visual Studio Code...")
    system = platform.system()
    try:
        if system == "Windows":
            subprocess.run(["code"], check=True)
        elif system == "Darwin":
            subprocess.run(["open", "-a", "Visual Studio Code"], check=True)
        else:
            subprocess.run(["code"], check=True)
        return "Opening VS Code."
    except (FileNotFoundError, subprocess.CalledProcessError):
        return "I couldn't find VS Code. Make sure it's installed and 'code' is in your system's PATH."