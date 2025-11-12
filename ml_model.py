#!/usr/bin/env python3
"""
ML model utilities: train and predict student performance percentages.
"""

import os, math, datetime as dt
import pandas as pd
import joblib
from sklearn.ensemble import RandomForestRegressor
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.pipeline import Pipeline
from database import db

MODEL_PATH = os.path.join(os.path.dirname(__file__), "models", "grade_predictor.joblib")

def _fetch_marks_df():
    rows = db.execute_query(
        """
        SELECT m.student_id, m.subject_id, m.teacher_id, m.exam_date,
               m.marks_obtained, m.total_marks
        FROM marks m
        WHERE m.total_marks IS NOT NULL AND m.marks_obtained IS NOT NULL
        ORDER BY m.student_id, m.subject_id, m.exam_date
        """
    ) or []
    if not rows:
        return pd.DataFrame([])
    df = pd.DataFrame(rows)
    df["exam_date"] = pd.to_datetime(df["exam_date"], errors="coerce")
    df["pct"] = (df["marks_obtained"].astype(float) / df["total_marks"].astype(float)) * 100.0
    return df.dropna(subset=["pct"])

def _feature_engineer(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df
    df = df.sort_values(["student_id", "subject_id", "exam_date"])
    # Overall student expanding mean (shifted)
    df["student_overall_avg"] = (
        df.groupby("student_id")["pct"].apply(lambda s: s.expanding().mean().shift(1)).reset_index(level=0, drop=True)
    )
    # Per student-subject expanding mean (shifted)
    df["subj_avg"] = (
        df.groupby(["student_id","subject_id"])["pct"].apply(lambda s: s.expanding().mean().shift(1)).reset_index(level=[0,1], drop=True)
    )
    # Attempt count and recency
    df["attempts_subj"] = df.groupby(["student_id","subject_id"]).cumcount()
    prev_date = df.groupby(["student_id","subject_id"])["exam_date"].shift(1)
    df["days_since"] = (df["exam_date"] - prev_date).dt.days.fillna(60)
    # Fills
    df["student_overall_avg"] = df["student_overall_avg"].fillna(df["pct"].mean())
    df["subj_avg"] = df["subj_avg"].fillna(df["student_overall_avg"])
    df["days_since"] = df["days_since"].fillna(60)
    return df

def build_dataset():
    df = _fetch_marks_df()
    if df.empty:
        return None, None, None
    df = _feature_engineer(df)
    df = df.dropna(subset=["student_overall_avg","subj_avg"])  # need history
    features = ["student_overall_avg","subj_avg","attempts_subj","days_since","subject_id","teacher_id"]
    X = df[features].copy()
    y = df["pct"].astype(float)
    return X, y, features

def train_and_save():
    X, y, features = build_dataset()
    if X is None or len(X) < 20:
        print("[WARN] Not enough data to train")
        return False
    preproc = ColumnTransformer([
        ("num", StandardScaler(), ["student_overall_avg","subj_avg","attempts_subj","days_since"]),
        ("cat", OneHotEncoder(handle_unknown="ignore"), ["subject_id","teacher_id"]),
    ])
    model = Pipeline([
        ("prep", preproc),
        ("rf", RandomForestRegressor(n_estimators=200, random_state=42))
    ])
    model.fit(X, y)
    os.makedirs(os.path.join(os.path.dirname(__file__), "models"), exist_ok=True)
    joblib.dump({"model": model, "features": features}, MODEL_PATH)
    print(f"[OK] Saved model to {MODEL_PATH}")
    return True

def load_model():
    if not os.path.exists(MODEL_PATH):
        train_and_save()
    if not os.path.exists(MODEL_PATH):
        return None
    return joblib.load(MODEL_PATH)

def _latest_stats(student_id, subject_id):
    rows = db.execute_query(
        """
        SELECT m.student_id, m.subject_id, m.teacher_id, m.exam_date,
               m.marks_obtained, m.total_marks
        FROM marks m
        WHERE m.student_id = %s AND m.subject_id = %s AND m.total_marks IS NOT NULL AND m.marks_obtained IS NOT NULL
        ORDER BY m.exam_date
        """, (student_id, subject_id)
    ) or []
    if not rows:
        return None, None
    df = pd.DataFrame(rows)
    df["exam_date"] = pd.to_datetime(df["exam_date"], errors="coerce")
    df["pct"] = (df["marks_obtained"].astype(float) / df["total_marks"].astype(float)) * 100.0
    all_student = db.execute_query(
        """
        SELECT m.exam_date, m.marks_obtained, m.total_marks
        FROM marks m WHERE m.student_id = %s AND m.total_marks IS NOT NULL AND m.marks_obtained IS NOT NULL
        ORDER BY m.exam_date
        """, (student_id,)
    ) or []
    if not all_student:
        return df, None
    s = pd.DataFrame(all_student)
    s["pct"] = (s["marks_obtained"].astype(float)/s["total_marks"].astype(float))*100.0
    student_overall = s["pct"].tail(5).mean() if len(s) >= 1 else s["pct"].mean()
    return df, float(student_overall) if not math.isnan(student_overall) else None

def predict_next_percentage(model_bundle, student_id, subject_id):
    if not model_bundle:
        return None
    model = model_bundle["model"]
    df, student_overall = _latest_stats(student_id, subject_id)
    if df is None or df.empty:
        return None
    df = df.sort_values("exam_date")
    subj_avg = df["pct"].tail(3).mean() if len(df) >= 1 else df["pct"].mean()
    attempts = len(df)
    last_date = df["exam_date"].iloc[-1]
    days_since = max((pd.Timestamp.today() - last_date).days, 1) if pd.notnull(last_date) else 60
    teacher_id = int(df["teacher_id"].iloc[-1]) if "teacher_id" in df.columns else 0
    student_overall = student_overall if student_overall is not None else subj_avg

    X_row = pd.DataFrame([{
        "student_overall_avg": float(student_overall),
        "subj_avg": float(subj_avg),
        "attempts_subj": int(attempts),
        "days_since": float(days_since),
        "subject_id": int(subject_id),
        "teacher_id": int(teacher_id),
    }])
    pred = float(model.predict(X_row)[0])
    return max(0.0, min(100.0, pred))

def percentage_to_grade(pct: float) -> str:
    if pct >= 90: return "A+"
    if pct >= 80: return "A"
    if pct >= 70: return "B"
    if pct >= 60: return "C"
    if pct >= 50: return "D"
    return "F"


