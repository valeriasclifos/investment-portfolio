# Investiții – Investment Portfolio Manager

Aplicație web pentru gestionarea unui portofoliu de investiții. 
Permite înregistrarea utilizatorilor, logare, gestionarea portofoliului, vizionarea tranzațiilor și vizualizarea informațiilor despre companii listate la bursă.

----------------------------------------------------------------------------

## Stack tehnic

- **Limbaj:** Python 3.9.x
- **UI / Frontend:** [Streamlit](https://streamlit.io/)
- **Persistență date utilizatori:** fișier JSON (`data/users.json`)
- **Integrare date bursiere:** `yfinance` (anterior Alpha Vantage)
- **Logging:** fișier `app.log`
- **Altele:** Git & GitHub pentru versionare

------------------------------------------------------------------

## Structura proiectului

investment_portfolio/
├── backend/
│   ├── manage.py
├── requirements.txt
│   ├── app.log
│   ├── data/
│   │   └── users.json
│   └── investment_portfolio/  # setări Django, aplicații, modele, views, API etc.
└── frontend/
    ├── package.json
    ├── src/
    └── public/
