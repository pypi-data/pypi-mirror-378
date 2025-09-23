# commands/df.py
import psutil
from typing import List, Tuple
from .base import BaseCommand

class DfCommand(BaseCommand):
    name = "df"
    aliases = []

    def run(self, args: List[str], current_directory: str) -> Tuple[str, int]:
        try:
            partitions = psutil.disk_partitions()
            result = ["Filesystem\tSize\tUsed\tAvail\tUse%\tMounted on"]
            result.append("-" * 70)
            for partition in partitions:
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    total_gb = usage.total // (1024**3)
                    used_gb = usage.used // (1024**3)
                    free_gb = usage.free // (1024**3)
                    percent = (usage.used / usage.total) * 100
                    result.append(f"{partition.device[:15]:<15}\t{total_gb}GB\t{used_gb}GB\t{free_gb}GB\t{percent:.1f}%\t{partition.mountpoint}")
                except PermissionError:
                    continue
            return "\n".join(result), 0
        except Exception as e:
            return f"Error: {e}", 1
