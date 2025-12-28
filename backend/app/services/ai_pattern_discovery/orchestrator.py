from .agents.curiosity_engine import CuriosityAgent
from .agents.discovery_miner import DiscoveryMinerAgent
from app.services.ai_price_action.inference import MarketPredictor
from app.services.ai_price_action.trainer import ModelTrainer
import os
import pandas as pd

class AI3Orchestrator:
    def __init__(self, data_dir="data"):
        self.data_dir = data_dir
        # AI #3 needs AI #1's brain.
        # We will instantiate a generic predictor that can be swapped per ticker
        self.miner = DiscoveryMinerAgent(data_dir=data_dir)

    def run_discovery_cycle(self, ticker):
        """
        Runs the full AI #3 logic across all timeframes for a given ticker.
        """
        # 1. Load Data for Ticker (Using AI #1's loader)
        # We need raw candles.
        trainer = ModelTrainer(ticker, data_dir=self.data_dir)
        try:
            df = trainer.load_data()
            raw_candles = df.values.tolist()
        except:
             return {"status": "error", "message": f"No data found for {ticker}"}
             
        # Initialize Curiosity Engine with a Predictor for this ticker
        predictor = MarketPredictor(ticker, data_dir=self.data_dir)
        curiosity = CuriosityAgent(predictor)

        discovery_report = {
            "ticker": ticker,
            "new_patterns": [],
            "journey_insights": [],
            "masking_summary": {"steps": 0, "surprises": 0}
        }

        # 2. Run Masking/Unmasking Curiosity Loop
        # In a real app we might chunk this or run as background task
        # We run on last 200 candles for demo speed
        recent_history = raw_candles[-200:]
        masking_results = curiosity.perform_masking_study(recent_history, ticker)
        
        high_surprise_count = 0
        
        # 3. Extract specific patterns from high 'surprise' areas
        for result in masking_results:
            if result['surprise_score'] > 0.05: # Sensitivity Threshold
                high_surprise_count += 1
                idx_in_recent = result['step']
                # Grab the sequence that caused the surprise (e.g. 5 candles leading up to it)
                if idx_in_recent >= 5:
                    pattern_seq = recent_history[idx_in_recent-5 : idx_in_recent]
                    new_pattern = self.miner.discover_new_pattern(pattern_seq)
                    discovery_report["new_patterns"].append(new_pattern)

        discovery_report["masking_summary"]["steps"] = len(masking_results)
        discovery_report["masking_summary"]["surprises"] = high_surprise_count
        
        # 4. Single-Timeframe Autonomous Mining
        # (Looking for entries without HTF help)
        standalone_spots = self._mine_standalone_entries(df)
        discovery_report["journey_insights"].extend(standalone_spots)

        return discovery_report

    def _mine_standalone_entries(self, df):
        # Autonomous logic to find patterns that repeat on just ONE timeframe
        # Placeholder for complex logic
        return ["Potential Standalone Entry identified at Index 150 (Example)"]

# Singleton for easy import
ai3_orchestrator = None # Will init with path in usage
