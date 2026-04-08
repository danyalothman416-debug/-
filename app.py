import streamlit as st
import random
import time

# ==================== ڕێکخستنی لاپەڕە ====================
st.set_page_config(
    page_title="🎴 KonKan - Kurdish Tile Game",
    page_icon="🎲",
    layout="wide"
)

# ==================== CSS بۆ جوانکاری ====================
st.markdown("""
<style>
    .tile-button {
        font-size: 24px !important;
        padding: 20px !important;
        border-radius: 15px !important;
        background: linear-gradient(145deg, #2d2d2d, #1a1a1a) !important;
        color: white !important;
        border: 2px solid gold !important;
        box-shadow: 0 4px 8px rgba(0,0,0,0.3) !important;
        transition: all 0.2s !important;
        width: 100% !important;
        height: 100px !important;
        font-weight: bold !important;
    }
    .tile-button:hover {
        transform: translateY(-5px) !important;
        box-shadow: 0 8px 16px rgba(0,0,0,0.4) !important;
        border-color: #ffd700 !important;
    }
    .discard-tile {
        font-size: 48px !important;
        padding: 30px !important;
        background: linear-gradient(145deg, #3d1a1a, #2d0a0a) !important;
        border-radius: 20px !important;
        text-align: center !important;
        border: 3px solid #ff4444 !important;
        color: white !important;
    }
    .bot-thinking {
        font-size: 20px !important;
        color: #888 !important;
        animation: pulse 1.5s infinite;
    }
    @keyframes pulse {
        0% { opacity: 0.5; }
        50% { opacity: 1; }
        100% { opacity: 0.5; }
    }
    .game-title {
        font-size: 48px !important;
        font-weight: bold !important;
        text-align: center !important;
        background: linear-gradient(45deg, gold, orange);
        -webkit-background-clip: text !important;
        -webkit-text-fill-color: transparent !important;
        margin-bottom: 30px !important;
    }
</style>
""", unsafe_allow_html=True)

# ==================== سەرەتاکردنی یاری ====================
def init_game():
    """دەستپێکردنەوەی یاری نوێ"""
    colors = ['🔴', '⚫', '🔵', '🟡']
    numbers = list(range(1, 14))
    
    # دروستکردنی 106 تایل (2 پاکەتی 53 تایلی)
    deck = []
    for _ in range(2):  # دوو پاکەت
        for color in colors:
            for num in numbers:
                deck.append(f"{color} {num}")
    deck.extend(['🌟 جۆکەر'] * 4)  # 4 جۆکەر
    
    random.shuffle(deck)
    
    # دابەشکردنی 14 تایل بۆ هەر یاریزانێک
    player_hand = sorted([deck.pop() for _ in range(14)], key=lambda x: (x.split()[-1] if 'جۆکەر' not in x else '99', x))
    bot_hand = [deck.pop() for _ in range(14)]
    
    return {
        'deck': deck,
        'player_hand': player_hand,
        'bot_hand': bot_hand,
        'discard_pile': [deck.pop()],
        'turn': 'player',  # 'player' یان 'bot'
        'game_over': False,
        'winner': None,
        'last_action': '🎮 یاری دەست پێکرد!'
    }

# ==================== هۆشمەندی ڕۆبۆت ====================
def bot_play():
    """ڕۆبۆت بڕیار دەدات چی بکات"""
    time.sleep(1.5)  # وا دەکات ڕۆبۆت بیربکاتەوە
    
    # هەڵگرتنی تایل (70% لە عەرزی، 30% لە خڕی فڕێدراو)
    if random.random() < 0.7 and st.session_state.deck:
        new_tile = st.session_state.deck.pop()
        st.session_state.last_action = f"🤖 ڕۆبۆت تایلی **{new_tile}** ی لە عەرزی هەڵگرت"
    else:
        new_tile = st.session_state.discard_pile.pop()
        st.session_state.last_action = f"🤖 ڕۆبۆت تایلی **{new_tile}** ی لە خڕی فڕێدراو هەڵگرت"
    
    st.session_state.bot_hand.append(new_tile)
    
    # هەڵبژاردنی تایلێک بۆ فڕێدان (زیرەکانە)
    if '🌟 جۆکەر' in st.session_state.bot_hand:
        # هەوڵدەدات جۆکەر هەڵنەگرێت
        non_jokers = [t for t in st.session_state.bot_hand if 'جۆکەر' not in t]
        discard = random.choice(non_jokers) if non_jokers else random.choice(st.session_state.bot_hand)
    else:
        discard = random.choice(st.session_state.bot_hand)
    
    st.session_state.bot_hand.remove(discard)
    st.session_state.discard_pile.append(discard)
    st.session_state.last_action += f"\n🤖 ڕۆبۆت تایلی **{discard}** ی فڕێدا"
    
    # پشکنینی بردنەوە (ئەگەر تەنها یەک تایل مابێت)
    if len(st.session_state.bot_hand) == 1:
        st.session_state.game_over = True
        st.session_state.winner = '🤖 ڕۆبۆت'
        st.session_state.last_action = "🏆 ڕۆبۆت یارییەکەی بردەوە!"
    
    st.session_state.turn = 'player'

# ==================== دەستپێکردنی سێشن ====================
if 'game_state' not in st.session_state:
    st.session_state.update(init_game())

# ==================== ناونیشانی سەرەکی ====================
st.markdown('<div class="game-title">🎴 KonKan - یاری تایلی کوردی</div>', unsafe_allow_html=True)

# ==================== پانێڵی زانیاری ====================
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("🎯 عەرزی", len(st.session_state.deck))
with col2:
    st.metric("🗑️ خڕی فڕێدراو", len(st.session_state.discard_pile))
with col3:
    st.metric("🤖 تایلەکانی ڕۆبۆت", len(st.session_state.bot_hand))
with col4:
    st.metric("👤 تایلەکانی تۆ", len(st.session_state.player_hand))

st.info(st.session_state.last_action)

# ==================== تایلی فڕێدراو ====================
st.markdown("---")
st.markdown("### 🗑️ تایلی فڕێدراو (دەتوانیت هەڵیگریت)")
if st.session_state.discard_pile:
    discard_tile = st.session_state.discard_pile[-1]
    st.markdown(f'<div class="discard-tile">{discard_tile}</div>', unsafe_allow_html=True)
    
    # دوگمەی هەڵگرتنی تایلی فڕێدراو
    if st.session_state.turn == 'player' and not st.session_state.game_over:
        if st.button("📥 هەڵگرتنی تایلی فڕێدراو", type="primary", use_container_width=True):
            st.session_state.player_hand.append(st.session_state.discard_pile.pop())
            st.session_state.last_action = f"👤 تۆ تایلی **{st.session_state.player_hand[-1]}** ت هەڵگرت"
            st.rerun()

# ==================== دوگمەی عەرزی ====================
if st.session_state.turn == 'player' and not st.session_state.game_over:
    if st.button("🎲 هەڵگرتنی تایل لە عەرزی", type="secondary", use_container_width=True):
        if st.session_state.deck:
            new_tile = st.session_state.deck.pop()
            st.session_state.player_hand.append(new_tile)
            st.session_state.last_action = f"👤 تۆ تایلی **{new_tile}** ت لە عەرزی هەڵگرت"
        st.rerun()

# ==================== تابلۆی یاریزان ====================
st.markdown("---")
st.markdown("### 👤 تایلەکانی تۆ (کلیک بکە بۆ فڕێدان)")

if st.session_state.player_hand:
    cols = st.columns(7)
    for i, tile in enumerate(sorted(st.session_state.player_hand, key=lambda x: (x.split()[-1] if 'جۆکەر' not in x else '99', x))):
        with cols[i % 7]:
            if st.button(tile, key=f"tile_{i}_{tile}", use_container_width=True):
                if st.session_state.turn == 'player' and not st.session_state.game_over:
                    st.session_state.player_hand.remove(tile)
                    st.session_state.discard_pile.append(tile)
                    st.session_state.last_action = f"👤 تۆ تایلی **{tile}** ت فڕێدا"
                    
                    # پشکنینی بردنەوە
                    if len(st.session_state.player_hand) == 1:
                        st.session_state.game_over = True
                        st.session_state.winner = '👤 تۆ'
                        st.session_state.last_action = "🎉 تۆ یارییەکەت بردەوە! پیرۆزە!"
                    else:
                        st.session_state.turn = 'bot'
                    
                    st.rerun()

# ==================== نۆرەی ڕۆبۆت ====================
if st.session_state.turn == 'bot' and not st.session_state.game_over:
    with st.spinner("🤖 ڕۆبۆت بیردەکاتەوە..."):
        bot_play()
    st.rerun()

# ==================== پانێڵی کۆتایی یاری ====================
if st.session_state.game_over:
    st.markdown("---")
    st.balloons()
    st.success(f"## 🏆 {st.session_state.winner} یارییەکەی بردەوە!")
    if st.button("🔄 یاری نوێ", type="primary", use_container_width=True):
        for key in list(st.session_state.keys()):
            if key != 'game_state':
                del st.session_state[key]
        st.session_state.update(init_game())
        st.rerun()

# ==================== سایدبار - زانیاری یاری ====================
with st.sidebar:
    st.markdown("## 📜 ڕێساکانی یاری")
    st.markdown("""
    - **14 تایل** بۆ هەر یاریزانێک
    - یاریزانان بە نۆرە تایل **هەڵدەگرن** و **فڕێدەدەن**
    - براوە یەکەم کەسە کە تەنها **1 تایل**ی بۆ بمێنێت
    """)
    
    st.markdown("---")
    st.markdown("## 🎮 کۆنترۆڵ")
    
    if st.button("🔄 دەستپێکردنەوەی یاری", use_container_width=True):
        for key in list(st.session_state.keys()):
            if key != 'game_state':
                del st.session_state[key]
        st.session_state.update(init_game())
        st.rerun()
    
    # دیباگ مۆد (بۆ پەرەپێدەر)
    st.markdown("---")
    with st.expander("🔧 ئامرازەکانی گەشەپێدەر"):
        if st.checkbox("نیشاندانی تابلۆی ڕۆبۆت"):
            st.write("**تایلەکانی ڕۆبۆت:**")
            for tile in st.session_state.bot_hand:
                st.write(f"- {tile}")
