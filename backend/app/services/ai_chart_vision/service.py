from .orchestrator import VisualOrchestrator
import os

class ChartVisionService:
    def __init__(self):
        # Determine data path relative to backend root
        self.root_data_dir = os.path.join(os.getcwd(), "..", "..", "data")
        if not os.path.exists(self.root_data_dir):
             self.root_data_dir = "data"
             
        self.orchestrator = VisualOrchestrator(data_dir=self.root_data_dir)

    def load_data(self, ticker: str):
        return self.orchestrator.load_dataset(ticker)

    def get_chart_data(self, ticker: str, timeframe: str = "4H", hover_index: int = None):
        """
        API Endpoint logic to get renderable state.
        """
        return self.orchestrator.get_chart_state(ticker, timeframe, hover_index)

chart_vision_service = ChartVisionService()
