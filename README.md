# VentureIQ Free Edition

A no-paid-API version of VentureIQ built with Streamlit.

## What it includes

- Dashboard and launch checklist
- Social Media Starter Pack generator
- 14-day content calendar
- Draft captions and post hooks
- Downloadable ZIP containing Markdown and CSV files
- Custom client content-plan draft
- Example product/service pricing page
- Simple sales tracker with CSV export

## What it does not include

- No OpenAI API connection or AI model calls
- No customer accounts or online storefront
- No payment processing
- No public hosting
- Sales entries are stored in the current Streamlit session and should be exported before closing

The generators use built-in templates. They create starting drafts, not original AI-generated market research. Check all facts and customise the content before selling or publishing it.

## Requirements

- Python 3.10 or later
- Internet connection for the first package installation

## Install on Windows

1. Extract the ZIP file.
2. Open the extracted `ventureiq_free` folder.
3. Click the File Explorer address bar, type `cmd`, and press Enter.
4. Run:

```bash
python -m pip install -r requirements.txt
```

5. Then launch:

```bash
python -m streamlit run app.py
```

6. Open `http://localhost:8501` in your browser if it does not open automatically.

## Stop the app

In the Command Prompt window, press `Ctrl + C`.

## Restart later

Open Command Prompt in this same folder and run:

```bash
python -m streamlit run app.py
```


