from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
import os

conf = ConnectionConfig(
    MAIL_USERNAME="daniel.arteagafajar@campusucc.edu.co",
    MAIL_PASSWORD="kxymqzsxytpvzqby",
    MAIL_FROM="daniel.arteagafajar@campusucc.edu.co",
    MAIL_PORT=587,
    MAIL_SERVER="smtp.office365.com",
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
)
