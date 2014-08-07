import sys
import masters.brewcommander
import masters.defaults
import masters.messages

ip = masters.defaults.MessageServerIP
port = masters.defaults.MessageServerPort

commander = masters.brewcommander.BrewCommander(ip, port)


def getcommand():
    print('Enter command: ')
    line = sys.stdin.readline().rstrip()
    cmd = line
    param = ''
    if line.__contains__(' '):
        index = line.find(' ')
        cmd = line[:index]
        param = line[(index + 1):]
    return cmd, param


command, worker = getcommand()
while command.upper() != 'EXIT':
    if command.upper() == masters.messages.MessageLoad:
        command = masters.messages.MessageLoad
        if worker is None or worker == '':
            print('Enter recipe name: ')
            worker = sys.stdin.readline().rstrip()
    commander.sendmaster(command, worker)
    command, worker = getcommand()