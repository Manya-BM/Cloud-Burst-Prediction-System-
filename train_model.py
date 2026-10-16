"""Train the CloudBurst risk model. Run once:  python train_model.py
Dataset: weatherAUS (Australian Bureau of Meteorology daily observations).
Label: IMD daily-rainfall classes of that day's Rainfall:
  Low < 15.6 mm | Moderate 15.6-64.4 mm | High >= 64.5 mm (IMD "heavy rain").
Rainfall itself is NOT a model input (it defines the label -> would be leakage)."""
import json
import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, confusion_matrix
from sklearn.model_selection import train_test_split

DATA = "data/weatherAUS.csv"
FEATURES = ["MinTemp", "MaxTemp", "Humidity9am", "Humidity3pm", "Pressure3pm", "WindGustSpeed", "Temp3pm"]
CLASSES = ["Low", "Moderate", "High"]

def to_risk(mm):
    if mm >= 64.5:
        return "High"
    if mm >= 15.6:
        return "Moderate"
    return "Low"

df = pd.read_csv(DATA)
df = df.dropna(subset=["Rainfall"])                       # need a label
df[FEATURES] = df[FEATURES].fillna(df[FEATURES].median())  # fill missing inputs with the median
df["Risk"] = df["Rainfall"].apply(to_risk)

X_train, X_test, y_train, y_test = train_test_split(
    df[FEATURES], df["Risk"], test_size=0.2, random_state=42, stratify=df["Risk"])
model = RandomForestClassifier(n_estimators=100, max_depth=12, class_weight="balanced",
                               n_jobs=-1, random_state=42)
model.fit(X_train, y_train)
pred = model.predict(X_test)

p, r, f, _ = precision_recall_fscore_support(y_test, pred, labels=CLASSES, average="macro", zero_division=0)
metrics = {"accuracy": accuracy_score(y_test, pred), "precision": p, "recall": r, "f1": f,
           "per_class_recall": dict(zip(CLASSES, precision_recall_fscore_support(
               y_test, pred, labels=CLASSES, zero_division=0)[1].tolist())),
           "confusion_matrix": confusion_matrix(y_test, pred, labels=CLASSES).tolist(),
           "classes": CLASSES, "train_rows": len(X_train), "test_rows": len(X_test)}

bins = [-0.01, 0, 5, 15.6, 64.5, 1e9]
labels = ["0", "0-5", "5-15.6", "15.6-64.5", "64.5+"]
stats = {"distribution": {"labels": labels,
                          "counts": pd.cut(df["Rainfall"], bins, labels=labels).value_counts().reindex(labels).tolist()},
         "by_location": df.groupby("Location")["Rainfall"].mean().sort_values(ascending=False).head(10).round(2).to_dict(),
         "importance": dict(zip(FEATURES, model.feature_importances_.round(3).tolist())),
         "class_counts": df["Risk"].value_counts().reindex(CLASSES).tolist()}

joblib.dump({"model": model, "features": FEATURES}, "models/cloudburst_model.joblib", compress=3)
json.dump(metrics, open("models/metrics.json", "w"), indent=2)
json.dump(stats, open("models/stats.json", "w"), indent=2)
print("Saved model. Accuracy:", round(metrics["accuracy"], 4), "| Macro F1:", round(f, 4))
print("Class counts:", dict(zip(CLASSES, stats["class_counts"])))
