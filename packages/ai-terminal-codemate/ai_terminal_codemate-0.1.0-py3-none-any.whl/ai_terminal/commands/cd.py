import os
from typing import List, Tuple
from .base import BaseCommand

class CdCommand(BaseCommand):
    name = "cd"
    aliases = []

    def run(self, args: List[str], current_directory: str) -> Tuple[str, int]:
        target = args[0] if args else os.path.expanduser("~")
        if not os.path.isabs(target):
            target = os.path.join(current_directory, target)
        target = os.path.abspath(target)
        if os.path.isdir(target):
            return f"{target}", 0
        return f"Error: Directory '{target}' not found", 1
