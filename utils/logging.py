#!/usr/bin python

# Change to False to diable debugging messages
DEBUG_BREW = True
# Debug message types
INFO = 'i'
WARNING = 'w'
ERROR = 'e'


def log_message(msg):
    print(msg)


def debug(message, messagetype=INFO):
    if not DEBUG_BREW:
        return
    try:
        log_message(u'[{0}] {1}'.format(messagetype, message))
    except:
        log_message(u'[{0}] {1}'.format(messagetype, message.decode('utf-8')))

def error(message):
    message = message.encode('utf-8')
    try:
        log_message(u'[{0}] {1}'.format(ERROR, message))
    except:
        log_message(u'[{0}] {1}'.format(ERROR, message.decode('utf-8')))
