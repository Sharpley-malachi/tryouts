import os
import json
import dataclasses
import datetime
from typing import Any, Dict, List, Optional
from .core.types import PredictionSnapshot, FeedbackRecord, MarketCandle

# Helper for JSON serialization of dates and dataclasses
class PipelineEncoder(json.JSONEncoder):
    def default(self, o):
        if dataclasses.is_dataclass(o):
            return dataclasses.asdict(o)
        if isinstance(o, (datetime.date, datetime.datetime)):
            return o.isoformat()
        return super().default(o)

class UnifiedStorage:
    def __init__(self, root_dir="data/pipeline_storage"):
        self.root_dir = root_dir
        self.bronze_dir = os.path.join(root_dir, "bronze")
        self.silver_dir = os.path.join(root_dir, "silver")
        self.gold_dir = os.path.join(root_dir, "gold")
        
        # Ensure directories exist
        for d in [self.bronze_dir, self.silver_dir, self.gold_dir]:
            if not os.path.exists(d):
                os.makedirs(d)

    def save_raw(self, batch_id: str, data: Any, metadata: Dict):
        """
        Layer 1 (Bronze): Save raw payload to JSON file
        """
        entry = {
            "batch_id": batch_id,
            "data": data,
            "metadata": metadata,
            "ingested_at": datetime.datetime.utcnow().isoformat()
        }
        path = os.path.join(self.bronze_dir, f"{batch_id}.json")
        with open(path, 'w') as f:
            json.dump(entry, f, cls=PipelineEncoder, indent=2)
        print(f"PIPELINE: Raw batch {batch_id} stored in Bronze Lake.")

    def save_feature(self, symbol: str, timeframe: str, candles: List[MarketCandle]):
        """
        Layer 2 (Silver): Update feature store file for Symbol/TF.
        """
        # Clean symbol for filename
        safe_sym = symbol.replace("=", "").replace("^", "")
        path = os.path.join(self.silver_dir, f"{safe_sym}_{timeframe}.json")
        
        existing_candles = []
        if os.path.exists(path):
            with open(path, 'r') as f:
                try:
                    data = json.load(f)
                    # Simple reload (in real system we'd parse objects)
                    existing_candles = data
                except:
                    existing_candles = []
        
        # Append new candles (Dict format)
        for c in candles:
            existing_candles.append(dataclasses.asdict(c))
            
        # Deduplicate by Timestamp (Simple)
        unique_map = {c['timestamp']: c for c in existing_candles}
        sorted_candles = sorted(unique_map.values(), key=lambda x: x['timestamp'])
        
        with open(path, 'w') as f:
            json.dump(sorted_candles, f, cls=PipelineEncoder)
        print(f"PIPELINE: {symbol}/{timeframe} updated in Silver Store ({len(sorted_candles)} records).")

    def store_prediction(self, prediction: PredictionSnapshot):
        """
        Layer 3 (Gold): Store / Append prediction.
        """
        path = os.path.join(self.gold_dir, "predictions.json")
        preds = self._load_json_list(path)
        preds.append(prediction)
        self._save_json_list(path, preds)
        print(f"PIPELINE: Prediction {prediction.prediction_id} stored in Gold Warehouse.")

    def get_pending_prediction(self, prediction_id: str) -> Optional[PredictionSnapshot]:
        path = os.path.join(self.gold_dir, "predictions.json")
        preds = self._load_json_list(path)
        for p in preds:
            if isinstance(p, dict):
                if p.get('prediction_id') == prediction_id and p.get('status') == 'PENDING':
                    # Reconstruct object
                    try:
                        # Parse date
                        p['timestamp'] = datetime.datetime.fromisoformat(p['timestamp'])
                    except: pass
                    return PredictionSnapshot(**p)
            elif p.prediction_id == prediction_id and p.status == 'PENDING':
                return p
        return None

    def close_loop(self, prediction_id: str, feedback: FeedbackRecord):
        """
        Updates prediction status and logs feedback.
        """
        # Update Prediction Status
        pred_path = os.path.join(self.gold_dir, "predictions.json")
        preds = self._load_json_list(pred_path)
        found = False
        for i, p in enumerate(preds):
            p_dict = p if isinstance(p, dict) else dataclasses.asdict(p)
            if p_dict['prediction_id'] == prediction_id:
                p_dict['status'] = 'CLOSED'
                preds[i] = p_dict
                found = True
                break
        
        if found:
            self._save_json_list(pred_path, preds)
        
        # Save Feedback
        fb_path = os.path.join(self.gold_dir, "feedback.json")
        fbs = self._load_json_list(fb_path)
        fbs.append(feedback)
        self._save_json_list(fb_path, fbs)
        
        print(f"PIPELINE: Loop Closed for {prediction_id}. Result: {feedback.result}")
        return True

    def query_state_at_time(self, symbol: str, query_time: datetime.datetime) -> Dict:
        """
        Hindsight Protection Query.
        """
        snapshot = {}
        # Ensure query_time is timezone-aware to avoid comparing naive vs aware datetimes
        if query_time.tzinfo is None:
            try:
                query_time = query_time.replace(tzinfo=datetime.timezone.utc)
            except Exception:
                pass

        safe_sym = symbol.replace("=", "").replace("^", "")
        
        # Iterate over known TFs 
        # (Prototype: assume we check standard ones)
        for tf in ["4H", "D", "W", "M"]:
            path = os.path.join(self.silver_dir, f"{safe_sym}_{tf}.json")
            if os.path.exists(path):
                with open(path, 'r') as f:
                    candles = json.load(f)
                    # Filter
                    valid = []
                    for c in candles:
                        try:
                            ts = datetime.datetime.fromisoformat(c['timestamp'])
                            if ts <= query_time:
                                valid.append(c)
                        except: pass
                    if valid:
                        snapshot[tf] = valid[-1] # Latest known
        return snapshot

    def _load_json_list(self, path):
        if not os.path.exists(path):
            return []
        with open(path, 'r') as f:
            try:
                return json.load(f)
            except:
                return []

    def _save_json_list(self, path, data):
        with open(path, 'w') as f:
            json.dump(data, f, cls=PipelineEncoder, indent=2)
