# skycastle/game_commands/interaction.py

from typing import List, Optional
from collections import defaultdict # Used for grouping items

# CORRECTED: Changed '.' to '..' for correct relative import to gamestate.py
from skycastle.gamestate import GameState, Item

from skycastle import ui # Relative import for UI functions

def _get_item_by_name(item_name: str, item_list: List[Item]) -> Optional[Item]:
    """Helper to find an item by its normalized name in a list."""
    for item in item_list:
        if item.name.lower() == item_name.lower():
            return item
    return None

def handle_look_command(command_parts: List[str], game_state: GameState) -> None:
    """
    Handles the 'look' command to inspect the current room or a specific item.
    """
    player = game_state.player
    current_room = game_state.rooms[player.current_room_id]

    if len(command_parts) < 2:
        ui.display_room_info(
            current_room.name,
            current_room.current_description,
            current_room.items,
            current_room.exits
        )
    else:
        item_name = ' '.join(command_parts[1:])
        
        item_in_room = _get_item_by_name(item_name, current_room.items)
        if item_in_room:
             ui.display_item_description(item_in_room.name, item_in_room.description)
             return
        
        item_in_inventory = _get_item_by_name(item_name, player.inventory)
        if item_in_inventory:
            ui.display_item_description(item_in_inventory.name, item_in_inventory.description)
            return

        ui.print_colored(f"You don't see a '{item_name}' here or in your inventory.", ui.Fore.RED)

def handle_take_command(command_parts: List[str], game_state: GameState) -> None:
    """
    Handles the 'take' command to pick up an item from the current room.
    """
    if len(command_parts) < 2:
        ui.print_colored("Take what?", ui.Fore.RED)
        return

    item_name = ' '.join(command_parts[1:])
    player = game_state.player
    current_room = game_state.rooms[player.current_room_id]
    
    item_to_take = _get_item_by_name(item_name, current_room.items)

    if item_to_take:
        if item_to_take.can_be_taken:
            current_room.items.remove(item_to_take)
            player.inventory.append(item_to_take)
            ui.print_colored(f"You take the {item_to_take.name}.", ui.Fore.LIGHTGREEN_EX)
        else:
            ui.print_colored(f"You cannot take the {item_to_take.name}.", ui.Fore.LIGHTRED_EX)
    else:
        ui.print_colored(f"There is no '{item_name}' here to take.", ui.Fore.RED)

def handle_drop_command(command_parts: List[str], game_state: GameState) -> None:
    """
    Handles the 'drop' command to place an item from inventory into the current room.
    """
    if len(command_parts) < 2:
        ui.print_colored("Drop what?", ui.Fore.RED)
        return

    item_name = ' '.join(command_parts[1:])
    player = game_state.player
    current_room = game_state.rooms[player.current_room_id]
    
    item_to_drop = _get_item_by_name(item_name, player.inventory)
    
    if item_to_drop:
        player.inventory.remove(item_to_drop)
        current_room.items.append(item_to_drop)
        ui.print_colored(f"You drop the {item_to_drop.name}.", ui.Fore.LIGHTGREEN_EX)
    else:
        ui.print_colored(f"You don't have a '{item_name}' to drop.", ui.Fore.RED)

def handle_inventory_command(game_state: GameState) -> None:
    """
    Handles the 'inventory' or 'i' command to display player's inventory.
    """
    ui.display_inventory(game_state.player.inventory)
