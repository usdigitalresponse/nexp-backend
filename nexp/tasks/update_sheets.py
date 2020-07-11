# nexp.tasks.update_sheets

from nexp.clients.all import Clients


class UpdateSheets:
    """Update our google sheets with everything in our google sheets"""

    def __init__(self, clients: Clients, dryrun: bool = False) -> None:
        self.clients = clients

    def __call__(self) -> None:
        self.clients.data.fill_sheets()
