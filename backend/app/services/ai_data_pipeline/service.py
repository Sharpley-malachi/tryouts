from .agent import DataPipelineAgent

class DataPipelineService:
    def __init__(self):
        self.agent = DataPipelineAgent()

    def ingest_data(self, payload):
        return self.agent.ingest_market_data(
            correlation_id=payload.get('correlation_id', 'MANUAL'),
            raw_csv_payload=payload.get('data', {}),
            metadata=payload.get('metadata', {})
        )

    def register_prediction(self, payload):
        return self.agent.create_prediction_snapshot(
            correlation_id=payload.get('correlation_id', 'AUTO'),
            strategy_output=payload.get('strategy_output', {}),
            symbol=payload.get('symbol', 'Unknown')
        )

    def submit_feedback(self, payload):
        return self.agent.process_feedback(
            prediction_id=payload.get('prediction_id'),
            outcome_data=payload.get('outcome_candles', [])
        )

pipeline_service = DataPipelineService()
