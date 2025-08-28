import os
from dotenv import load_dotenv

from fastapi_mail import FastMail, MessageSchema, ConnectionConfig

load_dotenv()

# FastMail configuration
mail_conf = ConnectionConfig(
    MAIL_USERNAME=os.getenv("MAIL_USERNAME"),
    MAIL_PASSWORD=os.getenv("MAIL_APP_PASSWORD"),
    MAIL_FROM=os.getenv("MAIL_FROM"),
    MAIL_PORT=587,
    MAIL_SERVER="smtp.gmail.com",
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
)

fastmail = FastMail(mail_conf)

class EmailServices:
    @staticmethod
    async def send_email(
        subject: str,
        recipients: list[str],
        body: str,
        subtype: str,
        attachments: list[dict],
    ) -> tuple[bool, str]:
        try:
            message = MessageSchema(
                subject=subject,
                recipients=recipients,
                body=body,
                subtype=subtype,
                attachments=attachments
            )
            await fastmail.send_message(message)
            return True, "Email sent."
        except Exception as e:
            # TODO - log error
            return False, str(e)