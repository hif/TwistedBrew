#!/usr/bin python
from time import mktime

def datetime_to_ms_str(dt):
    return str(1000*mktime(dt.timetuple()))

def datetime_to_ms(dt):
    return 1000*mktime(dt.timetuple())
