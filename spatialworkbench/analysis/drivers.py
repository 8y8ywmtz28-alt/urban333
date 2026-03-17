from __future__ import annotations

import pandas as pd
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.metrics import accuracy_score, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split


def run_random_forest(df: pd.DataFrame, target: str, task: str = "regression", n_estimators: int = 300):
    x = df.drop(columns=[target])
    y = df[target]
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.3, random_state=42)

    if task == "classification":
        model = RandomForestClassifier(n_estimators=n_estimators, random_state=42)
        model.fit(x_train, y_train)
        pred = model.predict(x_test)
        metrics = {"accuracy": float(accuracy_score(y_test, pred))}
    else:
        model = RandomForestRegressor(n_estimators=n_estimators, random_state=42)
        model.fit(x_train, y_train)
        pred = model.predict(x_test)
        metrics = {
            "r2": float(r2_score(y_test, pred)),
            "rmse": float(mean_squared_error(y_test, pred, squared=False)),
        }

    importance = pd.Series(model.feature_importances_, index=x.columns).sort_values(ascending=False)
    return model, metrics, importance
