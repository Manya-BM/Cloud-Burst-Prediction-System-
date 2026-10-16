# CloudBurst Prediction System (educational prototype)
Flask + scikit-learn dashboard that classifies **extreme-rainfall risk** (Low / Moderate / High).cd "C:\Users\bmman\Downloads\cloudburst-prediction-system\cloudburst-prediction-system"
python -m venv venv
venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
Not a validated cloudburst forecaster. Dataset: weatherAUS (Australian Bureau of Meteorology), no cloudburst labels.
Label = IMD daily-rainfall class of that day's rainfall (Low <15.6 mm, Moderate 15.6-64.4, High >=64.5). Rainfall is not an input (it would leak the label).

## Setup (Windows PowerShell, VS Code terminal)
```powershell
cd cloudburst-prediction-system          # or: mkdir cloudburst-prediction-system; cd cloudburst-prediction-system
python -m venv venv
venv\Scripts\Activate.ps1                # if blocked: Set-ExecutionPolicy -Scope Process Bypass
pip install -r requirements.txt
# Dataset is already in data/. To re-download:
Invoke-WebRequest https://raw.githubusercontent.com/tvdboom/ATOM/master/examples/datasets/weatherAUS.csv -OutFile data\weatherAUS.csv
python train_model.py                    # trains, prints real metrics, saves models/
python app.py                            # then open http://127.0.0.1:5000
python -m pytest tests -v                # run tests (needs trained model)
```

## Files
- `train_model.py` loads CSV, fills missing values, labels, splits 80/20 (stratified), trains Random Forest, saves model + metrics + chart data.
- `app.py` Flask routes: `/`, `/dashboard`, `/about`, `/api/predict`, `/api/stats`.
- `templates/`, `static/` pages, styling, and `dashboard.js` (charts + form).

## Prediction flow
Form -> `dashboard.js` sends JSON to `/api/predict` -> Flask validates ranges -> loads `.joblib` model -> `predict()` -> JSON -> JS draws the coloured result card and chart.


