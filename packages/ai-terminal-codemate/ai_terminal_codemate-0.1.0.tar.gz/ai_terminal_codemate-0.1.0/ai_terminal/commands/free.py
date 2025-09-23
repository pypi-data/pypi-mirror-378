# commands/free.py
import psutil
from typing import List, Tuple
from .base import BaseCommand

class FreeCommand(BaseCommand):
    name = "free"
    aliases = []

    def run(self, args: List[str], current_directory: str) -> Tuple[str, int]:
        try:
            memory = psutil.virtual_memory()
            swap = psutil.swap_memory()
            result = f"""Memory Usage:
Total    Used    Free    Available
Mem:      {memory.total // (1024**2):>8}MB {memory.used // (1024**2):>8}MB {memory.free // (1024**2):>8}MB {memory.available // (1024**2):>8}MB
Swap:     {swap.total // (1024**2):>8}MB {swap.used // (1024**2):>8}MB {swap.free // (1024**2):>8}MB"""
            return result, 0
        except Exception as e:
            return f"Error: {e}", 1
