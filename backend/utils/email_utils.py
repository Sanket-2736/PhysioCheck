import os
import aiosmtplib
from email.message import EmailMessage
from dotenv import load_dotenv

load_dotenv()


SMTP_HOST = os.getenv("SMTP_HOST")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USERNAME = os.getenv("SMTP_USERNAME")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
SMTP_FROM = os.getenv("SMTP_FROM", SMTP_USERNAME)


async def send_email(to: str, subject: str, html_content: str, attachments: list = None):
    """
    Send email using SMTP (Gmail, Outlook, Zoho, Custom SMTP)
    Supports HTML & attachments.
    """

    msg = EmailMessage()
    msg["From"] = SMTP_FROM
    msg["To"] = to
    msg["Subject"] = subject
    msg.set_content("Your email client does not support HTML")
    msg.add_alternative(html_content, subtype="html")

    # Attach files if provided
    if attachments:
        for file in attachments:
            file_content = file["content"]
            file_name = file["filename"]
            mime_type = file.get("mime_type", "application/octet-stream")

            maintype, subtype = mime_type.split("/", 1)
            msg.add_attachment(
                file_content,
                maintype=maintype,
                subtype=subtype,
                filename=file_name
            )

    try:
        await aiosmtplib.send(
            msg,
            hostname=SMTP_HOST,
            port=SMTP_PORT,
            username=SMTP_USERNAME,
            password=SMTP_PASSWORD,
            start_tls=True
        )
        return {"success": True, "message": "Email sent successfully"}
    
    except Exception as e:
        return {"success": False, "message": str(e)}
