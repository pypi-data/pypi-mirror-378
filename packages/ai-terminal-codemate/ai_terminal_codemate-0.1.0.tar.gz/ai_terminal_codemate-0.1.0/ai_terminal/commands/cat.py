import os
from typing import List, Tuple
from .base import BaseCommand

class CatCommand(BaseCommand):
    name = "cat"
    aliases = []

    def run(self, args: List[str], current_directory: str) -> Tuple[str, int]:
        if not args:
            return "Error: cat requires a file name", 1
        file_name = args[0]
        if not os.path.isabs(file_name):
            file_name = os.path.join(current_directory, file_name)
        if os.path.isfile(file_name):
            try:
                with open(file_name, 'r', encoding='utf-8') as f:
                    return f.read(), 0
            except Exception as e:
                return f"Error: {str(e)}", 1
        return f"Error: File '{file_name}' not found", 1
