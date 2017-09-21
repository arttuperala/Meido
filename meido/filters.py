from datetime import datetime
from humanize import naturaldelta
from PIL import ImageFont


def deltatime(value):
    return naturaldelta(datetime.utcnow() - value)


def text_width(value):
    return ImageFont.truetype('DejaVuSans.ttf', 11).getsize(value)[0]


__all__ = [deltatime, text_width]
