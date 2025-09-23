import os
from typing import List, Tuple
from .base import BaseCommand
class echo(BaseCommand):
    name = "echo"
    aliases = []

    def run(self, args: List[str], current_directory: str) -> Tuple[str, int]:
        """
        Handle echo command.
        - echo "text" prints text
        - echo "" > filename creates an empty file
        """
        if not args:
            return "Error: echo requires arguments", 1

        # Handle file creation: if first arg is empty string and '>' exists
        if len(args) >= 3 and args[0] == '""' and args[1] == '>':
            filename = args[2]
            if not os.path.isabs(filename):
                filename = os.path.join(current_directory, filename)
            try:
                with open(filename, 'w', encoding='utf-8'):
                    pass
                return f"Created file: {args[2]}", 0
            except Exception as e:
                return f"Error creating file: {e}", 1

        # Otherwise, normal echo
        return " ".join(args), 0
