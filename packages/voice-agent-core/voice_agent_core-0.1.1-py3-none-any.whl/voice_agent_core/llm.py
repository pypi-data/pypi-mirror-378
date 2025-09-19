import os
import google.generativeai as genai
from dotenv import load_dotenv
import src.actions as actions

tools = [
    {
        "name": "play_on_youtube",
        "description": "Opens YouTube and plays the given video or song query. Use this for any request to play music or videos.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "query": {
                    "type": "STRING",
                    "description": "The name of the song or video to play. For example: 'lofi hip hop radio'"
                }
            },
            "required": ["query"]
        }
    },
    {
        "name": "pause_or_resume",
        "description": "Pauses or resumes the currently playing media (like a YouTube video). Use this for 'pause the song' or 'resume playing'.",
        "parameters": {
            "type": "OBJECT",
            "properties": {}
        }
    },
    {
        "name": "stop_current_task",
        "description": "Stops the current task by closing the active tab in the browser. Use this for 'stop the music', 'end this', or 'close it'.",
        "parameters": {
            "type": "OBJECT",
            "properties": {}
        }
    },
    {
        "name": "open_website",
        "description": "Opens a website in the default browser given a valid URL. Use this for requests like 'open google.com'.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "url": {
                    "type": "STRING",
                    "description": "The full URL of the website to open. For example: 'wikipedia.org'"
                }
            },
            "required": ["url"]
        }
    },
    {
        "name": "search_google",
        "description": "Searches for a query on Google. Use this for general search requests or finding information.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "query": {
                    "type": "STRING",
                    "description": "The topic or question to search for on Google."
                }
            },
            "required": ["query"]
        }
    },
    {
        "name": "open_vscode",
        "description": "Opens the Visual Studio Code application. Use this for requests like 'open my code editor' or 'launch vs code'.",
        "parameters": {
            "type": "OBJECT",
            "properties": {}
        }
    }
]

def initialize_llm():
    """Initializes the Gemini model with the defined tools."""
    load_dotenv()
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    if not gemini_api_key:
        raise ValueError("GEMINI_API_KEY not found in .env file")
        
    genai.configure(api_key=gemini_api_key)
    
    model = genai.GenerativeModel(
        model_name='gemini-2.0-flash',
        generation_config={"temperature": 0.7},
        tools=tools
    )
    return model

def get_llm_response(model, user_text):
    """
    Analyzes user text, decides if a tool should be used, and returns either
    a function call or a conversational response.
    """
    try:
        chat = model.start_chat()
        response = chat.send_message(
            f"You are a helpful and friendly voice assistant named Jarvis. Here is the user's request: '{user_text}'"
        )
        part = response.candidates[0].content.parts[0]
        
        if hasattr(part, 'function_call'):
            function_call = part.function_call
            return {
                "type": "function_call",
                "name": function_call.name,
                "args": {key: value for key, value in function_call.args.items()} if function_call.args else {}
            }
        else:
            return {
                "type": "text_response",
                "content": response.text
            }

    except Exception as e:
        print(f"Error communicating with Gemini: {e}")
        return {
            "type": "text_response",
            "content": "I'm having a bit of trouble thinking right now. Please try again."
        }