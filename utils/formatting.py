import humanize
import datetime as dt
from .assets import config

def humanizeSeconds(n):
    return humanize.precisedelta(dt.timedelta(seconds=float(n)),minimum_unit=config.MINIMUM_TIME_UNIT)

def humanizeNumber(n):
    n=int(n)
    if n < 11: n = humanize.apnumber(n)
    elif n > 999: n = humanize.intword(n,"%0.2f")
    return n
