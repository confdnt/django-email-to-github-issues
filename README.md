
# Django Email to GitHub Issues

A reusable Django app that creates GitHub issues from incoming emails and can also reopen issues based on email replies.

## Features
- Fetch new emails and create GitHub issues.
- Attach email attachments to the GitHub issue.
- Include the GitHub issue number in email notifications.
- Reopen GitHub issues when users reply to the notification.

## Installation

### 1. Install the package:

       pip install django-email-to-github-issues

### 2. Add emailtogithub to INSTALLED_APPS in your Django project.

    INSTALLED_APPS = [
        # Other apps
        'emailtogithub',
    ]

### 3. Set up the necessary environment variables:

    GITHUB_TOKEN_E2GH=your_github_token
    GITHUB_REPO_E2GH=your_github_username/your_repo
    EMAIL_HOST_E2GH=imap.your-email-provider.com
    EMAIL_PORT_E2GH=993
    EMAIL_USERNAME_E2GH=your_email@example.com
    EMAIL_PASSWORD_E2GH=your_email_password

### 4.	Run migrations:

    python manage.py migrate

### License
```plaintext
MIT License
Build by Compliance.One GmbH with lots of AI and love in Munich.
