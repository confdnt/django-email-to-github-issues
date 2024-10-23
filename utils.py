import requests
from django.core.mail import send_mail
from .models import GitHubIssueReporter
import os

GITHUB_TOKEN = os.getenv('GITHUB_TOKEN_E2GH')
GITHUB_REPO = os.getenv('GITHUB_REPO_E2GH')

def create_github_issue(subject, body, attachments):
    headers = {
        'Authorization': f'token {GITHUB_TOKEN}',
        'Accept': 'application/vnd.github+json'
    }
    issue_data = {
        "title": subject,
        "body": body,
    }
    issue_url = f"https://api.github.com/repos/{GITHUB_REPO}/issues"
    response = requests.post(issue_url, json=issue_data, headers=headers)
    if response.status_code == 201:
        issue_number = response.json()['number']
        save_reporter_email(issue_number, "reporter@example.com")  # Use correct reporter's email

        for attachment in attachments:
            upload_attachment_to_issue(issue_number, attachment['filename'], attachment['data'])

def reopen_github_issue(issue_number):
    headers = {
        'Authorization': f'token {GITHUB_TOKEN}',
        'Accept': 'application/vnd.github+json'
    }
    issue_url = f"https://api.github.com/repos/{GITHUB_REPO}/issues/{issue_number}"
    issue_data = {"state": "open"}
    response = requests.patch(issue_url, json=issue_data, headers=headers)

    if response.status_code == 200:
        try:
            reporter = GitHubIssueReporter.objects.get(issue_number=issue_number)
            send_mail(
                subject=f"Issue #{issue_number} Reopened",
                message=f"The issue #{issue_number} has been reopened.",
                from_email='no-reply@yourapp.com',
                recipient_list=[reporter.reporter_email],
            )
        except GitHubIssueReporter.DoesNotExist:
            pass

def extract_attachments_from_email(msg):
    attachments = []
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_maintype() == 'multipart':
                continue
            if part.get('Content-Disposition') is None:
                continue
            filename = part.get_filename()
            if filename:
                attachments.append({
                    'filename': filename,
                    'data': part.get_payload(decode=True)
                })
    return attachments

def save_reporter_email(issue_number, reporter_email):
    GitHubIssueReporter.objects.create(issue_number=issue_number, reporter_email=reporter_email)
