from cvp_client import CVPClient


class AppState:
    def __init__(self):
        self.cvp_client = CVPClient()


app_state = AppState()
