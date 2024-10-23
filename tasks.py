# emailtogithub/tasks.py
import imaplib
import email
import re
from email.header import decode_header
import requests
from celery import shared_task
from django.core.mail import send_mail
from .models import GitHubIssueReporter
from .utils import create_github_issue, reopen_github_issue, extract_attachments_from_email

@shared_task
def fetch_and_create_github_issue():
    # Email server settings from environment variables
    EMAIL_HOST = os.getenv('EMAIL_HOST')
    EMAIL_PORT = os.getenv('EMAIL_PORT')
    EMAIL_USERNAME = os.getenv('EMAIL_USERNAME')
    EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')

    # Connect to the email server
    mail = imaplib.IMAP4_SSL(EMAIL_HOST, EMAIL_PORT)
    mail.login(EMAIL_USERNAME, EMAIL_PASSWORD)
    mail.select("inbox")  # Choose the folder

    # Search for unread emails
    status, messages = mail.search(None, '(UNSEEN)')
    if status == 'OK':
        for num in messages[0].split():
            status, msg_data = mail.fetch(num, '(RFC822)')
            if status == 'OK':
                msg = email.message_from_bytes(msg_data[0][1])
                subject, encoding = decode_header(msg["Subject"])[0]
                if isinstance(subject, bytes):
                    subject = subject.decode(encoding or 'utf-8')

                # Check if the subject contains an issue number like #123
                match = re.search(r'#(\d+)', subject)
                if match:
                    issue_number = int(match.group(1))
                    reopen_github_issue(issue_number)
                else:
                    from_ = msg.get("From")
                    issue_body = f"New email from {from_}\n\nSubject: {subject}"
                    attachments = extract_attachments_from_email(msg)
                    create_github_issue(subject, issue_body, attachments)

    mail.logout()
