import streamlit as st
import random
from typing import List, Dict, Tuple, Optional
from collections import Counter

# -------------------------------
# Game Constants & Configuration
# -------------------------------
COLORS = ['Red', 'Blue', 'Yellow', 'Black']
NUMBERS = list(range(1, 14))  # 1 to 13
JOKER_COUNT = 2

# Color mapping for visual styling
COLOR_STYLES = {
    'Red': {'bg': '#FFE5E5', 'border': '#FF0000', 'icon': '🔴'},
    'Blue': {'bg': '#E5F0FF', 'border': '#0000FF', 'icon': '🔵'},
    'Yellow': {'bg': '#FFF9E5', 'border': '#FFD700', 'icon': '🟡'},
    'Black': {'bg': '#E5E5E5', 'border': '#000000', 'icon': '⚫'},
    'Joker': {'bg': '#F0E6FF', 'border': '#9B59B6', 'icon': '🃏'}
}

# -------------------------------
# Tile Class
# -------------------------------
class Tile:
    def __init__(self, color: Optional[str] = None, number: Optional[int] = None, is_joker: bool = False):
        self.color = color
        self.number = number
        self.is_joker = is_joker
    
    def __repr__(self):
        if self.is_joker:
            return "Joker"
        return f"{self.color} {self.number}"
    
    def to_dict(self):
        return {
            'color': self.color,
            'number': self.number,
            'is_joker': self.is_joker
        }
    
    @staticmethod
    def from_dict(data):
        if data['is_joker']:
            return Tile(is_joker=True)
        return Tile(color=data['color'], number=data['number'], is_joker=False)

# -------------------------------
# Deck Creation & Management
# -------------------------------
def create_deck() -> List[Tile]:
    """Create a deck of 106 tiles (2 sets of 1-13 in 4 colors + 2 jokers)"""
    deck = []
    # Two copies of each number for each color
    for _ in range(2):  # Two sets
        for color in COLORS:
            for number in NUMBERS:
                deck.append(Tile(color=color, number=number, is_joker=False))
    # Add jokers
    for _ in range(JOKER_COUNT):
        deck.append(Tile(is_joker=True))
    return deck

def shuffle_deck(deck: List[Tile]) -> List[Tile]:
    """Shuffle the deck"""
    shuffled = deck.copy()
    random.shuffle(shuffled)
    return shuffled

def deal_initial_hand(deck: List[Tile]) -> Tuple[List[Tile], List[Tile]]:
    """Deal 14 tiles to the player"""
    hand = deck[:14]
    remaining_deck = deck[14:]
    return hand, remaining_deck

# -------------------------------
# Hand Sorting Function
# -------------------------------
def sort_hand(hand: List[Tile]) -> List[Tile]:
    """Sort hand by color and number, with jokers at the end"""
    # Separate jokers
    normal_tiles = [tile for tile in hand if not tile.is_joker]
    jokers = [tile for tile in hand if tile.is_joker]
    
    # Sort normal tiles by color order then number
    color_order = {color: idx for idx, color in enumerate(COLORS)}
    normal_tiles.sort(key=lambda tile: (color_order[tile.color], tile.number))
    
    return normal_tiles + jokers

# -------------------------------
# Win Validation Logic
# -------------------------------
def is_valid_set(tiles: List[Tile]) -> bool:
    """Check if tiles form a valid set (3+ of a kind, different colors)"""
    if len(tiles) < 3:
        return False
    
    # Extract normal tiles and jokers
    normal_tiles = [t for t in tiles if not t.is_joker]
    joker_count = len([t for t in tiles if t.is_joker])
    
    if len(normal_tiles) == 0:
        return False
    
    # Check if all normal tiles have the same number
    numbers = [t.number for t in normal_tiles]
    if len(set(numbers)) != 1:
        return False
    
    # Check if colors are distinct (set requirement)
    colors = [t.color for t in normal_tiles]
    if len(set(colors)) != len(normal_tiles):
        return False
    
    # With jokers, we need at least 3 tiles total
    return len(tiles) >= 3

def is_valid_run(tiles: List[Tile]) -> bool:
    """Check if tiles form a valid run (sequence of same color, consecutive numbers)"""
    if len(tiles) < 3:
        return False
    
    # Extract normal tiles and jokers
    normal_tiles = [t for t in tiles if not t.is_joker]
    joker_count = len([t for t in tiles if t.is_joker])
    
    if len(normal_tiles) == 0:
        return False
    
    # Check if all normal tiles have the same color
    colors = [t.color for t in normal_tiles]
    if len(set(colors)) != 1:
        return False
    
    # Get numbers and sort them
    numbers = sorted([t.number for t in normal_tiles])
    
    # Check for consecutive sequence (considering jokers)
    # Jokers can fill missing numbers
    needed_numbers = set(range(min(numbers), max(numbers) + 1))
    missing_count = len(needed_numbers - set(numbers))
    
    return missing_count <= joker_count and len(tiles) >= 3

def can_form_groups(hand: List[Tile]) -> Tuple[bool, str]:
    """Check if the entire hand can be grouped into valid sets and runs"""
    if len(hand) == 0:
        return True, "Empty hand!"
    
    # Simple validation: check if we can partition into valid groups
    # This is a simplified check - tries to find groups greedily
    remaining = hand.copy()
    groups = []
    
    while remaining:
        # Try to find a group of 3 or more tiles that form a valid set or run
        found_group = False
        
        # Check for runs first (more restrictive)
        for i in range(len(remaining) - 2):
            for j in range(i + 2, len(remaining)):
                candidate = remaining[i:j+1]
                if is_valid_run(candidate) or is_valid_set(candidate):
                    groups.append(candidate)
                    # Remove these tiles from remaining
                    for tile in candidate:
                        remaining.remove(tile)
                    found_group = True
                    break
            if found_group:
                break
        
        if not found_group:
            # If we can't find any group, check if remaining are all jokers
            if all(t.is_joker for t in remaining):
                groups.append(remaining)
                remaining = []
            else:
                return False, "Cannot form valid groups with all tiles"
    
    # Check if all tiles are used
    if len(hand) == sum(len(g) for g in groups):
        group_details = []
        for i, group in enumerate(groups, 1):
            if is_valid_set(group):
                group_details.append(f"Group {i}: SET - {', '.join(str(t) for t in group)}")
            else:
                group_details.append(f"Group {i}: RUN - {', '.join(str(t) for t in group)}")
        return True, "\n".join(group_details)
    
    return False, "Invalid grouping"

def check_winning_hand(hand: List[Tile]) -> Tuple[bool, str]:
    """Main function to check if the hand is a winning hand"""
    if len(hand) == 0:
        return False, "No tiles in hand!"
    
    # Sort hand first
    sorted_hand = sort_hand(hand)
    
    # Check if we can form valid groups
    can_win, message = can_form_groups(sorted_hand)
    
    if can_win:
        return True, f"🎉 WINNING HAND! 🎉\n\n{message}"
    else:
        return False, f"❌ Not a winning hand\n{message}\n\nTip: Need valid sets (3+ same number, different colors) or runs (3+ consecutive numbers, same color)"

# -------------------------------
# Streamlit UI Components
# -------------------------------
def display_tile_button(tile: Tile, tile_id: str, on_click_callback) -> None:
    """Display a single tile as a styled button"""
    if tile.is_joker:
        style = COLOR_STYLES['Joker']
        label = f"{style['icon']} JOKER"
    else:
        style = COLOR_STYLES[tile.color]
        label = f"{style['icon']} {tile.number}"
    
    # Create a custom styled button
    st.markdown(f"""
        <style>
        div[data-testid="column"]:has(button[data-tile-id="{tile_id}"]) button {{
            background-color: {style['bg']};
            border-left: 4px solid {style['border']};
            border-right: 4px solid {style['border']};
            border-top: 2px solid {style['border']};
            border-bottom: 2px solid {style['border']};
            font-weight: bold;
            padding: 0.5rem 1rem;
            margin: 0.2rem;
            width: 100%;
            min-width: 80px;
            transition: all 0.2s ease;
        }}
        div[data-testid="column"]:has(button[data-tile-id="{tile_id}"]) button:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        }}
        </style>
    """, unsafe_allow_html=True)
    
    if st.button(label, key=tile_id, use_container_width=True):
        on_click_callback(tile_id)

def display_hand(hand: List[Tile], on_discard_callback) -> None:
    """Display the player's hand in a horizontal rack"""
    if not hand:
        st.info("Your hand is empty!")
        return
    
    # Sort the hand before displaying
    sorted_hand = sort_hand(hand)
    
    # Display tiles in columns
    cols = st.columns(min(len(sorted_hand), 7))  # Max 7 tiles per row
    
    for idx, tile in enumerate(sorted_hand):
        col_idx = idx % 7
        if col_idx == 0 and idx > 0:
            cols = st.columns(min(len(sorted_hand) - idx, 7))
        
        with cols[col_idx]:
            tile_id = f"tile_{idx}_{id(tile)}"
            display_tile_button(tile, tile_id, on_discard_callback)

# -------------------------------
# Main Game Application
# -------------------------------
def init_game_state():
    """Initialize or reset the game state"""
    if 'game_initialized' not in st.session_state:
        deck = create_deck()
        shuffled_deck = shuffle_deck(deck)
        hand, remaining_deck = deal_initial_hand(shuffled_deck)
        
        st.session_state.deck = remaining_deck
        st.session_state.hand = hand
        st.session_state.discard_pile = []
        st.session_state.game_over = False
        st.session_state.message = "Game started! Draw a tile to begin."
        st.session_state.game_initialized = True

def draw_tile():
    """Draw a tile from the deck"""
    if st.session_state.game_over:
        st.session_state.message = "Game is over! Please start a new game."
        return
    
    if len(st.session_state.deck) == 0:
        st.session_state.message = "No more tiles in the deck! Game over."
        st.session_state.game_over = True
        return
    
    drawn_tile = st.session_state.deck.pop(0)
    st.session_state.hand.append(drawn_tile)
    st.session_state.hand = sort_hand(st.session_state.hand)
    st.session_state.message = f"🎲 You drew: {drawn_tile}"
    st.session_state.last_drawn = drawn_tile

def discard_tile(tile_id: str):
    """Discard a tile from the hand"""
    if st.session_state.game_over:
        st.session_state.message = "Game is over! Please start a new game."
        return
    
    # Extract the tile from the ID (simple approach: find by string representation)
    # For production, we'd store unique IDs, but for simplicity we'll use a counter
    tile_index = int(tile_id.split('_')[1])
    # This is a bit hacky; we need to find the actual tile object
    # Better approach: store tile IDs, but for demo we'll use the current hand
    if st.session_state.hand:
        # Discard the last tile as a simple demo (improved version below)
        # Actually, let's track by position in sorted hand
        sorted_hand = sort_hand(st.session_state.hand)
        if tile_index < len(sorted_hand):
            discarded = sorted_hand[tile_index]
            # Remove from hand
            for i, tile in enumerate(st.session_state.hand):
                if tile.color == discarded.color and tile.number == discarded.number and tile.is_joker == discarded.is_joker:
                    st.session_state.hand.pop(i)
                    break
            st.session_state.discard_pile.append(discarded)
            st.session_state.hand = sort_hand(st.session_state.hand)
            st.session_state.message = f"🗑️ Discarded: {discarded}"
            st.session_state.last_discard = discarded

def new_game():
    """Start a new game"""
    deck = create_deck()
    shuffled_deck = shuffle_deck(deck)
    hand, remaining_deck = deal_initial_hand(shuffled_deck)
    
    st.session_state.deck = remaining_deck
    st.session_state.hand = hand
    st.session_state.discard_pile = []
    st.session_state.game_over = False
    st.session_state.message = "New game started! Good luck!"
    st.session_state.last_drawn = None
    st.session_state.last_discard = None

def check_win():
    """Check if current hand is a winning hand"""
    can_win, message = check_winning_hand(st.session_state.hand)
    if can_win:
        st.session_state.game_over = True
        st.session_state.message = message
        st.balloons()
    else:
        st.session_state.message = message

# -------------------------------
# Main Streamlit App
# -------------------------------
def main():
    st.set_page_config(
        page_title="Okey/Konkan Game",
        page_icon="🀄",
        layout="wide"
    )
    
    # Custom CSS for better styling
    st.markdown("""
        <style>
        .stApp {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }
        .main-header {
            text-align: center;
            padding: 1rem;
            background: rgba(255,255,255,0.9);
            border-radius: 10px;
            margin-bottom: 2rem;
        }
        .info-panel {
            background: rgba(255,255,255,0.95);
            padding: 1rem;
            border-radius: 10px;
            margin-bottom: 1rem;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Header
    st.markdown("""
        <div class="main-header">
            <h1>🀄 Okey / Konkan Game 🀄</h1>
            <p>Classic Turkish tile-based game | Form sets and runs to win!</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Initialize game state
    init_game_state()
    
    # Game info panel
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("📚 Deck", len(st.session_state.deck))
    with col2:
        st.metric("🃟 Hand Size", len(st.session_state.hand))
    with col3:
        st.metric("🗑️ Discard Pile", len(st.session_state.discard_pile))
    with col4:
        if st.session_state.get('last_drawn'):
            st.info(f"Last drawn: {st.session_state.last_drawn}")
    
    # Message display
    if st.session_state.message:
        message_color = "green" if "Winning" in st.session_state.message or "🎉" in st.session_state.message else "blue"
        st.markdown(f"""
            <div class="info-panel" style="border-left: 4px solid {message_color};">
                <p style="margin: 0; font-size: 1.1rem;">{st.session_state.message}</p>
            </div>
        """, unsafe_allow_html=True)
    
    # Game controls
    col_controls1, col_controls2, col_controls3 = st.columns(3)
    with col_controls1:
        if st.button("🎲 Draw Tile", use_container_width=True, type="primary"):
            draw_tile()
            st.rerun()
    with col_controls2:
        if st.button("🏆 Check Winning Hand", use_container_width=True):
            check_win()
            st.rerun()
    with col_controls3:
        if st.button("🔄 New Game", use_container_width=True):
            new_game()
            st.rerun()
    
    st.divider()
    
    # Player's hand display
    st.subheader("🎯 Your Hand (Click any tile to discard)")
    st.caption("💡 Tip: Tiles are automatically sorted. Click a tile after drawing to discard it.")
    
    # Display hand with discard callback
    display_hand(st.session_state.hand, discard_tile)
    
    # Discard pile display (collapsible)
    with st.expander("🗑️ Discard Pile History", expanded=False):
        if st.session_state.discard_pile:
            discard_cols = st.columns(10)
            for idx, tile in enumerate(reversed(st.session_state.discard_pile[-20:])):  # Show last 20
                with discard_cols[idx % 10]:
                    if tile.is_joker:
                        st.markdown(f"**🃏**")
                    else:
                        st.markdown(f"**{tile.color[:1]}{tile.number}**")
        else:
            st.info("No tiles discarded yet")
    
    # Rules sidebar
    with st.sidebar:
        st.markdown("## 📖 Game Rules")
        st.markdown("""
        ### Objective
        Form valid **sets** and **runs** with all 14 tiles in your hand!
        
        ### Valid Combinations
        
        **SET** (3+ tiles):
        - Same number
        - Different colors
        - Example: 🔴5, 🔵5, 🟡5, ⚫5
        
        **RUN** (3+ tiles):
        - Same color
        - Consecutive numbers
        - Example: 🔴1, 🔴2, 🔴3, 🔴4
        
        ### Jokers 🃏
        - Jokers are wild cards
        - Can replace ANY tile in a set or run
        
        ### How to Play
        1. Click **Draw Tile** to take from deck
        2. Click any tile in your hand to discard it
        3. Try to organize all tiles into valid groups
        4. Click **Check Winning Hand** to see if you've won!
        
        ### Scoring
        - First player to organize all 14 tiles wins!
        """)
        
        st.markdown("---")
        st.markdown("### 🎮 Controls Summary")
        st.markdown("""
        - **Draw Tile**: Take new tile from deck
        - **Check Winning Hand**: Validate your hand
        - **New Game**: Start fresh
        - **Click tile**: Discard it
        """)

if __name__ == "__main__":
    main()
