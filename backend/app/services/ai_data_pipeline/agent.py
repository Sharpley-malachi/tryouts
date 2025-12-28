import uuid
import datetime
from ...utils.timezones import now_utc, ensure_aware
from typing import Dict, List, Any
from .storage import UnifiedStorage
from .core.types import MarketCandle, PredictionSnapshot, FeedbackRecord

class DataPipelineAgent:
    def __init__(self):
        self.storage = UnifiedStorage()
        self.drift_threshold_pips = 0.0005 # Approx 5 pips

    def ingest_market_data(self, correlation_id: str, raw_csv_payload: Dict[str, List[Dict]], metadata: Dict):
        """
        Primary Ingestion Pipeline.
        """
        batch_id = str(uuid.uuid4())[:8]
        
        # 1. Store Raw (Bronze)
        self.storage.save_raw(batch_id, raw_csv_payload, metadata)
        
        market_drift_report = {}
        
        # 2. Check Drift (Mock logic)
        user_price = metadata.get('user_observed_price')
        if user_price:
             # Basic drift check logic would go here
             pass

        # 3. Process to Silver
        symbol = metadata.get('symbol', 'UNKNOWN')
        
        for tf_name, rows in raw_csv_payload.items():
            processed_candles = []
            for row in rows:
                try:
                    ts = self._parse_time(row.get('time', str(now_utc())))
                    c = MarketCandle(
                        timestamp=ts,
                        open=float(row['open']),
                        high=float(row['high']),
                        low=float(row['low']),
                        close=float(row['close']),
                        timeframe=tf_name,
                        source_batch_id=batch_id
                    )
                    processed_candles.append(c)
                except Exception as e:
                    print(f"Skipping row in {tf_name}: {e}")
            
            if processed_candles:
                self.storage.save_feature(symbol, tf_name, processed_candles)

        return {
            "status": "SUCCESS",
            "batch_id": batch_id,
            "drift_report": market_drift_report
        }

    def create_prediction_snapshot(self, correlation_id: str, strategy_output: Dict, symbol: str) -> str:
        """
        Freezes the universe for a prediction.
        """
        pred_id = f"PRED-{uuid.uuid4().hex[:6]}"
        now = now_utc()
        
        # Snapshot current known state
        current_state = self.storage.query_state_at_time(symbol, now)
        
        snapshot = PredictionSnapshot(
            prediction_id=pred_id,
            correlation_id=correlation_id,
            timestamp=now,
            target_symbol=symbol,
            timeframe="4H",
            strategy_bias=strategy_output.get('bias', 'NEUTRAL'),
            market_state_snapshot=current_state,
            ai_confidence=strategy_output.get('confidence', 0.0)
        )
        
        self.storage.store_prediction(snapshot)
        return pred_id

    def process_feedback(self, prediction_id: str, outcome_data: List[Dict]):
        """
        Closes the feedback loop.
        """
        # Convert List[Dict] to List[MarketCandle]
        candles = []
        for row in outcome_data:
            candles.append(MarketCandle(
                timestamp=self._parse_time(row.get('time')),
                open=float(row['open']),high=float(row['high']),
                low=float(row['low']),close=float(row['close']),
                timeframe="4H", source_batch_id="FEEDBACK"
            ))
            
        # Determine Result (Simplistic)
        result = "UNKNOWN"
        if candles:
             if candles[-1].close > candles[0].open: result = "WIN" 
             else: result = "LOSS"

        record = FeedbackRecord(
            prediction_id=prediction_id,
            outcome_candles=candles,
            result=result,
            notes="Auto-Process"
        )
        
        success = self.storage.close_loop(prediction_id, record)
        return {"status": "CLOSED" if success else "ERROR", "result": result}

    def _parse_time(self, time_str):
        if not time_str: return now_utc()
        try:
            return datetime.datetime.fromisoformat(str(time_str).replace("Z", "+00:00"))
        except:
            return now_utc()
