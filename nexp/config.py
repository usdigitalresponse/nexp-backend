# nexp.config

from nexp.aliases import OptionalString
from cached_property import cached_property
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
    def sendgrid_api_key(self) -> str:
        """Your Sendgrid API Key"""
        return environ["SENDGRID_API_KEY"]

    @cached_property
    def override_email_destination(self) -> OptionalString:
        """Override all email destinations. Mainly for testing..."""
        return environ.get("OVERRIDE_EMAIL_DESTINATION")


# Exports ----------------------------------------------------------------------
config = Config()
