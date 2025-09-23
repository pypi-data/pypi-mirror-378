# command_registry.py
from ai_terminal.commands.base import BaseCommand

# Import all command modules
from ai_terminal.commands import touch, mkdir, ls, cat, cp, mv, top  # Add more as needed

COMMANDS = {}

# Dynamically register commands
for cmd_module in [touch, mkdir, ls, cat, cp, mv, top]:
    # Find class ending with Command
    cls_name = [c for c in dir(cmd_module) if c.endswith("Command")][0]
    cls = getattr(cmd_module, cls_name)
    COMMANDS[cls.name] = cls()
