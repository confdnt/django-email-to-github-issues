import requests
from django.core.mail import send_mail
from django.conf import settings
from .models import GitHubIssueReporter
import os
import base64

GITHUB_TOKEN = settings.GITHUB_TOKEN_E2GH
GITHUB_REPO = settings.GITHUB_REPO_E2GH


def upload_attachment_to_issue(issue_number, filename, file_data):
    """Uploads the attachment to the GitHub repository as a blob and links it in the issue."""

    # Step 1: Create a blob in the repository to store the attachment
    headers = {
        'Authorization': f'token {GITHUB_TOKEN}',
        'Accept': 'application/vnd.github+json'
    }

    # Convert the file data to base64 as required by GitHub's blob API
    encoded_content = base64.b64encode(file_data).decode('utf-8')

    blob_data = {
        "content": encoded_content,
        "encoding": "base64"
    }

    # API URL for creating a blob
    blob_url = f"https://api.github.com/repos/{GITHUB_REPO}/git/blobs"

    response = requests.post(blob_url, json=blob_data, headers=headers)

    if response.status_code == 201:
        blob_sha = response.json()['sha']

        # Step 2: Create a link to the blob in the issue
        attachment_url = f"https://github.com/{GITHUB_REPO}/blob/{blob_sha}/{filename}"

        comment_body = f"Attachment [{filename}]({attachment_url}) uploaded."

        # Post the comment with the attachment link to the issue
        comment_url = f"https://api.github.com/repos/{GITHUB_REPO}/issues/{issue_number}/comments"
        comment_data = {
            "body": comment_body
        }

        comment_response = requests.post(comment_url, json=comment_data, headers=headers)

        if comment_response.status_code == 201:
            print(f"Attachment '{filename}' successfully uploaded and linked to issue #{issue_number}.")
        else:
            print(f"Failed to comment on issue #{issue_number} with attachment: {comment_response.content}")
    else:
        print(f"Failed to upload attachment '{filename}' to the repository: {response.content}")


def create_github_issue(subject, body, attachments, sender_email):
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
        save_reporter_email(issue_number, sender_email)  # Use correct reporter's email

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
                from_email='bugs@support.confdnt.com',
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
