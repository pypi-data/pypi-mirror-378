import os
from typing import List, Tuple
from .base import BaseCommand

class MkdirCommand(BaseCommand):
    name = "mkdir"
    aliases = []

    def run(self, args: List[str], current_directory: str) -> Tuple[str, int]:
        if not args:
            return "Error: mkdir requires a directory name", 1
        try:
            for dir_name in args:
                if not os.path.isabs(dir_name):
                    dir_name = os.path.join(current_directory, dir_name)
                os.makedirs(dir_name, exist_ok=True)
            return f"Created directory(ies): {', '.join(args)}", 0
        except Exception as e:
            return f"Error: {str(e)}", 1
