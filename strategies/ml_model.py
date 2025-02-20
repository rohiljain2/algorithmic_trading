import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

class StockPredictor:
    def __init__(self):
        self.model = RandomForestClassifier(n_estimators=100, random_state=42)

    def prepare_data(self, data):
        """Prepare data for training the model"""
        data['returns'] = data['close'].pct_change()
        data['target'] = np.where(data['returns'].shift(-1) > 0, 1, 0)  # 1 if next day return is positive, else 0
        data.dropna(inplace=True)

        features = data[['close', 'volume']]
        target = data['target']

        return train_test_split(features, target, test_size=0.2, random_state=42)

    def train(self, data):
        """Train the model on historical data"""
        X_train, X_test, y_train, y_test = self.prepare_data(data)
        self.model.fit(X_train, y_train)

        # Evaluate the model
        predictions = self.model.predict(X_test)
        accuracy = accuracy_score(y_test, predictions)
        print(f"Model accuracy: {accuracy:.2f}")

    def predict(self, data):
        """Make predictions on new data"""
        return self.model.predict(data[['close', 'volume']]) 