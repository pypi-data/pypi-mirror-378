# from src.listening import listen_for_wake_word, listen_for_command
# from src.speaking import speak
# from src.llm import initialize_llm, get_llm_response
# import src.actions as toolbox

# def run_agent():
#     """Main loop for the wake-word driven voice agent."""
    
#     print("Initializing LLM with tools...")
#     model = initialize_llm()
    
#     available_tools = {
#         "play_on_youtube": toolbox.play_on_youtube,
#         "open_website": toolbox.open_website,
#         "search_google": toolbox.search_google,
#         "open_vscode": toolbox.open_vscode,
#         "pause_or_resume": toolbox.pause_or_resume,
#         "stop_current_task": toolbox.stop_current_task,
#     }
    
#     speak("Initialization complete. I am now passively listening for the wake word.")
    
#     while True:
#         # 1. Passively listen for the wake word
#         if listen_for_wake_word():
            
#             # 2. Acknowledge and actively listen for a command
#             speak("Yes?")
#             command = listen_for_command()
            
#             if command:
#                 if "goodbye" in command or "exit" in command:
#                     speak("Goodbye! Have a great day.")
#                     break

#                 # 3. Process the command with the LLM
#                 llm_decision = get_llm_response(model, command)

#                 if llm_decision['type'] == 'function_call':
#                     tool_name = llm_decision['name']
#                     tool_args = llm_decision['args']
                    
#                     if tool_name in available_tools:
#                         function_to_call = available_tools[tool_name]
                        
#                         try:
#                             result = function_to_call(**tool_args)
#                             speak(result)
#                         except TypeError:
#                             speak(f"To use the '{tool_name}' tool, I need more information. What should I search for?")
#                         except Exception as e:
#                             speak(f"An error occurred while using the {tool_name} tool.")
#                             print(f"Tool execution error: {e}")
#                     else:
#                         speak(f"I'm sorry, I don't know how to use a tool called '{tool_name}'.")

#                 elif llm_decision['type'] == 'text_response':
#                     speak(llm_decision['content'])
#             else:
#                 speak("I heard my name, but didn't catch a command.")

# if __name__ == '__main__':
#     run_agent()






# src/voice_agent_core/main.py (Only the run_agent function needs changing)

from .listening import listen_for_wake_word, listen_for_command
from .speaking import speak
# Updated import to get the new functions
from .llm import initialize_chat_session, get_llm_response, send_tool_response_to_llm
from . import actions as toolbox

def run_agent(available_tools: dict):
    """
    Main loop for the voice agent, now with a stateful chat session.
    
    Args:
        available_tools (dict): A dictionary mapping tool names to their functions.
    """
    print("Initializing LLM with tools...")
    # Initialize a stateful chat session instead of just the model
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

                # 1. Get the initial decision from the LLM
                llm_decision = get_llm_response(chat_session, command)

                if llm_decision['type'] == 'function_call':
                    function_call = llm_decision['call']
                    tool_name = function_call.name
                    tool_args = {key: value for key, value in function_call.args.items()}
                    
                    if tool_name in available_tools:
                        function_to_call = available_tools[tool_name]
                        
                        try:
                            # 2. Execute the function and get the result
                            result = function_to_call(**tool_args)
                            print(f"Tool '{tool_name}' executed. Result: {result}")
                            
                            # 3. Send the result back to the LLM for a final response
                            final_response = send_tool_response_to_llm(chat_session, function_call, result)
                            speak(final_response['content'])
                            
                        except Exception as e:
                            speak(f"An error occurred while using the {tool_name} tool.")
                            print(f"Tool execution error: {e}")
                    else:
                        speak(f"I'm sorry, I don't know how to use a tool called '{tool_name}'.")

                elif llm_decision['type'] == 'text_response':
                    # If it's a direct answer, just speak it
                    speak(llm_decision['content'])
            else:
                speak("I heard my name, but didn't catch a command.")


# --- This function will be our command-line entry point ---
def start_default_agent():
    """Defines the default tools and runs the agent."""
    
    # The default set of tools that come with the package
    default_tools = {
        "play_on_youtube": toolbox.play_on_youtube,
        "open_website": toolbox.open_website,
        "search_google": toolbox.search_google,
        "open_vscode": toolbox.open_vscode,
        "pause_or_resume": toolbox.pause_or_resume,
        "stop_current_task": toolbox.stop_current_task,
    }
    
    # Run the agent with the default tools
    run_agent(available_tools=default_tools)

if __name__ == '__main__':
    start_default_agent()