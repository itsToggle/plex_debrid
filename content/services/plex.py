#import modules
from base import *
#import parent modules
from content import classes
from ui.ui_print import *

name = 'Plex'
session = requests.Session()
users = []
headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
current_library = []

def setup(cls, new=False):
    from content.services import setup
    setup(cls,new)

def logerror(response):
    if not response.status_code == 200:
        ui_print("Plex error: " + str(response.content), debug=ui_settings.debug)
    if response.status_code == 401:
        name = ""
        for user in users:
            if user[1] in response.url:
                name = user[0]
                break
        if name == "":
            ui_print("plex error: (401 unauthorized): unnamed user token does not seem to work. check your plex user settings.")
        else:
            ui_print("plex error: (401 unauthorized): token for user '"+name+"' does not seem to work. check your plex user settings.")

def get(url, timeout=60):
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

def setEID(self):
    EID = []
    if hasattr(self,"Guid"):
        for guid in self.Guid:
            EID += [guid.id]
    return EID

class watchlist(classes.watchlist):
    autoremove = "movie"

    def __init__(self) -> None:
        if len(users) > 0:
            ui_print('[plex] getting all watchlists ...')
        self.data = []
        try:
            for user in users:
                added = 0
                total = 1
                while added < total:
                    total = 0
                    url = 'https://metadata.provider.plex.tv/library/sections/watchlist/all?X-Plex-Container-Size=200&X-Plex-Container-Start=' + str(added) + '&X-Plex-Token=' + user[1]
                    response = get(url)
                    if hasattr(response, 'MediaContainer'):
                        total = response.MediaContainer.totalSize
                        added += response.MediaContainer.size
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
            try:
                self.data.sort(key=lambda s: s.watchlistedAt, reverse=True)
            except:
                ui_print("[plex error]: (watchlist exception): could not sort watchlist chronologically for unknown reason", debug=ui_settings.debug)
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
                    url = 'https://metadata.provider.plex.tv/actions/removeFromWatchlist?ratingKey=' + item.ratingKey + '&X-Plex-Token=' + user[1]
                    try:
                        response = session.put(url, data={'ratingKey': item.ratingKey})
                        ui_print('[plex] item: "' + item.title + '" removed from ' + user[0] + '`s watchlist')
                    except:
                        ui_print('[plex] error: item "' + item.title + '" couldnt be removed from ' + user[0] + '`s watchlist')
                if not self == []:
                    self.data.remove(item)
            else:
                url = 'https://metadata.provider.plex.tv/actions/removeFromWatchlist?ratingKey=' + item.ratingKey + '&X-Plex-Token=' + item.user[1]
                try:
                    response = session.put(url, data={'ratingKey': item.ratingKey})
                    ui_print('[plex] item: "' + item.title + '" removed from ' + item.user[0] + '`s watchlist')
                except:
                    ui_print('[plex] error: item "' + item.title + '" couldnt be removed from ' + user[0] + '`s watchlist')
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
                                    ui_print('[plex] item: "' + entry.title + '" found in ' + user[0] + '`s watchlist')
                                    element.user += [user]
                                    if library.lable.name in classes.refresh.active:
                                        library.lable(element)
                        new_watchlist += response.MediaContainer.Metadata
            for entry in self.data[:]:
                if not entry in new_watchlist:
                    self.data.remove(entry)
            try:
                self.data.sort(key=lambda s: s.watchlistedAt, reverse=True)
            except:
                ui_print("[plex error]: (watchlist exception): could not sort watchlist chronologically for unknown reason", debug=ui_settings.debug)
        except Exception as e:
            ui_print("[plex error]: (watchlist exception): " + str(e), debug=ui_settings.debug)
            ui_print('[plex error]: could not reach plex')
        return update

class season(classes.media):
    def __init__(self, other):
        self.watchlist = watchlist
        self.__dict__.update(other.__dict__)
        self.EID = setEID(self)
        self.Episodes = []
        token = users[0][1]
        if library.ignore.name in classes.ignore.active:
            for user in users:
                if library.ignore.user == user[0]:
                    token = user[1]
        viewCount = 0
        while len(self.Episodes) < self.leafCount:
            url = 'https://metadata.provider.plex.tv/library/metadata/' + self.ratingKey + '/children?includeUserState=1&X-Plex-Container-Size=200&X-Plex-Container-Start=' + str(len(self.Episodes)) + '&X-Plex-Token=' + token
            response = get(url)
            if not response == None:
                if hasattr(response, 'MediaContainer'):
                    self.duration = 0
                    if hasattr(response.MediaContainer, 'Metadata'):
                        for episode_ in response.MediaContainer.Metadata:
                            episode_.grandparentYear = self.parentYear
                            episode_.grandparentEID = self.parentEID
                            episode_.parentEID = self.EID
                            viewCount += 1 if hasattr(episode_, "viewCount") and episode_.viewCount > 0 else 0
                            if hasattr(self,"user"):
                                episode_.user = self.user
                            self.Episodes += [episode(episode_)]
                            self.duration += episode_.duration if hasattr(episode_,"duration") else 0
                    self.leafCount = response.MediaContainer.totalSize
                    self.viewedLeafCount = viewCount
            else:
                time.sleep(1)

class episode(classes.media):
    def __init__(self, other):
        self.watchlist = watchlist
        self.__dict__.update(other.__dict__)
        self.EID = setEID(self)

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
        if library.ignore.name in classes.ignore.active:
            for user in users:
                if library.ignore.user == user[0]:
                    token = user[1]
        success = False
        while not success:
            url = 'https://metadata.provider.plex.tv/library/metadata/' + ratingKey + '?includeUserState=1&X-Plex-Token=' + token
            response = get(url)
            if not response == None:
                self.__dict__.update(response.MediaContainer.Metadata[0].__dict__)
                self.EID = setEID(self)
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
                                Season.parentEID = self.EID
                                if hasattr(self,"user"):
                                    Season.user = self.user
                                t = Thread(target=multi_init, args=(season, Season, results, index))
                                threads.append(t)
                                t.start()
                            # wait for the threads to complete
                            for t in threads:
                                t.join()
                            self.Seasons = results
                            self.leafCount = 0
                            self.viewedLeafCount = 0
                            self.duration = 0
                            for season_ in self.Seasons:
                                self.leafCount += season_.leafCount
                                self.viewedLeafCount += season_.viewedLeafCount
                                self.duration += season_.duration if hasattr(season_,"duration") else 0
                    success = True
                else:
                    time.sleep(1)
            else:
                time.sleep(1)
        if not hasattr(self,"watchlistedAt"):
            if hasattr(self,"addedAt"):
                self.watchlistedAt = self.addedAt
            else:
                self.watchlistedAt = 0

class movie(classes.media):
    def __init__(self, ratingKey):
        self.watchlist = watchlist
        token = users[0][1]
        if library.ignore.name in classes.ignore.active:
            for user in users:
                if library.ignore.user == user[0]:
                    token = user[1]
        if not isinstance(ratingKey, str):
            self.__dict__.update(ratingKey.__dict__)
            ratingKey = ratingKey.ratingKey
        elif ratingKey.startswith('plex://'):
            ratingKey = ratingKey.split('/')[-1]
        url = 'https://metadata.provider.plex.tv/library/metadata/' + ratingKey + '?includeUserState=1&X-Plex-Token=' + token
        response = get(url)
        self.__dict__.update(response.MediaContainer.Metadata[0].__dict__)
        self.EID = setEID(self)
        if not hasattr(self,"watchlistedAt"):
            if hasattr(self,"addedAt"):
                self.watchlistedAt = self.addedAt
            else:
                self.watchlistedAt = 0

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
        partial = "true"
        delay = "2"

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
                        print()
                        input("Press enter to try again: ")
                        print()
                        working = False
                except:
                    working = False
                    print("It looks like your plex server could not be reached at '" + library.url + "'. Make sure that plex media server is running, that you have claimed the server and that you have created at least one plex library.")
                    print()
                    for setting in settings:
                        if setting.name == "Plex server address":
                            setting.setup()
                    print()
            if not new:
                back = False
                while not back:
                    print("0) Back")
                    print("1) Plex Libraries to refresh")
                    print("2) Plex library refresh delay")
                    print("3) Plex library partial scan")
                    print()
                    choice0 = input("Choose an action: ")
                    ui_cls("Options/Settings/Library Services/Library update services")
                    if choice0 == "2":
                        for setting in settings:
                            if setting.name == "Plex library refresh delay":
                                setting.input()
                        back = True
                    if choice0 == "3":
                        for setting in settings:
                            if setting.name == "Plex library partial scan":
                                setting.input()
                        back = True
                    if choice0 == "1":
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

        def call(paths):
            try:
                for path in paths:
                    section = path[0]
                    folders = path[1]
                    if library.refresh.partial == "true":
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
                                    time.sleep(0.25)
                            url = library.url + '/library/sections/' + section + '/refresh?path='+folder+'&X-Plex-Token=' + users[0][1]
                            ui_print("refreshing plex via url: " + url, debug=ui_settings.debug)
                            response = session.get(url)
                    else:
                        url = library.url + '/library/sections/' + section + '/refresh?X-Plex-Token=' + users[0][1]
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
                            if hasattr(element,"downloaded_releases") and len(element.downloaded_releases) > 0 and library.refresh.partial == "true":
                                for release in element.downloaded_releases:
                                    folders += [requests.utils.quote(location.path + "/" + release)]
                            else:
                                folders += [requests.utils.quote(location.path)]
                        paths += [[section_.key,folders]]
                delay = 2
                try:
                    delay = float(library.refresh.delay)
                except:
                    ui_print("[plex] error: provided refresh delay is not a number! using default 2 second delay.")
                time.sleep(delay)
                ui_print('[plex] refreshing '+element_type+' library section/s: "' + '","'.join(names) + '"')
                results = [None]
                t = Thread(target=multi_init, args=(library.refresh.call, paths, results, 0))
                t.start()
            except:
                ui_print("[plex] error: couldnt refresh libraries. Make sure you have setup a plex user!")

    class lable(classes.refresh):

        name = 'Plex Lables'

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
                        print()
                        input("Press enter to try again: ")
                        print()
                        working = False
                except:
                    working = False
                    print("It looks like your plex server could not be reached at '" + library.url + "'. Make sure that plex media server is running, that you have claimed the server and that you have created at least one plex library.")
                    print()
                    for setting in settings:
                        if setting.name == "Plex server address":
                            setting.setup()
                    print()
            if not new:
                print()
                print("nothing to edit!")
                print()
                time.sleep(3)
            else:
                if not library.lable.name in classes.refresh.active:
                    classes.refresh.active += [library.lable.name]
                print()
                print("Successfully added plex lable update service!")
                print()
                time.sleep(3)

        def call(element):
            try:
                tags = element.post_tags
                retries = 0
                while element not in current_library and retries < 6:
                    time.sleep(10)
                    _ = library(silent=True)
                    retries += 1
                library_item = next((x for x in current_library if element == x), None)
                if library_item == None:
                    ui_print('[plex] error: couldnt add lables - item: "' + element.query() + '" could not be found on server.')
                    return
                tags_string = ""
                for tag in tags:
                    tags_string = '&label%5B-1%5D.tag.tag=' + tag
                    type_string = "1" if element.type == "movie" else "2"
                    url = library.url + '/library/sections/' + str(library_item.librarySectionID) + '/all?type=' + type_string + '&id=' + library_item.ratingKey + '&label.locked=1' + tags_string + '&X-Plex-Token=' + users[0][1]
                    response = session.put(url,headers=headers)
                url = library.url + '/library/metadata/' + library_item.ratingKey + '?X-Plex-Token=' + users[0][1]
                response = get(url)
                library_item.__dict__.update(response.MediaContainer.Metadata[0].__dict__)
            except Exception as e:
                ui_print("[plex] error: couldnt add lables! Turn on debug printing for more info.")
                ui_print(str(e), debug=ui_settings.debug)

        def __new__(cls, element):
            tags = []
            try:
                if not isinstance(element,classes.media):
                    return
                # Add user Tag
                if hasattr(element,"requestedBy"):
                    tags += [element.requestedBy.displayName]
                elif isinstance(element.user[0],list):
                    for user in element.user:
                        tags += ["From: " + user[0]]
                else:
                    tags += ["From: " + element.user[0]]
                # Add version Tag
                version_tags = False
                for version in element.downloaded_versions:
                    if element.query() in version and not "Version: " +version.split("[")[-1][:-1] in tags:
                        tags += ["Version: " +version.split("[")[-1][:-1]]
                        version_tags = True
                library_item = next((x for x in current_library if element == x), None)
                # Return if no version tags and not collected
                if library_item == None and version_tags == False:
                    return
                # Check existing Tags
                if hasattr(library_item,"Label"):
                    for lable in library_item.Label:
                        if lable.tag in tags:
                            tags.remove(lable.tag)
                if len(tags) == 0:
                    return
                element.post_tags = tags
                ui_print('[plex] adding lables: "' + '","'.join(tags) + '" to item: "' + element.query() + '"')
                results = [None]
                t = Thread(target=multi_init, args=(library.lable.call, element, results, 0))
                t.start()
            except Exception as e:
                ui_print("[plex] error: couldnt add lables! Turn on debug printing for more info.")
                ui_print(str(e), debug=ui_settings.debug)

    class ignore(classes.ignore):

        name = 'Plex Discover Watch Status'
        user = ""

        def setup(cls, new=False):
            ui_cls("Options/Settings/Library Services/Library ignore services")
            from settings import settings_list
            settings = []
            for category, allsettings in settings_list:
                for setting in allsettings:
                    settings += [setting]
            if not library.name in classes.library.active:
                print("It looks like you havent set your library collection service to plex. This is needed to accurately match content to the plex media type.")
                print("Please switch your library collection service to plex.")
                print()
                time.sleep(4)
                return
            if len(users) == 0:
                print("It looks like you havent setup a plex user. Please set up a plex user first.")
                print()
                for setting in settings:
                    if setting.name == "Plex users":
                        setting.setup()
            if not new:
                print("Current plex user, whose plex discover watch status is used to ignore content: '" + library.ignore.user + "'")
                print()
                print("0) Back")
                print("1) Change plex user")
                print()
                choice = input("Choose an action: ")
                if choice == '1':
                    addable_users = []
                    for index,plexuser in enumerate(users):
                        addable_users += [plexuser[0]]
                    if len(addable_users) == 0:
                        print()
                        print("It seems there only is one plex user!")
                        time.sleep(3)
                        return
                    indices = []
                    print("Please choose a plex users, whos plex discover watch status should be used to ignore content: ")
                    print()
                    print("0) Back")
                    for index,ignoreuser in enumerate(addable_users):
                        print(str(index+1) + ") Plex user '" + ignoreuser + "'")
                        indices += [str(index+1)]
                    print()
                    choice = input("Please choose a plex user: ")
                    if choice in indices:
                        library.ignore.user = addable_users[int(choice)-1]
                        print()
                        print("Successfully changed to plex user '" + addable_users[int(choice)-1] + "'")
                        print()
                        time.sleep(3)
            else:
                addable_users = []
                for index,plexuser in enumerate(users):
                    addable_users += [plexuser[0]]
                print("Please choose a plex user, whos plex discover watch status should be used to ignore content: ")
                print()
                indices = []
                for index,ignoreuser in enumerate(addable_users):
                        print(str(index+1) + ") Plex user '" + ignoreuser + "'")
                        indices += [str(index+1)]
                print()
                choice = input("Please choose a plex user: ")
                if choice in indices:
                    library.ignore.user = addable_users[int(choice)-1]
                    if not library.ignore.name in classes.ignore.active:
                        classes.ignore.active += [library.ignore.name]
                    print()
                    print("Successfully added plex user '" + addable_users[int(choice)-1] + "'")
                    print()
                    time.sleep(3)

        def add(self):
            try:
                ignoreuser = library.ignore.user
                user = None
                for plexuser in users:
                    if plexuser[0] == ignoreuser:
                        user = plexuser
                        break
                if user == None:
                    print("[plex] error: Could not find plex ignore service user: '"+ignoreuser+"'. Make sure this plex user exists.")
                    return
                ui_print('[plex] ignoring item: ' + self.query() + " for user: '" + ignoreuser + "'")
                url = 'https://metadata.provider.plex.tv/actions/scrobble?identifier=tv.plex.provider.metadata&key=' + self.ratingKey + '&X-Plex-Token=' + user[1]
                get(url)
                if not self in classes.ignore.ignored:
                    classes.ignore.ignored += [self]
            except Exception as e:
                ui_print("plex error: couldnt ignore item: " + str(e), debug=ui_settings.debug)

        def remove(self):
            try:
                ignoreuser = library.ignore.user
                user = None
                for plexuser in users:
                    if plexuser[0] == ignoreuser:
                        user = plexuser
                        break
                if user == None:
                    print("[plex] error: Could not find plex ignore service user: '"+ignoreuser+"'. Make sure this plex user exists.")
                    return
                ui_print('[plex] un-ignoring item: ' + self.query() + " for user: '" + ignoreuser + "'")
                url = 'https://metadata.provider.plex.tv/actions/unscrobble?identifier=tv.plex.provider.metadata&key=' + self.ratingKey + '&X-Plex-Token=' + user[1]
                get(url)
                if self in classes.ignore.ignored:
                    classes.ignore.ignored.remove(self)
            except Exception as e:
                ui_print("plex error: couldnt un-ignore item: " + str(e), debug=ui_settings.debug)

        def check(self):
            try:
                if self.type == 'movie' or self.type == 'episode':
                    if hasattr(self, 'viewCount'):
                        if self.viewCount > 0:
                            if not self in  classes.ignore.ignored:
                                classes.ignore.ignored += [self]
                            return True
                else:
                    if hasattr(self, 'viewedLeafCount'):
                        if self.viewedLeafCount >= self.leafCount:
                            if not self in  classes.ignore.ignored:
                                classes.ignore.ignored += [self]
                            return True
                return False
            except Exception as e:
                ui_print("[plex] error: couldnt check ignore status for item: " + str(e), debug=ui_settings.debug)
                return False

    def __new__(self,silent=False):
        global current_library
        list_ = []
        sections = []
        names = []
        first_load = False
        if len(current_library) == 0:
            first_load = True
            current_library = cache.load("plex","metadata")
        if library.check == [['']]:
            library.check = []
        try:
            response = get(library.url  + '/library/sections/?X-Plex-Token=' + users[0][1])
            for Directory in response.MediaContainer.Directory:
                if ([Directory.key] in library.check or library.check == []) and Directory.type in ["movie","show"]:
                    types = ['1'] if Directory.type == "movie" else  ['2', '3', '4']
                    sections += [[Directory.key,types]]
                    names += [Directory.title]
        except:
            ui_print("[plex error]: couldnt reach local plex server at: " + library.url + " to determine library sections. Make sure the address is correct, the server is running, and youve set up at least one library.")
        if len(sections) == 0:
            return list_
        if not silent:
            ui_print('[plex] getting plex library section/s "' + '","'.join(names) + '" ...')
        for section,types in sections:
            if section == '':
                continue
            section_response = []
            for type in types:
                url = library.url + '/library/sections/' + section + '/all?type=' + type + '&X-Plex-Token=' + users[0][1]
                response = get(url)
                if hasattr(response, 'MediaContainer'):
                    if hasattr(response.MediaContainer, 'Metadata'):
                        for element in response.MediaContainer.Metadata:
                            section_response += [classes.media(element)]
            if len(section_response) == 0:
                ui_print("[plex error]: couldnt reach local plex library section '" + section + "' at server address: " + library.url + " - or this library really is empty.")
                list_ = []
                break
            else:
                list_ += section_response
        if len(list_) == 0:
            ui_print("[plex error]: Your library seems empty. To prevent unwanted behaviour, no further downloads will be started. If your library really is empty, please add at least one media item manually.")
        shows = {}
        seasons = {}
        for item in list_:
            if item.type == "show":
                item.childCount = 0
                item.leafCount = 0
                item.Seasons = []
                shows[item.guid] = item
            elif item.type == "season":
                item.leafCount = 0
                item.Episodes = []
                seasons[item.guid] = item
        for episode in list_:
            if episode.type != "episode" or not episode.parentGuid in seasons:
                continue
            season = seasons[episode.parentGuid]
            if not season.parentGuid in shows:
                continue
            show = shows[season.parentGuid]
            season_ = next((x for x in show.Seasons if season == x), None)
            if season_ != None:
                season_.Episodes.append(episode)
                season_.leafCount += 1
                show.leafCount += 1
            else:
                season.Episodes.append(episode)
                season.leafCount += 1
                show.childCount += 1
                show.leafCount += 1
                show.Seasons.append(season)
        list_ = [item for item in list_ if item.type == "movie"]
        for value in shows.values():
            list_.append(value)
        if len(list_) - len(current_library) > 0:
            ui_print('done')
            ui_print('[plex] getting metadata for ' + str(len(list_) - len(current_library)) + ' collected movies/shows ...')
        updated = False
        for item in list_:
            try:
                if not item in current_library:
                    updated = True
                    url = library.url + '/library/metadata/' + item.ratingKey + '?X-Plex-Token=' + users[0][1]
                    response = get(url)
                    item.__dict__.update(response.MediaContainer.Metadata[0].__dict__)
                else:
                    match = next((x for x in current_library if item == x), None)
                    if hasattr(match,"Guid"):
                        item.Guid = match.Guid
                    if hasattr(match,"Label"):
                        item.Label = match.Label
                    if hasattr(match,"librarySectionID"):
                        item.librarySectionID = match.librarySectionID
                item.EID = setEID(item)
                if item.type == "show":
                    for season in item.Seasons:
                        season.parentEID = item.EID
                        for episode in season.Episodes:
                            episode.grandparentEID = item.EID
            except:
                ui_print('done')
                ui_print("[plex error]: found incorrectly matched library item : " + item.title + " - this item needs a metadata refresh (open plex webui, find item, open item menu, refresh metadata).")  
        ui_print('done')
        current_library = copy.deepcopy(list_)
        if first_load and updated:
            cache.save(current_library,"plex","metadata")       
        return list_

def search(query, library=[]):
    query = query.replace(' ', '%20')
    url = 'https://metadata.provider.plex.tv/library/search?query=' + query + '&limit=20&searchTypes=movies%2Ctv&includeMetadata=1&X-Plex-Token=' + users[0][1]
    response = get(url)
    try:
        return response.MediaContainer.SearchResult
    except:
        return []

def match(self):
    current_module = sys.modules[__name__]
    some_local_media = None
    if not current_library == []:
        if self.type in ["movie","show"]:
            for element in current_library:
                if element.type == self.type:
                    some_local_media = element
                    break
        elif self.type == "season":
            for element in current_library:
                if element.type == "show":
                    if hasattr(element,"Seasons"):
                        if len(element.Seasons) > 0:
                            some_local_media = element.Seasons[0]
                            break
        elif self.type == "episode":
            for element in current_library:
                if element.type == "show":
                    if hasattr(element,"Seasons"):
                        if len(element.Seasons) > 0:
                            if hasattr(element.Seasons[0],"Episodes"):
                                if len(element.Seasons[0].Episodes) > 0:
                                    some_local_media = element.Seasons[0].Episodes[0]
                                    break
    else:
        ui_print(
            "[plex error]: couldnt match content to plex media type, because the plex library is empty. Please add at least one movie and one show!")
        return None
    if some_local_media == None:
        ui_print("[plex error]: couldnt match content to plex media type, no media of the same type found!")
        return None
    if self.type == 'movie':
        agent = 'tv.plex.agents.movie'
    else:
        agent = 'tv.plex.agents.series'
    for EID in self.EID:
        service,query = EID.split('://')
        query = '-'.join([service,query])
        url = current_module.library.url + '/library/metadata/' + some_local_media.ratingKey + '/matches?manual=1&title=' + query + '&agent=' + agent + '&language=en-US&X-Plex-Token=' + users[0][1]
        response = get(url)
        try:
            match = response.MediaContainer.SearchResult[0]
            if match.type == 'show':
                return show(match.guid)
            elif match.type == 'movie':
                return movie(match.guid)
        except:
            continue
    return None

def multi_init(cls, obj, result, index):
    result[index] = cls(obj)
