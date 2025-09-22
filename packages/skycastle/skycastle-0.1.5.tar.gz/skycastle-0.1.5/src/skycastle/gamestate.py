# skycastle/gamestate.py

from dataclasses import dataclass, field
from typing import Dict, List, Optional
import json

from skycastle import worlddata

# --- Data Classes for Game Objects ---

@dataclass
class Item:
    """Represents an item in the game."""
    id: str
    name: str
    description: str
    can_be_taken: bool

@dataclass
class Exit:
    """Represents a connection from one room to another."""
    direction: str
    destination_room_id: str
    is_locked: bool = True

@dataclass
class Puzzle:
    """Represents a puzzle in the game."""
    id: str
    name: str
    room_id: str
    description: str
    required_items: List[str]
    action: str
    target_item_id: Optional[str]
    prereq_flags: List[str]
    unlocks_exits: Dict[str, Dict[str, str]]
    adds_items: List[str]
    removes_items: List[str]
    changes_room_desc: Optional[str]
    sets_flag: Optional[str]
    is_solved: bool = False

@dataclass
class Room:
    """Represents a location in the Sky Castle."""
    id: str
    name: str
    initial_description: str
    current_description: str
    items: List[Item] = field(default_factory=list)
    exits: Dict[str, Exit] = field(default_factory=dict)

@dataclass
class Player:
    """Represents the player character's state."""
    current_room_id: str = "crystal_atrium"
    inventory: List[Item] = field(default_factory=list)
    solved_flags: List[str] = field(default_factory=list)

@dataclass
class GameState:
    """Encapsulates the entire state of the game."""
    rooms: Dict[str, Room] = field(default_factory=dict)
    puzzles: Dict[str, Puzzle] = field(default_factory=dict)
    player: Player = field(default_factory=Player)
    all_item_prototypes: Dict[str, Item] = field(default_factory=dict)
    game_version: str = "0.1.0"
    current_loaded_save_id: Optional[str] = None # NEW: To track which save file is currently loaded/active

    def to_dict(self) -> Dict:
        """Serializes the GameState into a dictionary."""
        state_dict = {}
        state_dict['player'] = {
            'current_room_id': self.player.current_room_id,
            'inventory': [item.id for item in self.player.inventory],
            'solved_flags': self.player.solved_flags
        }
        state_dict['rooms'] = {
            room_id: {
                'current_description': room.current_description,
                'items': [item.id for item in room.items],
                'exits': {direction: {'destination_room_id': ex.destination_room_id, 'is_locked': ex.is_locked}
                          for direction, ex in room.exits.items()}
            }
            for room_id, room in self.rooms.items()
        }
        state_dict['puzzles'] = {
            puzzle_id: {'is_solved': puzzle.is_solved}
            for puzzle_id, puzzle in self.puzzles.items()
        }
        state_dict['game_version'] = self.game_version
        state_dict['current_loaded_save_id'] = self.current_loaded_save_id # NEW: Serialize this too
        return state_dict

    @classmethod
    def from_dict(cls, data: Dict) -> 'GameState':
        """
        Deserializes a dictionary into a GameState object.
        This reconstitutes the game state based on saved data,
        using the initial `worlddata` as a template to ensure all base objects exist.
        """
        game_state = create_game_state_from_data()

        game_state.game_version = data.get('game_version', game_state.game_version)

        player_data = data.get('player', {})
        game_state.player.current_room_id = player_data.get('current_room_id', game_state.player.current_room_id)
        game_state.player.solved_flags = player_data.get('solved_flags', [])
        game_state.player.inventory = [
            game_state.all_item_prototypes[item_id]
            for item_id in player_data.get('inventory', [])
            if item_id in game_state.all_item_prototypes
        ]

        for room_id, room_state_data in data.get('rooms', {}).items():
            if room_id in game_state.rooms:
                room = game_state.rooms[room_id]
                room.current_description = room_state_data.get('current_description', room.initial_description)
                room.items = [
                    game_state.all_item_prototypes[item_id]
                    for item_id in room_state_data.get('items', [])
                    if item_id in game_state.all_item_prototypes
                ]
                for direction, exit_data in room_state_data.get('exits', {}).items():
                    if direction in room.exits:
                        room.exits[direction].is_locked = exit_data.get('is_locked', True)

        for puzzle_id, puzzle_state_data in data.get('puzzles', {}).items():
            if puzzle_id in game_state.puzzles:
                game_state.puzzles[puzzle_id].is_solved = puzzle_state_data.get('is_solved', False)
                if game_state.puzzles[puzzle_id].is_solved and game_state.puzzles[puzzle_id].sets_flag and \
                   game_state.puzzles[puzzle_id].sets_flag not in game_state.player.solved_flags:
                   game_state.player.solved_flags.append(game_state.puzzles[puzzle_id].sets_flag)
        
        game_state.current_loaded_save_id = data.get('current_loaded_save_id') # NEW: Load this ID

        return game_state

# --- Factory Function to Initialize GameState from worlddata ---

def create_game_state_from_data() -> GameState:
    """
    Initializes a brand-new GameState object from the static data defined in worlddata.
    This function should be called at the start of a new game or as the base for loading.
    """
    all_item_prototypes: Dict[str, Item] = {}
    for item_data in worlddata.ITEMS_DATA:
        item = Item(
            id=item_data['id'],
            name=item_data['name'],
            description=item_data['description'],
            can_be_taken=item_data['can_be_taken']
        )
        all_item_prototypes[item.id] = item

    rooms_dict: Dict[str, Room] = {}
    for room_data in worlddata.ROOMS_DATA:
        initial_items_in_room = [all_item_prototypes[item_id] for item_id in room_data['items'] if item_id in all_item_prototypes]

        room_exits: Dict[str, Exit] = {}
        for direction, dest_room_id in room_data['exits'].items():
            room_exits[direction] = Exit(
                direction=direction,
                destination_room_id=dest_room_id,
                is_locked=False
            )

        room = Room(
            id=room_data['id'],
            name=room_data['name'],
            initial_description=room_data['description'],
            current_description=room_data['description'],
            items=initial_items_in_room,
            exits=room_exits
        )
        rooms_dict[room.id] = room

    puzzles_dict: Dict[str, Puzzle] = {}
    for puzzle_data in worlddata.PUZZLES_DATA:
        puzzle = Puzzle(
            id=puzzle_data['id'],
            name=puzzle_data['name'],
            room_id=puzzle_data['room_id'],
            description=puzzle_data['description'],
            required_items=puzzle_data['required_items'],
            action=puzzle_data['action'],
            target_item_id=puzzle_data['target_item_id'],
            prereq_flags=puzzle_data['prereq_flags'],
            unlocks_exits=puzzle_data['unlocks_exits'],
            adds_items=puzzle_data['adds_items'],
            removes_items=puzzle_data['removes_items'],
            changes_room_desc=puzzle_data['changes_room_desc'],
            sets_flag=puzzle_data['sets_flag'],
            is_solved=False
        )
        puzzles_dict[puzzle.id] = puzzle

        for target_room_id, exits_to_unlock in puzzle_data['unlocks_exits'].items():
            if target_room_id in rooms_dict:
                for direction_to_unlock, destination in exits_to_unlock.items():
                    if direction_to_unlock in rooms_dict[target_room_id].exits:
                        rooms_dict[target_room_id].exits[direction_to_unlock].is_locked = True
                    else:
                        rooms_dict[target_room_id].exits[direction_to_unlock] = Exit(
                            direction=direction_to_unlock,
                            destination_room_id=destination,
                            is_locked=True
                        )

    return GameState(
        rooms=rooms_dict,
        puzzles=puzzles_dict,
        player=Player(),
        all_item_prototypes=all_item_prototypes,
        game_version="0.1.0",
        current_loaded_save_id=None # NEW: New games start with no loaded save ID
    )
