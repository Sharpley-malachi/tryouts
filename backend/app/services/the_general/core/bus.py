from datetime import datetime

class OrchestrationBus:
    def __init__(self):
        # Stores the latest handshake/status from each agent
        self.registry = {
            "AI1_Price": {"status": "IDLE", "confidence": 0.0},
            "AI2_Strategy": {"status": "IDLE", "confidence": 0.0},
            "AI3_Discovery": {"status": "IDLE", "confidence": 0.0},
            "AI4_NLP": {"status": "IDLE", "confidence": 0.0},
            "AI5_Visuals": {"status": "IDLE", "confidence": 0.0},
            "AI6_Librarian": {"status": "IDLE", "confidence": 0.0}
        }
        self.message_log = []

    def update_status(self, agent_id, status, confidence):
        if agent_id in self.registry:
            self.registry[agent_id] = {"status": status, "confidence": confidence}

    def route_intelligence(self, source_agent, target_agent, data):
        """
        Enforces Dependency Injection.
        """
        # Example Blocking Logic
        if target_agent == "AI6_Librarian":
            if not self.check_handshake("AI4_NLP") or not self.check_handshake("AI5_Visuals"):
                print("BLOCKING: Librarian must wait for Author and Artist.")
                return False
        
        self.message_log.append({
            "timestamp": datetime.now().isoformat(),
            "source": source_agent,
            "target": target_agent,
            "data_summary": str(data)[:50] + "..."
        })
        return True

    def check_handshake(self, agent_id):
        # Checks the 'Confidence JSON' from the agent
        status = self.registry.get(agent_id, {})
        return status.get('confidence', 0) > 50  # Minimum threshold to proceed

    def broadcast_state_change(self, new_state):
        print(f"--- BUS BROADCAST: System transitioned to {new_state} ---")
