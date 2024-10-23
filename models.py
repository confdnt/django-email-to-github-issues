from django.db import models

class GitHubIssueReporter(models.Model):
    issue_number = models.IntegerField(unique=True)
    reporter_email = models.EmailField()

    def __str__(self):
        return f"Issue #{self.issue_number} - {self.reporter_email}"
