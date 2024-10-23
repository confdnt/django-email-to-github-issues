import json
import os
import hmac
import hashlib
from django.core.mail import send_mail
from django.http import JsonResponse, HttpResponseBadRequest
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from .models import GitHubIssueReporter

GITHUB_SECRET = settings.GITHUB_WEBHOOK_SECRET_E2GH
DEFAULT_EMAIL = settings.DEFAULT_EMAIL_E2GH

@csrf_exempt
def github_webhook(request):
    """Handle GitHub webhook events for issue closures and comments."""
    if request.method == 'POST':
        # Validate the webhook secret if provided
        if GITHUB_SECRET:
            signature = request.headers.get('X-Hub-Signature-256')
            if not validate_signature(signature, request.body, GITHUB_SECRET):
                return HttpResponseBadRequest('Invalid signature')

        # Parse the JSON payload from GitHub
        payload = json.loads(request.body.decode('utf-8'))
        action = payload.get('action')
        issue_data = payload.get('issue')
        comment_data = payload.get('comment')

        if issue_data:
            issue_number = issue_data['number']
            issue_title = issue_data['title']

            # Handle issue closure
            if action == 'closed':
                handle_issue_closed(issue_number, issue_title)

            # Handle new comments on the issue
            if action == 'created' and comment_data:
                comment_body = comment_data['body']
                handle_issue_comment(issue_number, issue_title, comment_body)

        return JsonResponse({'status': 'success'})

    return HttpResponseBadRequest('Only POST requests are accepted.')

def validate_signature(signature, payload_body, secret):
    """Validate the webhook signature from GitHub."""
    if not signature:
        return False
    sha_name, signature = signature.split('=')
    if sha_name != 'sha256':
        return False
    mac = hmac.new(bytes(secret, 'utf-8'), msg=payload_body, digestmod=hashlib.sha256)
    return hmac.compare_digest(mac.hexdigest(), signature)

def handle_issue_closed(issue_number, issue_title):
    """Send an email to the reporter when an issue is closed."""
    try:
        # Fetch the reporter's email from the database
        reporter = GitHubIssueReporter.objects.get(issue_number=issue_number)
        reporter_email = reporter.reporter_email

        # Compose the email
        subject = f"Issue #{issue_number} Closed: {issue_title}"
        message = f"Hello,\n\nThe issue you reported (#{issue_number}: {issue_title}) has been closed.\n\nThank you for your feedback."

        # Send the email
        send_mail(
            subject=subject,
            message=message,
            from_email=DEFAULT_EMAIL,
            recipient_list=[reporter_email],
        )
        print(f"Email sent to {reporter_email} for closed issue #{issue_number}.")
    except GitHubIssueReporter.DoesNotExist:
        print(f"Reporter for issue #{issue_number} not found.")

def handle_issue_comment(issue_number, issue_title, comment_body):
    """Send an email to the reporter when a new comment is posted on an issue."""
    try:
        # Fetch the reporter's email from the database
        reporter = GitHubIssueReporter.objects.get(issue_number=issue_number)
        reporter_email = reporter.reporter_email

        # Compose the email
        subject = f"New Comment on Issue #{issue_number}: {issue_title}"
        message = f"Hello,\n\nA new comment has been posted on the issue you reported (#{issue_number}: {issue_title}).\n\nComment:\n{comment_body}"

        # Send the email
        send_mail(
            subject=subject,
            message=message,
            from_email=DEFAULT_EMAIL,
            recipient_list=[reporter_email],
        )
        print(f"Email sent to {reporter_email} for comment on issue #{issue_number}.")
    except GitHubIssueReporter.DoesNotExist:
        print(f"Reporter for issue #{issue_number} not found.")
