# nexp.config

from nexp.aliases import OptionalString
from cached_property import cached_property
from os.path import dirname, join, realpath
from json import loads
from os import environ


class Config:
    """Maintains the shared configuartion of this backend service"""

    @cached_property
    def timezone(self) -> str:
        """In what timezone are we operating?"""
        return environ.get("NEXP_TIMEZONE", "US/Central")

    @cached_property
    def s3_bucket(self) -> str:
        """Where should these files live in S3?"""
        return environ["S3_BUCKET"]

    @cached_property
    def s3_prefix(self) -> str:
        """What prefix in S3 should we use for the files we generate?"""
        return environ["S3_PREFIX"]

    @cached_property
    def s3_url_expiry_seconds(self) -> int:
        """When should S3 URLs expire?"""
        return int(environ.get("S3_URL_EXPIRY_SECONDS", 60 * 60 * 12))

    @cached_property
    def airtable_api_key(self) -> str:
        """Your Airtable API Key"""
        return environ["AIRTABLE_API_KEY"]

    @cached_property
    def airtable_base_id(self) -> str:
        """The ID identifying the base where you data is stored"""
        return environ["AIRTABLE_BASE_ID"]

    @cached_property
    def airtable_candidates_table(self) -> str:
        """The name of the candidates table in Airtable"""
        return environ.get("AIRTABLE_CANDIDATES_TABLE", "Candidates")

    @cached_property
    def airtable_facilities_table(self) -> str:
        """The name of the facilities table in Airtable"""
        return environ.get("AIRTABLE_FACILITIES_TABLE", "Authorized Facilities")

    @cached_property
    def airtable_needs_table(self) -> str:
        """The name of the staffing needs table in Airtable"""
        return environ.get("AIRTABLE_NEEDS_TABLE", "Facility Staffing Needs")

    @cached_property
    def airtable_config_table(self) -> str:
        """The name of the config table in Airtable"""
        return environ.get("AIRTABLE_CONFIG_TABLE", "Configuration")

    @cached_property
    def airtable_tracking_table(self) -> str:
        """The name of the mailing tracking table in Airtable"""
        return environ.get("AIRTABLE_TRACKING_TABLE", "Mailing Tracking")

    @cached_property
    def airtable_candidate_tags_table(self) -> str:
        """The name of the candidate tags table in Airtable"""
        return environ.get("AIRTABLE_CANDIDATE_TAGS_TABLE", "Candidate Tags")

    @cached_property
    def sendgrid_api_key(self) -> str:
        """Your Sendgrid API Key"""
        return environ["SENDGRID_API_KEY"]

    @cached_property
    def override_email_destination(self) -> OptionalString:
        """Override all email destinations. Mainly for testing..."""
        return environ.get("OVERRIDE_EMAIL_DESTINATION")

    @cached_property
    def google_credentials(self) -> OptionalString:
        """Your Google Sheets Credentials"""
        return loads(environ["GOOGLE_CREDENTIALS"])

    @cached_property
    def google_spreadsheet_id(self) -> OptionalString:
        """What spreadsheets hosts the worksheets we're updating"""
        return environ.get(
            "GOOGLE_SPREADSHEET_ID", "1tth4m5nV6rIOKETdUa5g0D0skOBvIKlIBE1HmCFr7jE"
        )

    @cached_property
    def google_candidates_sheet_name(self) -> OptionalString:
        """What is the name of the Raw Candidates Sheet within Google Sheets?"""
        return environ.get("GOOGLE_CANDIDATES_SHEET_NAME", "[Raw] Candidates")

    @cached_property
    def google_facilities_sheet_name(self) -> OptionalString:
        """What is the name of the Raw Facilities Sheet within Google Sheets?"""
        return environ.get("GOOGLE_FACILITIES_SHEET_NAME", "[Raw] Facilities")

    @cached_property
    def google_needs_sheet_name(self) -> OptionalString:
        """What is the name of the Raw Needs Sheet within Google Sheets?"""
        return environ.get("GOOGLE_NEEDS_SHEET_NAME", "[Raw] Needs")

    @cached_property
    def google_tracking_sheet_name(self) -> OptionalString:
        """What is the name of the Raw Tracking Sheet within Google Sheets?"""
        return environ.get("GOOGLE_TRACKING_SHEET_NAME", "[Raw] Tracking")


# Exports ----------------------------------------------------------------------
config = Config()
