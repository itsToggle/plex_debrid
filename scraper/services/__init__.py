from base import *
#import child modules
from scraper.services import rarbg
from scraper.services import x1337
from scraper.services import jackett
from scraper.services import prowlarr
from scraper.services import orionoid

#define subclass method
def __subclasses__():
    return [rarbg,x1337,jackett,prowlarr,orionoid]

active = ['rarbg', '1337x', ]

def setup(cls, new=False):
    from settings import settings_list
    global active
    settings = []
    for category, allsettings in settings_list:
        for setting in allsettings:
            if setting.cls == cls:
                settings += [setting]
    if settings == []:
        if not cls.name in active:
            active += [cls.name]
    back = False
    if not new:
        while not back:
            print("0) Back")
            indices = []
            for index, setting in enumerate(settings):
                print(str(index + 1) + ') ' + setting.name)
                indices += [str(index + 1)]
            print()
            if settings == []:
                print("Nothing to edit!")
                print()
                time.sleep(3)
                return
            choice = input("Choose an action: ")
            if choice in indices:
                settings[int(choice) - 1].setup()
                if not cls.name in active:
                    active += [cls.name]
                back = True
            elif choice == '0':
                back = True
    else:
        print()
        indices = []
        for setting in settings:
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