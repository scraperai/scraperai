import logging

from aiosmtplib import SMTP, SMTPException
from settings import SMTP_HOST, SMTP_PASSWORD, SMTP_USER, SMTP_PORT


logger = logging.getLogger(__file__)


async def send_email(email: str, subject: str, body: str):
    message = f"Subject: {subject}\n\n{body}"
    try:
        async with SMTP(hostname=SMTP_HOST, port=SMTP_PORT) as smtp:
            await smtp.starttls()
            await smtp.login(SMTP_USER, SMTP_PASSWORD)
            await smtp.sendmail(SMTP_USER, email, message)
    except SMTPException as e:
        logger.error(e)
