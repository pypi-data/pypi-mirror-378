# skycastle/worlddata.py

# --- Items ---
# Each item is a dictionary with the following keys:
# 'id': A unique identifier (string).
# 'name': How the item is referred to in-game (string, lowercase for consistency).
# 'description': What the player sees when they 'look [item]'.
# 'can_be_taken': Boolean, true if the item can be added to the player's inventory.
#                 False for environmental objects that are interacted with in-place.
ITEMS_DATA = [
    {
        'id': 'tuning_fork',
        'name': 'tuning fork',
        'description': "A delicate silver tuning fork. It hums faintly with an unseen, resonant energy.",
        'can_be_taken': True
    },
    {
        'id': 'pocket_mirror',
        'name': 'pocket mirror',
        'description': "A small, ornate pocket mirror, its glass highly polished. It catches and reflects light beautifully.",
        'can_be_taken': True
    },
    {
        'id': 'seed_of_unity',
        'name': 'seed of unity',
        'description': "A single, pearlescent seed, pulsating with a soft, warm glow. It feels vital and ready for growth.",
        'can_be_taken': True
    },
    {
        'id': 'empty_dewdrop_vial',
        'name': 'empty dewdrop vial',
        'description': "A small, clear glass vial, designed to hold liquids. It's currently empty, waiting to be filled.",
        'can_be_taken': True
    },
    {
        'id': 'water_lever',
        'name': 'water lever',
        'description': "A large, rusty lever connected to a network of pipes. It looks like it could divert the flow of water.",
        'can_be_taken': False
    },
    {
        'id': 'father_journal',
        'name': "father's journal",
        'description': "Your father's leather-bound journal. It contains cryptic notes, sketches of mechanisms, and heartfelt entries about building a 'sky-high dream.'",
        'can_be_taken': True
    },
    {
        'id': 'fragmented_blueprint_1',
        'name': 'fragmented blueprint piece 1',
        'description': "A torn section of a detailed blueprint, showing part of an elaborate 'Sky Castle' structure. It has a jagged tear on one side.",
        'can_be_taken': True
    },
    {
        'id': 'fragmented_blueprint_2',
        'name': 'fragmented blueprint piece 2',
        'description': "Another torn section of a blueprint, this one illustrating a powerful energy conduit. It seems to have a matching jagged tear.",
        'can_be_taken': True
    },
    {
        'id': 'full_dewdrop_vial',
        'name': 'full dewdrop vial',
        'description': "The vial is now filled with shimmering, luminescent morning dew, pulsating with a gentle light. It smells faintly of ozone and fresh growth.",
        'can_be_taken': True # This item is generated upon puzzle completion
    },
]

# --- Rooms ---
# Each room is a dictionary with the following keys:
# 'id': A unique identifier (string).
# 'name': How the room is displayed to the player.
# 'description': The text shown when the player enters or 'looks' around the room.
# 'exits': A dictionary where keys are directions (e.g., 'north', 'east', 'up')
#          and values are the 'id' of the destination room.
#          Exits listed here are initially available. Conditional exits are handled by puzzles.
# 'items': A list of 'id's of items initially present in this room.
ROOMS_DATA = [
    {
        'id': 'crystal_atrium',
        'name': 'Crystal Atrium',
        'description': "You stand in the magnificent ***Crystal Atrium***, a soaring hall with walls of shimmering, giant glass tears slowly descending. Sunlight filters through, creating shifting patterns on the polished floor. To the north, a vibrant glow pulses; to the east, you hear the rush of water.",
        'exits': {
            'north': 'rainbow_gallery',
            'east': 'wasted_waterworks',
            # 'west' to father's study is initially locked
        },
        'items': []
    },
    {
        'id': 'rainbow_gallery',
        'name': 'Rainbow Gallery',
        'description': "This circular ***Rainbow Gallery*** is adorned with numerous stained-glass panels, but the light is diffuse and muted, lacking the vibrant spectrum you'd expect. A path leads south, back to the atrium.",
        'exits': {
            'south': 'crystal_atrium',
            # 'north' to Dawning Outlook is initially locked
        },
        'items': ['tuning_fork'] # Item placed here for balancing the flow
    },
    {
        'id': 'wasted_waterworks',
        'name': 'Wasted Waterworks',
        'description': "A vast, damp chamber, the ***Wasted Waterworks***, where strong currents of water gush from high pipes, only to disappear uselessly into drains below. No plant life can thrive here; the ground is barren and slick. West leads back to the atrium.",
        'exits': {
            'west': 'crystal_atrium',
            'north': 'garden_of_patience'
        },
        'items': ['water_lever'] # Environmental item
    },
    {
        'id': 'garden_of_patience',
        'name': 'Garden of Patience',
        'description': "A tranquil ***Garden of Patience***, surprisingly untouched by the nearby water's roar. The earth is rich, but most plants are dormant, waiting. A winding path leads south.",
        'exits': {
            'south': 'wasted_waterworks'
            # 'east' to Dawning Outlook is initially locked
        },
        'items': [] # seed_of_unity to be used here, but found elsewhere
    },
    {
        'id': 'fathers_study',
        'name': "Father's Study",
        'description': "This room, your ***Father's Study***, is cluttered with blueprints, notes, and mementos. It feels filled with your father's presence, though he's not here. A desk holds an open journal.",
        'exits': {
            'east': 'crystal_atrium' # Connects back to atrium for alternative path
        },
        'items': ['father_journal', 'fragmented_blueprint_1', 'pocket_mirror'] # Key items here
    },
    {
        'id': 'dawning_outlook',
        'name': 'Dawning Outlook',
        'description': "A high, serene vantage point, the ***Dawning Outlook***, shrouded in a soft, ethereal mist. From here, you can see parts of the castle sprawling below and the distant glow of a towering spire. An empty vial sits on a crystalline ledge. The air feels pregnant with possibility.",
        'exits': {
            # These exits appear as reverse directions once unlocked by puzzles in other rooms
            'south': 'rainbow_gallery',
            'west': 'garden_of_patience',
            'southwest': 'fathers_study', # Connects directly for non-linear exploration
            # 'up' to Sky-High Summit is locked.
        },
        'items': ['empty_dewdrop_vial', 'seed_of_unity'] # Items to collect/use here - placed both here for demonstration, but one might be found in father's study or elsewhere.
    },
    {
        'id': 'sky_high_summit',
        'name': 'Sky-High Summit',
        'description': "This is the very pinnacle of the ***Sky-High Summit***, a grand, unfinished workshop open to the expansive sky. Tools are scattered amongst blueprints, and a profound sense of purpose fills the air. It feels like the culmination of a lifelong project. You see a final piece of blueprint awaiting completion.",
        'exits': {
           'down': 'dawning_outlook'
        },
        'items': ['fragmented_blueprint_2']
    }
]

# --- Puzzles ---
# Each puzzle is a dictionary describing a logical challenge and its effects.
# 'id': Unique identifier for the puzzle.
# 'name': A short, descriptive name for the puzzle.
# 'room_id': The ID of the room where the puzzle primarily takes place or is relevant.
# 'description': A narrative hint or an observation that guides the player towards the puzzle.
# 'required_items': A list of item IDs needed in the player's inventory to attempt the puzzle.
# 'action': The command/action type needed (e.g., 'use', 'read', 'activate').
# 'target_item_id': If the action involves using an item on another, this is the target item's ID in the room or inventory.
#                    If None, it implies using a required_item in the room's context.
# 'prereq_flags': A list of 'id's of flags that must be set (puzzles solved) for this puzzle to be available.
# 'unlocks_exits': A dict mapping room 'id's to a dict of directions to unlock ({'room_id': {'direction': 'destination_room_id'}}).
# 'adds_items': A list of item IDs to add to the current room or player inventory upon solution.
# 'removes_items': A list of item IDs to remove from inventory upon solution.
# 'changes_room_desc': Optional, a new description for the room after the puzzle is solved.
# 'sets_flag': Optional, a string flag that will be set upon completion, influencing other puzzles or game state.
PUZZLES_DATA = [
    {
        'id': 'attune_crystals',
        'name': 'Attune the Crystals',
        'room_id': 'crystal_atrium',
        'description': "The descending crystal tears in the atrium seem to vibrate faintly, as if awaiting a specific resonance. Perhaps an item could help with this.",
        'required_items': ['tuning_fork'],
        'action': 'use',
        'target_item_id': None, # Means 'use tuning_fork' in the room context
        'prereq_flags': [],
        'unlocks_exits': {'crystal_atrium': {'west': 'fathers_study'}},
        'adds_items': [],
        'removes_items': [],
        'changes_room_desc': "The Crystal Atrium now hums with a harmonious resonance. A shimmering archway, previously unseen, has materialized to the west, beckoning you forward.",
        'sets_flag': 'crystal_attuned'
    },
    {
        'id': 'create_rainbow',
        'name': 'Create the Rainbow',
        'room_id': 'rainbow_gallery',
        'description': "The stained-glass panels year for light. If only something could focus the diffuse light into a brilliant spectrum. You sense a hidden path could be revealed.",
        'required_items': ['pocket_mirror'],
        'action': 'use',
        'target_item_id': None, # Means 'use pocket_mirror' in the room context
        'prereq_flags': [],
        'unlocks_exits': {'rainbow_gallery': {'north': 'dawning_outlook'}},
        'adds_items': [],
        'removes_items': [],
        'changes_room_desc': "A dazzling, full rainbow now arcs across the gallery, illuminating a previously hidden archway to the north with all its vibrant colors.",
        'sets_flag': 'rainbow_created'
    },
    {
        'id': 'divert_water',
        'name': 'Divert the Water',
        'room_id': 'wasted_waterworks',
        'description': "The mighty water lever looks like it could change the destiny of this gushing water. It seems wasteful for it to just disappear.",
        'required_items': [],
        'action': 'use',
        'target_item_id': 'water_lever', # Means 'use water_lever'
        'prereq_flags': [],
        'unlocks_exits': {}, # No direct exit unlock, but sets a flag.
        'adds_items': [],
        'removes_items': [],
        'changes_room_desc': "With a mighty grind, the water lever has been thrown! The gushing currents now flow through an unseen channel, and the air here feels less frantic, as if nature itself is preparing to make use of it.",
        'sets_flag': 'water_diverted'
    },
    {
        'id': 'plant_seed',
        'name': 'Plant the Seed of Unity',
        'room_id': 'garden_of_patience',
        'description': "The rich soil in the center of the garden seems to yearn for something to nurture. The pearlescent seed feels right at home here.",
        'required_items': ['seed_of_unity'],
        'action': 'use',
        'target_item_id': None, # Means 'use seed_of_unity' in the room context
        'prereq_flags': ['water_diverted'], # Water needs to be diverted for planting to be meaningful
        'unlocks_exits': {},
        'adds_items': [],
        'removes_items': ['seed_of_unity'],
        'changes_room_desc': "A tiny, hopeful sprout now emerges where you planted the pearlescent seed. It glows faintly, hinting at future growth.",
        'sets_flag': 'seed_planted'
    },
    {
        'id': 'nurture_plant',
        'name': 'Nurture the Sprout',
        'room_id': 'garden_of_patience',
        'description': "The sprout from the Seed of Unity looks healthy, but it needs something more to truly flourish, perhaps the essence of a new day.",
        'required_items': ['full_dewdrop_vial'],
        'action': 'use',
        'target_item_id': None, # Means 'use full_dewdrop_vial' in the room context (on the sprout)
        'prereq_flags': ['seed_planted'], # Needs the seed to be planted first
        'unlocks_exits': {'garden_of_patience': {'east': 'dawning_outlook'}},
        'adds_items': [],
        'removes_items': ['full_dewdrop_vial'],
        'changes_room_desc': "The sprout has burst into a magnificent, luminescent flower, its petals unfurling towards a newly revealed archway to the east, which shines brightly and leads upwards.",
        'sets_flag': 'plant_flourished'
    },
    {
        'id': 'collect_dew',
        'name': 'Collect Morning Dew',
        'room_id': 'dawning_outlook',
        'description': "The morning mist seems to condense into shimmering droplets, ripe for collection. You hold an empty vial.",
        'required_items': ['empty_dewdrop_vial'],
        'action': 'use',
        'target_item_id': None, # Means 'use empty_dewdrop_vial' in the room context
        'prereq_flags': [],
        'unlocks_exits': {},
        'adds_items': ['full_dewdrop_vial'], # The empty vial becomes full_dewdrop_vial
        'removes_items': ['empty_dewdrop_vial'],
        'changes_room_desc': "The Dawning Outlook feels lighter now that the essential dew has been collected. The mist has thinned slightly, revealing more of the castle spires.",
        'sets_flag': 'dew_collected'
    },
    {
        'id': 'decipher_journal',
        'name': 'Decipher Father\'s Journal',
        'room_id': 'fathers_study',
        'description': "The journal contains cryptic symbols and partial diagrams. Perhaps with enough focus, or a fresh perspective, its secrets can be revealed, hinting at a new path.",
        'required_items': ['father_journal'], # The journal must be in inventory
        'action': 'read',
        'target_item_id': 'father_journal',
        'prereq_flags': [],
        'unlocks_exits': {'fathers_study': {'north': 'dawning_outlook'}},
        'adds_items': [],
        'removes_items': [],
        'changes_room_desc': "Having pieced together some of your father's thoughts, the study seems to hum with a clearer understanding. A previously unnoticed passage to the north opens, leading towards the light.",
        'sets_flag': 'journal_deciphered'
    },
    {
        'id': 'open_summit',
        'name': 'Open Sky-High Summit',
        'room_id': 'dawning_outlook',
        'description': "The high tower remains unreachable, but the collective energy of the castle seems to be converging here. All paths lead to this dawn, and a final ascent awaits.",
        'required_items': [], # No specific inventory items, but requires certain state flags to be true.
        'action': 'activate', # A generic activate for an environmental effect
        'target_item_id': None, # 'activate' in the room context
        'prereq_flags': ['rainbow_created', 'plant_flourished', 'journal_deciphered', 'dew_collected'], # Need these key achievements
        'unlocks_exits': {'dawning_outlook': {'up': 'sky_high_summit'}},
        'adds_items': [],
        'removes_items': [],
        'changes_room_desc': "A magnificent stairway of light now spirals upwards from the center of the Dawning Outlook, leading directly to the Sky-High Summit! The air crackles with joyful energy, a beacon of your journey's end.",
        'sets_flag': 'summit_unlocked'
    },
    {
        'id': 'assemble_blueprint',
        'name': 'Assemble the Blueprint',
        'room_id': 'sky_high_summit',
        'description': "The pinnacle is clearly built from these very blueprints. Putting them together must be key to finding your father and completing his 'Sky Castle' vision.",
        'required_items': ['fragmented_blueprint_1', 'fragmented_blueprint_2'],
        'action': 'use',
        'target_item_id': None, # Means 'use fragmented_blueprint_1' in the room context (when blueprint 2 is also in inventory)
        'prereq_flags': [],
        'unlocks_exits': {}, # No exit unlock, leads to game end
        'adds_items': [],
        'removes_items': ['fragmented_blueprint_1', 'fragmented_blueprint_2'], # Blueprints are consumed to finish the structure
        'changes_room_desc': "With the blueprint pieces assembled, the final section of the Sky Castle shimmers into existence. Your father is here, his face filled with relief and love, gesturing to the magnificent view. You've found him! The journey is complete.",
        'sets_flag': 'father_found' # This flag will be checked for game completion.
    }
]


# --- Helper functions for easy data retrieval by ID ---
def _get_data_by_id(data_list, item_id):
    """Helper to find a dictionary in a list by its 'id' key."""
    for item in data_list:
        if item['id'] == item_id:
            return item
    return None

def get_room_data(room_id: str) -> dict | None:
    """Retrieves room data by its ID."""
    return _get_data_by_id(ROOMS_DATA, room_id)

def get_item_data(item_id: str) -> dict | None:
    """Retrieves item data by its ID."""
    return _get_data_by_id(ITEMS_DATA, item_id)

def get_puzzle_data(puzzle_id: str) -> dict | None:
    """Retrieves puzzle data by its ID."""
    return _get_data_by_id(PUZZLES_DATA, puzzle_id)
