import re

def parse_time(time_str):
    match = re.match(r"(\d+)([smhd])", time_str)
    if match:
        value, unit = match.groups()
        value = int(value)
        if unit == 's':
            return value
        elif unit == 'm':
            return value * 60
        elif unit == 'h':
            return value * 3600
        elif unit == 'd':
            return value * 86400
    return None

def parse_minutes_seconds(time_str):
    match = re.match(r"(\d+):(\d+)", time_str)
    if match:
        minutes, seconds = match.groups()
        return int(minutes) * 60 + int(seconds)
    return None



def format_datetime(dt):
    return dt.strftime("%d %B %Y, %H:%M")