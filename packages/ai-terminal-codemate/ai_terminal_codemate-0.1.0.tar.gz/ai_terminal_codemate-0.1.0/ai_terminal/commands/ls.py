import os
from typing import List, Tuple
from .base import BaseCommand

class LsCommand(BaseCommand):
    name = "ls"
    aliases = ["dir"]

    def run(self, args: List[str], current_directory: str) -> Tuple[str, int]:
        path = args[0] if args else current_directory
        if not os.path.isabs(path):
            path = os.path.join(current_directory, path)
        if not os.path.exists(path):
            return f"Error: Path '{path}' not found", 1
        if os.path.isfile(path):
            return os.path.basename(path), 0
        try:
            items = []
            for item in sorted(os.listdir(path)):
                item_path = os.path.join(path, item)
                if os.path.isdir(item_path):
                    items.append(f"{item}/")
                else:
                    items.append(item)
            return "\n".join(items) if items else "Directory is empty", 0
        except Exception as e:
            return f"Error: {str(e)}", 1
