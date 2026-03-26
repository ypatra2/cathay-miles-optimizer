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
    speech_html = "<!-- reset:" + str(reset_key) + """ -->
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
        .interim { opacity: 0.6; font-style: italic; }
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
        let hasInserted = false;
        let originalTextAreaValue = '';

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
            recognition.interimResults = true;
            recognition.lang = 'en-US';

            recognition.onresult = function(event) {
                let finalTranscript = '';
                let interimTranscript = '';

                for (let i = event.resultIndex; i < event.results.length; i++) {
                    const text = event.results[i][0].transcript;
                    if (event.results[i].isFinal) {
                        finalTranscript += text;
                    } else {
                        interimTranscript += text;
                    }
                }

                if (finalTranscript) {
                    transcriptBox.innerHTML = '🗣️ "' + finalTranscript + '"';
                } else if (interimTranscript) {
                    transcriptBox.innerHTML = '🗣️ <span class="interim">' + interimTranscript + '...</span>';
                }
                transcriptBox.classList.add('visible');

                if (finalTranscript && !hasInserted) {
                    hasInserted = true;
                    insertIntoTextArea(finalTranscript);
                    stopListening();
                }
            };

            recognition.onerror = function(event) {
                stopListening();
                if (event.error === 'not-allowed') {
                    status.textContent = '⚠️ Microphone access denied. Check browser permissions.';
                } else if (event.error === 'no-speech') {
                    status.textContent = '⚠️ No speech detected. Try again.';
                } else {
                    status.textContent = '⚠️ Error: ' + event.error;
                }
            };

            recognition.onend = function() {
                if (isListening) stopListening();
            };
        }

        function insertIntoTextArea(transcript) {
            try {
                const textareas = window.parent.document.querySelectorAll('textarea');
                if (textareas.length > 0) {
                    let targetTA = null;
                    textareas.forEach(function(ta) {
                        if (ta.placeholder && ta.placeholder.toLowerCase().includes('describe')) {
                            targetTA = ta;
                        }
                    });
                    if (!targetTA) targetTA = textareas[textareas.length - 1];

                    const separator = originalTextAreaValue.trim() ? '. ' : '';
                    const newValue = originalTextAreaValue + separator + transcript;

                    const nativeInputValueSetter = Object.getOwnPropertyDescriptor(
                        window.parent.HTMLTextAreaElement.prototype, 'value'
                    ).set;
                    nativeInputValueSetter.call(targetTA, newValue);
                    targetTA.dispatchEvent(new window.parent.Event('input', { bubbles: true }));
                    status.textContent = '✅ Inserted into text field!';
                }
            } catch(e) {
                try {
                    navigator.clipboard.writeText(transcript);
                    status.textContent = '📋 Copied to clipboard! Paste into the text field.';
                } catch(e2) {
                    status.textContent = '👆 Copy the text above and paste into the field.';
                }
            }
        }

        function toggleListening() {
            if (!recognition) return;
            if (isListening) { recognition.stop(); stopListening(); }
            else { startListening(); }
        }

        function startListening() {
            isListening = true;
            hasInserted = false;
            btn.classList.add('listening');
            icon.textContent = '⏹️';
            label.textContent = 'Listening...';
            status.textContent = 'Speak now — describe your transaction';
            transcriptBox.classList.remove('visible');

            try {
                const textareas = window.parent.document.querySelectorAll('textarea');
                let targetTA = null;
                textareas.forEach(function(ta) {
                    if (ta.placeholder && ta.placeholder.toLowerCase().includes('describe')) {
                        targetTA = ta;
                    }
                });
                if (!targetTA && textareas.length > 0) targetTA = textareas[textareas.length - 1];
                originalTextAreaValue = targetTA ? targetTA.value : '';
            } catch(e) {
                originalTextAreaValue = '';
            }

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
