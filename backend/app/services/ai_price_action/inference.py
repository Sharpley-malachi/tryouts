import torch
import numpy as np
import os
import json
from .model import PriceActionBrain

class MarketPredictor:
    def __init__(self, ticker, data_dir="data"):
        self.ticker = ticker
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model = PriceActionBrain().to(self.device)
        self.models_dir = os.path.join(data_dir, "models")
        self.path = os.path.join(self.models_dir, f"{ticker}_brain.pth")
        
        self.loaded = False
        if os.path.exists(self.path):
            self.model.load_state_dict(torch.load(self.path, map_location=self.device))
            self.model.eval()
            self.loaded = True
        else:
            print(f"Warning: No trained model found for {ticker}")

    def predict_next_candle(self, recent_candles):
        """
        Takes the current chart view (last 50 candles as list of lists) and predicts next.
        Input: [[O,H,L,C,V], ...] length 50
        """
        if not self.loaded:
            return {"error": "Model not loaded"}

        # Format input
        input_tensor = torch.FloatTensor(recent_candles).unsqueeze(0).to(self.device) # Add batch dim
        
        with torch.no_grad():
            prediction = self.model(input_tensor) # Returns [Next O, H, L, C]
            
        pred_vals = prediction.cpu().numpy()[0]
        
        # Visual Logic
        current_close = recent_candles[-1][3]
        predicted_close = pred_vals[3]
        
        direction = "BULLISH" if predicted_close > current_close else "BEARISH"
        
        return {
            "predicted_open": float(pred_vals[0]),
            "predicted_high": float(pred_vals[1]),
            "predicted_low": float(pred_vals[2]),
            "predicted_close": float(pred_vals[3]),
            "direction": direction,
            "confidence": "N/A" # Ideally derived from loss or ensemble variance
        }
