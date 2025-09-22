# skycastle/save_manager.py

import json
import uuid
import datetime
from pathlib import Path
from dataclasses import dataclass
from typing import List, Dict, Any, Optional

from platformdirs import user_data_dir

# Import GameState and its factory function
from skycastle.gamestate import GameState, create_game_state_from_data

# Define application information for platformdirs
APP_NAME = "sky-castle-game"
APP_AUTHOR = "sky_castle_dev" # Can be your name/team name

@dataclass
class SaveMetadata:
    """Metadata about a single save file, for display in UI."""
    save_id: str
    save_name: str
    timestamp: datetime.datetime
    current_room_name: str
    game_version: str = "0.1.0" # Keep track of game version for save compatibility

    def to_dict(self) -> Dict[str, Any]:
        """Converts metadata to a dictionary for serialization."""
        return {
            "save_id": self.save_id,
            "save_name": self.save_name,
            "timestamp": self.timestamp.isoformat(), # ISO format for datetime
            "current_room_name": self.current_room_name,
            "game_version": self.game_version
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SaveMetadata":
        """Reconstructs metadata from a dictionary."""
        return cls(
            save_id=data["save_id"],
            save_name=data["save_name"],
            timestamp=datetime.datetime.fromisoformat(data["timestamp"]), # Convert back from ISO
            current_room_name=data["current_room_name"],
            game_version=data.get("game_version", "unknown") # Handle older saves if version is missing
        )

def _get_save_directory() -> Path:
    """
    Returns the platform-specific directory for game saves,
    adhering to XDG Base Directory Specification.
    """
    data_dir = Path(user_data_dir(appname=APP_NAME, appauthor=APP_AUTHOR, ensure_exists=True))
    save_dir = data_dir / "saves"
    save_dir.mkdir(parents=True, exist_ok=True)
    return save_dir

def save_game(game_state: GameState, save_name: str, overwrite_id: Optional[str] = None) -> Optional[SaveMetadata]:
    """
    Saves the current game state to a file.
    If overwrite_id is provided, it tries to overwrite that specific save file.
    Otherwise, it creates a new save with a unique ID.

    Args:
        game_state: The current GameState object.
        save_name: A user-friendly name for this save.
        overwrite_id: Optional. The ID of an existing save file to overwrite.

    Returns:
        The metadata of the created/updated save, or None if save failed.
    """
    if overwrite_id:
        save_id = overwrite_id
        # When overwriting, try to retrieve original metadata to keep its save_name if applicable,
        # but for now we're explicitly being passed `save_name`.
        # The key aspect is using the existing save_id.
        print(f"Attempting to overwrite save with ID: {save_id}...")
    else:
        save_id = str(uuid.uuid4()) # Generate a new unique ID for the save file
        print(f"Creating new save with ID: {save_id}...")

    timestamp = datetime.datetime.now()
    current_room = game_state.rooms.get(game_state.player.current_room_id)
    current_room_name = current_room.name if current_room else "Unknown Location"

    metadata = SaveMetadata(
        save_id=save_id,
        save_name=save_name,
        timestamp=timestamp,
        current_room_name=current_room_name,
        game_version=game_state.game_version
    )

    # When saving, explicitly set the current_loaded_save_id in the game_state to this new save's ID.
    game_state.current_loaded_save_id = save_id

    save_data = {
        "metadata": metadata.to_dict(),
        "game_state": game_state.to_dict() # Serialize the actual game state
    }

    save_dir = _get_save_directory()
    save_path = save_dir / f"{save_id}.json"

    try:
        with open(save_path, 'w', encoding='utf-8') as f:
            json.dump(save_data, f, indent=4)
        print(f"Game '{save_name}' saved successfully to {save_path.name}.")
        return metadata
    except Exception as e:
        print(f"Error saving game '{save_name}' to {save_path.name}: {e}")
        return None


def load_game(save_id: str) -> Optional[GameState]:
    """
    Loads a game state from a specific save file.

    Args:
        save_id: The unique ID of the save file to load.

    Returns:
        The loaded GameState object, or None if the save file is not found or corrupted.
    """
    save_dir = _get_save_directory()
    save_path = save_dir / f"{save_id}.json"

    if not save_path.exists():
        print(f"Error: Save file '{save_id}.json' not found.")
        return None

    try:
        with open(save_path, 'r', encoding='utf-8') as f:
            save_data = json.load(f)

        loaded_game_state_dict = save_data.get('game_state')
        if not loaded_game_state_dict:
            raise ValueError("Save file does not contain 'game_state' data.")

        # GameState.from_dict handles re-creating the base state and applying changes.
        # It also now loads the 'current_loaded_save_id' if present in the loaded data.
        game_state = GameState.from_dict(loaded_game_state_dict)

        # Also ensure that the GameState's `current_loaded_save_id` is set to the ID of the file *just loaded*.
        # This is crucial for the "quick save" overwrite functionality.
        game_state.current_loaded_save_id = save_id

        print(f"Game '{save_id}' loaded successfully.")
        return game_state

    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from save file {save_path}.")
    except ValueError as e:
        print(f"Error loading game state from {save_path}: {e}")
    except Exception as e:
        print(f"An unexpected error occurred while loading {save_path}: {e}")
    return None

def list_saves() -> List[SaveMetadata]:
    """
    Lists all available save game metadata, sorted by timestamp (most recent first).

    Returns:
        A list of SaveMetadata objects.
    """
    save_dir = _get_save_directory()
    save_files = list(save_dir.glob("*.json"))
    
    saves_metadata: List[SaveMetadata] = []
    for save_path in save_files:
        try:
            with open(save_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            metadata_dict = data.get('metadata')
            if metadata_dict:
                # Validate save_id consistency between filename and metadata
                if metadata_dict.get('save_id') == save_path.stem:
                    metadata = SaveMetadata.from_dict(metadata_dict)
                    saves_metadata.append(metadata)
                else:
                    print(f"Warning: Save file {save_path.name} has inconsistent metadata ID. Skipping.")
            else:
                print(f"Warning: Save file {save_path.name} is missing metadata. Skipping.")
        except json.JSONDecodeError:
            print(f"Warning: Could not decode JSON from save file {save_path.name}. Skipping.")
        except Exception as e:
            print(f"Warning: Error reading metadata from {save_path.name}: {e}. Skipping.")
    
    # Sort by timestamp, most recent first
    saves_metadata.sort(key=lambda s: s.timestamp, reverse=True)
    return saves_metadata

def delete_game(save_id: str) -> bool:
    """
    Deletes a specific save game file.

    Args:
        save_id: The unique ID of the save file to delete.

    Returns:
        True if the save file was successfully deleted, False otherwise.
    """
    save_dir = _get_save_directory()
    save_path = save_dir / f"{save_id}.json"

    if not save_path.exists():
        print(f"Error: Save file '{save_id}.json' not found for deletion.")
        return False

    try:
        save_path.unlink() # Delete the file
        print(f"Save file '{save_id}.json' successfully deleted.")
        return True
    except OSError as e:
        print(f"Error deleting save file {save_path}: {e}")
        return False
