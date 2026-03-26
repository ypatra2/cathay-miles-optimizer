"""
Speech-to-Text Input for Streamlit
====================================
Uses st.components.v1.html() with browser's Web Speech API.
Works on Streamlit Cloud (HTTPS) in Chrome/Edge/Safari.
Returns transcript by directly updating the parent text area via DOM.
"""
import streamlit.components.v1 as components


def speech_to_text_button():
    """
    Renders a speech-to-text microphone button.
    When the user speaks, the recognized text is automatically
    inserted into the nearest Streamlit text area above via DOM manipulation.
    Also copies the transcript to clipboard as a fallback.
    """
    speech_html = """
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { background: transparent; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; }
        .speech-container { display: flex; flex-direction: column; gap: 6px; }
        .mic-btn {
            display: flex; align-items: center; gap: 8px;
            padding: 10px 20px; width: 100%; justify-content: center;
            border: 1px solid rgba(0, 178, 169, 0.4);
            border-radius: 10px;
            background: rgba(0, 178, 169, 0.1);
            color: #e2e8f0; font-size: 14px; font-weight: 600;
            cursor: pointer; transition: all 0.2s ease;
        }
        .mic-btn:hover {
            background: rgba(0, 178, 169, 0.2);
            border-color: rgba(0, 178, 169, 0.6);
            transform: translateY(-1px);
        }
        .mic-btn.listening {
            background: rgba(239, 68, 68, 0.2);
            border-color: rgba(239, 68, 68, 0.5);
            animation: pulse 1.5s infinite;
        }
        .mic-btn.unsupported { opacity: 0.4; cursor: not-allowed; }
        @keyframes pulse {
            0%, 100% { box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.3); }
            50% { box-shadow: 0 0 0 8px rgba(239, 68, 68, 0); }
        }
        .status-text { font-size: 12px; color: #94a3b8; min-height: 18px; }
        .transcript-box {
            background: rgba(0, 178, 169, 0.08);
            border: 1px solid rgba(0, 178, 169, 0.2);
            border-radius: 8px; padding: 8px 12px;
            color: #e2e8f0; font-size: 13px;
            display: none;
        }
        .transcript-box.visible { display: block; }
    </style>
    <div class="speech-container">
        <button class="mic-btn" id="micBtn" onclick="toggleListening()">
            <span id="micIcon">🎤</span>
            <span id="micLabel">Tap to Speak</span>
        </button>
        <div class="status-text" id="statusText"></div>
        <div class="transcript-box" id="transcriptBox"></div>
    </div>
    <script>
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        let recognition = null;
        let isListening = false;
        const btn = document.getElementById('micBtn');
        const icon = document.getElementById('micIcon');
        const label = document.getElementById('micLabel');
        const status = document.getElementById('statusText');
        const transcriptBox = document.getElementById('transcriptBox');

        if (!SpeechRecognition) {
            btn.classList.add('unsupported');
            label.textContent = 'Speech not supported';
            status.textContent = 'Use Chrome, Edge, or Safari for voice input';
        } else {
            recognition = new SpeechRecognition();
            recognition.continuous = false;
            recognition.interimResults = false;
            recognition.lang = 'en-US';

            recognition.onresult = function(event) {
                const transcript = event.results[0][0].transcript;
                stopListening();
                transcriptBox.textContent = '🗣️ "' + transcript + '"';
                transcriptBox.classList.add('visible');

                // Try to insert into the Streamlit text area via parent DOM
                try {
                    const textareas = window.parent.document.querySelectorAll('textarea');
                    if (textareas.length > 0) {
                        // Find the context textarea (usually the last one or one with specific placeholder)
                        let targetTA = null;
                        textareas.forEach(function(ta) {
                            if (ta.placeholder && ta.placeholder.toLowerCase().includes('describe')) {
                                targetTA = ta;
                            }
                        });
                        if (!targetTA) targetTA = textareas[textareas.length - 1];

                        // Append transcript
                        const separator = targetTA.value.trim() ? '. ' : '';
                        const nativeInputValueSetter = Object.getOwnPropertyDescriptor(
                            window.parent.HTMLTextAreaElement.prototype, 'value'
                        ).set;
                        nativeInputValueSetter.call(targetTA, targetTA.value + separator + transcript);
                        targetTA.dispatchEvent(new window.parent.Event('input', { bubbles: true }));
                        status.textContent = '✅ Inserted into text field!';
                    }
                } catch(e) {
                    // Fallback: copy to clipboard
                    try {
                        navigator.clipboard.writeText(transcript);
                        status.textContent = '📋 Copied to clipboard! Paste into the text field.';
                    } catch(e2) {
                        status.textContent = '👆 Copy the text above and paste into the field.';
                    }
                }
            };

            recognition.onerror = function(event) {
                stopListening();
                if (event.error === 'not-allowed') {
                    status.textContent = '⚠️ Microphone access denied. Check browser permissions.';
                } else {
                    status.textContent = '⚠️ Error: ' + event.error;
                }
            };

            recognition.onend = function() {
                if (isListening) stopListening();
            };
        }

        function toggleListening() {
            if (!recognition) return;
            if (isListening) { recognition.stop(); stopListening(); }
            else { startListening(); }
        }

        function startListening() {
            isListening = true;
            btn.classList.add('listening');
            icon.textContent = '⏹️';
            label.textContent = 'Listening...';
            status.textContent = 'Speak now — describe your transaction';
            transcriptBox.classList.remove('visible');
            recognition.start();
        }

        function stopListening() {
            isListening = false;
            btn.classList.remove('listening');
            icon.textContent = '🎤';
            label.textContent = 'Tap to Speak';
        }
    </script>
    """
    components.html(speech_html, height=120)
