"""
Speech-to-Text Custom Streamlit Component
==========================================
Uses the browser's built-in Web Speech API (Chrome/Edge/Safari).
Returns recognized text to Streamlit via declare_component.
No external dependencies required.
"""
import os
import streamlit.components.v1 as components

# Point to the directory containing index.html
_COMPONENT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "speech_component")

_speech_component = components.declare_component(
    "speech_to_text",
    path=_COMPONENT_DIR
)


def speech_to_text_button(key=None):
    """
    Renders a speech-to-text button. Returns the recognized text string
    when the user finishes speaking, or None if no speech captured yet.
    """
    result = _speech_component(key=key, default=None)
    return result
