#import modules
from base import *
#import parent modules
from content import classes
from content.services import plex
from content.services import trakt
from ui.ui_print import *

name = 'Overseerr'
base_url = ""
users = ['all']
allowed_movie_status = [['2'], ['3']]
allowed_show_status = [['2'], ['3'], ['4'], ['5']]
api_key = ""
session = requests.Session()
last_requests = []

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
        response = session.get(base_url + '/api/v1/request', headers={"X-Api-Key": api_key}, timeout=0.5)
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
            print("Looks like overseerr couldn't be reached under the default base url ('" + base_url + "').")
        else:
            print("Looks like overseerr couldn't be reached under the current base url ('" + base_url + "').")
        print("Please make sure overseerr is running and try again, or provide your overseerr base URL below.")
        print("Please provide your overseerr base URL in the following format 'http://localhost:5055' or press enter to return to the main menu.")
        print()
        base_url = input("Please provide your overseerr base URL: ")
        if base_url == "":
            return
        working_key = False
        working_url = False
        try:
            response = session.get(base_url + '/api/v1/request', headers={"X-Api-Key": api_key}, timeout=0.5)
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
            print("To setup overseerr, please provide your overseerr API Key. Press enter to return to the main menu.")
        else:
            print("Looks like your current API Key ('" + api_key + "') doesnt work.")
        print()
        api_key = input("Please enter your overseerr API Key: ")
        if api_key == "":
            return
        working_key = False
        working_url = False
        try:
            response = session.get(base_url + '/api/v1/request', headers={"X-Api-Key": api_key}, timeout=0.5)
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
    response = get(base_url + '/api/v1/user?take=10000')
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
        self.watchlistedAt = datetime.datetime.timestamp(datetime.datetime.strptime(self.updatedAt,'%Y-%m-%dT%H:%M:%S.000Z'))

class show(classes.media):
    def __init__(self, other):
        self.__dict__.update(other.__dict__)
        self.type = 'show'
        self.EID = setEID(self)
        self.watchlistedAt = datetime.datetime.timestamp(datetime.datetime.strptime(self.updatedAt,'%Y-%m-%dT%H:%M:%S.000Z'))
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
        global last_requests
        last_requests = []
        self.data = []
        if len(users) > 0 and len(api_key) > 0:
            ui_print('[overseerr] getting all overseerr requests ...')
            try:
                response = get(base_url + '/api/v1/request?take=10000')
                for element in response.results:
                    if not element in self.data and (element.requestedBy.displayName in users or users == ['all']) and ([str(element.media.status)] in allowed_movie_status if element.type == 'movie' else [str(element.media.status)] in allowed_show_status):
                        last_requests.append(element)
            except Exception as e:
                ui_print('[overseerr] error: ' + str(e), ui_settings.debug)
                ui_print('[overseerr] error: overseerr couldnt be reached. turn on debug printing for more info.')
                last_requests = []
            ui_print('done')
            if last_requests == []:
                return
            matching_service = ''
            if len(sys.modules['content.services.plex'].users) > 0:
                matching_service = 'content.services.plex'
            elif len(sys.modules['content.services.trakt'].users) > 0:
                matching_service = 'content.services.trakt'
            else:
                ui_print("[overseerr] error: couldnt match overseerr content to either plex or trakt - add at least one plex or trakt user. No requests will be downloaded.")
                return
            ui_print('[overseerr] matching overseerr requests to service ' + matching_service + ' ...')
            add = []
            for element_ in last_requests:
                element = copy.deepcopy(element_)
                if element.type == "movie":
                    element = movie(element)
                elif element.type == "tv":
                    element = show(element)
                try:
                    element.match(matching_service)
                    element.watchlist = sys.modules[matching_service].watchlist
                    element.request_id = element_.media.id
                    add += [element]
                except:
                    ui_print('[overseerr] error: couldnt match item to service ' + matching_service, ui_settings.debug)
            for element in add:
                if not element in self.data:
                    self.data.append(element)
            ui_print('done')

    def update(self):
        global last_requests
        if len(users) > 0 and len(api_key) > 0:
            refresh = False
            try:
                response = get(base_url + '/api/v1/request?take=10000')
                for element_ in response.results:
                    if not any(x.id == element_.id and x.updatedAt == element_.updatedAt for x in last_requests) and (element_.requestedBy.displayName in users or users == ['all']) and ([str(element_.media.status)] in allowed_movie_status if element_.type == 'movie' else [str(element_.media.status)] in allowed_show_status):
                        ui_print('[overseerr] found new overseerr request by user "' + element_.requestedBy.displayName + '".')
                        refresh = True
                        last_requests.append(element_)
                        if len(sys.modules['content.services.plex'].users) > 0:
                            matching_service = 'content.services.plex'
                        elif len(sys.modules['content.services.trakt'].users) > 0:
                            matching_service = 'content.services.trakt'
                        else:
                            ui_print("[overseerr] error: couldnt match overseerr content to either plex or trakt - add at least one plex or trakt user. No requests will be downloaded.")
                            return False
                        ui_print('[overseerr] matching overseerr requests to service ' + matching_service + ' ...')
                        element = copy.deepcopy(element_)
                        if element.type == "movie":
                            element = movie(element)
                        elif element.type == "tv":
                            element = show(element)
                        try:
                            element.match(matching_service)
                            element.watchlist = sys.modules[matching_service].watchlist
                        except:
                            ui_print('[overseerr] error: couldnt match item to service ' + matching_service, ui_settings.debug)
                        element.request_id = element_.media.id
                        if not element in self.data:
                            self.data.append(element)
                        else:
                            existing = next(x for x in self.data if x == element)
                            if element.type == "show":
                                for season in element.Seasons:
                                    if not any(season.index == x.index for x in existing.Seasons):
                                        existing.Seasons.append(season)
                        ui_print('done')
                for element in last_requests[:]:
                    if not element.id in (x.id for x in response.results):
                        last_requests.remove(element)
                if refresh:
                    return True
            except:
                return False
        return False

class library():
    name = 'Overseerr Requests'

    class refresh(classes.refresh):
        name = 'Overseerr Requests'

        def setup(cls, new=False):
            ui_cls("Options/Settings/Library Services/Library update services")
            from settings import settings_list
            settings = []
            for category, allsettings in settings_list:
                for setting in allsettings:
                    settings += [setting]
            if len(api_key) == 0:
                print("It looks like you havent setup an overseerr api key. Please set up an overseerr api key first.")
                print()
                for setting in settings:
                    if setting.name == "Overseerr API Key":
                        setting.setup()
            if not new:
                if not library.refresh.name in classes.refresh.active:
                    classes.refresh.active += [library.refresh.name]
                    print()
                    print("Successfully added Overserr!")
                    print()
                    time.sleep(3)
                else:
                    print()
                    print("Nothing to edit!")
                    print()
                    time.sleep(3)
                return
            else:
                if not library.refresh.name in classes.refresh.active:
                    classes.refresh.active += [library.refresh.name]
                    print()
                    print("Successfully added Overserr!")
                    print()
                    time.sleep(3)
                return

        def __new__(cls, element):
            try:
                if not hasattr(element,"request_id"):
                    return
                ui_print('[overserr] marking request as available')
                url = base_url + "/api/v1/media/" + str(element.request_id) + "/available"
                response = post(url,'{"is4k":false}')
            except:
                print("[overserr] error: couldnt mark requests as available")
