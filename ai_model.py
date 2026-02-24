# -*- coding: utf-8 -*-
"""
AI Model - Random Forest Regressor for Traffic Light Control
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
import joblib
import os


class TrafficAIModel:
    def __init__(self, model_path=None):
        """
        Initialize AI model - load existing or train new
        """
        if model_path and os.path.exists(model_path):
            print(f"Loading model from {model_path}")
            self.model = joblib.load(model_path)
            print("Model loaded successfully!")
        else:
            print("Training new model...")
            self.model = self.train_model()
            print("Model trained successfully!")

    def teacher_green_time(self, Q, s, t_lost, g_min=15, g_max=90):
        """Teacher Equation for green time calculation"""
        g = (Q / s) + t_lost
        g = max(g_min, min(g, g_max))
        return g

    def generate_training_data(self, N=5000):
        """Generate synthetic training data"""
        Q = np.random.randint(0, 80, size=N)
        lanes = np.random.randint(1, 4, size=N)
        s_per_lane = np.random.uniform(0.45, 0.60, size=N)
        s = lanes * s_per_lane
        t_lost = np.random.uniform(2, 5, size=N)

        y = np.array([self.teacher_green_time(Q[i], s[i], t_lost[i]) for i in range(N)])
        y = y + np.random.normal(0, 1.5, size=N)
        y = np.clip(y, 15, 90)

        data = pd.DataFrame({
            "Q_queue": Q,
            "lanes": lanes,
            "s_total": s,
            "t_lost": t_lost,
            "green_time": y
        })

        return data

    def train_model(self):
        """Train Random Forest model"""
        data = self.generate_training_data(5000)
        X = data[["Q_queue", "lanes", "s_total", "t_lost"]]
        y = data["green_time"]

        model = RandomForestRegressor(n_estimators=250, random_state=42)
        model.fit(X, y)

        return model

    def predict_green_time(self, Q_queue, lanes, t_lost=3.0):
        """Predict green time based on queue and lanes"""
        g_min = 15
        g_max = 90
        s_per_lane = 0.55
        s_total = lanes * s_per_lane

        X_in = pd.DataFrame([[Q_queue, lanes, s_total, t_lost]],
                            columns=["Q_queue", "lanes", "s_total", "t_lost"])

        g = self.model.predict(X_in)[0]
        g = max(g_min, min(g, g_max))

        return round(g, 2)

    def save_model(self, filepath="traffic_ai_model.pkl"):
        """Save trained model to file"""
        joblib.dump(self.model, filepath)
        print(f"Model saved to {filepath}")

    def test_model(self):
        """Test model with different scenarios"""
        tests = [
            {"Q": 5, "lanes": 1, "description": "Low density - 1 lane"},
            {"Q": 25, "lanes": 1, "description": "Medium density - 1 lane"},
            {"Q": 25, "lanes": 2, "description": "Medium density - 2 lanes"},
            {"Q": 60, "lanes": 2, "description": "High density - 2 lanes"},
            {"Q": 60, "lanes": 3, "description": "High density - 3 lanes"},
            {"Q": 40, "lanes": 2, "description": "Medium scenario"},
        ]

        print("\n" + "/=/" * 50)
        print("TESTING AI MODEL WITH DIFFERENT SCENARIOS")
        print("=" * 50)

        for t in tests:
            g = self.predict_green_time(Q_queue=t["Q"], lanes=t["lanes"])
            print(f"  {t['description']}:")
            print(f"    {t['Q']} cars | {t['lanes']} lanes -> {g} sec")

        print("/=/" * 50)


if __name__ == "__main__":
    print("Starting AI Model...")
    ai_model = TrafficAIModel()
    ai_model.test_model()
    ai_model.save_model("traffic_ai_model.pkl")