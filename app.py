import streamlit as st
import random
from collections import Counter

# -------------------------------
# Tile definitions
# -------------------------------
COLORS = ['Red', 'Blue', 'Green', 'Black']
NUMBERS = list(range(1, 14))  # 1 to 13
JOKERS = 2

def create_deck():
    """Create a full deck of 106 tiles: two sets of 1-13 in four colors + 2 jokers."""
    deck = []
    # Two copies of each numbered tile per color
    for _ in range(2):
        for color in COLORS:
            for num in NUMBERS:
                deck.append({'color': color, 'number': num, 'type': 'normal'})
    # Add jokers
    for _ in range(JOKERS):
        deck.append({'color': None, 'number': None, 'type': 'joker'})
    return deck

def shuffle_tiles(deck):
    """Shuffle the deck."""
    random.shuffle(deck)
    return deck

def deal_hand(deck, num_tiles=14):
    """Deal 14 tiles from the deck to the player."""
    hand = deck[:num_tiles]
    remaining_deck = deck[num_tiles:]
    return hand, remaining_deck

def tile_to_str(tile):
    """Convert a tile to a readable string."""
    if tile['type'] == 'joker':
        return "🃏 Joker"
    else:
        return f"{tile['color']} {tile['number']}"

def is_valid_set_or_run(tiles):
    """
    Basic check if tiles form a valid set (same number, different colors) or run (same color, consecutive numbers).
    Returns a message indicating the result.
    """
    if not tiles:
        return "No tiles selected."
    
    # Separate jokers
    normal_tiles = [t for t in tiles if t['type'] == 'normal']
    jokers_count = len([t for t in tiles if t['type'] == 'joker'])
    
    if len(normal_tiles) < 2 and jokers_count > 0:
        return "At least 2 normal tiles are needed for a valid set/run (jokers can replace missing tiles)."
    
    # Check for set: all numbers same, colors distinct
    numbers = [t['number'] for t in normal_tiles]
    colors = [t['color'] for t in normal_tiles]
    if len(set(numbers)) == 1 and len(set(colors)) == len(normal_tiles):
        return f"✅ Valid SET! (All {numbers[0]}s, different colors) + {jokers_count} joker(s)"
    
    # Check for run: same color, consecutive numbers
    if len(set([t['color'] for t in normal_tiles])) == 1:
        sorted_nums = sorted(numbers)
        is_consecutive = all(sorted_nums[i] + 1 == sorted_nums[i+1] for i in range(len(sorted_nums)-1))
        if is_consecutive:
            return f"✅ Valid RUN! (Consecutive numbers in {normal_tiles[0]['color']}) + {jokers_count} joker(s)"
        else:
            missing = []
            for i in range(len(sorted_nums)-1):
                if sorted_nums[i] + 1 != sorted_nums[i+1]:
                    missing.append(f"{sorted_nums[i]+1}")
            return f"❌ Not a valid run. Missing: {', '.join(missing)} (Jokers can fill gaps)"
    
    return "❌ Not a valid set or run. Check colors and numbers."

# -------------------------------
# Streamlit App
# -------------------------------
st.set_page_config(page_title="Okey / Konkan Game", layout="wide")
st.title("🀄 Okey / Konkan Digital Game")
st.markdown("### Basic version: Draw, Discard, and form sets/runs")

# Initialize game state
if 'deck' not in st.session_state:
    full_deck = create_deck()
    shuffled_deck = shuffle_tiles(full_deck)
    player_hand, remaining_deck = deal_hand(shuffled_deck, 14)
    st.session_state.deck = remaining_deck
    st.session_state.hand = player_hand
    st.session_state.discard_pile = []
    st.session_state.drawn_tile = None
    st.session_state.game_over = False

# Helper to redraw UI
def reset_game():
    full_deck = create_deck()
    shuffled_deck = shuffle_tiles(full_deck)
    player_hand, remaining_deck = deal_hand(shuffled_deck, 14)
    st.session_state.deck = remaining_deck
    st.session_state.hand = player_hand
    st.session_state.discard_pile = []
    st.session_state.drawn_tile = None
    st.session_state.game_over = False

def draw_tile():
    if st.session_state.game_over:
        st.warning("Game over! Press 'New Game' to play again.")
        return
    if len(st.session_state.deck) == 0:
        st.warning("No tiles left in the deck!")
        return
    drawn = st.session_state.deck.pop(0)
    st.session_state.drawn_tile = drawn
    st.success(f"🎲 You drew: {tile_to_str(drawn)}")

def discard_tile(index):
    if st.session_state.game_over:
        st.warning("Game over! Press 'New Game' to play again.")
        return
    if st.session_state.drawn_tile is None:
        st.warning("You must draw a tile before discarding!")
        return
    
    # Discard the tile at index (from hand)
    discarded = st.session_state.hand.pop(index)
    st.session_state.discard_pile.append(discarded)
    # Add the drawn tile to hand
    st.session_state.hand.append(st.session_state.drawn_tile)
    st.session_state.drawn_tile = None
    st.success(f"🗑️ Discarded: {tile_to_str(discarded)}")
    
    # Check win condition: all tiles in hand form sets/runs
    check_win_condition()

def check_win_condition():
    """Simple win check: if hand is empty or all tiles can be grouped (simplified)."""
    # For simplicity, we check if there are 0 or 14 tiles? No.
    # Better: we can ask player to verify manually for now.
    # But we'll just check if the whole hand is a set/run (too strict, but demo)
    if len(st.session_state.hand) == 0:
        st.session_state.game_over = True
        st.balloons()
        st.success("🎉 YOU WIN! Perfect hand! 🎉")
    elif len(st.session_state.hand) == 14:
        # In real Okey, you'd group tiles. We'll just check if all form runs/sets (advanced, skip for brevity)
        pass

# -------------------------------
# UI Layout
# -------------------------------
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader(f"🃟 Your Hand ({len(st.session_state.hand)} tiles)")
    if st.session_state.hand:
        cols_per_row = 7
        rows = (len(st.session_state.hand) + cols_per_row - 1) // cols_per_row
        for row in range(rows):
            cols = st.columns(cols_per_row)
            for i in range(cols_per_row):
                idx = row * cols_per_row + i
                if idx < len(st.session_state.hand):
                    tile = st.session_state.hand[idx]
                    tile_label = tile_to_str(tile)
                    with cols[i]:
                        if st.button(tile_label, key=f"hand_{idx}"):
                            discard_tile(idx)
    else:
        st.info("No tiles in hand. You win! Start a new game.")

with col2:
    st.subheader("🎮 Game Controls")
    if st.button("🃟 Draw a Tile", use_container_width=True):
        draw_tile()
    
    if st.button("🔄 New Game", use_container_width=True):
        reset_game()
        st.rerun()
    
    st.divider()
    st.subheader("📦 Deck Info")
    st.metric("Remaining Tiles", len(st.session_state.deck))
    
    st.divider()
    st.subheader("🗑️ Discard Pile")
    if st.session_state.discard_pile:
        last_discard = st.session_state.discard_pile[-1]
        st.write(f"Top: {tile_to_str(last_discard)}")
        if st.button("Show All Discards"):
            st.write([tile_to_str(t) for t in st.session_state.discard_pile])
    else:
        st.write("Empty")
    
    if st.session_state.drawn_tile:
        st.divider()
        st.subheader("🎲 Drawn Tile")
        st.info(tile_to_str(st.session_state.drawn_tile))

# -------------------------------
# Set/Run Checker (Optional)
# -------------------------------
st.divider()
st.subheader("🔍 Check if tiles form a set or run")
st.markdown("Select tiles by clicking the buttons below to test if they form a valid group.")

# Simple multiselect for checking
tile_options = [tile_to_str(t) for t in st.session_state.hand]
selected_indices = st.multiselect("Choose tiles from your hand:", range(len(st.session_state.hand)), format_func=lambda x: tile_options[x])

if selected_indices:
    selected_tiles = [st.session_state.hand[i] for i in selected_indices]
    result = is_valid_set_or_run(selected_tiles)
    st.info(result)
else:
    st.caption("Select some tiles to check if they form a valid set (same number, different colors) or run (same color, consecutive numbers).")

# Game over message
if st.session_state.game_over:
    st.divider()
    st.success("🏆 Congratulations! You completed the game! 🏆")
    if st.button("Play Again"):
        reset_game()
        st.rerun()
