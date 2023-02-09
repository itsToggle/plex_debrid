from base import *

from ui import ui_settings

sameline = False
sameline_log = False
config_dir = "."

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

def set_log_dir(config):
    global config_dir
    config_dir = config

def ui_print(string: str, debug="true", end=""):
    global sameline
    global sameline_log
    try:
        #log
        if ui_settings.log == "true":
            try:
                with open(config_dir + '/plex_debrid.log', 'a') as f:
                    if string == 'done' and sameline_log:
                        f.write('done' + '\n')
                        sameline_log = False
                    elif sameline_log and string.startswith('done'):
                        f.write(string + '\n')
                        sameline_log = False
                    elif sameline_log and string.endswith('...'):
                        f.write('done' + '\n')
                        f.write('[' + str(datetime.datetime.now().strftime("%d/%m/%y %H:%M:%S")) + '] ' + string  + ' ')
                        sameline_log = True
                    elif string.endswith('...'):
                        f.write('[' + str(datetime.datetime.now().strftime("%d/%m/%y %H:%M:%S")) + '] ' + string + ' ')
                        sameline_log = True
                    elif not string.startswith('done') and sameline_log:
                        f.write('done' + '\n')
                        f.write('[' + str(datetime.datetime.now().strftime("%d/%m/%y %H:%M:%S")) + '] ' + string + '\n')
                        sameline_log = False
                    elif not string.startswith('done'):
                        f.write('[' + str(datetime.datetime.now().strftime("%d/%m/%y %H:%M:%S")) + '] ' + string + '\n')
                        sameline_log = False
            except:
                print('[' + str(datetime.datetime.now().strftime("%d/%m/%y %H:%M:%S")) + '] logging error: couldnt write into log file at: ' + config_dir + '/plex_debrid.log')
        #ui
        if end != "":
            print('[' + str(datetime.datetime.now().strftime("%d/%m/%y %H:%M:%S")) + '] ' + string, end=end)
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
    except:
        sys.stdout.flush()
