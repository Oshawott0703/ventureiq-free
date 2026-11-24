VentureIQ Free Edition — Web Search Update

Files to upload to the root of your GitHub repository:
- app.py
- product_builder.py
- requirements.txt

What changed:
- Keeps the existing VentureIQ dashboard and content pack tools.
- Adds an optional “Search the web for my next question” switch in the chatbot.
- Uses the ddgs Python package to retrieve public search results without a paid search API key.
- Shows result previews and clickable source links.
- Keeps the built-in rules/templates for normal chat questions.

Important limitations:
- Web search is not the same as an AI language model. This version retrieves search results and previews; it does not reason across webpages like ChatGPT.
- Public search services may rate-limit or change access. Streamlit hosting may also restrict some outbound connections, so test the feature after deployment.
- Search snippets can be incomplete or outdated. Open and check original sources before relying on important information.
- No OpenAI API key or paid AI API is used.

Deployment:
1. Extract this ZIP.
2. Upload/replace app.py, product_builder.py and requirements.txt in your GitHub repository.
3. Commit the changes. Streamlit Community Cloud should reinstall requirements and redeploy.
4. Open VentureIQ, go to Dashboard, switch on “Search the web for my next question”, and try a specific search query.
