from typing import List, Tuple
import psutil
import os

from .base import BaseCommand

class TopCommand(BaseCommand):
    name = "top"
    aliases = []

    def run(self, args: List[str], current_directory: str) -> Tuple[str, int]:
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')

            # Optional: load average on Unix
            load_avg = os.getloadavg() if hasattr(os, 'getloadavg') else (0, 0, 0)

            info = (
                f"System Resources:\n"
                f"CPU Usage: {cpu_percent}%\n"
                f"Memory: {memory.percent}% ({memory.used // (1024**2)}MB / {memory.total // (1024**2)}MB)\n"
                f"Disk: {disk.percent}% ({disk.used // (1024**3)}GB / {disk.total // (1024**3)}GB)\n"
                f"Load Average: {load_avg}"
            )
            return info, 0
        except Exception as e:
            return f"Error: {e}", 1
