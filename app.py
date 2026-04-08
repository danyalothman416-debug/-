import streamlit as st
import random

# --- ڕێکخستنی سەرەتایی یاری ---
if 'deck' not in st.session_state:
    # دروستکردنی تایلەکان: 1-13 لە 4 ڕەنگ + 2 جۆکەر
    colors = ['🔴 سوور', '⚫ ڕەش', '🔵 شین', '🟡 زەرد']
    st.session_state.deck = [f"{num} {color}" for color in colors for num in range(1, 14)] + ['🌟 جۆکەر', '🌟 جۆکەر']
    random.shuffle(st.session_state.deck)
    
    # دابەشکردنی تایل بەسەر یاریزانان (بۆ نموونە 2 یاریزان)
    st.session_state.player_hand = [st.session_state.deck.pop() for _ in range(14)]
    st.session_state.opponent_hand = [st.session_state.deck.pop() for _ in range(14)]
    st.session_state.discard_pile = [st.session_state.deck.pop()]
    st.session_state.current_player = "تۆ"
    st.session_state.game_over = False

# --- ناونیشانی ئەپەکە ---
st.set_page_config(page_title="KonKan - Kurdish Tile Game", layout="wide")
st.title("🎴 KonKan - یاری تایلی کوردی")
st.caption("وەشانی ستریم لایت - یاری بکە لەگەڵ هاوڕێکانت")

# --- ڕووکاری یاری ---
col1, col2 = st.columns([3, 1])

with col1:
    st.subheader(f"👤 تابلۆی {st.session_state.current_player}")
    st.write("**تایلەکانی تۆ:**")
    
    # نیشاندانی تایلەکانی یاریزانی ئێستا
    cols = st.columns(7)
    for i, tile in enumerate(st.session_state.player_hand):
        with cols[i % 7]:
            if st.button(tile, key=f"tile_{i}"):
                if not st.session_state.game_over:
                    # فڕێدانی تایلی هەڵبژێردراو
                    st.session_state.player_hand.pop(i)
                    st.session_state.discard_pile.append(tile)
                    st.session_state.current_player = "بەرامبەر"
                    st.rerun()
    
    st.divider()
    st.write("**تایلی فڕێدراو:**")
    st.markdown(f"### {st.session_state.discard_pile[-1]}")

with col2:
    st.subheader("📊 دۆخی یاری")
    st.metric("ژمارەی تایلەکان لە عەرزیدا", len(st.session_state.deck))
    st.metric("تایلەکانی بەرامبەر", len(st.session_state.opponent_hand))
    
    if st.session_state.current_player == "بەرامبەر" and not st.session_state.game_over:
        if st.button("🔄 نۆرەی بەرامبەر (هەڵگرتنی تایلی نوێ)"):
            # هەڵگرتنی تایل لە عەرزی یان خڕی فڕێدراو
            if random.choice([True, False]) and len(st.session_state.deck) > 0:
                new_tile = st.session_state.deck.pop()
                st.session_state.opponent_hand.append(new_tile)
                st.toast(f"بەرامبەر تایلی **{new_tile}** ی هەڵگرت")
            else:
                new_tile = st.session_state.discard_pile.pop()
                st.session_state.opponent_hand.append(new_tile)
                st.toast(f"بەرامبەر تایلی **{new_tile}** ی لە خڕی فڕێدراو هەڵگرت")
            
            # فڕێدانی تایلێک لەلایەن بەرامبەر
            discard = random.choice(st.session_state.opponent_hand)
            st.session_state.opponent_hand.remove(discard)
            st.session_state.discard_pile.append(discard)
            st.toast(f"بەرامبەر تایلی **{discard}** ی فڕێدا")
            
            st.session_state.current_player = "تۆ"
            st.rerun()
    
    if st.button("🔄 یاری نوێ", type="primary"):
        for key in ['deck', 'player_hand', 'opponent_hand', 'discard_pile', 'current_player', 'game_over']:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()

# --- دیباگی تایبەت (بۆ بینینی تابلۆی بەرامبەر لەکاتی دیزاین) ---
with st.expander("🔧 ئامرازەکانی گەشەپێدەر"):
    if st.checkbox("نیشاندانی تابلۆی بەرامبەر"):
        st.write("**تایلەکانی بەرامبەر:**", st.session_state.opponent_hand)
    if st.checkbox("نیشاندانی عەرزی"):
        st.write("**تایلەکانی عەرزی:**", st.session_state.deck)
