import logging
import os
import smtplib

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

error_logger = logging.getLogger("error_logger")

def email_admin(e):
    send_mail(name="Admin", user_email=os.environ.get("mail_username"), message=f"Irrecoverable error from OpenAI: {e}")
    
def send_mail(name: str, user_email: str, message: str) -> None:
    """
    Send user the pdf of their story bible.

    Arguments:
        folder_name: Name of the folder containing the story bible.
        book_name: Name of the book.
        user_email: Email address of the user.
    """

    password = os.environ.get('mail_password')
    username = os.environ.get('mail_username')

    server = "server310.web-hosting.com"
    port = 465

    email_body = f"Name: {name}\nMessage: {message}"

    try:
        s = smtplib.SMTP_SSL(host=server, port=port)
        s.login(username, password)

        msg = MIMEMultipart()
        msg["To"] =    username
        msg["From"] = username
        msg["Reply-To"] = user_email
        msg["Subject"] = "Contact form submission"
        msg.attach(MIMEText(email_body, "html"))
        s.send_message(msg)
    except Exception as e:
        error_logger.exception(f"Failed to send email. Reason: {e}")
        print(f"Failed to send email. Reason: {e}")
