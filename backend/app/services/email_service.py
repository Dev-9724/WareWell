import os
import smtplib
from email.message import EmailMessage


def send_password_reset_email(to_email: str, reset_link: str) -> None:
    smtp_host = os.getenv("SMTP_HOST", "")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_username = os.getenv("SMTP_USERNAME", "")
    smtp_password = os.getenv("SMTP_PASSWORD", "")
    email_from = os.getenv("EMAIL_FROM", smtp_username)

    if not smtp_host or not smtp_username or not smtp_password or not email_from:
        raise RuntimeError("Email settings are not configured correctly.")

    message = EmailMessage()
    message["Subject"] = "WareWell Password Reset"
    message["From"] = email_from
    message["To"] = to_email

    message.set_content(
        f"""Hello,

We received a request to reset your WareWell password.

Use the link below to set a new password:
{reset_link}

This link will expire soon. If you did not request this, you can safely ignore this email.

Regards,
WareWell
"""
    )

    with smtplib.SMTP(smtp_host, smtp_port) as server:
        server.starttls()
        server.login(smtp_username, smtp_password)
        server.send_message(message)