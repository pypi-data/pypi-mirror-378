# src/voice_agent_core/llm.py

import os
import inspect
import google.generativeai as genai
from dotenv import load_dotenv
import google.ai.generativelanguage as glm

def generate_gemini_tool_schema(func):
    """
    Generates a Gemini tool schema from a Python function's signature and docstring.
    """
    signature = inspect.signature(func)
    docstring = inspect.getdoc(func)
    
    description = docstring.split('\n\n')[0]
    
    properties = {}
    required = []
    
    for name, param in signature.parameters.items():
        param_type = "STRING"
        if param.annotation == int or param.annotation == float:
            param_type = "NUMBER"
        elif param.annotation == bool:
            param_type = "BOOLEAN"
            
        param_description = ""
        if "Args:" in docstring:
            for line in docstring.split("Args:")[1].split('\n'):
                if line.strip().startswith(name):
                    param_description = line.split(':', 1)[1].strip()
                    break

        properties[name] = {"type": param_type, "description": param_description}
        
        if param.default is inspect.Parameter.empty:
            required.append(name)
            
    return {
        "name": func.__name__,
        "description": description,
        "parameters": {
            "type": "OBJECT",
            "properties": properties,
            "required": required
        }
    }

# --- NEW, MORE INTELLIGENT SYSTEM PROMPT ---
SYSTEM_PROMPT = """
You are Saara, a highly intelligent, friendly, and conversational voice assistant. Your primary goal is to understand the user's intent and assist them effectively.

Your core principles are:
1.  **Be Conversational:** Do not just be a command executor. If the user says "hello" or asks how you are, respond naturally. Maintain a friendly and helpful tone.
2.  **Clarify Ambiguity:** This is your most important rule. If a user's request is vague or missing information needed for a tool, YOU MUST ask for clarification. Do not guess.
    - User: "Play some music." -> You: "Of course, what kind of music would you like to hear?"
    - User: "Open the website." -> You: "Certainly, which website should I open for you?"
3.  **Reason About Tools:** Analyze the user's request to determine the most appropriate tool. Do not just match keywords. Understand the semantic meaning. If a user says "I want to listen to some hindi songs," you should know to use the `play_on_youtube` tool with the query "hindi songs".
4.  **Execute or Converse:** If the request clearly maps to a tool and has all the necessary information, call the tool. If the request is conversational or you need more information, respond with text.
5.  **Be Concise:** Keep your spoken responses clear and to the point.
"""

def initialize_chat_session(available_tools: dict):
    """
    Initializes the Gemini model and a stateful chat session with dynamically generated tools.
    """
    load_dotenv()
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    if not gemini_api_key:
        raise ValueError("GEMINI_API_KEY not found in environment variables or .env file")
        
    genai.configure(api_key=gemini_api_key)
    
    tools = [generate_gemini_tool_schema(func) for func in available_tools.values()]
    
    # --- MODEL UPGRADE ---
    model = genai.GenerativeModel(
        model_name='gemini-1.5-pro-latest', # <-- UPGRADED MODEL
        generation_config={"temperature": 0.7},
        tools=tools,
        system_instruction=SYSTEM_PROMPT
    )
    
    chat = model.start_chat()
    return chat

def get_llm_response(chat_session, user_text: str):
    """
    Sends the user's text to the stateful chat session and returns the model's response.
    """
    try:
        response = chat_session.send_message(user_text)
        part = response.candidates[0].content.parts[0]
        
        if hasattr(part, 'function_call'):
            return {
                "type": "function_call",
                "call": part.function_call
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

def send_tool_response_to_llm(chat_session, function_call, tool_result: str):
    """
    Sends the result of a tool execution back to the LLM and gets the final conversational response.
    """
    try:
        response = chat_session.send_message(
            glm.Part(
                function_response=glm.FunctionResponse(
                    name=function_call.name,
                    response={"result": tool_result},
                )
            ),
        )
        return {
            "type": "text_response",
            "content": response.text
        }
    except Exception as e:
        print(f"Error sending tool response to Gemini: {e}")
        return {
            "type": "text_response",
            "content": "There was an issue processing the tool's result."
        }