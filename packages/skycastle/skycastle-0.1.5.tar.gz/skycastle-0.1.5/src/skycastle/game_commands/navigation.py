# skycastle/game_commands/navigation.py

from typing import List

from skycastle.gamestate import GameState # Relative import for GameState
from skycastle import ui # Relative import for UI functions
# No need to import Fore or Style here; they are accessed via ui.Fore/ui.Style
# from colorama import Fore, Style # REMOVED: Not needed here

def handle_go_command(command_parts: List[str], game_state: GameState) -> None:
    """
    Handles the 'go' command for player movement between rooms.
    """
    if len(command_parts) < 2:
        # CORRECTED: Use ui.Fore.RED for error
        ui.print_colored("Go where?", ui.Fore.RED)
        return

    direction = command_parts[1] # e.g., 'north', 'east'
    player = game_state.player
    current_room = game_state.rooms[player.current_room_id]

    if direction in current_room.exits:
        exit_obj = current_room.exits[direction]
        if not exit_obj.is_locked:
            player.current_room_id = exit_obj.destination_room_id
            new_room = game_state.rooms[player.current_room_id]
            ui.display_room_info(
                new_room.name,
                new_room.current_description,
                new_room.items,
                new_room.exits
            )
        else:
            # CORRECTED: Use ui.Fore.LIGHTRED_EX for warning
            ui.print_colored(f"The path to the {direction} is currently blocked or locked.", ui.Fore.LIGHTRED_EX)
    else:
        # CORRECTED: Use ui.Fore.RED for error
        ui.print_colored(f"You cannot go '{direction}' from here.", ui.Fore.RED)
