"""RandoPony app credentials.

Put real credential strings in :mod:`private_credentials` module and
exclude it from VCS tracking so that credentials won't be committed.
"""
import logging

log = logging.getLogger(__name__)


persona_secret = None

google_docs_username = None
google_docs_password = None

email_host_username = None
email_host_password = None

try:
    from .private_credentials import (
        persona_secret,
        google_docs_username,
        google_docs_password,
        email_host_username,
        email_host_password,
        )
except ImportError:
    log.error('private_credentials.py module missing or incomplete')