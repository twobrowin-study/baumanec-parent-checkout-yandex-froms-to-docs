import os
from email.header import Header
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from smtplib import SMTP_SSL

SMTP_ADDRESS = os.environ["SMTP_ADDRESS"]
SMTP_PORT = int(os.environ["SMTP_PORT"])
SMTP_LOGIN = os.environ["SMTP_LOGIN"]
SMTP_PASSWORD = os.environ["SMTP_PASSWORD"]


def mail_send_documents(issue: dict, documents: dict):
    """
    Высылает документы по почте
    """
    mail_message = MIMEMultipart()
    mail_message["Subject"] = issue["mail_subject"]
    mail_message["From"] = (
        f"{Header(issue['mail_from_alias']).encode()} <{issue['mail_from_mail']}>"
    )
    mail_message["To"] = issue["mail_to"]

    mail_message.attach(MIMEText(issue["mail_text"], "html", _charset="utf8"))

    for filename, document in documents.items():
        part = MIMEApplication(document, Name=filename)
        part["Content-Disposition"] = f'attachment; filename="{filename}"'
        mail_message.attach(part)

    smtp = SMTP_SSL(SMTP_ADDRESS, SMTP_PORT)
    smtp.login(SMTP_LOGIN, SMTP_PASSWORD)
    smtp.send_message(mail_message)
