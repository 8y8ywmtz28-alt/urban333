from __future__ import annotations

import pandas as pd
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.metrics import accuracy_score, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split


def run_driver_model(df: pd.DataFrame, target: str, features: list[str], mode: str = "classification"):
    x = df[features]
    y = df[target]
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.25, random_state=42)

    if mode == "classification":
        model = RandomForestClassifier(n_estimators=300, random_state=42)
        model.fit(x_train, y_train)
        pred = model.predict(x_test)
        metric = {"accuracy": accuracy_score(y_test, pred)}
    else:
        model = RandomForestRegressor(n_estimators=300, random_state=42)
        model.fit(x_train, y_train)
        pred = model.predict(x_test)
        metric = {"r2": r2_score(y_test, pred), "rmse": mean_squared_error(y_test, pred) ** 0.5}

    importance = pd.DataFrame({"feature": features, "importance": model.feature_importances_}).sort_values("importance", ascending=False)
    return metric, importance
