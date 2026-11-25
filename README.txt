VENTUREIQ CHATBOT UPDATE KIT

This is an update kit, not a complete replacement project ZIP. It includes:
- apply_chatbot_update.py: safely patches your existing app.py to add greeting recognition before web search and removes the obsolete unreachable duplicate search code.
- product_builder.py: the VentureIQ product-generation module recovered from your previously saved project file.
- requirements.txt: the dependencies you supplied.

HOW TO USE
1. Make a backup copy of your current app.py.
2. Put apply_chatbot_update.py in the same folder as app.py.
3. Run: python apply_chatbot_update.py
4. The script updates app.py in place. Check the changes, then commit app.py to GitHub.
5. Keep product_builder.py and requirements.txt in the same project folder/repository as app.py.

The updater does not require an OpenAI API key or paid AI service. Greetings are matched locally and do not trigger web search.

Recognised messages include: hi, hello, hey, good morning, good afternoon, good evening, how are you, thanks, thank you, bye and goodbye.
