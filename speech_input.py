"""
Speech-to-Text Input for Streamlit
====================================
Uses st.components.v1.html() with browser's Web Speech API.
Works on Streamlit Cloud (HTTPS) in Chrome/Edge/Safari.
Returns transcript by directly updating the parent text area via DOM.
"""
import streamlit.components.v1 as components


def speech_to_text_button(reset_key=0):
    """
    Renders a speech-to-text microphone button.
    When the user speaks, the recognized text is automatically
    inserted into the nearest Streamlit text area above via DOM manipulation.
    Also copies the transcript to clipboard as a fallback.
    reset_key: change this value to force the component to re-render fresh.
    """
    # Use string concatenation instead of f-string to avoid CSS/JS brace conflicts
    speech_html = "<!-- reset:" + str(reset_