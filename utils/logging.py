# Change to False to diable debugging messages
DEBUG_BREW = True
# Debug message types
INFO = 'i'
WARNING = 'w'
ERROR = 'e'


def logmessage(msg):
    print(msg)


def debug(message, messagetype=INFO):
    if not DEBUG_BREW:
        return
    logmessage(u'[{0}] {1}'.format(messagetype, message))


def error(message):
    logmessage(u'[{0}] {1}'.format(ERROR, message))
