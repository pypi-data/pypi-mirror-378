# Import the Rust extension as the base
from .ovault import *

from ovault.ansi import *

def _backup_warning():
    print(
        f"{YELLOW}"
        "WARNING: OVault can modify many files in your Obsidian vault at once.\n"
        "\n"
        f"{BOLD}MAKE SURE YOU HAVE A BACKUP{RESET}{YELLOW} of your vault before using OVault, as changes made\n"
        "by OVault may be difficult or impossible to undo.\n"
        + RESET
    )

    answer = input(f"Are you {ITALIC+BOLD}sure{RESET} you want to continue? [y/N]\n> ").strip().lower()

    if answer != 'y':
        print("Aborting.")
        exit(1)

    print()
