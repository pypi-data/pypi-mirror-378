from typing import List, Tuple

class BaseCommand:
    name: str = ""
    aliases: list[str] = []

    def run(self, args: List[str], current_directory: str) -> Tuple[str, int]:
        """Run the command. Returns (output, exit_code)."""
        raise NotImplementedError("Each command must implement run()")
