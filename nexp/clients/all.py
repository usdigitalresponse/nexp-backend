# nexp.clients.all

from typing import Union

from nexp.clients.data import Data
from nexp.clients.email import Email
from nexp.clients.blobs import Blobs


class Clients:
    """Hang onto all of the clients our tasks need"""

    def __init__(
        self,
        data: Union[Data, None] = None,
        email: Union[Email, None] = None,
        blobs: Union[Blobs, None] = None,
    ) -> None:
        self.data = data or Data()
        self.email = email or Email()
        self.blobs = blobs or Blobs()
