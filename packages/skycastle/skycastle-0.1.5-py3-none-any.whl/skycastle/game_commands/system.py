# skycastle/game_commands/system.py

from typing import List

# Relative imports for GameState
from skycastle.gamestate import GameState
# Relative import for UI functions
from skycastle import ui
# No need to import Fore or Style here; they are accessed via ui.Fore/ui.Style
# from colorama import Fore, Style # REMOVED: Not needed here

def handle_save_command(game_state: GameState, save_game_func, list_saves_func) -> None:
    """
    Handles the 'save' command, allowing players to save their game.
    Supports quicksave if a name is left blank and a game was previously loaded.
    """
    save_name_input = ui.get_player_input("Enter a name for your save (leave blank to quicksave): ").strip()

    if not save_name_input: # If name is blank or only whitespace
        if game_state.current_loaded_save_id:
            # Find the metadata for the currently loaded save to get its original name
            all_saves = list_saves_func() # Use the passed function to list saves
            original_save_metadata = next(
                (s for s in all_saves if s.save_id == game_state.current_loaded_save_id),
                None
            )
            
            if original_save_metadata:
                # Use the original name for the overwrite
                name_for_overwrite = original_save_metadata.save_name
                # CORRECTED: Use ui.Fore.MAGENTA for info messages
                ui.print_colored(f"Overwriting save '{name_for_overwrite}' (ID: {game_state.current_loaded_save_id[:8]}...)...", ui.Fore.MAGENTA)
                save_game_func(game_state, name_for_overwrite, overwrite_id=game_state.current_loaded_save_id)
            else:
                # CORRECTED: Use ui.Fore.LIGHTRED_EX for warnings
                ui.print_colored("Cannot quicksave: original save file metadata not found. Please provide a new name.", ui.Fore.LIGHTRED_EX)
                new_save_name = ui.get_player_input("Enter a NEW name for your save: ").strip()
                if new_save_name:
                    save_game_func(game_state, new_save_name)
                else:
                    # CORRECTED: Use ui.Fore.LIGHTRED_EX for warnings
                    ui.print_colored("Save operation cancelled.", ui.Fore.LIGHTRED_EX)
        else:
            # CORRECTED: Use ui.Fore.LIGHTRED_EX for warnings
            ui.print_colored("Cannot quicksave: No game currently loaded or previously saved. Please provide a name for a new save.", ui.Fore.LIGHTRED_EX)
            new_save_name = ui.get_player_input("Enter a NEW name for your save: ").strip()
            if new_save_name:
                save_game_func(game_state, new_save_name)
            else:
                # CORRECTED: Use ui.Fore.LIGHTRED_EX for warnings
                ui.print_colored("Save operation cancelled.", ui.Fore.LIGHTRED_EX)
    else: # If a name was provided
        # CORRECTED: Use ui.Fore.MAGENTA for info messages
        ui.print_colored(f"Saving game as '{save_name_input}'...", ui.Fore.MAGENTA)
        save_game_func(game_state, save_name_input)
    
    # CORRECTED: Use ui.Fore.LIGHTGREEN_EX for highlight
    ui.print_colored("Game save operation complete.", ui.Fore.LIGHTGREEN_EX)

def handle_help_command() -> None:
    """
    Handles the 'help' command to display available game commands.
    """
    ui.display_help_commands()

