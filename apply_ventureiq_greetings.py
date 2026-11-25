from pathlib import Path
import re
import sys

APP = Path('app.py')
if not APP.exists():
    sys.exit('ERROR: app.py was not found. Put this script in the same folder as app.py.')

source = APP.read_text(encoding='utf-8')
original = source

function = '''def ventureiq_greeting_response(message: str):
    """Recognise greetings and polite conversational messages."""

    text = message.lower().strip()
    text = re.sub(r"[^\\w\\s']", "", text)
    text = re.sub(r"\\s+", " ", text)

    greetings = {
        "hi": "Hi! Welcome to VentureIQ. How can I help you today?",
        "hello": "Hello! Great to have you here. What would you like help with?",
        "hey": "Hey! What can I help you work on today?",
        "good morning": "Good morning! Ready to work on your business ideas?",
        "good afternoon": "Good afternoon! How can I help you today?",
        "good evening": "Good evening! What can I help you with?",
        "how are you": "I'm doing well, thanks for asking! How can I help you today?",
        "how are you doing": "I'm doing well, thanks for asking! What can I help you with?",
        "thanks": "You're welcome! Happy to help.",
        "thank you": "You're very welcome! What else can I help you with?",
        "bye": "Goodbye! Thanks for using VentureIQ.",
        "goodbye": "Goodbye! Have a great day!",
    }

    return greetings.get(text)


'''

if 'def ventureiq_greeting_response(message: str):' not in source:
    marker = 'def render_personal_ai_chatbot() -> None:\n'
    if source.count(marker) != 1:
        sys.exit('ERROR: Could not safely find the chatbot function exactly once. No changes were made.')
    source = source.replace(marker, function + marker, 1)

old = '''        if prompt:
            st.session_state.ai_messages.append({"role": "user", "content": prompt})
            if web_search_on:
'''
new = '''        if prompt:
            st.session_state.ai_messages.append({"role": "user", "content": prompt})
            greeting = ventureiq_greeting_response(prompt)
            if greeting:
                st.session_state.ai_messages.append({"role": "assistant", "content": greeting})
            elif web_search_on:
'''
if old in source:
    source = source.replace(old, new, 1)
elif new not in source:
    sys.exit('ERROR: Could not safely find the expected chat-input block. No changes were made.')

# Remove the obsolete unreachable second implementation that follows the active
# search function's RuntimeError. It ends immediately before fetch_page_text.
start = source.find('    """Search several public search backends, without a paid API key."""')
if start != -1:
    end_marker = '\n\n@st.cache_data(ttl=3600, show_spinner=False)\ndef fetch_page_text'
    end = source.find(end_marker, start)
    if end == -1:
        sys.exit('ERROR: Found the old duplicate search block but could not find its end. No changes were made.')
    source = source[:start] + source[end:]

if source == original:
    print('No changes needed: greetings are already integrated and duplicate search code is absent.')
else:
    backup = APP.with_name('app.py.before_greetings_backup')
    if not backup.exists():
        backup.write_text(original, encoding='utf-8')
    APP.write_text(source, encoding='utf-8')
    print('SUCCESS: Greetings integrated. A backup was saved as app.py.before_greetings_backup.')

# Basic syntax check of the resulting app before the user commits it.
import ast
try:
    ast.parse(source)
except SyntaxError as exc:
    APP.write_text(original, encoding='utf-8')
    sys.exit(f'ERROR: Syntax check failed; app.py was restored. {exc}')
print('Python syntax check passed.')
