#!/usr/bin python
from time import mktime
from datetime import datetime



def datetime_to_ms_str(dt):
    return str(1000*mktime(dt.timetuple()))


def datetime_to_ms(dt):
    return 1000*mktime(dt.timetuple())

def ms_to_datetime(dt):
    return datetime.fromtimestamp(dt/1000)