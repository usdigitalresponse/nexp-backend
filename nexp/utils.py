# nexp.utils

from typing import Any, Union
from datetime import datetime
import pathlib

import pytz

from nexp.config import config


class Sheet:
    """
    Sheet class
    """

    def __init__(self, workbook, name) -> None:
        self.workbook = workbook
        self.name = name
        self.widths = {}
        self.row = 1
        self.data_sheet = self.create_worksheet()

    def create_worksheet(self):
        return self.workbook.add_worksheet(self.name)

    def set_widths(self, i, length):
        self.widths[i] = length

    def space_column_widths(self):
        for column_index, length in self.widths.items():
            self.data_sheet.set_column(column_index, column_index, length)

    def write_candidates(self, candidates, cols):
        for record in candidates:
            for i, (key, _) in enumerate(cols):
                value = getattr(record, key) if hasattr(record, key) else None

                # A bunch of the data from airtable shows up as lists. We just
                # comma delimit those when that's the case
                if isinstance(value, list):
                    value = ", ".join(value)

                self.data_sheet.write(self.row, i, value)
                value_length = len(str(value))

                if value_length > self.widths[i]:
                    self.set_widths(i, value_length)

            self.row += 1


def datetime_now() -> datetime:
    return datetime.now(pytz.timezone(config.timezone))


def date_string(date: Union[datetime, None] = None) -> str:
    return (date or datetime_now()).strftime("%Y/%m/%d")


def filename_date_string(date: Union[datetime, None] = None) -> str:
    return (date or datetime_now()).strftime("%Y-%m-%d")


def display_date_string(date: Union[datetime, None] = None) -> str:
    return (date or datetime_now()).strftime("%B %-d, %Y")


def prefill_facility_link(base_url: str, id_: str) -> str:
    return f"{base_url}?prefill_Facility={id_}"


def mkdirp(dirpath: str) -> None:
    return pathlib.Path(dirpath).mkdir(parents=True, exist_ok=True)


def safe_list_convert(value: Any) -> Any:
    if isinstance(value, list):
        return ", ".join(value)
    return value
