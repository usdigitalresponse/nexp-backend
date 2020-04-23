# nexp.utils

from typing import Union
from datetime import datetime
import pathlib

import pytz

from nexp.config import config


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
