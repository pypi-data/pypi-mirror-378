# src/voice_agent_core/llm.py

import os
import inspect
import google.generativeai as genai
from dotenv import load_dotenv
import google.ai.generativelanguage as glm

# --- Helper Function to Auto-Generate Tool Schemas ---
def generate_gemini_tool_schema(func):
    """
    Generates a Gemini tool schema from a Python function's signature and docstring.
    """
    signature = inspect.signature(func)
    docstring = inspect.getdoc(func)
    
    # Parse the main description from the docstring
    description = docstring.split('\n\n')[0]
    
    properties = {}
    required = []
    
    for name, param in signature.parameters.items():
        # Map Python types to Gemini's schema types
        param_type = "STRING" # Default to string
        if param.annotation == int:
            param_type = "NUMBER"
        elif param.annotation == float:
            param_type = "NUMBER"
        elif param.annotation == bool:
            param_type = "BOOLEAN"
            
        # Parse parameter description from the docstring's "Args:" section
        param_description = ""
        if "Args:" in docstring:
            for line in docstring.split("Args:")[1].split('\n'):
                if line.strip().startswith(name):
                    param_description = line.split(':', 1)[1].strip()
                    break

        properties[name] = {"type": param_type, "description": param_description}
        
        # Assume all parameters are required if they don't have a default value
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


# --- Main LLM Functions ---

SYSTEM_PROMPT = """
You are Saara, a friendly and helpful voice assistant. Your primary goal is to assist the user with their requests.
- Be conversational and concise in your responses.
- If the user asks you to perform an action, use the available tools.
- If the user's request is ambiguous, ask for clarification.
- If the request is a general question or conversation, provide a direct, helpful text response without using a tool.
"""

def initialize_chat_session(available_tools: dict):
    """
    Initializes the Gemini model and a stateful chat session with dynamically generated tools.

    Args:
        available_tools (dict): A dictionary mapping tool names to their functions.
    
    Returns:
        A Gemini chat session object.
    """
    load_dotenv()
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    if not gemini_api_key:
        raise ValueError("GEMINI_API_KEY not found in environment variables or .env file")
        
    genai.configure(api_key=gemini_api_key)
    
    # Dynamically generate tool schemas from the provided functions
    tools = [generate_gemini_tool_schema(func) for func in available_tools.values()]
    
    model = genai.GenerativeModel(
        model_name='gemini-1.5-flash', # Correct model name
        generation_config={"temperature": 0.7},
        tools=tools,
        system_instruction=SYSTEM_PROMPT
    )
    
    # Start a stateful chat session
    chat = model.start_chat()
    return chat

def get_llm_response(chat_session, user_text: str):
    """
    Sends the user's text to the stateful chat session and returns the model's response.
    This response could be a function call or a text reply.
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