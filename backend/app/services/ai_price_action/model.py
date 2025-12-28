import torch
import torch.nn as nn

class PriceActionBrain(nn.Module):
    def __init__(self, input_size=5, hidden_size=128, num_layers=2, output_size=4):
        super(PriceActionBrain, self).__init__()
        
        # 1. The Memory Core (LSTM)
        # It takes Open, High, Low, Close, Volume
        self.lstm = nn.LSTM(input_size, hidden_size, num_layers, batch_first=True)
        
        # 2. The Interpretation Layers
        # Converts the LSTM memory into a decision
        self.fc_1 = nn.Linear(hidden_size, 64)
        self.relu = nn.ReLU()  # Activation function (like neurons firing)
        
        # 3. The Output Layer
        # Predicts: Next High, Next Low, Next Close, Direction (Up/Down)
        self.fc_out = nn.Linear(64, output_size)

    def forward(self, x):
        # x represents the sequence of candles (e.g., last 50 candles)
        
        # Initialize hidden state (Short term memory)
        h0 = torch.zeros(2, x.size(0), 128).to(x.device)
        c0 = torch.zeros(2, x.size(0), 128).to(x.device)
        
        # Pass data through the brain
        out, _ = self.lstm(x, (h0, c0))
        
        # Look only at the last time step (the current moment)
        out = self.fc_1(out[:, -1, :])
        out = self.relu(out)
        
        prediction = self.fc_out(out)
        return prediction
