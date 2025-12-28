from .dependencies import the_general

class KeyCommandService:
    def __init__(self):
        self.general = the_general

    def switch_mode(self, mode: str):
        return self.general.set_system_state(mode)

    def heartbeat(self, agent_id: str, confidence: float):
        return self.general.register_agent_heartbeat(agent_id, confidence)

    def get_dashboard_metrics(self):
        return self.general.get_system_health()

command_service = KeyCommandService()
