import os, pkgutil, importlib
from typing import Dict, Tuple
from ai_terminal.commands.base import BaseCommand

class CommandProcessor:
    def __init__(self):
        self.current_directory = os.getcwd()
        self.command_history = []
        self.commands: Dict[str, BaseCommand] = {}
        self._load_commands()

    def _load_commands(self):
        import ai_terminal.commands
        for _, module_name, _ in pkgutil.iter_modules(ai_terminal.commands.__path__):
            if module_name == "base":
                continue
            module = importlib.import_module(f"ai_terminal.commands.{module_name}")
            for attr in dir(module):
                obj = getattr(module, attr)
                if isinstance(obj, type) and issubclass(obj, BaseCommand) and obj is not BaseCommand:
                    cmd = obj()
                    self.commands[cmd.name] = cmd
                    for alias in cmd.aliases:
                        self.commands[alias] = cmd

    def execute_command(self, command_line: str) -> Tuple[str, int]:
        if not command_line.strip():
            return "", 0
        self.command_history.append(command_line)
        parts = command_line.split()
        cmd_name = parts[0]
        args = parts[1:]
        cmd = self.commands.get(cmd_name)
        if cmd:
            return cmd.run(args, self.current_directory)
        return f"Error: Unknown command '{cmd_name}'", 1
