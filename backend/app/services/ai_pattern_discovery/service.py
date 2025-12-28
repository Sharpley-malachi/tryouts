from .orchestrator import AI3Orchestrator
import os
import json

class PatternDiscoveryService:
    def __init__(self):
        # Determine data path relative to backend root
        self.root_data_dir = os.path.join(os.getcwd(), "..", "..", "data")
        if not os.path.exists(self.root_data_dir):
             self.root_data_dir = "data"
             
        self.orchestrator = AI3Orchestrator(data_dir=self.root_data_dir)

    def run_discovery(self, ticker: str):
        """
        Trigger the discovery cycle for a specific ticker.
        """
        try:
            report = self.orchestrator.run_discovery_cycle(ticker)
            return {"status": "success", "report": report}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def get_patterns(self):
        """
        Retrieve all discovered patterns from memory.
        """
        try:
            return self.orchestrator.miner.pattern_memory
        except Exception as e:
            return {"status": "error", "message": str(e)}

pattern_discovery_service = PatternDiscoveryService()
