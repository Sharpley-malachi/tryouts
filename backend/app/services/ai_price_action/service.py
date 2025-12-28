from .fetcher import DataAgent
from .trainer import ModelTrainer
from .inference import MarketPredictor
import os
import pandas as pd
import json

class PriceActionService:
    def __init__(self):
        # Determine data path relative to backend root or configured path
        # Assuming backend runs from 'backend/' root, data is ../../data ?? 
        # Actually user config says "data/" at root.
        # Let's fix pathing.
        self.root_data_dir = os.path.join(os.getcwd(), "..", "..", "data") 
        if not os.path.exists(self.root_data_dir):
             self.root_data_dir = "data" # Fallback relative
             
        self.fetcher = DataAgent(data_dir=self.root_data_dir)

    def fetch_all_data(self):
        """Trigger automated data fetching for all configured assets."""
        data = self.fetcher.fetch_automated_data()
        count = self.fetcher.save_to_local_storage(data)
        return {"status": "success", "assets_updated": count}

    def train_model(self, ticker: str):
        """Train the LSTM for a specific ticker."""
        trainer = ModelTrainer(ticker, data_dir=self.root_data_dir)
        result = trainer.train(epochs=50) # kept low for demo speed
        return result

    def predict(self, ticker: str):
        """
        Load data, pick last sequence, predict next candle.
        """
        # 1. Load actual recent data to feed the model
        # Re-using logic from Trainer to load dataframe
        trainer = ModelTrainer(ticker, data_dir=self.root_data_dir)
        try:
            df = trainer.load_data()
            last_sequence = df.values[-50:] # Last 50 candles
            
            if len(last_sequence) < 50:
                return {"status": "error", "message": "Not enough history"}
                
            predictor = MarketPredictor(ticker, data_dir=self.root_data_dir)
            prediction = predictor.predict_next_candle(last_sequence)
            return prediction
        except Exception as e:
            return {"status": "error", "message": str(e)}

price_action_service = PriceActionService()
