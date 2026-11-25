VENTUREIQ GREETINGS UPDATE

This is a small update kit for your existing VentureIQ project, not a complete replacement project.

WHAT IT DOES
- Adds your 12 exact greeting and polite-message responses.
- Checks greetings before web search, so messages such as "Hi" do not trigger a search.
- Removes the obsolete unreachable duplicate web-search code in your current app.py.
- Keeps the rest of your existing app.py unchanged.

HOW TO APPLY IT (WINDOWS)
1. Download and extract this ZIP.
2. Copy apply_ventureiq_greetings.py into the same folder as your existing app.py.
3. Open that folder in File Explorer.
4. Click the address bar, type cmd, and press Enter.
5. In the Command Prompt window, run:
       python apply_ventureiq_greetings.py
6. The script creates app.py.before_greetings_backup, updates app.py, and checks Python syntax.
7. Open the app locally or commit the updated app.py to your GitHub repository so Streamlit Cloud deploys it.

Keep product_builder.py and requirements.txt in your project folder. The copies in this ZIP are included for reference and are not intended to overwrite newer versions unless you need them.

If the script reports an error, do not delete your original app.py. The script is designed to stop rather than guess when it cannot safely identify the expected code.
