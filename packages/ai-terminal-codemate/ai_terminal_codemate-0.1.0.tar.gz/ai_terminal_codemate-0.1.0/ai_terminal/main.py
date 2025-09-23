# main.py
from ai_terminal.command_processor import CommandProcessor
from ai_terminal.ai_command_processor import AICommandProcessor
from ai_terminal.command_registry import COMMANDS

def run():
    executor = CommandProcessor()
    ai = AICommandProcessor()

    print("AI-Powered Terminal")
    print("Type 'exit' to quit")
    print("-" * 50)

    while True:
        try:
            prompt = f"{executor.current_directory}$ "
            query = input(prompt)

            if query.strip().lower() == "exit":
                print("Goodbye!")
                break

            # Check if natural language
            if ai.is_natural_language(query):
                suggestions = ai.process_natural_language(query)
                command_string = suggestions[0].command if suggestions else query
                print(f"AI Suggestion → {command_string}")
            else:
                command_string = query

            # Split command and arguments
            parts = command_string.strip().split()
            if not parts:
                continue

            cmd_name, *args = parts

            # Check registry first
            if cmd_name in COMMANDS:
                output, code = COMMANDS[cmd_name].run(args, executor.current_directory)
            else:
                # Fallback to normal executor
                output, code = executor.execute_command(command_string)

            if output:
                print(output)

        except KeyboardInterrupt:
            print("\nUse 'exit' to quit")
        except EOFError:
            break

# Allow running directly as a script
if __name__ == "__main__":
    run()
