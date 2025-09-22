
# skycastle/__main__.py

import sys
import argparse # NEW: For command-line argument parsing
from typing import Optional, TextIO

# Import Style specifically for direct input prompts (still needed for menu options)
from colorama import Style, Fore # Fore imported for direct styling in menu

# Import modules we've created
from skycastle.gamestate import GameState, create_game_state_from_data
from skycastle.save_manager import save_game, load_game, list_saves, delete_game
from skycastle import ui         # UI functions
from skycastle.game_commands import main_handler as commands # Main command handler

def new_game() -> GameState:
    """Starts a new game, initializing the GameState and displaying intro."""
    ui.print_colored("Starting a new adventure in the Sky Castle...", ui.Fore.LIGHTGREEN_EX)
    game_state = create_game_state_from_data()
    ui.display_intro_sequence() # Display the game's introduction
    return game_state

def load_previous_game() -> Optional[GameState]:
    """Allows the player to load a previously saved game."""
    saves = list_saves()
    if not saves:
        ui.print_colored("No saved games found.", ui.Fore.RED)
        return None

    ui.print_colored("\n--- Saved Games ---", ui.Fore.LIGHTGREEN_EX)
    for i, save in enumerate(saves):
        ui.print_colored(f"{i+1}. '{save.save_name}' - Room: {save.current_room_name} "
                         f"(Saved: {save.timestamp.strftime('%Y-%m-%d %H:%M')})", ui.Fore.CYAN, indent=ui._INDENT_LEVEL)
    ui.print_colored("-------------------\n", ui.Fore.LIGHTGREEN_EX)

    while True:
        choice = ui.get_player_input("Enter the number of the game to load (or 'back' to return to main menu): ")
        if choice == 'back':
            return None
        try:
            index = int(choice) - 1
            if 0 <= index < len(saves):
                selected_save_id = saves[index].save_id
                return load_game(selected_save_id)
            else:
                ui.print_colored("Invalid selection. Please try again.", ui.Fore.RED)
        except ValueError:
            ui.print_colored("Invalid input. Please enter a number or 'back'.", ui.Fore.RED)

def delete_save_game():
    """Manages the process of deleting a saved game."""
    saves = list_saves()
    if not saves:
        ui.print_colored("No saved games found to delete.", ui.Fore.RED)
        return

    ui.print_colored("\n--- Saved Games for Deletion ---", ui.Fore.LIGHTGREEN_EX)
    for i, save in enumerate(saves):
        ui.print_colored(f"{i+1}. '{save.save_name}' - Room: {save.current_room_name} "
                         f"(Saved: {save.timestamp.strftime('%Y-%m-%d %H:%M')}) - ID: {save.save_id[:8]}...", ui.Fore.CYAN, indent=ui._INDENT_LEVEL)
    ui.print_colored("--------------------------------\n", ui.Fore.LIGHTGREEN_EX)

    while True:
        choice = ui.get_player_input("Enter the number of the game to DELETE (or 'back' to return to main menu): ")
        if choice == 'back':
            return
        try:
            index = int(choice) - 1
            if 0 <= index < len(saves):
                selected_save = saves[index]
                # Using direct input for the confirmation prompt to handle its specific color better.
                raw_confirm = input(f"{ui.Fore.LIGHTRED_EX}Are you sure you want to delete '{selected_save.save_name}'? This cannot be undone. (yes/no): {Style.RESET_ALL}").strip().lower()

                if raw_confirm == 'yes':
                    if delete_game(selected_save.save_id):
                        ui.print_colored(f"'{selected_save.save_name}' has been definitively removed.", ui.Fore.LIGHTGREEN_EX)
                    else:
                        ui.print_colored(f"Failed to delete '{selected_save.save_name}'.", ui.Fore.RED)
                else:
                    ui.print_colored("Deletion cancelled.", ui.Fore.CYAN)
                return
            else:
                ui.print_colored("Invalid selection. Please try again.", ui.Fore.RED)
        except ValueError:
            ui.print_colored("Invalid input. Please enter a number or 'back'.", ui.Fore.RED)


def game_loop(game_state: GameState):
    """The main game-playing loop."""
    ui.print_colored(f"\nWelcome to Sky Castle! You are in the {game_state.rooms[game_state.player.current_room_id].name}.", ui.Fore.LIGHTGREEN_EX, Style.BRIGHT)
    ui.display_room_info(        # Display initial room info using the UI module
        game_state.rooms[game_state.player.current_room_id].name,
        game_state.rooms[game_state.player.current_room_id].current_description,
        game_state.rooms[game_state.player.current_room_id].items,
        game_state.rooms[game_state.player.current_room_id].exits
    )

    running = True
    while running:
        if 'father_found' in game_state.player.solved_flags:
            running = False
            continue

        raw_user_input = ui.get_player_input("\nWhat would you like to do? (Type 'help' for commands): ")
        
        # Check if the player wants to quit explicitly before parsing complex commands
        # In test mode, get_player_input will return "quit" at EOF
        if raw_user_input.lower() in ['quit', 'q', 'quitgame']:
            if not ui._ENABLE_COLOR: # In test mode, auto-confirm quit
                running = False
            else: # Interactive mode, ask for confirmation
                confirm_quit = ui.get_player_input(f"{ui.Fore.LIGHTRED_EX}Are you sure you want to quit? (yes/no): {Style.RESET_ALL}").lower()
                if confirm_quit == 'yes':
                    running = False
                else:
                    ui.print_colored("Quit cancelled. Continuing game.", ui.Fore.CYAN)
            continue
            
        commands.handle_command(raw_user_input, game_state, save_game, list_saves)

        if 'father_found' in game_state.player.solved_flags:
            running = False

    if 'father_found' in game_state.player.solved_flags:
        ui.display_win_screen()
        ui.display_credits()
    else:
        ui.print_colored("\nExiting Sky Castle. See you next time!", ui.Fore.LIGHTGREEN_EX)
        if not ui._ENABLE_COLOR: # In test mode, exit cleanly if we're not winning but quitting
            return False


def main():
    parser = argparse.ArgumentParser(description="Sky Castle Text Adventure Game")
    parser.add_argument(
        '--test-mode',
        action='store_true',
        help="Run in test mode: disable colors, read commands from stdin, write output to stdout."
    )
    parser.add_argument(
        '--test-input-file',
        type=argparse.FileType('r'), # Automatically handles opening the file for reading
        help="Specify an input file for test mode. Required when --test-mode is used."
    )

    args = parser.parse_args()

    # Store original stdin/stdout to restore later if needed (though sys.exit prevents it here)
    original_stdin = sys.stdin

    if args.test_mode:
        ui.set_color_enabled(False) # Disable color output
        if args.test_input_file:
            sys.stdin = args.test_input_file # Redirect stdin to the test file
            # In test mode, we usually want to skip the main menu and go straight to new game
            game_state = new_game() # Always start a new game in test mode
            game_loop(game_state)
            # After game_loop, ensure the input file is closed
            args.test_input_file.close()
            sys.stdin = original_stdin # Restore stdin just in case
        else:
            print("Error: --test-input-file is required when --test-mode is used.", file=sys.stderr)
            sys.exit(1)
    else:
        # Normal interactive game mode
        while True:
            ui.display_title_screen()
            choice = ui.get_player_input("Choose an option: ")

            if choice == '1': # New Game
                game_state = new_game()
                if not game_loop(game_state):
                    break
            elif choice == '2': # Load Game
                game_state = load_previous_game()
                if game_state:
                    if not game_loop(game_state):
                        break
            elif choice == '3': # Delete Game
                delete_save_game()
            elif choice == '4': # Quit (now option 4)
                ui.print_colored("Thank you for playing Sky Castle!", ui.Fore.LIGHTGREEN_EX, Style.BRIGHT)
                break
            else:
                ui.print_colored("Invalid option. Please enter 1, 2, 3, or 4.", ui.Fore.RED)
    
if __name__ == "__main__":
    main()
