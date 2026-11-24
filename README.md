# VentureIQ Free Edition - Product Studio upgrade

A no-paid-API Streamlit app for preparing social media content packs and simple business planning resources.

## New Product Studio features

- Generates a 30-day social media content calendar
- Creates 12 editable caption drafts and 15 post hooks
- Exports a designed PDF workbook using ReportLab
- Exports an editable CSV calendar
- Bundles PDF, CSV, Markdown notes and a start-here file into one ZIP
- Includes a generic blank 30-day planner download from Products & Pricing
- Keeps the custom client content-pack workflow
- Includes a simple prototype sales tracker (fictional test data only on Streamlit Community Cloud)

## Important product notes

- The generators use original built-in templates, not a paid AI model, live trend data or automated market research.
- A filled sample pack is an example for a fictional cafe; replace the details for each real client.
- All generated drafts must be reviewed and personalised before they are sold or published.
- Get permission before using customer names, photos, reviews or stories.
- Do not enter private customer details, payment details or sensitive financial information into the hosted demo.
- Before taking real orders or collecting customer information, have a parent/guardian review suitable commercial hosting, platform age rules, privacy, refund arrangements and business/tax obligations.

## Requirements

- Python 3.10 or later
- Internet connection for first-time package installation

## Install on Windows

1. Extract the ZIP file.
2. Open the extracted `ventureiq_free` folder.
3. Click the File Explorer address bar, type `cmd`, and press Enter.
4. Run:

```bash
python -m pip install -r requirements.txt
```

5. Launch the app:

```bash
python -m streamlit run app.py
```

6. Open `http://localhost:8501` if the browser does not open automatically.

## Deploying updates

The updated files need to be committed to the existing GitHub repository. Streamlit Community Cloud will then rebuild the app from the new commit. Use the same repository and main file path (`app.py`).

## Stop and restart

- Stop: press `Ctrl + C` in the Command Prompt.
- Restart: run `python -m streamlit run app.py` from this folder.
