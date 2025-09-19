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






# src/voice_agent_core/main.py

# Use relative imports because these modules are now in the same package
from .listening import listen_for_wake_word, listen_for_command
from .speaking import speak
from .llm import initialize_llm, get_llm_response
from . import actions as toolbox

# --- This is the reusable library function ---
def run_agent(available_tools: dict):
    """
    Main loop for the voice agent, designed to be used as a library function.
    
    Args:
        available_tools (dict): A dictionary mapping tool names to their functions.
    """
    print("Initializing LLM with tools...")
    model = initialize_llm()
    
    speak("Initialization complete. I am now passively listening for the wake word.")
    
    while True:
        if listen_for_wake_word():
            speak("Yes?")
            command = listen_for_command()
            
            if command:
                if "goodbye" in command or "exit" in command:
                    speak("Goodbye! Have a great day.")
                    break

                llm_decision = get_llm_response(model, command)

                if llm_decision['type'] == 'function_call':
                    tool_name = llm_decision['name']
                    tool_args = llm_decision['args']
                    
                    if tool_name in available_tools:
                        function_to_call = available_tools[tool_name]
                        try:
                            result = function_to_call(**tool_args)
                            speak(result)
                        except TypeError:
                            speak(f"To use the '{tool_name}' tool, I need more information.")
                        except Exception as e:
                            speak(f"An error occurred while using the {tool_name} tool.")
                            print(f"Tool execution error: {e}")
                    else:
                        speak(f"I'm sorry, I don't know how to use a tool called '{tool_name}'.")

                elif llm_decision['type'] == 'text_response':
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