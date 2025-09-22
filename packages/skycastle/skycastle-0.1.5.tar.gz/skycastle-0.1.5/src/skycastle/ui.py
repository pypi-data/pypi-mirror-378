# skycastle/ui.py

import sys
import textwrap
import shutil
from typing import Optional, List, Dict
from collections import defaultdict

from colorama import init, Fore, Style

# Import specific dataclasses from gamestate for type hinting
from skycastle.gamestate import Item, Exit # CORRECTED: Ensure these are correctly imported

# Initialize colorama for cross-platform colored terminal output
init(autoreset=True)

# --- Global flag for color output control ---
_ENABLE_COLOR: bool = True # Default to True for normal play
COLOR_ERROR = Fore.RED # Define a standard color for error messages
COLOR_WARNING = Fore.YELLOW # Define a standard color for warning messages

def set_color_enabled(enabled: bool) -> None:
    """Sets whether color output should be enabled."""
    global _ENABLE_COLOR
    _ENABLE_COLOR = enabled

# A fixed width for game content to ensure consistent wrapping across terminals
_GAME_CONTENT_WIDTH = 78
_INDENT_LEVEL = 2

def get_terminal_width(fallback: int = _GAME_CONTENT_WIDTH) -> int:
    """Returns the current terminal width, or a fallback if it cannot be determined."""
    return min(shutil.get_terminal_size(fallback=(fallback, 24)).columns, fallback)

def wrap_text(text: str, width: Optional[int] = None, indent: int = 0) -> str:
    """
    Wraps text to the specified width (or a default game content width if None).
    Applies an optional hanging indent for subsequent lines.
    """
    if width is None:
        width = get_terminal_width()

    effective_width = max(10, width - indent)

    paragraphs = text.split('\n')
    wrapped_lines = []
    for para in paragraphs:
        if para.strip():
            wrapped_lines.extend(textwrap.wrap(para, width=effective_width))
        else:
            wrapped_lines.append('') # Preserve empty lines

    return '\n'.join([(' ' * indent) + line for line in wrapped_lines])

def print_colored(text: str, color: str = Fore.CYAN, style: str = Style.NORMAL, wrap: bool = True, indent: int = 0) -> None:
    """Prints text with specified color and style, with optional word wrapping and indentation."""
    if wrap:
        final_text = wrap_text(text, indent=indent)
    else:
        final_text = '\n'.join([(' ' * indent) + line for line in text.split('\n')])

    if _ENABLE_COLOR:
        print(f"{color}{style}{final_text}{Style.RESET_ALL}")
    else:
        # In test mode, strip known colorama codes to ensure pure text output.
        stripped_text = final_text.replace(Style.RESET_ALL, "")
        for col in [Fore.BLACK, Fore.BLUE, Fore.CYAN, Fore.GREEN, Fore.LIGHTBLACK_EX,
                    Fore.LIGHTBLUE_EX, Fore.LIGHTCYAN_EX, Fore.LIGHTGREEN_EX,
                    Fore.LIGHTMAGENTA_EX, Fore.LIGHTRED_EX, Fore.LIGHTWHITE_EX,
                    Fore.LIGHTYELLOW_EX, Fore.MAGENTA, Fore.RED, Fore.WHITE, Fore.YELLOW]:
            stripped_text = stripped_text.replace(col, "")
        for sty in [Style.BRIGHT, Style.DIM, Style.NORMAL]:
             stripped_text = stripped_text.replace(sty, "")
        print(stripped_text) # Print plain text without color codes

def get_player_input(prompt: str = "> ") -> str:
    """
    Gets and normalizes player input.
    In test mode (_ENABLE_COLOR is False), it reads from the current stdin
    without printing a prompt and ignores lines starting with '#'.
    """
    if _ENABLE_COLOR:
        return input(f"{Fore.LIGHTGREEN_EX}{prompt}{Style.RESET_ALL}").strip().lower()
    else:
        # Test mode: read a line from stdin (which is redirected from a file)
        while True: # Loop until a non-comment, non-empty line or EOF
            line = sys.stdin.readline()
            if not line: # End of file
                return "quit" # Automatically quit if script runs out of commands
            
            # CORRECTED: Handle inline comments by stripping everything after the first '#'
            if '#' in line:
                line = line.split('#', 1)[0]
            
            stripped_line = line.strip()
            
            if stripped_line: # After stripping comments and whitespace, if anything remains, it's a command
                return stripped_line.lower()
            # Else, it became empty after stripping, so read the next line.

# --- Specific UI/Display Functions ---

def display_title_screen() -> None:
    title_width = get_terminal_width()
    print_colored("-" * title_width, Fore.LIGHTGREEN_EX, wrap=False)
    print_colored(f"{' ' * ((title_width - len('WELCOME TO SKY CASTLE')) // 2)}WELCOME TO SKY CASTLE", Fore.LIGHTGREEN_EX, Style.BRIGHT, wrap=False)
    print_colored(f"{' ' * ((title_width - len('A Text Adventure of Love and Dreams')) // 2)}A Text Adventure of Love and Dreams", Fore.LIGHTGREEN_EX, wrap=False)
    print_colored("-" * title_width + "\n", Fore.LIGHTGREEN_EX, wrap=False)

    print_colored(f"{' ' * _INDENT_LEVEL}1. New Game", Fore.YELLOW, wrap=False)
    print_colored(f"{' ' * _INDENT_LEVEL}2. Load Game", Fore.YELLOW, wrap=False)
    print_colored(f"{' ' * _INDENT_LEVEL}3. Delete Game", Fore.YELLOW, wrap=False)
    print_colored(f"{' ' * _INDENT_LEVEL}4. Quit", Fore.YELLOW, wrap=False)
    print("\n")

def display_intro_sequence() -> None:
    intro_text = (
        "The Sky Castle, a magnificent structure woven from memories and dreams, "
        "once sparkled like a jewel suspended amongst the clouds. You remember "
        "your father, a visionary architect, his eyes filled with the joy of creation, "
        "always humming and planning, building your shared 'castle in the sky.' "
        "His favorite song, 'Just the Two of Us,' was the very blueprint of his heart.\n\n"
        "But recently, the crystal raindrops have turned to tears, the rainbows faded. "
        "Your father embarked on a final, grand project within the castle's highest spires, "
        "and he has not returned. Days have blurred into nights, and a quiet, unsettling "
        "silence has settled over the once vibrant halls.\n\n"
        "Determined, you've snuck into the entrance — the Crystal Atrium. "
        "You carry with you the faint echo of his song and the unwavering belief that "
        "together, you can make it if you try. Your quest is clear: find your father, "
        "bring his dream back to life, and restore the sunshine to your Sky Castle.\n"
        "\"Good things might come to those who wait, but not for those who wait too late.\"\n"
        "You must go for all you know."
    )
    print_colored("\n--- The Calling of the Sky Castle ---", Fore.LIGHTBLUE_EX, Style.BRIGHT)
    print_colored(intro_text, Fore.LIGHTBLUE_EX, wrap=True, indent=_INDENT_LEVEL)
    _ = get_player_input("Press Enter to embark on your journey...") # Discard input
    print("\n")

def display_room_info(room_name: str, room_description: str, room_items: List[Item], room_exits: Dict[str, Exit]) -> None:
    print_colored(f"\n{room_name}", Fore.LIGHTGREEN_EX, Style.BRIGHT)
    print_colored("=" * len(room_name), Fore.LIGHTGREEN_EX, wrap=False)
    print_colored(room_description, indent=_INDENT_LEVEL)

    if room_items:
        item_counts = defaultdict(int)
        for item in room_items:
            item_counts[item.name] += 1
        item_list = [
            f"{name} ({count})" if count > 1 else name
            for name, count in item_counts.items()
        ]
        print_colored(f"\nYou see: {', '.join(item_list)}", Fore.MAGENTA, indent=_INDENT_LEVEL)

    available_exit_directions = []
    for direction, ex in room_exits.items():
        if not ex.is_locked:
            available_exit_directions.append(direction.capitalize())
    if available_exit_directions:
        print_colored(f"Exits: {', '.join(available_exit_directions)}", Fore.MAGENTA, indent=_INDENT_LEVEL)
    else:
        print_colored("You see no obvious exits from here.", Fore.LIGHTRED_EX, indent=_INDENT_LEVEL)

def display_item_description(item_name: str, item_description: str) -> None:
    print_colored(f"\n{item_name.capitalize()}: {item_description}", Fore.MAGENTA, indent=_INDENT_LEVEL)

def display_inventory(inventory_items: List[Item]) -> None:
    if inventory_items:
        print_colored("\n--- Your Inventory ---", Fore.LIGHTGREEN_EX)
        item_counts = defaultdict(int)
        for item in inventory_items:
            item_counts[item.name] += 1
        for name, count in item_counts.items():
            print_colored(f"- {name.capitalize()} ({count})" if count > 1 else f"- {name.capitalize()}", Fore.MAGENTA, indent=_INDENT_LEVEL)
        print_colored("----------------------", Fore.LIGHTGREEN_EX)
    else:
        print_colored("Your inventory is empty.", Fore.MAGENTA)

def display_help_commands() -> None:
    print_colored("\n--- Available Commands ---", Fore.LIGHTGREEN_EX)
    print_colored("  go [direction]    - Move in a direction (e.g., 'go north', 'go east')", Fore.MAGENTA, indent=_INDENT_LEVEL)
    print_colored("  look              - Look around the current room again", Fore.MAGENTA, indent=_INDENT_LEVEL)
    print_colored("  look [item name]  - Inspect an item in the room or your inventory", Fore.MAGENTA, indent=_INDENT_LEVEL)
    print_colored("  take [item name]  - Pick up an item from the room", Fore.MAGENTA, indent=_INDENT_LEVEL)
    print_colored("  drop [item name]  - Place an item from your inventory into the room", Fore.MAGENTA, indent=_INDENT_LEVEL)
    print_colored("  inventory / i     - View items you are carrying", Fore.MAGENTA, indent=_INDENT_LEVEL)
    print_colored("  save              - Save your current game progress", Fore.MAGENTA, indent=_INDENT_LEVEL)
    print_colored("  quit              - Exit the game (will prompt to save if needed)", Fore.MAGENTA, indent=_INDENT_LEVEL)
    print_colored("  help              - Display this list of commands", Fore.MAGENTA, indent=_INDENT_LEVEL)
    print_colored("------------------------", Fore.LIGHTGREEN_EX)

def display_win_screen() -> None:
    win_message = (
        "\n"
        "=================================================================\n"
        "                  CONGRATULATIONS! YOU DID IT!\n"
        "=================================================================\n"
        "After a long and winding journey through the Sky Castle, you finally\n"
        "reach the pinnacle. There, amidst scattered blueprints and tools,\n"
        "you find your father! His face, initially etched with concentration,\n"
        "breaks into a joyous smile as he sees you. The final piece of your\n"
        "'Castle in the Sky' is complete, built not just from dreams, but from\n"
        "your enduring bond. Together, you look out at the magnificent view,\n"
        "just the two of you, having truly made it, trying.\n"
        "\n"
        "=================================================================\n"
    )
    print_colored(win_message, Fore.LIGHTYELLOW_EX, Style.BRIGHT, wrap=True, indent=_INDENT_LEVEL)
    _ = get_player_input("Press Enter to continue to the credits...")

def display_credits() -> None:
    credits_text = (
        "\n"
        "=================================================================\n"
        "--------------------------  CREDITS  ---------------------------\n"
        "=================================================================\n"
        "\n"
        "                  Game Design & Development:\n"
        "                         Papai\n"
        "\n"
        "=================================================================\n"
        "\n"
        "              Thank you for playing Sky Castle!\n"
    )
    print_colored(credits_text, Fore.LIGHTWHITE_EX, Style.BRIGHT, wrap=True, indent=_INDENT_LEVEL)
    _ = get_player_input("Press Enter to return to the main menu...")
