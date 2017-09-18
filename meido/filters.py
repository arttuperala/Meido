from datetime import datetime
from humanize import naturaldelta


def deltatime(value):
    return naturaldelta(datetime.utcnow() - value)

__all__ = [deltatime]
