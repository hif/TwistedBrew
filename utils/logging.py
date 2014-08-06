# Change to False to diable debugging messages
DEBUG_BREW = True
# Debug message types
INFO = 'i'
WARNING = 'w'
ERROR = 'e'

def logMessage(msg):
    print(msg)

def debug(message, type=INFO):
    if(not DEBUG_BREW):
        return
    logMessage('[{0}] {1}'.format(type, str(message)))


def error(message):
    message('[{0}] {1}'.format(ERROR, str(message)))
