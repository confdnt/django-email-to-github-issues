from setuptools import setup, find_packages

setup(
    name='django-email-to-github-issues',
    version='0.9',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'Django>=3.2',
        'celery>=5.0',
        'requests',
        'imaplib2',
    ],
    license='MIT',
    description='Django app to create GitHub issues from emails, with attachments.',
    author='David Klement',
    author_email='d.klement@compliance.one',
    url='https://github.com/yourusername/django-email-to-github-issues',
)