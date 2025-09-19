# src/voice_agent_core/main.py

from .listening import listen_for_wake_word, listen_for_command
from .speaking import speak  # Correctly imports from your new, robust speaking.py
from .llm import initialize_chat_session, get_llm_response, send_tool_response_to_llm
from . import actions as toolbox

def run_agent(available_tools: dict):
    """
    Main loop for the voice agent, featuring a stateful chat session, robust
    error handling, and dynamic tool use.
    """
    print("Initializing LLM with tools...")
    chat_session = initialize_chat_session(available_tools)
    
    speak("Initialization complete. I am now passively listening for the wake word.")
    
    while True:
        if listen_for_wake_word():
            speak("Yes?")
            command = listen_for_command()
            
            if command:
                if "goodbye" in command or "exit" in command:
                    speak("Goodbye! Have a great day.")
                    break

                # Get the initial decision (text or function call) from the LLM
                llm_decision = get_llm_response(chat_session, command)

                if llm_decision['type'] == 'function_call':
                    function_call = llm_decision['call']
                    tool_name = function_call.name
                    
                    # Safely handle function calls that have no arguments to prevent crashes
                    tool_args = {}
                    if function_call.args:  # Check if args is not None or empty
                        tool_args = {key: value for key, value in function_call.args.items()}
                    
                    if tool_name in available_tools:
                        function_to_call = available_tools[tool_name]
                        try:
                            # 1. Execute the identified tool with its arguments
                            result = function_to_call(**tool_args)
                            print(f"Tool '{tool_name}' executed. Result: {result}")
                            
                            # 2. Send the result back to the LLM for a final, natural response
                            final_response = send_tool_response_to_llm(chat_session, function_call, result)
                            speak(final_response['content'])
                            
                        except TypeError as e:
                            # Gracefully handle incomplete commands that are missing required arguments
                            print(f"Tool TypeError: {e}")
                            speak(f"To use the {tool_name} tool, I need more information. Please try again.")
                        except Exception as e:
                            speak(f"An error occurred while using the {tool_name} tool.")
                            print(f"Tool execution error: {e}")
                    else:
                        speak(f"I'm sorry, I don't know how to use a tool called '{tool_name}'.")

                elif llm_decision['type'] == 'text_response':
                    # If it's a direct conversational answer, just speak it
                    speak(llm_decision['content'])
            else:
                speak("I heard my name, but didn't catch a command.")

def start_default_agent():
    """Defines the complete set of default tools and runs the agent."""
    
    default_tools = {
        # Media & System Controls
        "play_on_youtube": toolbox.play_on_youtube,
        "pause_or_resume": toolbox.pause_or_resume,
        "stop_current_task": toolbox.stop_current_task,
        "open_vscode": toolbox.open_vscode,
        
        # Web & Information Tools
        "open_website": toolbox.open_website,
        "search_google": toolbox.search_google,
        "get_weather": toolbox.get_weather,
    }
    
    run_agent(available_tools=default_tools)