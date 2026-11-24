VentureIQ Free Edition — Web Overview Update

Upload these files to the root of your GitHub repository:
- app.py
- product_builder.py
- requirements.txt

What changed:
- Web search now attempts to open and read the returned public webpages.
- VentureIQ creates an on-page overview with key extracted points.
- Source links are kept in a collapsed Sources section beneath the overview.
- Search remains optional and does not require an OpenAI API key or paid AI API.

Important limitations:
- This is an automated extractive summary, not a generative AI model. It selects relevant sentences from readable webpage text.
- Some websites block automated access, require JavaScript, or expose only part of their content. If that happens, VentureIQ falls back to the search preview or explains that it could not create an overview.
- Always check source dates and original context for important decisions. Search services and websites may rate-limit or change access.

Deployment:
1. Extract this ZIP.
2. Replace app.py, product_builder.py and requirements.txt in your GitHub repository.
3. Commit the changes and allow Streamlit Community Cloud to redeploy.
4. Enable “Search the web for my next question” and ask a specific question.
5. The overview should appear directly in the chat; expand Sources only if you want the links.
