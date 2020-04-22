# handlers

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
    run = SendNeedsRequests(clients)
    run()
