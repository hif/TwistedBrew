#!/usr/bin python
from web.models import Message
from datetime import datetime as dt

LOG_RECEIVER_DB = 1
LOG_RECEIVER_STD = 2
LOG_RECEIVER_BOTH = 3
LOG_RECEIVER = LOG_RECEIVER_BOTH

# Change to False to disable debugging messages
DEBUG_BREW = True
# Debug message types
DEBUG = 'd'
INFO = 'i'
WARNING = 'w'
ERROR = 'e'
LOG_TYPE_TEXT = {DEBUG: 'Debug', INFO: 'Info', WARNING: 'Warning', ERROR: 'Error'}


def log_message(msg, type):
    try:
        umsg = unicode(msg)
    except:
        umsg = msg.decode('utf-8')
    if LOG_RECEIVER == LOG_RECEIVER_BOTH or LOG_RECEIVER == LOG_RECEIVER_STD:
        print(u'[{0}] {1}'.format(type, umsg))
    if LOG_RECEIVER == LOG_RECEIVER_BOTH or LOG_RECEIVER == LOG_RECEIVER_DB:
        db_item = Message()
        db_item.timestamp = dt.now()
        db_item.type = LOG_TYPE_TEXT[type]
        db_item.text = umsg
        db_item.save()


def debug(message):
    if not DEBUG_BREW:
        return
    log_message(message, DEBUG)


def info(message):
    log_message(message, INFO)


def warning(message):
    log_message(message, WARNING)


def error(message):
    log_message(message, ERROR)
