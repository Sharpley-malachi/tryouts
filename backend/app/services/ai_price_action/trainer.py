import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
import os
import json
from .model import PriceActionBrain

class ModelTrainer:
    def __init__(self, ticker, data_dir="data"):
        self.ticker = ticker
        self.data_dir = data_dir
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model = PriceActionBrain().to(self.device)
        self.optimizer = optim.Adam(self.model.parameters(), lr=0.001)
        self.criterion = nn.MSELoss()  # Measures how "wrong" the guess was
        self.models_dir = os.path.join(data_dir, "models")
        if not os.path.exists(self.models_dir):
            os.makedirs(self.models_dir)

    def load_data(self):
        """Loads flattened candle data from the hierarchical JSON."""
        clean_name = self.ticker.replace("=X", "").replace("^", "")
        file_path = os.path.join(self.data_dir, "price_action_data", f"{clean_name}.json")
        
        if not os.path.exists(file_path):
             raise FileNotFoundError(f"Data for {self.ticker} not found at {file_path}")
             
        with open(file_path, 'r') as f:
            hierarchy = json.load(f)
            
        # Flatten logic: Extract all 4H candles (or Daily) for training sequence
        # For simplicity in this demo, let's extract all DAILY candles from the structure
        flat_candles = []
        for month in hierarchy:
            for week in month.get('children_weekly', []):
                for day in week.get('children_daily', []):
                    # ohlc is dict
                    ohlc = day['ohlc']
                    # Ensure format
                    flat_candles.append([
                        ohlc.get('Open', 0),
                        ohlc.get('High', 0),
                        ohlc.get('Low', 0),
                        ohlc.get('Close', 0),
                        ohlc.get('Volume', 0)
                    ])
        
        # Sort by date usually handled by ingestion structure, but safe to assume chronological for now
        return pd.DataFrame(flat_candles, columns=['Open', 'High', 'Low', 'Close', 'Volume'])

    def prepare_sequences(self, df, seq_length=50):
        """
        Implements the MASKING Logic.
        """
        sequences = []
        targets = []
        
        raw_data = df.values.astype(float)
        
        if len(raw_data) <= seq_length:
            return None, None

        for i in range(len(raw_data) - seq_length):
            # Input: Candles 0 to 50
            seq = raw_data[i : i+seq_length]
            # Target: Candle 51 (Predicting Close price)
            # In real system, we predict Next H, L, C. Here just Close for simplicity or map to output size.
            # Model output size is 4 (H, L, C, Dir?). Let's target Close.
            # Wait, model output_size=4. So target should include 4 values ideally?
            # Let's target Next Open(0), High(1), Low(2), Close(3)
            # Actually next candle is at i+seq_length
            next_candle = raw_data[i+seq_length]
            target = next_candle[0:4] # Predict O, H, L, C next
            
            sequences.append(seq)
            targets.append(target)
            
        return torch.FloatTensor(np.array(sequences)), torch.FloatTensor(np.array(targets))

    def train(self, epochs=50):
        print(f"--- Starting Training for {self.ticker} ---")
        
        # 1. Get Data
        try:
            df = self.load_data()
        except Exception as e:
            return {"status": "error", "message":str(e)}

        # 2. Sequence Prep
        X, y = self.prepare_sequences(df)
        if X is None:
             return {"status": "error", "message": "Not enough data for sequence length"}
             
        X, y = X.to(self.device), y.to(self.device)
        
        # 3. Learning Loop
        for epoch in range(epochs):
            self.model.train()
            
            # Forward
            outputs = self.model(X) # Output shape (batch, 4)
            # Resize y to match output if needed. y is (batch, 4) if we targeted correctly.
            
            # Error
            loss = self.criterion(outputs, y)
            
            # Backward
            self.optimizer.zero_grad()
            loss.backward()
            self.optimizer.step()
            
            if (epoch+1) % 10 == 0:
                print(f'Epoch [{epoch+1}/{epochs}], Error: {loss.item():.4f}')
        
        # 4. Save
        path = os.path.join(self.models_dir, f"{self.ticker}_brain.pth")
        torch.save(self.model.state_dict(), path)
        print(f"Brain saved at {path}")
        return {"status": "success", "loss": loss.item(), "path": path}
