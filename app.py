import streamlit as st
import random
import time

# ==================== ڕێکخستنی لاپەڕە ====================
st.set_page_config(
    page_title="🎴 KonKan Pro | Kurdish Okey",
    page_icon="🃏",
    layout="wide"
)

# ==================== CSS ی پڕۆفیشناڵ ====================
st.markdown("""
<style>
    /* باکگراوندی سەرەکی وەک مێزی یاری */
    .stApp {
        background: linear-gradient(135deg, #1a472a 0%, #0d2818 100%);
        background-image: radial-gradient(circle at 20% 30%, #2d5a3f 0%, #0a1c11 90%);
    }
    
    /* ناونیشانی سەرەکی */
    .game-title {
        font-size: 3.5rem !important;
        font-weight: 800 !important;
        text-align: center !important;
        background: linear-gradient(135deg, #FFD700, #FFA500, #FFD700);
        -webkit-background-clip: text !important;
        -webkit-text-fill-color: transparent !important;
        text-shadow: 0 4px 15px rgba(0,0,0,0.5);
        margin: 10px 0 20px 0 !important;
        letter-spacing: 3px;
        font-family: 'Segoe UI', 'Helvetica', sans-serif;
    }
    
    /* کۆنتێنەری سەرەکی یاری */
    .game-container {
        max-width: 1400px;
        margin: 0 auto;
        padding: 20px;
    }
    
    /* ناوچەی سەرەوە - عەرزی و خڕی فڕێدراو */
    .top-area {
        display: flex;
        justify-content: center;
        align-items: center;
        gap: 60px;
        padding: 40px 20px;
        background: rgba(0,0,0,0.2);
        border-radius: 30px;
        margin-bottom: 30px;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255,215,0,0.2);
    }
    
    /* کارتی عەرزی */
    .deck-card {
        text-align: center;
        cursor: pointer;
        transition: all 0.3s ease;
        filter: drop-shadow(0 10px 20px rgba(0,0,0,0.5));
    }
    .deck-card:hover {
        transform: translateY(-10px) scale(1.05);
        filter: drop-shadow(0 15px 30px rgba(0,0,0,0.7));
    }
    .deck-card .card-back {
        width: 120px;
        height: 160px;
        background: linear-gradient(145deg, #2c3e50, #1a252f);
        border-radius: 15px;
        border: 3px solid #FFD700;
        box-shadow: 0 8px 0 #0a0e11;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        color: #FFD700;
        font-size: 24px;
        font-weight: bold;
        position: relative;
        overflow: hidden;
    }
    .card-back::before {
        content: "🃏";
        position: absolute;
        font-size: 80px;
        opacity: 0.15;
        transform: rotate(-15deg);
    }
    .deck-count {
        font-size: 32px;
        font-weight: bold;
        color: white;
        text-shadow: 2px 2px 4px black;
        margin-top: 10px;
    }
    
    /* کارتی فڕێدراو */
    .discard-card {
        text-align: center;
    }
    .discard-label {
        color: rgba(255,255,255,0.7);
        font-size: 14px;
        margin-bottom: 10px;
        text-transform: uppercase;
        letter-spacing: 3px;
    }
    
    /* تایلی فڕێدراو - شێوازی تایبەت */
    .discard-tile-display {
        width: 120px;
        height: 160px;
        margin: 0 auto;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        border-radius: 15px;
        font-size: 48px;
        font-weight: bold;
        box-shadow: 0 8px 0 rgba(0,0,0,0.3), 0 15px 30px rgba(0,0,0,0.5);
        border: 3px solid #FFD700;
        transition: all 0.3s ease;
        position: relative;
    }
    .discard-tile-display[data-color="red"] {
        background: linear-gradient(145deg, #ff6b6b, #c0392b);
    }
    .discard-tile-display[data-color="black"] {
        background: linear-gradient(145deg, #555, #222);
    }
    .discard-tile-display[data-color="blue"] {
        background: linear-gradient(145deg, #74b9ff, #0984e3);
    }
    .discard-tile-display[data-color="yellow"] {
        background: linear-gradient(145deg, #ffeaa7, #fdcb6e);
    }
    .discard-tile-display[data-color="joker"] {
        background: linear-gradient(145deg, #fd79a8, #e84393);
    }
    .tile-number {
        font-size: 56px;
        color: white;
        text-shadow: 3px 3px 0 rgba(0,0,0,0.3);
    }
    .tile-symbol {
        font-size: 36px;
    }
    
    /* ناوچەی تابلۆی یاریزان */
    .player-area {
        padding: 30px 20px;
        background: rgba(0,0,0,0.3);
        border-radius: 30px 30px 20px 20px;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255,215,0,0.3);
        margin-top: 20px;
    }
    .player-label {
        color: rgba(255,255,255,0.8);
        font-size: 18px;
        margin-bottom: 20px;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    .player-label span {
        background: #FFD700;
        color: #1a472a;
        padding: 5px 15px;
        border-radius: 20px;
        font-weight: bold;
    }
    
    /* تابلۆی ئاسۆیی */
    .tile-rack {
        display: flex;
        justify-content: center;
        gap: 8px;
        flex-wrap: wrap;
        padding: 20px 0;
    }
    
    /* دوگمەی تایلی تاک */
    div[data-testid="stHorizontalBlock"] div[data-testid="column"] {
        padding: 0 4px !important;
    }
    
    /* ستایلی دوگمەی تایل */
    .stButton > button {
        width: 100px !important;
        height: 140px !important;
        border-radius: 15px !important;
        font-size: 42px !important;
        font-weight: bold !important;
        border: 3px solid #FFD700 !important;
        box-shadow: 0 6px 0 rgba(0,0,0,0.3), 0 8px 15px rgba(0,0,0,0.4) !important;
        transition: all 0.15s ease !important;
        padding: 0 !important;
        margin: 0 !important;
        position: relative;
        color: white !important;
        text-shadow: 2px 2px 0 rgba(0,0,0,0.3) !important;
    }
    .stButton > button:hover {
        transform: translateY(-8px) !important;
        box-shadow: 0 12px 0 rgba(0,0,0,0.3), 0 15px 25px rgba(0,0,0,0.5) !important;
        border-color: #FFA500 !important;
    }
    .stButton > button:active {
        transform: translateY(4px) !important;
        box-shadow: 0 4px 0 rgba(0,0,0,0.3), 0 8px 15px rgba(0,0,0,0.4) !important;
    }
    
    /* ڕەنگەکانی تایل بە پێی جۆر */
    button:has(:contains("🔴")) {
        background: linear-gradient(145deg, #ff7675, #d63031) !important;
    }
    button:has(:contains("⚫")) {
        background: linear-gradient(145deg, #636e72, #2d3436) !important;
    }
    button:has(:contains("🔵")) {
        background: linear-gradient(145deg, #74b9ff, #0984e3) !important;
    }
    button:has(:contains("🟡")) {
        background: linear-gradient(145deg, #ffeaa7, #fdcb6e) !important;
        color: #2d3436 !important;
    }
    button:has(:contains("🌟")) {
        background: linear-gradient(145deg, #fd79a8, #e84393) !important;
    }
    
    /* پانێڵی زانیاری */
    .info-panel {
        background: rgba(0,0,0,0.4);
        border-radius: 50px;
        padding: 15px 30px;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255,215,0,0.3);
        display: inline-block;
        margin-bottom: 20px;
    }
    .info-text {
        color: #FFD700;
        font-size: 18px;
        margin: 0;
    }
    
    /* ستایلی دوگمەکانی کردار */
    .action-button {
        text-align: center;
    }
    
    /* سایدبار */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0d2818 0%, #1a472a 100%);
        border-right: 2px solid #FFD700;
    }
    section[data-testid="stSidebar"] * {
        color: white !important;
    }
    
    /* دوگمەی سەرەکی */
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #FFD700, #FFA500) !important;
        color: #1a472a !important;
        font-weight: bold !important;
        font-size: 18px !important;
        border: none !important;
        box-shadow: 0 5px 0 #b8860b, 0 8px 15px rgba(0,0,0,0.3) !important;
    }
    .stButton > button[kind="primary"]:hover {
        transform: translateY(-3px) !important;
        box-shadow: 0 8px 0 #b8860b, 0 12px 20px rgba(0,0,0,0.4) !important;
    }
    
    /* هۆشداری */
    .stAlert {
        background: rgba(0,0,0,0.5) !important;
        backdrop-filter: blur(10px);
        border: 1px solid #FFD700 !important;
        color: white !important;
        border-radius: 15px !important;
    }
</style>
""", unsafe_allow_html=True)

# ==================== فەنکشنی یارمەتیدەر بۆ ڕەنگی تایل ====================
def get_tile_color(tile):
    if '🔴' in tile:
        return 'red'
    elif '⚫' in tile:
        return 'black'
    elif '🔵' in tile:
        return 'blue'
    elif '🟡' in tile:
        return 'yellow'
    elif '🌟' in tile:
        return 'joker'
    return 'default'

def format_tile_display(tile):
    """جیاکردنەوەی ئیمۆجی و ژمارە بۆ نمایشی جوانتر"""
    if '🌟' in tile:
        return '🌟', 'جۆکەر'
    parts = tile.split()
    if len(parts) == 2:
        return parts[0], parts[1]
    return '', tile

# ==================== سەرەتاکردنی یاری ====================
def init_game():
    colors = ['🔴', '⚫', '🔵', '🟡']
    numbers = list(range(1, 14))
    
    # 106 تایل (2 پاکەت)
    deck = []
    for _ in range(2):
        for color in colors:
            for num in numbers:
                deck.append(f"{color}{num}")
    deck.extend(['🌟جۆکەر'] * 4)
    
    random.shuffle(deck)
    
    player_hand = sorted([deck.pop() for _ in range(14)], 
                        key=lambda x: (x[1:] if x[0] in ['🔴','⚫','🔵','🟡'] else '99', x))
    bot_hand = [deck.pop() for _ in range(14)]
    
    return {
        'deck': deck,
        'player_hand': player_hand,
        'bot_hand': bot_hand,
        'discard_pile': [deck.pop()],
        'turn': 'player',
        'game_over': False,
        'winner': None,
        'last_action': '🎮 یاری دەستی پێکرد!',
        'selected_tile': None
    }

# ==================== هۆشمەندی ڕۆبۆت ====================
def bot_play():
    time.sleep(1.2)
    
    if random.random() < 0.65 and st.session_state.deck:
        new_tile = st.session_state.deck.pop()
        st.session_state.last_action = f"🤖 ڕۆبۆت تایلی **{new_tile}** ی لە عەرزی هەڵگرت"
    else:
        new_tile = st.session_state.discard_pile.pop()
        st.session_state.last_action = f"🤖 ڕۆبۆت تایلی **{new_tile}** ی لە خڕی فڕێدراو هەڵگرت"
    
    st.session_state.bot_hand.append(new_tile)
    
    if '🌟' in ''.join(st.session_state.bot_hand):
        non_jokers = [t for t in st.session_state.bot_hand if '🌟' not in t]
        discard = random.choice(non_jokers) if non_jokers else random.choice(st.session_state.bot_hand)
    else:
        discard = random.choice(st.session_state.bot_hand)
    
    st.session_state.bot_hand.remove(discard)
    st.session_state.discard_pile.append(discard)
    st.session_state.last_action += f" و تایلی **{discard}** ی فڕێدا"
    
    if len(st.session_state.bot_hand) == 1:
        st.session_state.game_over = True
        st.session_state.winner = '🤖 ڕۆبۆت'
        st.session_state.last_action = "🏆 ڕۆبۆت یارییەکەی بردەوە!"
    
    st.session_state.turn = 'player'

# ==================== دەستپێکردنی سێشن ====================
if 'game_state' not in st.session_state:
    st.session_state.update(init_game())

# ==================== ناونیشان ====================
st.markdown('<div class="game-title">🎮 KONKAN PRO</div>', unsafe_allow_html=True)
st.markdown('<p style="text-align:center; color:#aaa; margin-top:-10px;">یاری تایلی کوردی</p>', unsafe_allow_html=True)

# ==================== کۆنتێنەری سەرەکی ====================
st.markdown('<div class="game-container">', unsafe_allow_html=True)

# ==================== ناوچەی سەرەوە - عەرزی و فڕێدراو ====================
col_left, col_center, col_right = st.columns([2, 3, 2])

with col_left:
    st.markdown("""
    <div style="text-align:center;">
        <div style="color:#FFD700; font-size:14px; letter-spacing:2px; margin-bottom:10px;">🎯 عەرزی</div>
    </div>
    """, unsafe_allow_html=True)
    
    if st.session_state.deck:
        if st.button(f"🃏\n\n{len(st.session_state.deck)} تایل", key="deck_draw", use_container_width=True):
            if st.session_state.turn == 'player' and not st.session_state.game_over:
                new_tile = st.session_state.deck.pop()
                st.session_state.player_hand.append(new_tile)
                st.session_state.last_action = f"👤 تۆ تایلی **{new_tile}** ت لە عەرزی هەڵگرت"
                st.rerun()

with col_center:
    st.markdown("""
    <div style="text-align:center;">
        <div style="color:#FFD700; font-size:14px; letter-spacing:2px; margin-bottom:10px;">🗑️ خڕی فڕێدراو</div>
    </div>
    """, unsafe_allow_html=True)
    
    if st.session_state.discard_pile:
        discard_tile = st.session_state.discard_pile[-1]
        tile_color = get_tile_color(discard_tile)
        symbol, number = format_tile_display(discard_tile)
        
        st.markdown(f"""
        <div class="discard-tile-display" data-color="{tile_color}">
            <div class="tile-symbol">{symbol}</div>
            <div class="tile-number">{number}</div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("📥 هەڵگرتن", key="pickup_discard", use_container_width=True):
            if st.session_state.turn == 'player' and not st.session_state.game_over:
                st.session_state.player_hand.append(st.session_state.discard_pile.pop())
                st.session_state.last_action = f"👤 تۆ تایلی **{st.session_state.player_hand[-1]}** ت هەڵگرت"
                st.rerun()

with col_right:
    st.markdown("""
    <div style="text-align:center;">
        <div style="color:#FFD700; font-size:14px; letter-spacing:2px; margin-bottom:10px;">🤖 ڕۆبۆت</div>
        <div style="background:rgba(0,0,0,0.3); border-radius:15px; padding:20px;">
            <div style="font-size:48px;">🤖</div>
            <div style="font-size:24px; color:white;">{}</div>
            <div style="color:#aaa; font-size:14px;">تایل</div>
        </div>
    </div>
    """.format(len(st.session_state.bot_hand)), unsafe_allow_html=True)

# ==================== پانێڵی زانیاری ====================
st.markdown(f"""
<div class="info-panel">
    <p class="info-text">💬 {st.session_state.last_action}</p>
</div>
""", unsafe_allow_html=True)

# ==================== ناوچەی تابلۆی یاریزان (خوارەوە) ====================
st.markdown("""
<div class="player-area">
    <div class="player-label">
        <span>👤 تابلۆی تۆ</span> 
        <span style="background:transparent; color:#FFD700;">{}</span>
    </div>
""".format(f"{len(st.session_state.player_hand)} تایل"), unsafe_allow_html=True)

# ==================== تابلۆی ئاسۆیی - دوو ڕیز ====================
if st.session_state.player_hand:
    sorted_hand = sorted(st.session_state.player_hand, 
                        key=lambda x: (x[1:] if len(x)>1 and x[0] in ['🔴','⚫','🔵','🟡'] else '99', x))
    
    # دابەشکردن بۆ دوو ڕیز ئەگەر زیاتر لە 7 تایل هەبێت
    if len(sorted_hand) > 7:
        mid = len(sorted_hand) // 2
        row1 = sorted_hand[:mid]
        row2 = sorted_hand[mid:]
        
        for row in [row1, row2]:
            cols = st.columns(len(row))
            for i, tile in enumerate(row):
                with cols[i]:
                    if st.button(tile, key=f"tile_{i}_{tile}_{random.randint(0,9999)}", use_container_width=True):
                        if st.session_state.turn == 'player' and not st.session_state.game_over:
                            st.session_state.player_hand.remove(tile)
                            st.session_state.discard_pile.append(tile)
                            st.session_state.last_action = f"👤 تۆ تایلی **{tile}** ت فڕێدا"
                            
                            if len(st.session_state.player_hand) == 1:
                                st.session_state.game_over = True
                                st.session_state.winner = '👤 تۆ'
                                st.session_state.last_action = "🎉 تۆ یارییەکەت بردەوە! پیرۆزە!"
                            else:
                                st.session_state.turn = 'bot'
                            
                            st.rerun()
    else:
        cols = st.columns(len(sorted_hand))
        for i, tile in enumerate(sorted_hand):
            with cols[i]:
                if st.button(tile, key=f"tile_{i}_{tile}", use_container_width=True):
                    if st.session_state.turn == 'player' and not st.session_state.game_over:
                        st.session_state.player_hand.remove(tile)
                        st.session_state.discard_pile.append(tile)
                        st.session_state.last_action = f"👤 تۆ تایلی **{tile}** ت فڕێدا"
                        
                        if len(st.session_state.player_hand) == 1:
                            st.session_state.game_over = True
                            st.session_state.winner = '👤 تۆ'
                            st.session_state.last_action = "🎉 تۆ یارییەکەت بردەوە! پیرۆزە!"
                        else:
                            st.session_state.turn = 'bot'
                        
                        st.rerun()

st.markdown('</div>', unsafe_allow_html=True)

# ==================== نۆرەی ڕۆبۆت ====================
if st.session_state.turn == 'bot' and not st.session_state.game_over:
    with st.spinner("🤖 ڕۆبۆت بیردەکاتەوە..."):
        bot_play()
    st.rerun()

# ==================== کۆتایی یاری ====================
if st.session_state.game_over:
    st.markdown('</div>', unsafe_allow_html=True)  # داخستنی game-container
    st.balloons()
    st.success(f"## 🏆 {st.session_state.winner} یارییەکەی بردەوە!")
    
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        if st.button("🔄 یاری نوێ", type="primary", use_container_width=True):
            for key in list(st.session_state.keys()):
                if key != 'game_state':
                    del st.session_state[key]
            st.session_state.update(init_game())
            st.rerun()
else:
    st.markdown('</div>', unsafe_allow_html=True)

# ==================== سایدبار ====================
with st.sidebar:
    st.markdown("## 🎮 KonKan Pro")
    st.markdown("---")
    
    st.markdown("### 📜 ڕێساکان")
    st.markdown("""
    - **14 تایل** بۆ هەر یاریزان
    - تایل هەڵبگرە لە **عەرزی** یان **خڕی فڕێدراو**
    - تایلێک **فڕێبدە** بۆ کۆتایی نۆرە
    - براوە: یەکەم کەس کە **1 تایل**ی مابێت
    """)
    
    st.markdown("---")
    st.markdown("### 🎯 ئامار")
    st.metric("عەرزی", len(st.session_state.deck))
    st.metric("تایلەکانی ڕۆبۆت", len(st.session_state.bot_hand))
    st.metric("تایلەکانی تۆ", len(st.session_state.player_hand))
    
    st.markdown("---")
    if st.button("🔄 دەستپێکردنەوە", use_container_width=True):
        for key in list(st.session_state.keys()):
            if key != 'game_state':
                del st.session_state[key]
        st.session_state.update(init_game())
        st.rerun()
    
    st.markdown("---")
    st.markdown("### 🔧 ڕێکخستن")
    with st.expander("پەرەپێدەر"):
        if st.checkbox("نیشاندانی تابلۆی ڕۆبۆت"):
            st.write(st.session_state.bot_hand)
