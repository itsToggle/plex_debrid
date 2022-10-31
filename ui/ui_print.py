from base import *

from ui import ui_settings

sameline = False

def ui_cls(path=''):
    os.system('cls' if os.name == 'nt' else 'clear')
    logo(path=path)

def logo(path=''):
    print('                                                         ')
    print('           __                  __     __         _     __')
    print('    ____  / /__  _  __    ____/ /__  / /_  _____(_)___/ /')
    print('   / __ \/ / _ \| |/_/   / __  / _ \/ __ \/ ___/ / __  / ')
    print('  / /_/ / /  __/>  <    / /_/ /  __/ /_/ / /  / / /_/ /  ')
    print(' / .___/_/\___/_/|_|____\__,_/\___/_.___/_/  /_/\__,_/   ')
    print('/_/               /_____/                         [v' + ui_settings.version[0] + ']')
    print()
    print(path)
    print()
    sys.stdout.flush()

def ui_print(string: str, debug="true"):
    global sameline
    if debug == "true":
        if string == 'done' and sameline:
            print('done')
            sameline = False
        elif sameline and string.startswith('done'):
            print(string)
            sameline = False
        elif sameline and string.endswith('...'):
            print('done')
            print('[' + str(datetime.datetime.now().strftime("%d/%m/%y %H:%M:%S")) + '] ' + string, end=' ')
            sameline = True
        elif string.endswith('...'):
            print('[' + str(datetime.datetime.now().strftime("%d/%m/%y %H:%M:%S")) + '] ' + string, end=' ')
            sameline = True
        elif not string.startswith('done') and sameline:
            print('done')
            print('[' + str(datetime.datetime.now().strftime("%d/%m/%y %H:%M:%S")) + '] ' + string)
            sameline = False
        elif not string.startswith('done'):
            print('[' + str(datetime.datetime.now().strftime("%d/%m/%y %H:%M:%S")) + '] ' + string)
            sameline = False
        sys.stdout.flush()
