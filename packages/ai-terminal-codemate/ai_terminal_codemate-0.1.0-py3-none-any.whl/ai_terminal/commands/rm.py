import os
from typing import List, Tuple
from .base import BaseCommand

class RmCommand(BaseCommand):
    name = "rm"
    aliases = []

    def run(self, args: List[str], current_directory: str) -> Tuple[str, int]:
        if not args:
            return "Error: rm requires a file name", 1
        try:
            for file_name in args:
                if not os.path.isabs(file_name):
                    file_name = os.path.join(current_directory, file_name)
                if os.path.exists(file_name) and os.path.isfile(file_name):
                    os.remove(file_name)
                else:
                    return f"Error: File '{file_name}' not found or not a file", 1
            return f"Removed file(s): {', '.join(args)}", 0
        except Exception as e:
            return f"Error: {str(e)}", 1
