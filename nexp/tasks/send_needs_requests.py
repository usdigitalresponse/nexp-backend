# nexp.tasks.send_needs_requests

from typing import Any
import logging

from nexp.clients.all import Clients
from nexp import utils


class SendNeedsRequests:
    """Creates a fancy function that will ask facilities to update us on
    their needs"""

    def __init__(self, clients: Clients, dryrun: bool = False) -> None:
        self.clients = clients
        self.__dryrun = dryrun

    def handle_facility(self, facility: Any) -> None:
        """Send the needs request email to the given facility"""
        if self.__dryrun:
            logging.info(
                f"Not sending email during dry run. (facility: {facility.facility_name})"
            )
            return  # Early Return

        date_string = utils.display_date_string()
        self.clients.email.send_transactional_template(
            facility.contact_email.lower().strip(),
            self.clients.data.send_email_from,
            self.clients.data.needs_template_id,
            self.clients.data.unsubscribe_group_id,
            template_data={
                "name": facility.contact_name,
                "facility_name": facility.facility_name,
                "date": date_string,
                "feedback_form_url": utils.prefill_facility_link(
                    self.clients.data.feedback_form_url, facility.id_
                ),
                "needs_form_url": utils.prefill_facility_link(
                    self.clients.data.needs_form_url, facility.id_
                ),
            },
        )

    def __call__(self) -> None:
        """Send needs request emails to all facilities"""
        for facility in self.clients.data.list_facilities():
            if not hasattr(facility, "contact_email") or not facility.contact_email:
                logging.warn(
                    f"Could not send needs request facility. Email missing (facility: '{facility.facility_name}')"
                )
                continue  # Early Continuation

            try:
                self.handle_facility(facility)
            except:
                logging.exception(
                    f"Failed handling facility. (facility: '{facility.facility_name}; email: ({facility.contact_email})')"
                )
            else:
                logging.info(
                    f"Sent needs request. (facility: {facility.facility_name}; email: {facility.contact_email})"
                )
