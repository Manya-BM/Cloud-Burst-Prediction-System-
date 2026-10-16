"""Flask app: serves pages and runs the saved model."""
import json
import os
import joblib
from flask import Flask, jsonify, render_template, request

app = Flask(__name__)
MODEL_PATH, METRICS_PATH, STATS_PATH = "models/cloudburst_model.joblib", "models/metrics.json", "models/stats.json"

# name -> (label, unit, min, max)  (ranges are sanity limits, not model limits)
FIELDS = {
    "MinTemp": ("Min Temperature", "°C", -10, 40),
    "MaxTemp": ("Max Temperature", "°C", -5, 50),
    "Humidity9am": ("Humidity 9am", "%", 0, 100),
    "Humidity3pm": ("Humidity 3pm", "%", 0, 100),
    "Pressure3pm": ("Pressure 3pm", "hPa", 950, 1050),
    "WindGustSpeed": ("Wind Gust Speed", "km/h", 0, 150),
    "Temp3pm": ("Temperature 3pm", "°C", -5, 50),
}
EXPLAIN = {
    "Low": "Conditions look like an ordinary day. Heavy rain is unlikely.",
    "Moderate": "Conditions resemble days with moderate-to-heavy rain (15.6-64.4 mm). Stay aware.",
    "High": "Conditions resemble rare extreme-rain days (64.5 mm or more). Check official forecasts.",
}

def load_json(path):
    return json.load(open(path)) if os.path.exists(path) else None

def load_model():
    return joblib.load(MODEL_PATH) if os.path.exists(MODEL_PATH) else None

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html", fields=FIELDS, metrics=load_json(METRICS_PATH),
                           ready=os.path.exists(MODEL_PATH))

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/api/stats")
def stats():
    data = load_json(STATS_PATH)
    if data is None:
        return jsonify(error="Run 'python train_model.py' first."), 503
    return jsonify(stats=data, metrics=load_json(METRICS_PATH))

@app.route("/api/predict", methods=["POST"])
def predict():
    saved = load_model()
    if saved is None:
        return jsonify(error="Model not found. Run 'python train_model.py' first."), 503
    body = request.get_json(silent=True) or {}
    values, errors = {}, {}
    for name, (label, unit, lo, hi) in FIELDS.items():
        try:
            v = float(body.get(name))
            if v != v or not lo <= v <= hi:
                raise ValueError
            values[name] = v
        except (TypeError, ValueError):
            errors[name] = f"{label} must be a number between {lo} and {hi} {unit}."
    if errors:
        return jsonify(error="Please fix the highlighted fields.", fields=errors), 400
    row = [[values[f] for f in saved["features"]]]
    risk = saved["model"].predict(row)[0]
    return jsonify(risk=risk, explanation=EXPLAIN[risk], inputs=values)

if __name__ == "__main__":
    app.run(debug=True)
