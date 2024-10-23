import imaplib
import email
import re
import os
from email.header import decode_header
import requests
from celery import shared_task
from django.core.mail import send_mail
from .models import GitHubIssueReporter
from .utils import create_github_issue, reopen_github_issue, extract_attachments_from_email
from django.conf import settings
from email.utils import parseaddr


@shared_task
def fetch_and_create_github_issue():
    # Email server settings from environment variables
    EMAIL_HOST = settings.EMAIL_HOST_E2GH
    EMAIL_PORT = settings.EMAIL_PORT_E2GH
    EMAIL_USERNAME = settings.EMAIL_USERNAME_E2GH
    EMAIL_PASSWORD = settings.EMAIL_PASSWORD_E2GH

    # Connect to the email server
    mail = imaplib.IMAP4_SSL(EMAIL_HOST, EMAIL_PORT)
    mail.login(EMAIL_USERNAME, EMAIL_PASSWORD)
    mail.select("INBOX")  # Choose the folder

    # Search for all emails in the inbox
    status, messages = mail.search(None, 'ALL')
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
                issue_body = ""

                # Check if the email is multipart (it usually is)
                if msg.is_multipart():
                    # Iterate through each part of the email
                    for part in msg.walk():
                        # If the part is the plain text part, extract it
                        if part.get_content_type() == "text/plain":
                            body = part.get_payload(decode=True).decode(part.get_content_charset() or 'utf-8')
                            issue_body += body
                else:
                    # If the email isn't multipart, just get the payload
                    issue_body = msg.get_payload(decode=True).decode(msg.get_content_charset() or 'utf-8')

                if match:
                    issue_number = int(match.group(1))
                    reopen_github_issue(issue_number)
                else:
                    from_ = msg.get("From")
                    email_address = parseaddr(from_)[1]
                    issue_body = f"{issue_body}"
                    attachments = extract_attachments_from_email(msg)
                    create_github_issue(subject, issue_body, attachments, email_address)

                # Mark email for deletion after processing
                mail.store(num, '+FLAGS', '\\Deleted')

    # Permanently delete the marked emails
    mail.expunge()
    mail.logout()
