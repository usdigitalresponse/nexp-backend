# handlers

from nexp.tasks.update_sheets import UpdateSheets
from nexp.tasks.send_candidate_lists import SendCandidateLists
from nexp.tasks.send_needs_requests import SendNeedsRequests
from nexp.clients.all import Clients

clients = Clients()


def send_candidates_lists(*args):
    # Always refill the local database
    clients.data.fill()
    run = SendCandidateLists(clients)
    run()


def send_needs_requests(*args):
    # Always refill the local database
    clients.data.fill()
    run = SendNeedsRequests(clients)
    run()


def update_sheets(*args):
    # Always refill the local database
    clients.data.fill()
    run = UpdateSheets(clients)
    run()
