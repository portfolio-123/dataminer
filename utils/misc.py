import datetime
import re


date_regex = re.compile('\\d{1,2}/\\d{1,2}/(\\d{2}|\\d{4})')


def is_list(i):
    return isinstance(i, list)


def is_int(i):
    return isinstance(i, int)


def is_str(i):
    return isinstance(i, str)


def is_float(i):
    return isinstance(i, float)


def is_number(i):
    return isinstance(i, int) or isinstance(i, float)


def is_date(i):
    return isinstance(i, datetime.date)


def is_dict(i):
    return isinstance(i, dict)


def is_bool(b):
    return isinstance(b, bool)


def coalesce(var, default):
    return var if var is not None else default


def round_or_none(val, precision=2):
    if val is not None:
        val = round(val, precision)
    return val


def parse_date(val):
    if is_str(val) and date_regex.fullmatch(val):
        val = val.split('/')
        if len(val[0]) == 1:
            val[0] = '0' + val[0]
        if len(val[1]) == 1:
            val[1] = '0' + val[1]
        val = datetime.datetime.strptime('/'.join(val), '%m/%d/%Y' if len(val[2]) == 4 else '%m/%d/%y')
    return val if is_date(val) else None
