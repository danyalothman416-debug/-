# --- 16. MAIN APP ---
def main():
    # Apply settings
    apply_language_direction()
    apply_theme()
    
    # Sidebar settings
    with st.sidebar:
        st.markdown("### ⚙️ Settings")
        st.session_state.lang_choice = st.selectbox(
            get_text("settings"),
            options=list(languages.keys()),
            index=list(languages.keys()).index(st.session_state.lang_choice)
        )
        
        st.session_state.theme_choice = st.radio(
            get_text("theme_label"),
            [get_text("light"), get_text("dark")],
            index=0 if st.session_state.theme_choice == "Light ☀️" else 1
        )
        
        admin_login()
        
        if st.session_state.user_email:
            st.markdown("---")
            st.caption(f"👤 {st.session_state.user_name}")
    
    # Main navigation
    selected = option_menu(
        menu_title=None,
        options=[get_text("nav_home"), get_text("nav_order"), get_text("nav_track"), 
                 get_text("nav_profile"), get_text("nav_terms"), get_text("nav_support")],
        icons=["house", "truck", "map", "person", "file-text", "envelope"],
        menu_icon="cast",
        default_index=0,
        orientation="horizontal",
        styles={
            "container": {"padding": "0!important", "background-color": "#fafafa"},
            "icon": {"color": "orange", "font-size": "20px"},
            "nav-link": {"font-size": "16px", "text-align": "center", "margin": "0px"},
            "nav-link-selected": {"background-color": "#ff4b4b"},
        }
    )
    
    # Page routing
    if selected == get_text("nav_home"):
        home_page()
    elif selected == get_text("nav_order"):
        order_page()
    elif selected == get_text("nav_track"):
        track_page()
    elif selected == get_text("nav_profile"):
        profile_page()
    elif selected == get_text("nav_terms"):
        terms_page()
    elif selected == get_text("nav_support"):
        support_page()
    
    # Admin panel (shown at bottom if authenticated)
    if st.session_state.admin_authenticated:
        st.markdown("---")
        admin_panel()

# --- 17. MAIN ENTRY POINT ---
if name == "main":
    main()
