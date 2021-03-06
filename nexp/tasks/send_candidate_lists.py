# nexp.tasks.send_candidate_lists

from typing import Any, Tuple
from tempfile import TemporaryDirectory
from os import path
import logging

import xlsxwriter

from nexp.clients.data import ModelIterator
from nexp.clients.all import Clients
from nexp.aliases import ListAny, OptionalString
from nexp import utils
from nexp.utils import Sheet


class SendCandidateLists:
    """Creates a fancy function that will send candidate update emails to folks
    who are subscribed to receive these messages"""

    # Content type for a spreadsheet
    __candidate_file_content_type = (
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    # Attribute to column mappings for the xlsx file
    __candidate_columns = (
        ("name", "Name"),
        ("previouslySentGroup", "Previously Sent"),
        ("phone_number", "Phone Number"),
        ("email_address", "Email Address"),
        ("high_priority_health_care_practice", "High Priority Practice"),
        ("additional_practice_areas", "Additional Practice Areas"),
        ("regional_availability", "Regional Availability"),
        ("practice_recency", "Practice Recency"),
        ("license_status", "License Status"),
        ("license_number", "License Number"),
        ("out_of_state_license", "Out of State License"),
        ("certifications", "Certifications"),
        ("ft_v_pt", "Full-time or Part-time?"),
        ("workday_availability", "Shift Preference"),
        ("available_on_weekdays", "Weekday Availability"),
        ("date_available", "Date Available"),
        ("notes_about_availability", "Notes about Availability"),
        ("covid_comfort", "Comfortable working with CoVid patients?"),
        ("critical_care_comfort", "Comfortable working in critical care settings?"),
        ("retirement_home_availability", "Willing to work at nursing homes?"),
        ("telehealth_availability", "Open to a telehealth role?"),
        ("mrc_member", "Is an Medical Reserve Corps Member?"),
        ("need_housing", "Would need housing?"),
        ("over_18", "Over 18?"),
        ("street_address", "Street Address"),
        ("city", "City"),
        ("zip_code", "Zip Code"),
        ("state", "State"),
        ("interest_and_ability", "Interest and Ability"),
    )

    def __init__(self, clients: Clients, dryrun: bool = False):
        self.clients = clients
        self.__dryrun = dryrun

    def get_facility_candidates(self, facility: Any) -> ModelIterator:
        """Given a facility object, returns a generator of candidates that match
        their latest filter criteria"""
        return self.clients.data.candidates_for_facility(facility)

    def write_excel_file(
        self, facility: Any, dirpath: str, data: ListAny
    ) -> Tuple[str, str]:
        """Given a facility object, a directory path (for the xlsx file), and
        a generator that yields candidate records, fill a xlsx file with the
        candidate data and return its filepath and filename"""
        filename = (
            f"{facility.facility_name.strip()} - {utils.filename_date_string()}.xlsx"
        )
        filepath = path.join(dirpath, f"{facility.id_}-{filename}")

        workbook = xlsxwriter.Workbook(filepath)

        sheet = Sheet(workbook, "Candidates")

        # Write the header
        for i, (_, name) in enumerate(self.__candidate_columns):
            sheet.data_sheet.write(0, i, name)
            sheet.set_widths(i, len(name))

        # Write the rows for new candidates first and then old ones
        new_candidates = [x for x in data if x.previouslySentGroup == "No"]
        previously_sent_candidates = [x for x in data if x.previouslySentGroup == "Yes"]

        sheet.write_candidates(new_candidates, self.__candidate_columns)
        sheet.write_candidates(previously_sent_candidates, self.__candidate_columns)

        # Set the column widths to the lengths of their longest values. These
        # numbers aren't strictly "right", but in practice they get us relatively
        # close to where we'd want these thigns to wind up. Technically, you'd
        # need to do it based on the font and its rendered size, but that really
        # seems like overkill for this. I just don't want folks opening a sheet
        # with a bunch of overlapping things on it.
        sheet.space_column_widths()

        workbook.close()
        return filepath, filename

    def upload_facility_list(
        self,
        facility: Any,
        filepath: str,
        filename: str,
        content_type: OptionalString = None,
    ) -> str:
        """Given the facility object, filepath, filename, and an optional content,
        upload a file to S3 and return its presigned GET url"""
        content_type = content_type or self.__candidate_file_content_type

        response = self.clients.blobs.upload_file_and_presign(
            filepath, "candidates", f"{facility.id_}/{filename}", content_type
        )
        return response

    def send_facility_candiates_email(
        self, facility: Any, download_url: str, count: int
    ) -> None:
        """Given a facility object and the download_url of their download link,
        send them and email"""
        datestring = utils.display_date_string()

        self.clients.email.send_transactional_template(
            facility.contact_email.lower().strip(),
            self.clients.data.send_email_from,
            self.clients.data.candidates_template_id,
            self.clients.data.unsubscribe_group_id,
            {
                "download_url": download_url,
                "feedback_form_url": utils.prefill_facility_link(
                    self.clients.data.feedback_form_url, facility.id_
                ),
                "date": datestring,
                "name": facility.contact_name,
                "facility_name": facility.facility_name,
                "candidate_count_string": f"are {count} candidates"
                if count > 1
                else "is 1 candidate",
            },
        )

    def handle_facility_with_candidates(
        self, facility: Any, dirpath: str, candidates: ListAny
    ) -> None:
        """Given a facility object, the directory path in which to store
        temporary files, and a list of candiates, throw candidates in an xlsx file,
        upload it to S3, and send an email to the facility point of contact
        with a link to that file included."""

        self.clients.data.update_facility_no_candidates_suppression(facility, False)

        filepath, filename = self.write_excel_file(facility, dirpath, candidates)

        url = self.upload_facility_list(facility, filepath, filename)

        if self.__dryrun:
            logging.info(
                f"Not sending email during dry run. (facility: {facility.facility_name})"
            )
            return  # Early Return

        self.send_facility_candiates_email(facility, url, len(candidates))
        self.clients.data.track_candidates(
            facility.contact_email.lower().strip(), facility, candidates
        )

        logging.info(
            f"Sent candiates list email to facility. (facility: {facility.facility_name})"
        )

    def handle_facility_without_candidates(self, facility: Any) -> None:
        """Given a facility without matching candiates, send them either the
        "No Candidates" email or take no action. If we are sending the "No Candidates"
        email, suppress future "No Candidate" sends"""
        if self.__dryrun:
            logging.info(
                f"Not sending email during dry run. (facility: {facility.facility_name})"
            )
            return  # Early Return

        # Let's add a record to the tracking table
        self.clients.data.track_candidates(
            facility.contact_email.lower().strip(), facility, []
        )

        if (
            hasattr(facility, "suppress_no_candidates_email")
            and facility.suppress_no_candidates_email
        ):
            logging.warn(
                f"Suppressing 'no matching candiates' email for facility. (facility: {facility.facility_name})"
            )
            return  # Early Return

        self.clients.data.update_facility_no_candidates_suppression(facility, True)

        self.clients.email.send_transactional_template(
            facility.contact_email,
            self.clients.data.send_email_from,
            self.clients.data.no_candidates_template_id,
            self.clients.data.unsubscribe_group_id,
            {
                "feedback_form_url": utils.prefill_facility_link(
                    self.clients.data.feedback_form_url, facility.id_
                ),
                "date": utils.display_date_string(),
                "name": facility.contact_name,
            },
        )

        logging.info(
            f"Sent no candidates email to facility. (facility: {facility.facility_name})"
        )

    def handle_facility(self, facility: Any, dirpath: str) -> None:
        """Given a facility object and the directory path in which to store
        temporary files, find matching candidates. Based on the count, determine
        whether we'll be sending them a list of candiates or following the no
        canidates path"""

        candidates = list(self.get_facility_candidates(facility))

        if len(candidates):
            return self.handle_facility_with_candidates(facility, dirpath, candidates)
        else:
            return self.handle_facility_without_candidates(facility)

    def __call__(self) -> None:
        """Send out candidate lists to all approved facilities"""
        with TemporaryDirectory() as dirpath:
            for facility in self.clients.data.facilities_in_need():
                if not hasattr(facility, "contact_email") or not facility.contact_email:
                    logging.warn(
                        f"Could not send candidates list to facility. Email missing (facility: '{facility.facility_name}')"
                    )
                    continue  # Early Continuation

                try:
                    self.handle_facility(facility, dirpath)
                except:
                    logging.exception(
                        f"Failed handling candidates list for facility. (facility: '{facility.facility_name}; email: ({facility.contact_email})')"
                    )
                else:
                    logging.info(
                        f"Finished candiates list task for facility. (facility: {facility.facility_name}; email: {facility.contact_email})"
                    )
