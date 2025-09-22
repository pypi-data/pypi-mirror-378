# skycastle/game_commands/main_handler.py

from typing import List, Tuple, Optional, Dict

# Relative imports for GameState
from skycastle.gamestate import GameState, Item # Item added for type hinting in _get_item_by_name_fuzzy
# Relative import for UI functions
from skycastle import ui

# Import specific command handlers from submodules
from skycastle.game_commands import navigation
from skycastle.game_commands import interaction
from skycastle.game_commands import puzzles
from skycastle.game_commands import system


# --- Command Mapping for Synonyms and Aliases ---
_COMMAND_ALIASES = {
    # Navigation
    'n': 'go north', 's': 'go south', 'e': 'go east', 'w': 'go west',
    'u': 'go up', 'd': 'go down',
    'north': 'go north', 'south': 'go south', 'east': 'go east',
    'west': 'go west', 'up': 'go up', 'down': 'go down',
    'move north': 'go north', 'walk north': 'go north', 'travel north': 'go north',
    # Interaction
    'get': 'take', 'pick up': 'take', 'grab': 'take',
    'put down': 'drop',
    'examine': 'look', 'inspect': 'look',
    'inv': 'inventory', 'i': 'inventory',
    # Puzzles - These are typically direct verbs, no aliases needed for the verb itself,
    # but the parser must recognize them as valid starting points for puzzle actions.
    'read': 'read', 'activate': 'activate', 'use': 'use', # Explicitly list them for clarity
    # System
    'savegame': 'save', 'quitgame': 'quit', '?': 'help'
}

_IGNORABLE_WORDS = ['the', 'a', 'an', 'on', 'with', 'in', 'at', 'to', 'from']


def _normalize_command_parts(raw_input: str) -> List[str]:
    """
    Normalizes the raw player input by applying aliases and splitting into parts.
    Filters out ignorable words.
    """
    normalized_input = raw_input.lower().strip()

    # Step 1: Check for exact alias matches (single word or multi-word)
    if normalized_input in _COMMAND_ALIASES:
        normalized_input = _COMMAND_ALIASES[normalized_input]
    else:
        # Step 2: Check for multi-word aliases at the beginning of the input
        # This handles cases like "move north key" where "move north" is an alias for "go north"
        longest_alias_match = None
        for alias in sorted(_COMMAND_ALIASES.keys(), key=len, reverse=True): # Check longer aliases first
            if normalized_input.startswith(f"{alias} "):
                longest_alias_match = alias
                break
        
        if longest_alias_match:
            replacement = _COMMAND_ALIASES[longest_alias_match]
            normalized_input = f"{replacement} {normalized_input[len(longest_alias_match)+1:]}"


    # Step 3: Split into words and filter out ignorable words
    # This list of `_IGNORABLE_WORDS` only explicitly contains single words. If a multi-word alias
    # leads to a replacement that has 'on', 'the', etc., those will be handled in this step.
    parts = [word for word in normalized_input.split() if word not in _IGNORABLE_WORDS]
    
    # Special handling for single words that are alias parts but also potential commands
    # e.g., 'read' is a valid command itself
    if not parts and normalized_input not in _IGNORABLE_WORDS:
        # If after filtering, parts become empty but raw_input was meaningful (not just ignorable words),
        # then the raw_input itself might be the command.
        # This can happen if, for example, 'read' is an alias for 'read', and 'the' is an ignorable word.
        # Input 'read the' -> normalized 'read '. Split and filter -> []. This is a tricky edge case.
        # For now, we trust the `_COMMAND_ALIASES` to ensure commands are correctly formed.
        pass # The parsing logic above should generally handle this for known commands

    return parts


def handle_command(raw_input: str, game_state: GameState, save_game_func, list_saves_func) -> None:
    """
    Main command handler that normalizes player input and dispatches to the appropriate submodule.

    Args:
        raw_input: The raw string input from the player.
        game_state: The current GameState object.
        save_game_func: A callable function (from save_manager) to save the game.
        list_saves_func: A callable function (from save_manager) to get a list of save metadata.
    """
    command_parts = _normalize_command_parts(raw_input)

    if not command_parts:
        ui.print_colored("I didn't understand that. Try 'help'.", ui.COLOR_ERROR)
        return

    cmd = command_parts[0] # The primary verb/command after normalization
    
    # Puzzle commands (use, read, activate)
    if cmd in ['use', 'read', 'activate']:
        puzzles.handle_puzzle_command(command_parts, game_state)
    
    # Navigation commands
    elif cmd == 'go':
        navigation.handle_go_command(command_parts, game_state)

    # Interaction commands
    elif cmd == 'look':
        interaction.handle_look_command(command_parts, game_state)
    elif cmd == 'take':
        interaction.handle_take_command(command_parts, game_state)
    elif cmd == 'drop':
        interaction.handle_drop_command(command_parts, game_state)
    elif cmd == 'inventory': # 'i' or 'inv' would have been aliased to 'inventory'
        interaction.handle_inventory_command(game_state)

    # System commands
    elif cmd == 'save':
        system.handle_save_command(game_state, save_game_func, list_saves_func)
    elif cmd == 'help':
        system.handle_help_command()
    
    # Commands affecting the main loop (like 'quit') are typically managed outside this handler
    # in __main__.py. If it makes it here, warn the player.
    elif cmd == 'quit':
        ui.print_colored("Quitting... (Confirmation will appear next)", ui.COLOR_WARNING)

    else:
        ui.print_colored(f"I don't understand the command '{cmd}'. Type 'help' for a list of commands.", ui.COLOR_ERROR)
