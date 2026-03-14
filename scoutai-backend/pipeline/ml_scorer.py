"""
ScoutAI — ML Talent Scorer (XGBoost)
Trains on synthetic data if no model exists, then scores athlete metrics.
"""

import os
import numpy as np
import joblib

MODEL_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "ml_models")
MODEL_PATH = os.path.join(MODEL_DIR, "talent_scorer.pkl")


def train_synthetic_model():
    """
    Train an XGBoost model on synthetic data and save it.
    Features: [avg_speed, max_speed, jump_height, form_score, agility, consistency]
    Target: talent_score (0–100)
    """
    try:
        import xgboost as xgb
    except ImportError:
        print("[WARNING] xgboost not installed, using fallback scorer")
        return None

    np.random.seed(42)
    n_samples = 2000

    # Generate synthetic features
    avg_speed = np.random.uniform(5, 30, n_samples)
    max_speed = avg_speed + np.random.uniform(2, 15, n_samples)
    jump_height = np.random.uniform(0, 80, n_samples)
    form_score = np.random.uniform(20, 100, n_samples)
    agility = np.random.uniform(10, 100, n_samples)
    consistency = np.random.uniform(20, 100, n_samples)

    X = np.column_stack([avg_speed, max_speed, jump_height, form_score, agility, consistency])

    # Synthetic talent score formula (weighted combination with noise)
    y = (
        avg_speed * 1.2
        + max_speed * 0.5
        + jump_height * 0.6
        + form_score * 0.4
        + agility * 0.3
        + consistency * 0.3
        + np.random.normal(0, 3, n_samples)
    )
    # Normalize to 0–100
    y = (y - y.min()) / (y.max() - y.min()) * 100
    y = np.clip(y, 0, 100)

    model = xgb.XGBRegressor(
        n_estimators=100,
        max_depth=5,
        learning_rate=0.1,
        objective="reg:squarederror",
        random_state=42,
    )
    model.fit(X, y)

    os.makedirs(MODEL_DIR, exist_ok=True)
    joblib.dump(model, MODEL_PATH)
    print(f"[INFO] Talent scorer model trained and saved to {MODEL_PATH}")
    return model


def _load_model():
    """Load the talent scorer model, training on synthetic data if needed."""
    if os.path.exists(MODEL_PATH):
        return joblib.load(MODEL_PATH)
    return train_synthetic_model()


def score_talent(metrics: dict) -> dict:
    """
    Score an athlete's talent based on computed metrics.
    
    Args:
        metrics: dict with keys avg_speed, max_speed, jump_height, form_score, agility, consistency
    
    Returns:
        dict with talent_score (0–100), grade (string), and breakdown (dict)
    """
    model = _load_model()

    features = np.array([[
        metrics.get("avg_speed", 10),
        metrics.get("max_speed", 15),
        metrics.get("jump_height", 30),
        metrics.get("form_score", 50),
        metrics.get("agility", 50),
        metrics.get("consistency", 50),
    ]])

    if model is not None:
        raw_score = model.predict(features)[0]
    else:
        # Fallback: simple weighted average
        raw_score = (
            metrics.get("avg_speed", 10) * 1.5
            + metrics.get("form_score", 50) * 0.5
            + metrics.get("jump_height", 30) * 0.5
            + metrics.get("agility", 50) * 0.3
            + metrics.get("consistency", 50) * 0.2
        ) / 3

    percentile = float(np.clip(raw_score, 0, 100))

    if percentile > 85:
        grade = "Elite"
    elif percentile > 70:
        grade = "Advanced"
    elif percentile > 50:
        grade = "Developing"
    else:
        grade = "Beginner"

    return {
        "talent_score": round(percentile, 1),
        "grade": grade,
        "breakdown": {
            "speed": round(min(100, metrics.get("avg_speed", 0) * 5), 1),
            "athleticism": round(min(100, metrics.get("jump_height", 0) * 2), 1),
            "technique": round(metrics.get("form_score", 0), 1),
            "agility": round(metrics.get("agility", 0), 1),
            "consistency": round(metrics.get("consistency", 0), 1),
        },
    }
