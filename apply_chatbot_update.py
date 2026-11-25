from pathlib import Path
import re

APP = Path('app.py')
if not APP.exists():
    raise SystemExit('Could not find app.py. Put this script in the same folder as app.py and run it there.')

source = APP.read_text(encoding='utf-8')

helper = '''def ventureiq_greeting_response(message: str):
    """Return a polite local response for common greetings and courtesies."""
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

if 'def ventureiq_greeting_response(' not in source:
    marker = 'def render_personal_ai_chatbot() -> None:'
    if marker not in source:
        raise SystemExit('Could not find render_personal_ai_chatbot() in app.py; no changes made.')
    source = source.replace(marker, helper + marker, 1)

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
elif 'greeting = ventureiq_greeting_response(prompt)' not in source:
    raise SystemExit('Could not find the expected chatbot prompt block; no changes made.')

# Remove the obsolete, unreachable duplicate search implementation left after the current function's raise.
source = re.sub(
    r'\n    """Search several public search backends, without a paid API key\.""".*?(?=\n\n@st\.cache_data\(ttl=3600)',
    '', source, count=1, flags=re.S
)

APP.write_text(source, encoding='utf-8')
print('Updated app.py successfully. Greetings are now handled locally before web search.')
