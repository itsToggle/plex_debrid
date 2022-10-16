
from base import *
#import child modules
from content.services import plex
from content.services import trakt
from content.services import overseerr

#define subclass method
def __subclasses__():
    return [plex,trakt,overseerr]

active = ['Plex', 'Trakt', 'Overseerr']

def setup(cls, new=False):
    from settings import settings_list
    global active
    settings = []
    for category, allsettings in settings_list:
        for setting in allsettings:
            if setting.cls == cls or setting.name == cls.name + ' auto remove':
                settings += [setting]
    back = False
    if not new:
        while not back:
            print("0) Back")
            indices = []
            for index, setting in enumerate(settings):
                print(str(index + 1) + ') ' + setting.name)
                indices += [str(index + 1)]
            print()
            choice = input("Choose an action: ")
            if choice in indices:
                settings[int(choice) - 1].input()
                if not cls.name in active:
                    active += [cls.name]
                back = True
            elif choice == '0':
                back = True
    else:
        print()
        indices = []
        for setting in settings:
            if not setting.name == cls.name + ' auto remove':
                setting.setup()
                if not cls.name in active:
                    active += [cls.name]

def get():
    cls = sys.modules[__name__]
    activeservices = []
    for servicename in active:
        for service in cls.__subclasses__():
            if service.name == servicename:
                activeservices += [service]
    return activeservices
