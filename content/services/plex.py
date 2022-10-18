#import modules
from base import *
#import parent modules
from content import classes
from ui.ui_print import *

name = 'Plex'
session = requests.Session()
users = []
headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
ignored = []

def setup(cls, new=False):
    from content.services import setup
    setup(cls,new)

def logerror(response):
    if not response.status_code == 200:
        ui_print("Plex error: " + str(response.content), debug=ui_settings.debug)
    if response.status_code == 401:
        ui_print("plex error: (401 unauthorized): user token does not seem to work. check your plex user settings.")

def get(url, timeout=30):
    try:
        response = session.get(url, headers=headers, timeout=timeout)
        logerror(response)
        response = json.loads(response.content, object_hook=lambda d: SimpleNamespace(**d))
        return response
    except Exception as e:
        ui_print("plex error: (json exception): " + str(e), debug=ui_settings.debug)
        return None

def post(url, data):
    try:
        response = session.post(url, data=data, headers=headers)
        logerror(response)
        response = json.loads(response.content, object_hook=lambda d: SimpleNamespace(**d))
        return response
    except Exception as e:
        ui_print("plex error: (json exception): " + str(e), debug=ui_settings.debug)
        return None

class watchlist(classes.watchlist):
    autoremove = "movie"

    def __init__(self) -> None:
        if len(users) > 0:
            ui_print('[plex] getting all watchlists ...')
        self.data = []
        try:
            for user in users:
                url = 'https://metadata.provider.plex.tv/library/sections/watchlist/all?X-Plex-Token=' + user[1]
                response = get(url)
                if hasattr(response, 'MediaContainer'):
                    if hasattr(response.MediaContainer, 'Metadata'):
                        for entry in response.MediaContainer.Metadata:
                            entry.user = [user]
                            if not entry in self.data:
                                if entry.type == 'show':
                                    self.data += [show(entry)]
                                if entry.type == 'movie':
                                    self.data += [movie(entry)]
                            else:
                                element = next(x for x in self.data if x == entry)
                                if not user in element.user:
                                    element.user += [user]
            self.data.sort(key=lambda s: s.watchlistedAt, reverse=True)
        except Exception as e:
            ui_print('done')
            ui_print("[plex error]: (watchlist exception): " + str(e), debug=ui_settings.debug)
            ui_print('[plex error]: could not reach plex')
        if len(users) > 0:
            ui_print('done')

    def remove(self, item):
        if hasattr(item, 'user'):
            if isinstance(item.user[0], list):
                for user in item.user:
                    ui_print('[plex] item: "' + item.title + '" removed from ' + user[0] + '`s watchlist')
                    url = 'https://metadata.provider.plex.tv/actions/removeFromWatchlist?ratingKey=' + item.ratingKey + '&X-Plex-Token=' + \
                            user[1]
                    response = session.put(url, data={'ratingKey': item.ratingKey})
                if not self == []:
                    self.data.remove(item)
            else:
                ui_print('[plex] item: "' + item.title + '" removed from ' + item.user[0] + '`s watchlist')
                url = 'https://metadata.provider.plex.tv/actions/removeFromWatchlist?ratingKey=' + item.ratingKey + '&X-Plex-Token=' + \
                        item.user[1]
                response = session.put(url, data={'ratingKey': item.ratingKey})
                if not self == []:
                    self.data.remove(item)

    def add(self, item, user):
        ui_print('[plex] item: "' + item.title + '" added to ' + user[0] + '`s watchlist')
        url = 'https://metadata.provider.plex.tv/actions/addToWatchlist?ratingKey=' + item.ratingKey + '&X-Plex-Token=' + \
                user[1]
        response = session.put(url, data={'ratingKey': item.ratingKey})
        if item.type == 'show':
            self.data.append(show(item.ratingKey))
        elif item.type == 'movie':
            self.data.append(movie(item.ratingKey))

    def update(self):
        if len(users) > 0:
            ui_print("[plex] updating all watchlists ...", debug=ui_settings.debug)
        update = False
        new_watchlist = []
        try:
            for user in users:
                url = 'https://metadata.provider.plex.tv/library/sections/watchlist/all?X-Plex-Token=' + user[1]
                response = get(url)
                if hasattr(response, 'MediaContainer'):
                    if hasattr(response.MediaContainer, 'Metadata'):
                        for entry in response.MediaContainer.Metadata:
                            entry.user = [user]
                            if not entry in self.data:
                                ui_print('[plex] item: "' + entry.title + '" found in ' + user[0] + '`s watchlist')
                                update = True
                                if entry.type == 'show':
                                    self.data += [show(entry)]
                                if entry.type == 'movie':
                                    self.data += [movie(entry)]
                            else:
                                element = next(x for x in self.data if x == entry)
                                if not user in element.user:
                                    element.user += [user]
                        new_watchlist += response.MediaContainer.Metadata
            for entry in self.data[:]:
                if not entry in new_watchlist:
                    self.data.remove(entry)
            self.data.sort(key=lambda s: s.watchlistedAt, reverse=True)
        except Exception as e:
            ui_print('done')
            ui_print("[plex error]: (watchlist exception): " + str(e), debug=ui_settings.debug)
            ui_print('[plex error]: could not reach plex')
        if len(users) > 0:
            ui_print('done')
        return update

class season(classes.media):
    def __init__(self, other):
        self.watchlist = watchlist
        self.__dict__.update(other.__dict__)
        self.Episodes = []
        while len(self.Episodes) < self.leafCount:
            url = 'https://metadata.provider.plex.tv/library/metadata/' + self.ratingKey + '/children?includeUserState=1&X-Plex-Container-Size=200&X-Plex-Container-Start=' + str(
                len(self.Episodes)) + '&X-Plex-Token=' + users[0][1]
            response = get(url)
            if not response == None:
                if hasattr(response, 'MediaContainer'):
                    if hasattr(response.MediaContainer, 'Metadata'):
                        for episode_ in response.MediaContainer.Metadata:
                            episode_.grandparentYear = self.parentYear
                            self.Episodes += [episode(episode_)]
                    self.leafCount = response.MediaContainer.totalSize
            else:
                time.sleep(1)

class episode(classes.media):
    def __init__(self, other):
        self.watchlist = watchlist
        self.__dict__.update(other.__dict__)

class show(classes.media):
    def __init__(self, ratingKey):
        self.watchlist = watchlist
        if not isinstance(ratingKey, str):
            self.__dict__.update(ratingKey.__dict__)
            ratingKey = ratingKey.ratingKey
            if isinstance(self.user[0], list):
                token = self.user[0][1]
            else:
                token = self.user[1]
        else:
            if ratingKey.startswith('plex://'):
                ratingKey = ratingKey.split('/')[-1]
            token = users[0][1]
        success = False
        while not success:
            url = 'https://metadata.provider.plex.tv/library/metadata/' + ratingKey + '?includeUserState=1&X-Plex-Token=' + token
            response = get(url)
            if not response == None:
                self.__dict__.update(response.MediaContainer.Metadata[0].__dict__)
                self.Seasons = []
                url = 'https://metadata.provider.plex.tv/library/metadata/' + ratingKey + '/children?includeUserState=1&X-Plex-Container-Size=200&X-Plex-Container-Start=0&X-Plex-Token=' + token
                response = get(url)
                if not response == None:
                    if hasattr(response, 'MediaContainer'):
                        if hasattr(response.MediaContainer, 'Metadata'):
                            for Season in response.MediaContainer.Metadata[:]:
                                if Season.index == 0:
                                    response.MediaContainer.Metadata.remove(Season)
                            results = [None] * len(response.MediaContainer.Metadata)
                            threads = []
                            # start thread for each season
                            for index, Season in enumerate(response.MediaContainer.Metadata):
                                Season.parentYear = self.year
                                t = Thread(target=multi_init, args=(season, Season, results, index))
                                threads.append(t)
                                t.start()
                            # wait for the threads to complete
                            for t in threads:
                                t.join()
                            self.Seasons = results
                    success = True
                else:
                    time.sleep(1)
            else:
                time.sleep(1)

class movie(classes.media):
    def __init__(self, ratingKey):
        self.watchlist = watchlist
        if not isinstance(ratingKey, str):
            self.__dict__.update(ratingKey.__dict__)
            ratingKey = ratingKey.ratingKey
        elif ratingKey.startswith('plex://'):
            ratingKey = ratingKey.split('/')[-1]
        url = 'https://metadata.provider.plex.tv/library/metadata/' + ratingKey + '?includeUserState=1&X-Plex-Token=' + \
                users[0][1]
        response = get(url)
        self.__dict__.update(response.MediaContainer.Metadata[0].__dict__)

class library(classes.library):
    name = 'Plex Library'
    url = 'http://localhost:32400'
    check = []

    def setup(cls, new=False):
        from settings import settings_list
        if new:
            print()
            settings = []
            for category, allsettings in settings_list:
                for setting in allsettings:
                    settings += [setting]
            if len(users) == 0:
                print('Please set up a plex user first:')
                print()
                for setting in settings:
                    if setting.name == 'Plex users':
                        setting.setup()
                print()
            for setting in settings:
                if setting.name == 'Plex server address':
                    setting.setup()
                    print()
            classes.library.active = [library.name]
        else:
            classes.library.setup(library)

    class refresh(classes.refresh):

        name = 'Plex Libraries'
        sections = []

        def setup(cls, new=False):
            ui_cls("Options/Settings/Library Services/Library update services")
            from settings import settings_list
            settings = []
            for category, allsettings in settings_list:
                for setting in allsettings:
                    settings += [setting]
            if len(users) == 0:
                print("It looks like you havent setup a plex user. Please set up a plex user first.")
                print()
                for setting in settings:
                    if setting.name == "Plex users":
                        setting.setup()
            working = False
            while not working:
                try:
                    response = get(library.url  + '/library/sections/?X-Plex-Token=' + users[0][1])
                    working = True
                    if len(response.MediaContainer.Directory) == 0:
                        print("It looks like this server does not have any libraries set-up! Please open the plex webui, setup at least one library and point it to your mounted debrid service drive.")
                        time.sleep(3)
                        return
                except:
                    print("It looks like your plex server could not be reached at '" + library.url + "'")
                    print()
                    for setting in settings:
                        if setting.name == "Plex server address":
                            setting.setup()
                    print()
            if not new:
                back = False
                while not back:
                    print("Current plex library sections that are refreshed after a successful download: ")
                    print()
                    print("0) Back")
                    indices = []
                    for index,section in enumerate(library.refresh.sections):
                        for section_ in response.MediaContainer.Directory:
                            if section_.key == section:
                                print(str(index+1) + ") Plex library section '" + section_.title + "' of type '" + section_.type + "'")
                                indices += [str(index+1)]
                                break
                    print()
                    print("Type 'add' to add another plex library section that should be refreshed.")
                    print()
                    choice = input("Please choose a plex library section: ")
                    if choice in indices:
                        print()
                        print("0) Back")
                        print("1) Remove plex library section")
                        print()
                        choice2 = input("Choose an action: ")
                        if choice2 == "1":
                            library.refresh.sections.remove(library.refresh.sections[int(choice)-1])
                    if choice == '0':
                        back=True
                    if choice == 'add':
                        sections = []
                        for index,section in enumerate(response.MediaContainer.Directory):
                            if not section.key in library.refresh.sections:
                                sections += [section]
                        if len(sections) == 0:
                            print()
                            print("It seems youve added all plex library sections of this server!")
                            time.sleep(3)
                            return
                        indices = []
                        print("Please choose a plex library section that should be refreshed after a successful download: ")
                        print()
                        print("0) Back")
                        for index,section in enumerate(sections):
                            print(str(index+1) + ") Plex library section '" + section.title + "' of type '" + section.type + "'")
                            indices += [str(index+1)]
                        print()
                        choice = input("Please choose a plex library section: ")
                        if choice in indices:
                            library.refresh.sections += [sections[int(choice)-1].key]
                            print()
                            print("Successfully added plex library section '" + sections[int(choice)-1].title + "'")
                            print()
                            time.sleep(3)
            else:
                back = False
                initial = False
                while not back:
                    sections = []
                    for index,section in enumerate(response.MediaContainer.Directory):
                        if not section.key in library.refresh.sections:
                            sections += [section]
                    if len(sections) == 0:
                        print("It seems youve added all plex library sections of this server!")
                        time.sleep(3)
                        return
                    print("Please choose at least one plex library section that should be refreshed after a successful download: ")
                    print()
                    indices = []
                    if classes.refresh.active == [] or initial:
                        if initial:
                            print("0) Done")
                        initial = True
                    else:
                        print("0) Back")
                    for index,section in enumerate(sections):
                        print(str(index+1) + ") Plex library section '" + section.title + "' of type '" + section.type + "'")
                        indices += [str(index+1)]
                    print()
                    choice = input("Please choose a plex library section: ")
                    if choice in indices:
                        library.refresh.sections += [sections[int(choice)-1].key]
                        if not library.refresh.name in classes.refresh.active:
                            classes.refresh.active += [library.refresh.name]
                        print()
                        print("Successfully added plex library section '" + sections[int(choice)-1].title + "'")
                        print()
                        time.sleep(3)
                    if choice == '0' and not classes.refresh.active == []:
                        back=True

        def call(path):
            try:
                section = path[0]
                folders = path[1]
                for folder in folders:
                    refreshing = True
                    while refreshing:
                        refreshing = False
                        url = library.url + '/library/sections/?X-Plex-Token=' + users[0][1]
                        response = get(url)
                        for section_ in response.MediaContainer.Directory:
                            if section_.refreshing:
                                refreshing = True
                        if refreshing:
                            time.sleep(1)
                    url = library.url + '/library/sections/' + section + '/refresh?path='+folder+'&X-Plex-Token=' + users[0][1]
                    ui_print("refreshing plex via url: " + url, debug=ui_settings.debug)
                    response = session.get(url)
            except Exception as e:
                ui_print(str(e), debug=ui_settings.debug)

        def __new__(cls, element):
            try:
                names = []
                element_type = ("show" if element.type in ["show","season","episode"] else "movie")
                url = library.url + '/library/sections/?X-Plex-Token=' + users[0][1]
                response = get(url)
                paths = []
                for section_ in response.MediaContainer.Directory:
                    if section_.key in library.refresh.sections and element_type == section_.type:
                        names += [section_.title]
                        folders = []
                        for location in section_.Location:
                            if hasattr(element,"downloaded_releases"):
                                for release in element.downloaded_releases:
                                    folders += [requests.utils.quote(location.path + "/" + release)]
                            else:
                                folders += [requests.utils.quote(location.path)]
                        paths += [[section_.key,folders]]
                ui_print('[plex] refreshing '+element_type+' library section/s: "' + '","'.join(names) + '"')
                for path in paths:
                    t = Thread(target=multi_init, args=(library.refresh.call, path, [None], 0))
                    t.start()
                    time.sleep(0.1)
            except:
                print("[plex] error: couldnt refresh libraries")

    def __new__(self):
        list = []
        if not library.check == [['']] and not library.check == []:
            ui_print(
                '[plex] getting plex library section/s "' + ','.join(x[0] for x in library.check) + '" ...')
            types = ['1', '2', '3', '4']
            for section in library.check:
                if section[0] == '':
                    continue
                section_response = []
                for type in types:
                    url = library.url + '/library/sections/' + section[
                        0] + '/all?type=' + type + '&X-Plex-Token=' + users[0][1]
                    response = get(url)
                    if hasattr(response, 'MediaContainer'):
                        if hasattr(response.MediaContainer, 'Metadata'):
                            for element in response.MediaContainer.Metadata:
                                section_response += [classes.media(element)]
                if len(section_response) == 0:
                    ui_print("[plex error]: couldnt reach local plex library section '" + section[
                        0] + "' at server address: " + library.url + " - or this library really is empty.")
                else:
                    list += section_response
            ui_print('done')
        else:
            ui_print('[plex] getting entire plex library ...')
            url = library.url + '/library/all?X-Plex-Token=' + users[0][1]
            response = get(url)
            ui_print('done')
            if hasattr(response, 'MediaContainer'):
                if hasattr(response.MediaContainer, 'Metadata'):
                    for element in response.MediaContainer.Metadata:
                        list += [classes.media(element)]
            else:
                ui_print(
                    "[plex error]: couldnt reach local plex server at server address: " + library.url + " - or this library really is empty.")
        if len(list) == 0:
            ui_print(
                "[plex error]: Your library seems empty. To prevent unwanted behaviour, no further downloads will be started. If your library really is empty, please add at least one media item manually.")
        return list

def search(query, library=[]):
    query = query.replace(' ', '%20')
    url = 'https://metadata.provider.plex.tv/library/search?query=' + query + '&limit=20&searchTypes=movies%2Ctv&includeMetadata=1&X-Plex-Token=' + \
            users[0][1]
    response = get(url)
    try:
        return response.MediaContainer.SearchResult
    except:
        return []

def match(query, type, library=[]):
    current_module = sys.modules[__name__]
    if not library == []:
        for element in library:
            if element.type == type:
                some_local_media = element
                break
    else:
        ui_print(
            "[plex error]: couldnt match content to plex media type, because the plex library is empty. Please add at least one movie and one show!")
        return []
    if type == 'movie':
        agent = 'tv.plex.agents.movie'
    else:
        agent = 'tv.plex.agents.series'
    url = current_module.library.url + '/library/metadata/' + some_local_media.ratingKey + '/matches?manual=1&title=' + query + '&agent=' + agent + '&language=en-US&X-Plex-Token=' + \
            users[0][1]
    response = get(url)
    try:
        match = response.MediaContainer.SearchResult[0]
        if match.type == 'show':
            return [show(match.guid)]
        elif match.type == 'movie':
            return [movie(match.guid)]
    except:
        return []

# Multiprocessing watchlist method
def multi_init(cls, obj, result, index):
    result[index] = cls(obj)
