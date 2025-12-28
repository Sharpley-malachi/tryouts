import numpy as np

class CuriosityAgent:
    def __init__(self, model_service):
        """
        model_service: Wrapper to call AI #1's prediction logic.
        """
        self.model_service = model_service 
        self.discovery_log = []

    def perform_masking_study(self, sequence_data, ticker):
        """
        The 'Offshore' Logic: Predict N+1, Unmask, Evaluate.
        sequence_data: List of OHLC candles (e.g. last 100).
        """
        findings = []
        
        # We need at least 50 candles to make a prediction using AI #1
        if len(sequence_data) < 51:
            return []

        # We start from a 'window' and move one candle at a time
        # Start at index 50 (first valid prediction point)
        for i in range(50, len(sequence_data) - 1):
            
            # 1. Masking: Visible history is 0 to i
            visible_candles = sequence_data[i-50 : i] # Inputs for model
            actual_next_candle = sequence_data[i]     # The Target (N+1)
            
            # AI makes a 'Structural Prediction'
            # (Is the next candle an Expansion, Retracement, or Consolidation?)
            # We assume model_service can take raw list of lists
            prediction = self.model_service.predict_next_candle(visible_candles)
            
            if 'error' in prediction:
                continue

            # 2. Unmasking: Compare prediction to reality
            # actual_next_candle is [O, H, L, C, V]
            actual_close = actual_next_candle[3]
            pred_close = prediction['predicted_close']
            
            error_metrics = self._calculate_structural_surprise(pred_close, actual_close)
            
            # Simple direction check
            actual_dir = "BULLISH" if actual_close >= actual_next_candle[0] else "BEARISH"
            pred_dir = prediction['direction']
            
            is_anomaly = self._detect_micro_anomaly(prediction, actual_next_candle)

            findings.append({
                "step": i,
                "predicted_bias": pred_dir,
                "actual_outcome": "HIT" if pred_dir == actual_dir else "MISS",
                "surprise_score": float(error_metrics),
                "is_anomaly": is_anomaly,
                "timestamp": datetime.now().isoformat()
            })
            
        return findings

    def _calculate_structural_surprise(self, pred_price, actual_price):
        # Measures how much the market 'deviated' from the expected path
        # High surprise = Potential new pattern discovery point
        # Normalize relative to price roughly
        if actual_price == 0: return 0
        return np.abs(pred_price - actual_price) / actual_price

    def _detect_micro_anomaly(self, prediction, actual_candle):
        # Did the market move opposite to strong confidence?
        # Or did it move significantly more than expected (volatility shock)?
        pred_close = prediction['predicted_close']
        actual_close = actual_candle[3]
        
        # Simple placeholder logic for anomaly: > 10% separate (which is huge in forex, but okay for code structure)
        if abs(pred_close - actual_close) > (actual_close * 0.01): 
            return True
        return False
