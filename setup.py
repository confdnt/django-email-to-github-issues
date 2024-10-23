from setuptools import setup, find_packages

setup(
    name='django-email-to-github-issues',
    version='0.9.1',
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
    url='https://github.com/confdnt/django-email-to-github-issues',
    classifiers=[
        'Framework :: Django',
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.9',
)
