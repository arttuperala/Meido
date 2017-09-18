from flask import request
from pathlib import Path
from sqlalchemy.exc import SQLAlchemyError
from urllib.parse import urlparse, urljoin

from meido.database import db
from meido.extensions import sentry


def commit_or_rollback() -> bool:
    """Attempts to commit the current session and rollbacks on SQLAlchemy errors. Reports
    all database commit errors to Sentry. Returns True if the commit was successful.
    """
    success = True
    try:
        db.session.commit()
    except SQLAlchemyError:  # pragma: no cover
        sentry.captureException()
        db.session.rollback()
        success = False
    return success


def extension_from_filename(filename: str) -> str:
    """Returns the extension for given filename. Returns two suffixes for .gz extensions
    if such is possible.
    """
    suffixes = Path(filename).suffixes
    if len(suffixes) > 1 and suffixes[-1] == '.gz' and suffixes[-1][0] == '.':
        return ''.join(suffixes[-2:])
    return suffixes[-1]


def is_safe_url(target: str) -> bool:
    """Checks if the given URL will lead to the same server and is thus safe to use for
    redirects.
    """
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc
