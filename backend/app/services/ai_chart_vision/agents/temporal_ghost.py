class TemporalGhostAgent:
    def get_hindsight_mask(self, hover_index, total_candles):
        """
        Returns the range of indices that should be hidden (opacity 0).
        """
        if hover_index >= total_candles:
            return None
        return list(range(hover_index + 1, total_candles))

    def generate_prediction_ghost(self, prediction_data, current_candle_index):
        """
        Generates the coordinates for the 'Anticipated Path' or Ghost Candle.
        """
        if not prediction_data:
            return None
            
        direction = prediction_data.get('direction', 'NEUTRAL')
        ghost_color = "rgba(0, 255, 0, 0.2)" if direction == "BULLISH" else "rgba(255, 0, 0, 0.2)"
        
        return {
            "x": current_candle_index + 1, # Next candle slot
            "predicted_close": prediction_data.get('predicted_close'),
            "predicted_high": prediction_data.get('predicted_high'),
            "predicted_low": prediction_data.get('predicted_low'),
            "color": ghost_color,
            "is_ghost": True
        }
