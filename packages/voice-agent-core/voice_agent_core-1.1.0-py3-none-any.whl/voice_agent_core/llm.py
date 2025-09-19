# src/voice_agent_core/llm.py

import os
import inspect
import google.generativeai as genai
from dotenv import load_dotenv
import google.ai.generativelanguage as glm

def generate_gemini_tool_schema(func):
    """Generates a Gemini tool schema from a Python function's signature and docstring."""
    signature = inspect.signature(func)
    docstring = inspect.getdoc(func)
    description = docstring.split('\n\n')[0]
    properties = {}
    required = []
    for name, param in signature.parameters.items():
        param_type = "STRING"
        if param.annotation in (int, float): param_type = "NUMBER"
        elif param.annotation == bool: param_type = "BOOLEAN"
        param_description = ""
        if "Args:" in docstring:
            for line in docstring.split("Args:")[1].split('\n'):
                if line.strip().startswith(name):
                    param_description = line.split(':', 1)[1].strip()
                    break
        properties[name] = {"type": param_type, "description": param_description}
        if param.default is inspect.Parameter.empty:
            required.append(name)
    return {"name": func.__name__, "description": description, "parameters": {"type": "OBJECT", "properties": properties, "required": required}}

# --- FINAL, HIGHLY-INTELLIGENT SYSTEM PROMPT ---
SYSTEM_PROMPT = """
You are Saara, a friendly and intelligent voice assistant. Your goal is to be genuinely helpful and conversational.

Follow this decision-making hierarchy strictly:

1.  **GREETINGS & SMALL TALK:** If the user says "hi", "hello", "how are you", or makes a similar conversational gesture, respond naturally and do NOT use a tool. Your goal is to be a pleasant conversational partner.

2.  **CLARIFY AMBIGUOUS COMMANDS:** If a user's request seems like it needs a tool but is missing key information, your ABSOLUTE PRIORITY is to ask for clarification. Do NOT guess.
    - User: "Play some music." -> Your Response: "Of course, what song or artist would you like to hear?"
    - User: "Open a website." -> Your Response: "Certainly, what is the address of the website you'd like to open?"

3.  **EXECUTE CLEAR COMMANDS:** If the user's request is specific, clear, and has all the information needed for a tool, call that tool.
    - User: "What's the weather in Paris?" -> Tool Call: `get_weather(location='Paris')`
    - User: "Play lofi hip hop radio on youtube" -> Tool Call: `play_on_youtube(query='lofi hip hop radio')`

4.  **ANSWER GENERAL KNOWLEDGE QUESTIONS:** If the user asks a general question that doesn't fit a tool (e.g., "What is the capital of France?"), answer it directly using your own knowledge. Do not try to force it into a search tool unless necessary.
"""

def initialize_chat_session(available_tools: dict):
    """Initializes the Gemini model and a stateful chat session."""
    load_dotenv()
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    if not gemini_api_key:
        raise ValueError("GEMINI_API_KEY not found in environment variables or .env file")
        
    genai.configure(api_key=gemini_api_key)
    
    tools = [generate_gemini_tool_schema(func) for func in available_tools.values()]
    
    model = genai.GenerativeModel(
        model_name='gemini-1.5-pro-latest',
        generation_config={"temperature": 0.7},
        tools=tools,
        system_instruction=SYSTEM_PROMPT
    )
    
    chat = model.start_chat()
    return chat

def get_llm_response(chat_session, user_text: str):
    """Sends the user's raw text to the chat session and returns the model's response."""
    try:
        response = chat_session.send_message(user_text)
        part = response.candidates[0].content.parts[0]
        
        if hasattr(part, 'function_call'):
            return {"type": "function_call", "call": part.function_call}
        else:
            return {"type": "text_response", "content": response.text}

    except Exception as e:
        print(f"Error communicating with Gemini: {e}")
        return {"type": "text_response", "content": "I'm having a bit of trouble thinking right now."}

def send_tool_response_to_llm(chat_session, function_call, tool_result: str):
    """Sends the result of a tool execution back to the LLM for a final conversational response."""
    try:
        response = chat_session.send_message(
            glm.Part(function_response=glm.FunctionResponse(name=function_call.name, response={"result": tool_result})),
        )
        return {"type": "text_response", "content": response.text}
    except Exception as e:
        print(f"Error sending tool response to Gemini: {e}")
        return {"type": "text_response", "content": "There was an issue processing the tool's result."}