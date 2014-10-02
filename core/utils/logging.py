#!/usr/bin python
from twisted_brew.models import Message
from django.utils import timezone as dt
import threading

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


message_lock = threading.Lock()


def log_message(msg, msg_type, only_std=False):
    try:
        try:
            umsg = unicode(msg)
        except:
            umsg = msg.decode('utf-8')
        if only_std or LOG_RECEIVER == LOG_RECEIVER_BOTH or LOG_RECEIVER == LOG_RECEIVER_STD:
            print(u'[{0}] {1}'.format(msg_type, umsg))
        if not only_std and (LOG_RECEIVER == LOG_RECEIVER_BOTH or LOG_RECEIVER == LOG_RECEIVER_DB):
            try:
                with message_lock:
                    db_item = Message()
                    db_item.timestamp = dt.now()
                    db_item.type = LOG_TYPE_TEXT[msg_type]
                    db_item.text = umsg
                    db_item.save()
            except Exception as e:
                log_message('Logger could not save message to database ({0})'.format(e.args[0]), ERROR, True)
    except Exception as e:
        if e.message == "Unable to log Debug message: global name 'Error' is not defined":
            print 'hey you'
        log_message('Unable to log {0} message: {1}'.format(LOG_TYPE_TEXT[msg_type], e.args[0]), ERROR)


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
