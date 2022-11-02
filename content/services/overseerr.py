#import modules
from base import *
#import parent modules
from content import classes
from content.services import plex
from content.services import trakt
from ui.ui_print import *

name = 'Overseerr'
base_url = "http://localhost:5055"
users = ['all']
allowed_status = [['2'], ]
api_key = ""
session = requests.Session()

def setup(self):
    global base_url
    global api_key
    global users
    global allowed_status
    global session
    from settings import settings_list
    ui_cls("Options/Settings/Content Services/Content Services/Overseerr")
    working_key = False
    working_url = False
    if len(plex.users) == 0 and len(trakt.users) == 0:
        print('Looks like you havent connected plex_debrid to any other content service! Please setup at least one other content service.')
        time.sleep(3)
        return
    try:
        response = session.get(base_url + '/api/v1/request',
                                            headers={"X-Api-Key": api_key}, timeout=0.5)
        if response.status_code == 200:
            working_key = True
            working_url = True
        else:
            working_key = False
            working_url = True
    except:
        working_url = False
    while not working_url:
        if base_url == "http://localhost:5055":
            print(
                "Looks like overseerr couldn't be reached under the default base url ('" + base_url + "').")
        else:
            print(
                "Looks like overseerr couldn't be reached under the current base url ('" + base_url + "').")
        print("Please make sure overseerr is running and try again, or provide your overseerr base URL below.")
        print("Please provide your overseerr base URL in the following format 'http://localhost:5055' or press enter to return to the main menu.")
        print()
        base_url = input("Please provide your overseerr base URL: ")
        if base_url == "":
            return
        working_key = False
        working_url = False
        try:
            response = session.get(base_url + '/api/v1/request',
                                                headers={"X-Api-Key": api_key}, timeout=0.5)
            if response.status_code == 200:
                working_key = True
                working_url = True
            else:
                working_key = False
                working_url = True
        except:
            working_url = False
    while not working_key:
        if api_key == "":
            print(
                "To setup overseerr, please provide your overseerr API Key. Press enter to return to the main menu.")
        else:
            print("Looks like your current API Key ('" + api_key + "') doesnt work.")
        print()
        api_key = input("Please enter your overseerr API Key: ")
        if api_key == "":
            return
        working_key = False
        working_url = False
        try:
            response = session.get(base_url + '/api/v1/request',
                                                headers={"X-Api-Key": api_key}, timeout=0.5)
            if response.status_code == 200:
                working_key = True
                working_url = True
            else:
                working_key = False
                working_url = True
        except:
            working_url = False
    settings = []
    for category, allsettings in settings_list:
        for setting in allsettings:
            if setting.cls == self or setting.name.startswith(self.name):
                settings += [setting]
    response = get(base_url + '/api/v1/user')
    users_ = response.results
    new_users = []
    for user in users_:
        if not user.displayName in users:
            new_users += [user.displayName]
    back = False
    ui_cls("Options/Settings/Content Services/Content Services/Overseerr")
    while not back:
        print("0) Back")
        indices = []
        for index, setting in enumerate(settings):
            print(str(index + 1) + ') ' + setting.name)
            indices += [str(index + 1)]
        print()
        choice = input("Choose an action: ")
        if choice in indices:
            if settings[int(choice) - 1].name == "Overseerr users":
                print()
                print("You can define which users approved requests should be downloaded by plex_debrid.")
                print()
                print('Currently monitored Overseerr users: "' + str(users) + '"')
                print()
                print('0) Back')
                print('1) Always monitor all users')
                print('2) Add user')
                if len(users) > 0 and not users == ['all']:
                    print('3) Remove user')
                print()
                choice = input('Choose an action: ')
                print()
                if choice == '1':
                    users = ['all']
                    return True
                elif choice == '2':
                    print(
                        "Choose which users approved requests should be downloaded by plex_debrid. Type 'all' to add all currently listed users.")
                    print()
                    i = 0
                    indices = []
                    add_user = []
                    print('0) Back')
                    for user in users_:
                        if not user.displayName in users:
                            print(str(i + 1) + ') ' + user.displayName)
                            indices += [str(i + 1)]
                            add_user += [user.displayName]
                            i += 1
                    print()
                    choice = input("Choose a user: ")
                    if choice == '0':
                        back = True
                    elif choice == 'all':
                        users += new_users
                        return True
                    elif choice in indices:
                        users += [add_user[int(choice) - 1]]
                        return True
                elif choice == '3':
                    indices = []
                    print("Choose a user to remove.")
                    print()
                    print('0) Back')
                    for index, user in enumerate(users):
                        print(str(index + 1) + ') ' + user)
                        indices += [str(index + 1)]
                    print()
                    choice = input("Choose a user: ")
                    if choice == '0':
                        back = True
                    elif choice in indices:
                        users.remove(users[int(choice) - 1])
                        return True
            else:
                settings[int(choice) - 1].input()
            back = True
        elif choice == '0':
            back = True

def logerror(response):
    if not response.status_code == 200:
        ui_print("[overseerr] error: " + str(response.content), debug=ui_settings.debug)
    if response.status_code == 401:
        ui_print("[overseerr] error: (401 unauthorized): overserr api key does not seem to work.")

def get(url):
    try:
        response = session.get(url, headers={
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36',
            'Content-type': "application/json", "X-Api-Key": api_key})
        logerror(response)
        response = json.loads(response.content, object_hook=lambda d: SimpleNamespace(**d))
    except Exception as e:
        ui_print("[overseerr] error: (exception): " + str(e), debug=ui_settings.debug)
        return None
    return response

def post(url, data):
    try:
        response = session.post(url, headers={
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36',
            'Content-type': "application/json", "X-Api-Key": api_key}, data=data)
        logerror(response)
        response = json.loads(response.content, object_hook=lambda d: SimpleNamespace(**d))
    except Exception as e:
        ui_print("[overseerr] error: (exception): " + str(e), debug=ui_settings.debug)
        return None
    return response

def setEID(self):
    EID = []
    if hasattr(self,"media"):    
        if hasattr(self.media,"imdbId"):
            if not self.media.imdbId == None:
                EID += ['imdb://' + str(self.media.imdbId)]
        if hasattr(self.media,"tmdbId"):
            if not self.media.tmdbId == None:
                EID += ['tmdb://' + str(self.media.tmdbId)]
        if hasattr(self.media,"tvdbId"):
            if not self.media.tvdbId == None:
                EID += ['tvdb://' + str(self.media.tvdbId)]
    return EID

class media(classes.media):
    def __init__(self, other):
        super().__init__(other)

class movie(classes.media):
    def __init__(self, other):
        self.__dict__.update(other.__dict__)
        self.EID = setEID(self)

class show(classes.media):
    def __init__(self, other):
        self.__dict__.update(other.__dict__)
        self.type = 'show'
        self.EID = setEID(self)
        self.Seasons = []
        if hasattr(self,'seasons'):
            for season in self.seasons:
                season.type = "season"
                season.index = season.seasonNumber
                season.parentEID = self.EID
                season.Episodes = []
                self.Seasons += [season]

class requests(classes.watchlist):

    def __init__(self):
        self.data = []
        if len(users) > 0 and len(api_key) > 0:
            ui_print('[overseerr] getting all overseerr requests ...')
            try:
                response = get(base_url + '/api/v1/request')
                for element in response.results:
                    if not element in self.data and (
                            element.requestedBy.displayName in users or users == ['all']) and [
                        str(element.status)] in allowed_status:
                        self.data.append(element)
            except:
                ui_print(
                    '[overseerr] error: looks like overseerr couldnt be reached. Turn on debug printing for more info.')
                self.data = []
            ui_print('done')

    def sync(self, other):
        add = []
        for element_ in self.data:
            element = copy.deepcopy(element_)
            if element.type == "movie":
                element = movie(element)
            elif element.type == "tv":
                element = show(element)
            element.match(other.__module__)
            element.watchlist = sys.modules[other.__module__].watchlist
            add += [element]
        for element in add:
            if not element in other:
                other.data.append(element)

    def update(self):
        if len(users) > 0 and len(api_key) > 0:
            refresh = False
            try:
                response = get(base_url + '/api/v1/request')
                for element in response.results:
                    if not element in self.data and (element.requestedBy.displayName in users or users == ['all']) and [str(element.status)] in allowed_status:
                        ui_print('[overseerr] found new overseerr request by user "' + element.requestedBy.displayName + '".')
                        refresh = True
                        self.data.append(element)
                for element in self.data[:]:
                    if not element in response.results:
                        self.data.remove(element)
                if refresh:
                    return True
            except:
                return False
        return False
