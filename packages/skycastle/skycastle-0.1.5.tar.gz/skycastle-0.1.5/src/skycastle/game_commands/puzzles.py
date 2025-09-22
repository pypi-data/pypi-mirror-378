# skycastle/game_commands/puzzles.py

from typing import List, Optional, Tuple # Ensure Tuple is imported
# No longer directly using defaultdict in this file after refactor

# Relative imports for GameState, Item, Exit, Puzzle dataclasses
from skycastle.gamestate import GameState, Item, Exit, Puzzle
# Relative import for UI functions
from skycastle import ui
# Import Style explicitly for ui.Style.BRIGHT usage in this file
from colorama import Style


def _get_item_by_name(item_name: str, item_list: List[Item]) -> Optional[Item]:
    """Helper to find an item by its normalized name in a list."""
    for item in item_list:
        if item.name.lower() == item_name.lower():
            return item
    return None

def _attempt_puzzle_solve(command_parts: List[str], game_state: GameState) -> Tuple[bool, str]:
    """
    Attempts to solve a puzzle based on the player's command.
    Returns a tuple: (True/False if a puzzle was solved, feedback_message)
    """
    cmd = command_parts[0] # e.g., 'use', 'read', 'activate'
    args = command_parts[1:]
    player = game_state.player
    current_room = game_state.rooms[player.current_room_id]

    target_item_name = ' '.join(args).strip() if args else None

    possible_puzzles = [
        p for p in game_state.puzzles.values()
        if not p.is_solved and p.room_id == current_room.id
    ]

    # Keep track of specific failure reasons to give better feedback
    found_relevant_puzzle_but_failed_prereqs = False
    found_relevant_puzzle_but_missing_item = False
    found_relevant_puzzle_but_wrong_target = False
    # found_relevant_puzzle_but_wrong_action_on_target = False # Not currently used for distinct feedback

    for puzzle in possible_puzzles:
        # **1. ACTION MATCH:** Check if the command action matches the puzzle's expected action
        if puzzle.action != cmd:
            continue # Not this puzzle, continue to next possible puzzle

        # We found a puzzle matching the action in the current room. Now check other conditions.
        # This implies it's a "relevant" puzzle, even if it fails later checks.


        # **2. PREREQUISITE FLAGS:** Check if all prerequisite flags are met
        if not all(flag in player.solved_flags for flag in puzzle.prereq_flags):
            found_relevant_puzzle_but_failed_prereqs = True
            continue # Failed prereqs, continue to next possible puzzle

        # **3. TARGET ITEM MATCH:** Check if the target specified (or implied) matches the puzzle's requirement
        target_item_matched_for_puzzle = False
        if puzzle.target_item_id is None:
            # Puzzle has no specific target_item_id. This means the action is 'general' in the room,
            # or a specific item *from required_items* is essentially the target (e.g., 'plant seed').
            if not target_item_name: # No target named by player
                target_item_matched_for_puzzle = True
            elif target_item_name in [game_state.all_item_prototypes[req_id].name.lower() for req_id in puzzle.required_items if req_id in game_state.all_item_prototypes]:
                # The player might name a required item, meaning 'use [required_item]'
                target_item_matched_for_puzzle = True
            # else:
            #     found_relevant_puzzle_but_wrong_target = True # Removed for cleaner flow if target_item_id is None

        else: # Puzzle requires a specific target_item_id
            if target_item_name:
                item_in_room = _get_item_by_name(target_item_name, current_room.items)
                item_in_inventory = _get_item_by_name(target_item_name, player.inventory)

                # Check if the puzzle's required target_item_id matches the item found (by ID for robustness)
                if (item_in_room and item_in_room.id == puzzle.target_item_id) or \
                   (item_in_inventory and item_in_inventory.id == puzzle.target_item_id):
                    target_item_matched_for_puzzle = True
                else:
                    found_relevant_puzzle_but_wrong_target = True
            else:
                # Puzzle needs a target_item_id but player didn't specify one
                found_relevant_puzzle_but_wrong_target = True
        
        if not target_item_matched_for_puzzle:
            continue # Failed target match, continue to next possible puzzle


        # **4. REQUIRED ITEMS IN INVENTORY:** Check if all required items are in the player's inventory
        has_all_required_items = True
        missing_item_names = []
        current_inventory_ids = {item.id for item in player.inventory}
        for req_item_id in puzzle.required_items:
            if req_item_id not in current_inventory_ids:
                has_all_required_items = False
                # Try to get the actual item name for feedback
                if req_item_id in game_state.all_item_prototypes:
                    missing_item_names.append(game_state.all_item_prototypes[req_item_id].name)
                else:
                    missing_item_names.append(req_item_id) # Fallback to ID if prototype not found
                # No need to break, gather all missing items for a comprehensive message

        if not has_all_required_items:
            found_relevant_puzzle_but_missing_item = True
            # Store the specific item names for feedback
            # CORRECTED: Use ui.Fore.LIGHTRED_EX and ui.Style.NORMAL
            return (False, f"You are missing the following item(s) to {cmd} '{target_item_name or cmd.removesuffix('e') or cmd}': {', '.join(missing_item_names)}. Look for them!")
            # Note: We return immediately here for the "missing item" case because it's definitive.
            # If multiple puzzles could match, we'd need a more complex error aggregation.


        # --- PUZZLE SOLVED! ---
        # CORRECTED: Using ui.Fore.LIGHTGREEN_EX and direct Style.BRIGHT
        ui.print_colored(f"\n<<< You have solved: {puzzle.name}! >>>", ui.Fore.LIGHTGREEN_EX, Style.BRIGHT)
        puzzle.is_solved = True

        # Apply puzzle effects:
        if puzzle.sets_flag and puzzle.sets_flag not in player.solved_flags:
            player.solved_flags.append(puzzle.sets_flag)

        if puzzle.changes_room_desc:
            current_room.current_description = puzzle.changes_room_desc

        for item_id_to_remove in puzzle.removes_items:
            prototype_item_name = game_state.all_item_prototypes[item_id_to_remove].name if item_id_to_remove in game_state.all_item_prototypes else item_id_to_remove

            # Try to remove from inventory
            item_obj_in_inv = _get_item_by_name(prototype_item_name, player.inventory)
            if item_obj_in_inv:
                # CORRECTED: Use ui.Fore.MAGENTA
                player.inventory.remove(item_obj_in_inv)
                ui.print_colored(f"The {item_obj_in_inv.name} is consumed.", ui.Fore.MAGENTA)

            # Try to remove from room (for environmental items or those dropped)
            item_obj_in_room = _get_item_by_name(prototype_item_name, current_room.items)
            if item_obj_in_room:
                 # CORRECTED: Use ui.Fore.MAGENTA
                 current_room.items.remove(item_obj_in_room)


        for item_id_to_add in puzzle.adds_items:
            if item_id_to_add in game_state.all_item_prototypes:
                new_item = game_state.all_item_prototypes[item_id_to_add]
                if new_item.can_be_taken:
                    # CORRECTED: Use ui.Fore.MAGENTA
                    player.inventory.append(new_item)
                    ui.print_colored(f"You acquire a {new_item.name}.", ui.Fore.MAGENTA)
                else:
                    # CORRECTED: Use ui.Fore.MAGENTA
                    current_room.items.append(new_item)
                    ui.print_colored(f"A {new_item.name} appears in the room.", ui.Fore.MAGENTA)


        for target_room_id, exits_to_unlock in puzzle.unlocks_exits.items():
            if target_room_id in game_state.rooms:
                room_to_affect = game_state.rooms[target_room_id]
                for direction, destination_room_id in exits_to_unlock.items():
                    if direction in room_to_affect.exits:
                        room_to_affect.exits[direction].is_locked = False
                        # CORRECTED: Use ui.Fore.LIGHTGREEN_EX
                        ui.print_colored(f"A path opens towards the {direction}!", ui.Fore.LIGHTGREEN_EX)
                    else:
                        new_exit = Exit(direction=direction, destination_room_id=destination_room_id, is_locked=False)
                        room_to_affect.exits[direction] = new_exit
                        # CORRECTED: Use ui.Fore.LIGHTGREEN_EX
                        ui.print_colored(f"A new path emerges towards the {direction}!", ui.Fore.LIGHTGREEN_EX)

        # After applying effects and before returning, redisplay the room to show changes.
        # This prevents the need for an extra 'look' command.
        ui.display_room_info(
            current_room.name,
            current_room.current_description,
            current_room.items,
            current_room.exits
        )
        return (True, f"Puzzle '{puzzle.name}' solved!") # Puzzle solved!

    # If we fall through the loop, no puzzle was solved for the given command.
    # Provide intelligent fallback feedback based on flags.
    if found_relevant_puzzle_but_failed_prereqs:
        # CORRECTED: Use ui.Fore.LIGHTRED_EX
        return (False, f"A puzzle related to '{target_item_name or cmd}' is here, but you lack the necessary insight or conditions to proceed.")
    if found_relevant_puzzle_but_wrong_target:
        # CORRECTED: Use ui.Fore.LIGHTRED_EX
        return (False, f"You try to {cmd} the '{target_item_name or 'something'}', but it doesn't seem to have the desired effect here.")
    
    # Generic failure if no specific reason was found
    # CORRECTED: Use ui.Fore.LIGHTRED_EX
    return (False, f"You try to {cmd} the {target_item_name or 'air'}, but nothing happens.")


def handle_puzzle_command(command_parts: List[str], game_state: GameState) -> None:
    """
    Acts as the entry point for commands related to puzzle solving (use, read, activate).
    """
    solved, feedback_message = _attempt_puzzle_solve(command_parts, game_state)
    if not solved:
        # CORRECTED: Use ui.Fore.LIGHTRED_EX for error/warning
        ui.print_colored(feedback_message, ui.Fore.LIGHTRED_EX)
    # If solved, _attempt_puzzle_solve already printed success and room info.
