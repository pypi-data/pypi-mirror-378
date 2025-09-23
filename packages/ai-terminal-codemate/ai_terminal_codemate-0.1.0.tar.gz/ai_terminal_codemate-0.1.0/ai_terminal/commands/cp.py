import os, shutil
from typing import List, Tuple
from .base import BaseCommand

class CpCommand(BaseCommand):
    name = "cp"
    aliases = []

    def run(self, args: List[str], current_directory: str) -> Tuple[str, int]:
        if len(args) < 2:
            return "Error: cp requires source and destination", 1
        source, dest = args[0], args[1]
        if not os.path.isabs(source):
            source = os.path.join(current_directory, source)
        if not os.path.isabs(dest):
            dest = os.path.join(current_directory, dest)
        if os.path.isfile(source):
            try:
                shutil.copy2(source, dest)
                return f"Copied '{args[0]}' to '{args[1]}'", 0
            except Exception as e:
                return f"Error: {str(e)}", 1
        return f"Error: Source '{source}' not found or not a file", 1
