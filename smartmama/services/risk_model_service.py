import os
import joblib

MODEL_PATH = os.path.join(os.path.dirname(__file__), "..", "ML_Models", "risk_rf_model.joblib")

_model = None


def _get_model():
    """Loads the model once else catch & raise error if file is missing or corrupt"""
    global _model
    if _model is None:
        _model = joblib.load(MODEL_PATH)
    return _model


RISK_LABELS = {0: "Low", 1: "Medium", 2: "High"}

RISK_RECOMMENDATIONS = {
    "Low": "Continue routine antenatal visits as scheduled.",
    "Medium": "Schedule a follow-up visit within the next 2 weeks and monitor symptoms closely.",
    "High": "Refer the mother to the hospital immediately for further evaluation.",
}


def predict_risk(age: int, systolic_bp: int, diastolic_bp: int, blood_sugar: float, body_temp: float) -> tuple[str, float]:
    model = _get_model()
    features = [[age, systolic_bp, diastolic_bp, blood_sugar, body_temp]]
    prediction = model.predict(features)[0]
    probabilities = model.predict_proba(features)[0]
    confidence = float(probabilities[prediction])
    risk_level = RISK_LABELS[prediction]
    return risk_level, round(confidence, 2)