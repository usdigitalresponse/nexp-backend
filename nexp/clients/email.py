# nexp.clients.email

import logging
from typing import Union

from sendgrid import SendGridAPIClient

from nexp.aliases import OptionalString
from nexp.config import config


class Email:
    def __init__(self, client: Union[SendGridAPIClient, None] = None) -> None:
        self.__client = client or SendGridAPIClient(config.sendgrid_api_key)

    def send_transactional_template(
        self,
        to_email: str,
        from_email: str,
        template_id: str,
        asm_group_id: str,
        template_data: dict,
        reply_to: OptionalString = None,
    ) -> None:
        """Send a transaction templated email"""
        # why would yapf do this?...
        if config.override_email_destination:
            to_email = str(config.override_email_destination)

        data = {
            "personalizations": [
                {"to": [{"email": to_email}], "dynamic_template_data": template_data}
            ],
            "from": {"email": from_email,},
            "reply_to": {"email": reply_to or from_email,},
            "asm": {"group_id": int(asm_group_id)},
            "template_id": template_id,
        }

        try:
            response = self.__client.client.mail.send.post(request_body=data)
            assert 200 <= response.status_code < 300
        except Exception as e:
            if (
                hasattr(e, "status_code")
                and hasattr(e, "body")
                and hasattr(e, "headers")
            ):
                logging.exception(f"Failed sending email. (status_code: {e.status_code}; body: {e.body})")  # type: ignore
                print(e.status_code)  # type: ignore
                print(e.body)  # type: ignore
                print(e.headers)  # type: ignore
            raise e
