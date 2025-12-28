from .agents.projection_agent import ProjectionAgent
from .agents.temporal_ghost import TemporalGhostAgent
from app.services.ai_price_action.trainer import ModelTrainer # Data Loader
import pandas as pd
import json

class VisualOrchestrator:
    def __init__(self, data_dir="data"):
        self.data_dir = data_dir
        self.projection = ProjectionAgent()
        self.ghost = TemporalGhostAgent()
        # In a real persistence layer, we'd cache this
        self.data_package = {} 

    def load_dataset(self, ticker):
        """
        Loads the hierarchy for a ticker, similar to AI #1 trainer.
        """
        trainer = ModelTrainer(ticker, data_dir=self.data_dir)
        try:
            # We are using the flat load for simple demo, 
            # ideally we load the full hierarchical structure for projection logic.
            # Here we mock the hierarchy by loading the same data for different TFs 
            # (since we don't have separate CSVs for D/W in this prototype yet)
            df = trainer.load_data()
            if not df.index.name:
                # Mock Dates if missing (Trainer flattens, so we might lose index for now)
                # Re-loading proper hierarchy would be better, but sticking to prototype flow:
                df.index = pd.date_range(end=pd.Timestamp.now(), periods=len(df), freq='4H')
            
            self.data_package = {
                "4H": df,
                "DAILY": df.resample('D').agg({'Open':'first', 'High':'max', 'Low':'min', 'Close':'last'}).dropna(),
                "WEEKLY": df.resample('W').agg({'Open':'first', 'High':'max', 'Low':'min', 'Close':'last'}).dropna()
            }
            return {"status": "loaded", "candles_count": len(df)}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def get_chart_state(self, ticker, timeframe="4H", hover_index=None):
        """
        Returns the JSON payload for the Frontend Canvas to render.
        This includes candles, active annotations, ghosts, and opacity masks.
        """
        if timeframe not in self.data_package:
            return {"error": "Timeframe data not loaded"}
            
        df = self.data_package[timeframe]
        
        # 1. Base Candles
        candles = []
        for i, (idx, row) in enumerate(df.iterrows()):
            candles.append({
                "x": i,
                "time": idx.isoformat(),
                "o": row['Open'],"h": row['High'],"l": row['Low'],"c": row['Close'],
                "opacity": 1.0 # Default
            })

        response = {
            "candles": candles,
            "annotations": [],
            "ghosts": [],
            "popup": None
        }

        # If no hover, return clean chart
        if hover_index is None:
            return response

        # 2. Apply Hindsight Shield (Visual Logic)
        # Mark future candles as hidden in response
        # In actual Canvas, we just don't draw them or set global alpha 0
        response['mask_start_index'] = hover_index + 1
        
        # 3. Render Prediction Ghost (Mocking AI #3 output)
        # In real flow: query_ai3_prediction(timestamp)
        # Mock:
        current_close = candles[hover_index]['c']
        mock_pred = {
            "direction": "BULLISH",
            "predicted_close": current_close * 1.002, 
            "predicted_high": current_close * 1.005,
            "predicted_low": current_close * 0.999
        }
        ghost = self.ghost.generate_prediction_ghost(mock_pred, hover_index)
        if ghost:
            response['ghosts'].append(ghost)

        # 4. Render Annotations (Mocking AI #2 output)
        # Mock FVG
        mock_fvg = {
            "type": "ZONE",
            "color": "rgba(0, 255, 0, 0.3)",
            "x_start": hover_index - 5,
            "x_end": hover_index + 5,
            "y_top": current_close * 1.001,
            "y_bottom": current_close * 0.999,
            "label": "4H FVG"
        }
        response['annotations'].append(mock_fvg)
        
        # 5. Popup Data
        response['popup'] = {
            "x": hover_index,
            "title": f"Candle #{hover_index}",
            "strategy": "Liquidity Sweep detected",
            "prediction": "Expect Expansion to upside"
        }

        return response
