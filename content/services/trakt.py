#import modules
from base import *
#import parent modules
from content import classes
from ui.ui_print import *


name = 'Trakt'
client_id = "0183a05ad97098d87287fe46da4ae286f434f32e8e951caad4cc147c947d79a3"
client_secret = "87109ed53fe1b4d6b0239e671f36cd2f17378384fa1ae09888a32643f83b7e6c"
lists = []
users = []
current_user = ["", ""]
session = requests.Session()

def setup(self, new=False):
    from settings import settings_list
    global lists
    global current_user
    back = False
    settings = []
    for category, allsettings in settings_list:
        for setting in allsettings:
            if setting.cls == self or setting.name == self.name + ' auto remove':
                settings += [setting]
    ui_cls("Options/Settings/Content Services/Content Services/Trakt")
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
                if settings[int(choice) - 1].name == "Trakt lists":
                    print()
                    print(
                        "You can define which trakt lists should be monitored by plex_debrid. This includes public lists and your trakt users watchlists and collections.")
                    print()
                    print('Currently monitored trakt lists: "' + str(lists) + '"')
                    print()
                    print('0) Back')
                    print('1) Add list')
                    if len(lists) > 0:
                        print('2) Remove list')
                    print()
                    choice = input('Choose an action: ')
                    print()
                    if choice == '1':
                        print("Choose a trakt list that should be monitored by plex_debrid.")
                        print()
                        i = 1
                        indices = []
                        add_user = []
                        print('0) Back')
                        print('1) add public list')
                        for user in users:
                            if not user[0] + "'s watchlist" in lists:
                                print(str(i + 1) + ') add ' + user[0] + "'s watchlist")
                                indices += [str(i + 1)]
                                add_user += [user[0] + "'s watchlist"]
                                i += 1
                            if not user[0] + "'s collection" in lists:
                                print(str(i + 1) + ') add ' + user[0] + "'s collection")
                                indices += [str(i + 1)]
                                add_user += [user[0] + "'s collection"]
                                i += 1
                            current_user = user
                            response, header = get('https://api.trakt.tv/users/me/lists')
                            if not response == None:
                                for p_list in response:
                                    if not user[0] + "'s private list: " + p_list.name in lists:
                                        print(str(i + 1) + ') add ' + user[0] + "'s private list: " + p_list.name)
                                        indices += [str(i + 1)]
                                        add_user += [user[0] + "'s private list: " + p_list.name]
                                        i += 1
                        print()
                        choice = input("Choose a list: ")
                        if choice == '0':
                            back = True
                        elif choice == '1':
                            print("To add a public list, please enter the lists url in the format shown by this example: (Example URL: '/users/giladg/lists/latest-releases') ")
                            print()
                            url = input("Please enter the public list url: ")
                            current_user = users[0]
                            if current_user[1] == "":
                                print("Please add at least one trakt user before adding a trakt list!")
                                time.sleep(5)
                                return False
                            response, header = get('https://api.trakt.tv' + url + '/items')
                            while response == None:
                                print()
                                print(
                                    "Looks like that url didnt work. Please enter the lists url in the format shown by this example: (Example URL: '/users/giladg/lists/latest-releases') ")
                                print()
                                url = input("Please enter the public list url: ")
                                response, header = get('https://api.trakt.tv' + url)
                            lists += [url]
                            return True
                        elif choice in indices:
                            lists += [add_user[int(choice) - 2]]
                            return True
                    elif choice == '2':
                        indices = []
                        print("Choose a list to remove.")
                        print()
                        print('0) Back')
                        for index, list in enumerate(lists):
                            print(str(index + 1) + ') ' + list)
                            indices += [str(index + 1)]
                        print()
                        choice = input("Choose a list: ")
                        if choice == '0':
                            back = True
                        elif choice in indices:
                            lists.remove(lists[int(choice) - 1])
                            return True
                else:
                    settings[int(choice) - 1].input()
                back = True
            elif choice == '0':
                back = True
    else:
        print('Please add at least one trakt user:')
        for setting in settings:
            if setting.name == 'Trakt users':
                setting.setup()
        lists = [users[0][0] + "'s watchlist"]

def logerror(response):
    if not response.status_code == 200:
        ui_print("[trakt] error: " + str(response.content), debug=ui_settings.debug)
    if response.status_code == 401:
        ui_print("[trakt] error: (401 unauthorized): trakt api key for user '" + current_user[
            0] + "' does not seem to work. Consider re-authorizing plex_debrid for this trakt user.")

def get(url):
    try:
        response = session.get(url, headers={
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36',
            'Content-type': "application/json", "trakt-api-key": client_id, "trakt-api-version": "2",
            "Authorization": "Bearer " + current_user[1]})
        logerror(response)
        header = response.headers
        response = json.loads(response.content, object_hook=lambda d: SimpleNamespace(**d))
    except:
        response = None
        header = None
    return response, header

def post(url, data):
    try:
        response = session.post(url, headers={
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36',
            'Content-type': "application/json", "trakt-api-key": client_id, "trakt-api-version": "2",
            "Authorization": "Bearer " + current_user[1]}, data=data)
        logerror(response)
        response = json.loads(response.content, object_hook=lambda d: SimpleNamespace(**d))
        time.sleep(1.1)
    except:
        response = None
    return response

def oauth(code=""):
    if code == "":
        response = post('https://api.trakt.tv/oauth/device/code', json.dumps({'client_id': client_id}))
        if not response == None:
            return response.device_code, response.user_code
        else:
            print("trakt.tv could not be reached right now! Please try again later. The script will most likely exit after this message.")
            time.sleep(5)
    else:
        response = None
        while response == None:
            response = post('https://api.trakt.tv/oauth/device/token', json.dumps(
                {'code': code, 'client_id': client_id, 'client_secret': client_secret}))
            time.sleep(1)
        return response.access_token

def setEID(self):
    EID = []
    if hasattr(self,"ids"):
        if hasattr(self.ids,"imdb"):
            if not self.ids.imdb == None:
                EID += ['imdb://' + str(self.ids.imdb)]
        if hasattr(self.ids,"tmdb"):
            if not self.ids.tmdb == None:
                EID += ['tmdb://' + str(self.ids.tmdb)]
        if hasattr(self.ids,"tvdb"):
            if not self.ids.tvdb == None:
                EID += ['tvdb://' + str(self.ids.tvdb)]
    return EID

class watchlist(classes.watchlist):
    autoremove = "movie"

    def __init__(self):
        global current_user
        global lists
        if len(lists) > 0:
            ui_print('[trakt] getting all trakt lists ...')
        self.data = []
        for list in lists:
            list_type = "public"
            for user in users:
                if list == user[0] + "'s watchlist":
                    list_type = "watchlist"
                    break
                if list == user[0] + "'s collection":
                    list_type = "collection"
                    break
                if list.startswith(user[0] + "'s private list:"):
                    list_type = "private"
                    break
            current_user = user
            if list_type == "watchlist":
                try:
                    watchlist_items, header = get('https://api.trakt.tv/users/me/watchlist/movies,shows?extended=full')
                    for element in watchlist_items:
                        if hasattr(element, 'show'):
                            element.show.type = 'show'
                            element.show.user = user
                            element.show.guid = element.show.ids.trakt
                            if not element.show in self.data:
                                self.data.append(show(element.show))
                        elif hasattr(element, 'movie'):
                            element.movie.type = 'movie'
                            element.movie.user = user
                            element.movie.guid = element.movie.ids.trakt
                            if not element.movie in self.data:
                                self.data.append(movie(element.movie))
                except Exception as e:
                    ui_print("[trakt error]: (exception): " + str(e), debug=ui_settings.debug)
                    continue
            elif list_type == "collection":
                try:
                    watchlist_items, header = get('https://api.trakt.tv/sync/collection/shows?extended=full')
                    for element in watchlist_items:
                        if hasattr(element, 'show'):
                            element.show.type = 'show'
                            element.show.user = user
                            element.show.guid = element.show.ids.trakt
                            if not element.show in self.data:
                                self.data.append(show(element.show))
                except Exception as e:
                    ui_print("[trakt error]: (exception): " + str(e), debug=ui_settings.debug)
                    continue
            elif list_type == "private":
                try:
                    response, header = get('https://api.trakt.tv/users/me/lists')
                    p_list_id = None
                    for p_list in response:
                        if list == user[0] + "'s private list: " + p_list.name:
                            p_list_id = p_list.ids.trakt
                            break
                    if not p_list_id == None:
                        watchlist_items, header = get('https://api.trakt.tv/users/me/lists/'+str(p_list_id)+'/items/movies,shows?extended=full')
                        for element in watchlist_items:
                            if hasattr(element, 'show'):
                                element.show.type = 'show'
                                element.show.user = user
                                element.show.guid = element.show.ids.trakt
                                if not element.show in self.data:
                                    self.data.append(show(element.show))
                            elif hasattr(element, 'movie'):
                                element.movie.type = 'movie'
                                element.movie.user = user
                                element.movie.guid = element.movie.ids.trakt
                                if not element.movie in self.data:
                                    self.data.append(movie(element.movie))
                except Exception as e:
                    ui_print("[trakt error]: (exception): " + str(e), debug=ui_settings.debug)
                    continue
            else:
                try:
                    watchlist_items, header = get('https://api.trakt.tv' + list + '/items/movies,shows?extended=full')
                    for element in watchlist_items:
                        if hasattr(element, 'show'):
                            element.show.type = 'show'
                            element.show.user = user
                            element.show.guid = element.show.ids.trakt
                            if not element.show in self.data:
                                self.data.append(show(element.show))
                        elif hasattr(element, 'movie'):
                            element.movie.type = 'movie'
                            element.movie.user = user
                            element.movie.guid = element.movie.ids.trakt
                            if not element.movie in self.data:
                                self.data.append(movie(element.movie))
                except Exception as e:
                    ui_print("[trakt error]: (exception): " + str(e), debug=ui_settings.debug)
                    continue
        ui_print('done')

    def update(self):
        global current_user
        global users
        refresh = False
        new_watchlist = []
        for list in lists:
            list_type = "public"
            for user in users:
                if list == user[0] + "'s watchlist":
                    list_type = "watchlist"
                    break
                if list.startswith(user[0] + "'s private list:"):
                    list_type = "private"
                    break
            current_user = user
            if list_type == "watchlist":
                try:
                    watchlist_items, header = get('https://api.trakt.tv/users/me/watchlist/movies,shows?extended=full')
                    for element in watchlist_items:
                        if hasattr(element, 'show'):
                            element.show.type = 'show'
                            element.show.user = user
                            element.show.guid = element.show.ids.trakt
                            if not element.show in self.data:
                                refresh = True
                                ui_print('[trakt] item: "' + element.show.title + '" found in ' + current_user[0] + "'s trakt watchlist.")
                                self.data.append(show(element.show))
                            new_watchlist += [element.show]
                        elif hasattr(element, 'movie'):
                            element.movie.type = 'movie'
                            element.movie.user = user
                            element.movie.guid = element.movie.ids.trakt
                            if not element.movie in self.data:
                                refresh = True
                                ui_print('[trakt] item: "' + element.movie.title + '" found in ' + current_user[0] + "'s trakt watchlist.")
                                self.data.append(movie(element.movie))
                            new_watchlist += [element.movie]
                except Exception as e:
                    ui_print("[trakt error]: (exception): " + str(e), debug=ui_settings.debug)
                    continue
            if list_type == "private":
                try:
                    response, header = get('https://api.trakt.tv/users/me/lists')
                    p_list_id = None
                    for p_list in response:
                        if list == user[0] + "'s private list: " + p_list.name:
                            p_list_id = p_list.ids.trakt
                            break
                    if not p_list_id == None:
                        watchlist_items, header = get('https://api.trakt.tv/users/me/lists/'+str(p_list_id)+'/items/movies,shows?extended=full')
                        for element in watchlist_items:
                            if hasattr(element, 'show'):
                                element.show.type = 'show'
                                element.show.user = user
                                element.show.guid = element.show.ids.trakt
                                if not element.show in self.data:
                                    refresh = True
                                    ui_print('[trakt] item: "' + element.show.title + '" found in ' + current_user[0] + "'s private list: "+p_list.name+".")
                                    self.data.append(show(element.show))
                                new_watchlist += [element.show]
                            elif hasattr(element, 'movie'):
                                element.movie.type = 'movie'
                                element.movie.user = user
                                element.movie.guid = element.movie.ids.trakt
                                if not element.movie in self.data:
                                    refresh = True
                                    ui_print('[trakt] item: "' + element.movie.title + '" found in ' + current_user[0] + "'s private list: "+p_list.name+".")
                                    self.data.append(movie(element.movie))
                                new_watchlist += [element.movie]
                except Exception as e:
                    ui_print("[trakt error]: (exception): " + str(e), debug=ui_settings.debug)
                    continue
        for element in self.data[:]:
            if not element in new_watchlist:
                self.data.remove(element)
        if refresh:
            return True
        return False

    def remove(self, original_element):
        global current_user
        element = copy.deepcopy(original_element)
        user = copy.deepcopy(element.user)
        data = []
        shows = []
        movies = []
        if element.type == 'tv':
            for ids in element.ids.__dict__.copy():
                value = getattr(element.ids, ids)
                if not value:
                    delattr(element.ids, ids)
            for attribute in element.__dict__.copy():
                if not (
                        attribute == 'ids' or attribute == 'seasons' or attribute == 'title' or attribute == 'year'):
                    delattr(element, attribute)
            ui_print('[trakt] item: "' + element.title + '" removed from ' + user[0] + '`s watchlist')
            shows += [element]
        elif element.type == 'movie':
            for ids in element.ids.__dict__.copy():
                value = getattr(element.ids, ids)
                if not value:
                    delattr(element.ids, ids)
            for attribute in element.__dict__.copy():
                if not (attribute == 'ids' or attribute == 'title' or attribute == 'year'):
                    delattr(element, attribute)
            ui_print('[trakt] item: "' + element.title + '" removed from ' + user[0] + '`s watchlist')
            movies += [element]
        data = {'movies': movies, 'shows': shows}
        current_user = user
        post('https://api.trakt.tv/sync/watchlist/remove', json.dumps(data, default=lambda o: o.__dict__))
        try:
            p_lists = []
            for list in lists:
                if list.startswith(user[0] + "'s private list: "):
                    p_lists += [list]
            if len(p_lists) > 0:
                response, header = get('https://api.trakt.tv/users/me/lists')
                p_list_id = None
                for list in p_lists:
                    for p_list in response:
                        if list == user[0] + "'s private list: " + p_list.name:
                            p_list_id = p_list.ids.trakt
                            break
                    if not p_list_id == None:
                        post('https://api.trakt.tv/users/me/lists/'+p_list_id+'/items/remove', json.dumps(data, default=lambda o: o.__dict__))
        except Exception as e:
            ui_print("[trakt error]: (exception): " + str(e), debug=ui_settings.debug)

class season(classes.media):
    def __init__(self, other):
        self.watchlist = watchlist
        self.__dict__.update(other.__dict__)
        self.EID = setEID(self)
        self.Episodes = []
        if hasattr(self, 'ids.trakt'):
            self.guid = self.ids.trakt
        else:
            self.guid = None
        try:
            if hasattr(self, 'first_aired'):
                if not self.first_aired == None:
                    self.originallyAvailableAt = datetime.datetime.strptime(self.first_aired,
                                                                            '%Y-%m-%dT%H:%M:%S.000Z').strftime(
                        '%Y-%m-%d')
                else:
                    self.originallyAvailableAt = datetime.datetime.utcnow().strftime('%Y-%m-%d')
            else:
                self.originallyAvailableAt = datetime.datetime.utcnow().strftime('%Y-%m-%d')
        except:
            self.originallyAvailableAt = datetime.datetime.utcnow().strftime('%Y-%m-%d')
        self.index = self.number
        self.type = 'season'
        for episode_ in self.episodes:
            episode_.grandparentYear = self.parentYear
            episode_.grandparentTitle = self.parentTitle
            episode_.grandparentGuid = self.parentGuid
            episode_.grandparentEID = self.parentEID
            episode_.parentIndex = self.index
            episode_.parentEID = self.EID
            self.Episodes += [episode(episode_)]
        self.leafCount = len(self.Episodes)

class episode(classes.media):
    def __init__(self, other):
        self.watchlist = watchlist
        self.__dict__.update(other.__dict__)
        self.EID = setEID(self)
        if hasattr(self, 'ids.trakt'):
            self.guid = self.ids.trakt
        else:
            self.guid = None
        try:
            if hasattr(self, 'first_aired'):
                if not self.first_aired == None:
                    self.originallyAvailableAt = datetime.datetime.strptime(self.first_aired,
                                                                            '%Y-%m-%dT%H:%M:%S.000Z').strftime(
                        '%Y-%m-%d')
                else:
                    self.originallyAvailableAt = datetime.datetime.utcnow().strftime('%Y-%m-%d')
            else:
                self.originallyAvailableAt = datetime.datetime.utcnow().strftime('%Y-%m-%d')
        except:
            self.originallyAvailableAt = datetime.datetime.utcnow().strftime('%Y-%m-%d')
        self.index = self.number
        self.type = 'episode'

class show(classes.media):
    def __init__(self, other):
        self.watchlist = watchlist
        self.__dict__.update(other.__dict__)
        self.Seasons = []
        self.guid = self.ids.trakt
        self.EID = setEID(self)
        try:
            self.originallyAvailableAt = datetime.datetime.strptime(self.first_aired,
                                                                    '%Y-%m-%dT%H:%M:%S.000Z').strftime('%Y-%m-%d')
        except:
            self.originallyAvailableAt = datetime.datetime.utcnow().strftime('%Y-%m-%d')
        response, header = get(
            'https://api.trakt.tv/shows/' + str(self.ids.trakt) + '/seasons?extended=episodes,full')
        leafCount = 0
        for season_ in response:
            if not season_.number == 0:
                season_.parentYear = self.year
                season_.parentTitle = self.title
                season_.parentGuid = self.guid
                season_.parentEID = self.EID
                self.Seasons += [season(season_)]
        for season_ in self.Seasons:
            leafCount += season_.leafCount
        self.leafCount = leafCount

class movie(classes.media):
    def __init__(self, other):
        self.watchlist = watchlist
        try:
            self.originallyAvailableAt = other.released
            delattr(other, 'released')
        except:
            self.originallyAvailableAt = datetime.datetime.utcnow().strftime('%Y-%m-%d')
        self.__dict__.update(other.__dict__)
        self.EID = setEID(self)

class library(classes.library):
    name = 'Trakt Collection'
    user = []

    def setup(cls, new=False):
        from settings import settings_list
        print()
        traktuser = []
        for category, allsettings in settings_list:
            for setting in allsettings:
                if setting.name == 'Trakt users':
                    traktuser = setting
        if len(users) == 0:
            print('Please set up a trakt user first:')
            print()
            traktuser.setup()
            print()
        back = False
        while not back:
            print('Please choose the trakt user whos trakt collection plex_debrid should use to determine your current media collection.')
            print()
            indices = []
            for index, user in enumerate(users):
                print(str(index + 1) + ') ' + user[0] + "'s trakt collection")
                indices += [str(index + 1)]
            print()
            choice = input("Choose a trakt users collection: ")
            if choice in indices:
                library.user = users[int(choice) - 1]
                classes.library.active = [library.name]
                back = True

    def __new__(self):
        global current_user
        current_user = library.user
        ui_print('[trakt] getting ' + current_user[0] + "'s" + ' entire trakt collection ...')
        watchlist_items = []
        collection = []
        try:
            collection_movies, header = get('https://api.trakt.tv/sync/collection/movies?extended=metadata')
            collection_shows, header = get('https://api.trakt.tv/sync/collection/shows?extended=metadata')
            watchlist_items += collection_movies
            watchlist_items += collection_shows
            for element in watchlist_items:
                if hasattr(element, 'show'):
                    element.show.type = 'show'
                    element.show.user = library.user
                    element.show.guid = element.show.ids.trakt
                    element.show.EID = setEID(element.show)
                    element.show.Seasons = []
                    for season_ in element.seasons:
                        season_.parentYear = element.show.year
                        season_.parentTitle = element.show.title
                        season_.parentGuid = element.show.guid
                        season_.parentEID = element.show.EID
                        element.show.Seasons += [season(season_)]
                    leafCount = 0
                    for season_ in element.show.Seasons:
                        leafCount += season_.leafCount
                    element.show.leafCount = leafCount
                    collection.append(classes.media(element.show))
                elif hasattr(element, 'movie'):
                    element.movie.type = 'movie'
                    element.movie.user = library.user
                    element.movie.guid = element.movie.ids.trakt
                    element.movie.EID = setEID(element.movie)
                    collection.append(classes.media(element.movie))
            ui_print('done')
            return collection
        except Exception as e:
            ui_print("[trakt] error: (exception): " + str(e), debug=ui_settings.debug)
            ui_print("[trakt] error: couldnt get trakt collection. the script will pause all downloads to avoid unwanted behavior.")
            return []

    class refresh(classes.refresh):
        
        user = []
        name = 'Trakt Collection'

        def setup(cls, new=False):
            from settings import settings_list
            print()
            traktuser = []
            for category, allsettings in settings_list:
                for setting in allsettings:
                    if setting.name == 'Trakt users':
                        traktuser = setting
            if len(users) == 0:
                print('Please set up a trakt user first:')
                print()
                traktuser.setup()
                print()
            back = False
            while not back:
                print('Please choose the trakt user whos trakt collection plex_debrid should update after a successful download.')
                print()
                indices = []
                for index, user in enumerate(users):
                    print(str(index + 1) + ') ' + user[0] + "'s trakt collection")
                    indices += [str(index + 1)]
                print()
                choice = input("Choose a trakt users collection: ")
                if choice in indices:
                    library.refresh.user = users[int(choice) - 1]
                    classes.refresh.active += [library.refresh.name]
                    back = True

        def __new__(cls, original_element):
            global current_user
            element = copy.deepcopy(original_element)
            data = []
            shows = []
            movies = []
            # determine release quality
            try:
                if len(element.Releases) == 0:
                    element.Releases += [element.Seasons[0].Releases[0]]
                resolution = regex.search(r'(2160|1080|720)(?=p)', element.Releases[0].title, regex.I)
            except:
                resolution = False
            if resolution:
                if resolution.group() == '2160':
                    resolution = 'uhd_4k'
                elif resolution.group() == '1080':
                    resolution = 'hd_1080p'
                elif resolution.group() == '720':
                    resolution = 'hd_720p'
            else:
                resolution = 'sd_480p'
            try:
                hdr = regex.search(r'(HDR)', element.Releases[0].title, regex.I)
            except:
                hdr = False
            if hdr:
                hdr = 'hdr10'
            # add release quality to element
            if element.type == 'show':
                if hasattr(element, 'Seasons'):
                    for season in element.Seasons:
                        for attribute in season.__dict__.copy():
                            if not (attribute == 'ids' or attribute == 'episodes' or attribute == 'number'):
                                delattr(season, attribute)
                        for episode in season.episodes:
                            if hdr:
                                episode.media_type = 'digital'
                                episode.resolution = resolution
                                episode.hdr = hdr
                            else:
                                episode.media_type = 'digital'
                                episode.resolution = resolution
                else:
                    ui_print("[trakt] error: couldnt find seasons in show object", debug=ui_settings.debug)
                # remove unwanted attributes from element
                element.seasons = element.Seasons
                for ids in element.ids.__dict__.copy():
                    value = getattr(element.ids, ids)
                    if not value:
                        delattr(element.ids, ids)
                for attribute in element.__dict__.copy():
                    if not (
                            attribute == 'ids' or attribute == 'seasons' or attribute == 'title' or attribute == 'year'):
                        delattr(element, attribute)
                shows += [element]
            elif element.type == 'movie':
                if hdr:
                    element.media_type = 'digital'
                    element.resolution = resolution
                    element.hdr = hdr
                else:
                    element.media_type = 'digital'
                    element.resolution = resolution
                # remove unwanted attributes from element
                for ids in element.ids.__dict__.copy():
                    value = getattr(element.ids, ids)
                    if not value:
                        delattr(element.ids, ids)
                for attribute in element.__dict__.copy():
                    if not (
                            attribute == 'ids' or attribute == 'resolution' or attribute == 'media_type' or attribute == 'hdr' or attribute == 'title' or attribute == 'year'):
                        delattr(element, attribute)
                movies += [element]
            # add element to collection
            current_user = library.refresh.user
            data = {'movies': movies, 'shows': shows}
            response = post('https://api.trakt.tv/sync/collection',
                                    json.dumps(data, default=lambda o: o.__dict__))
            ui_print('[trakt] item: ' + element.title + ' added to ' + library.refresh.user[0] + "'s collection")

    class ignore(classes.ignore):

        name = 'Trakt Watch Status'
        user = ""
        last_check = None
        watched = []

        def setup(cls, new=False):
            ui_cls("Options/Settings/Library Services/Library ignore services")
            from settings import settings_list
            settings = []
            for category, allsettings in settings_list:
                for setting in allsettings:
                    settings += [setting]
            if len(users) == 0:
                print("It looks like you havent setup a trakt user. Please set up a trakt user first.")
                print()
                for setting in settings:
                    if setting.name == "Trakt users":
                        setting.setup()
            if not new:
                print("Current trakt user, whos watch status is used to ignore content: '" + library.ignore.user + "'")
                print()
                print("0) Back")
                print("1) Change trakt user")
                print()
                choice = input("Choose an action: ")
                if choice == '1':
                    addable_users = []
                    for index,plexuser in enumerate(users):
                        addable_users += [plexuser[0]]
                    if len(addable_users) == 0:
                        print()
                        print("It seems there only is one trakt user!")
                        time.sleep(3)
                        return
                    indices = []
                    print("Please choose a trakt users, whos watch status should be used to ignore content: ")
                    print()
                    print("0) Back")
                    for index,ignoreuser in enumerate(addable_users):
                        print(str(index+1) + ") Trakt user '" + ignoreuser + "'")
                        indices += [str(index+1)]
                    print()
                    choice = input("Please choose a trakt user: ")
                    if choice in indices:
                        library.ignore.user = addable_users[int(choice)-1]
                        print()
                        print("Successfully changed to trakt user '" + addable_users[int(choice)-1] + "'")
                        print()
                        time.sleep(3)
            else:
                addable_users = []
                for index,plexuser in enumerate(users):
                    addable_users += [plexuser[0]]
                print("Please choose a trakt user, whos watch status should be used to ignore content: ")
                print()
                indices = []
                for index,ignoreuser in enumerate(addable_users):
                    print(str(index+1) + ") Trakt user '" + ignoreuser + "'")
                    indices += [str(index+1)]
                print()
                choice = input("Please choose a trakt user: ")
                if choice in indices:
                    library.ignore.user = addable_users[int(choice)-1]
                    if not library.ignore.name in classes.ignore.active:
                        classes.ignore.active += [library.ignore.name]
                    print()
                    print("Successfully added trakt user '" + addable_users[int(choice)-1] + "'")
                    print()
                    time.sleep(3)

        def add(self):
            global current_user
            try:
                ignoreuser = library.ignore.user
                user = None
                for plexuser in users:
                    if plexuser[0] == ignoreuser:
                        user = plexuser
                        break
                if user == None:
                    print("[trakt] error: Could not find trakt ignore service user: '"+ignoreuser+"'. Make sure this trakt user exists.")
                    return
                current_user = user
                ui_print('[trakt] ignoring item: ' + self.query() + " for user: '" + ignoreuser + "'")
                element = copy.deepcopy(self)
                data = []
                shows = []
                movies = []
                seasons = []
                episodes = []
                if element.type == 'show':
                    if hasattr(element, 'Seasons'):
                        for season in element.Seasons:
                            for attribute in season.__dict__.copy():
                                if not (attribute == 'ids' or attribute == 'episodes' or attribute == 'number'):
                                    delattr(season, attribute)
                    else:
                        ui_print("[trakt] error: couldnt find seasons in show object", debug=ui_settings.debug)
                    # remove unwanted attributes from element
                    element.seasons = element.Seasons
                    for ids in element.ids.__dict__.copy():
                        value = getattr(element.ids, ids)
                        if not value:
                            delattr(element.ids, ids)
                    for attribute in element.__dict__.copy():
                        if not (attribute == 'ids' or attribute == 'seasons' or attribute == 'title' or attribute == 'year'):
                            delattr(element, attribute)
                    shows += [element]
                elif element.type == 'season':
                    if hasattr(element, 'seasons'):
                        for episode in element.episodes:
                            for attribute in episode.__dict__.copy():
                                if not (attribute == 'ids' or attribute == 'number'):
                                    delattr(episode, attribute)
                    # remove unwanted attributes from element
                    for ids in element.ids.__dict__.copy():
                        value = getattr(element.ids, ids)
                        if not value:
                            delattr(element.ids, ids)
                    for attribute in element.__dict__.copy():
                        if not (attribute == 'ids' or attribute == 'episodes' or attribute == 'title' or attribute == 'year'):
                            delattr(element, attribute)
                    seasons += [element]
                elif element.type == 'movie':
                    # remove unwanted attributes from element
                    for ids in element.ids.__dict__.copy():
                        value = getattr(element.ids, ids)
                        if not value:
                            delattr(element.ids, ids)
                    for attribute in element.__dict__.copy():
                        if not (attribute == 'ids' or attribute == 'resolution' or attribute == 'media_type' or attribute == 'hdr' or attribute == 'title' or attribute == 'year'):
                            delattr(element, attribute)
                    movies += [element]
                elif element.type == 'episode':
                    # remove unwanted attributes from element
                    for ids in element.ids.__dict__.copy():
                        value = getattr(element.ids, ids)
                        if not value:
                            delattr(element.ids, ids)
                    for attribute in element.__dict__.copy():
                        if not (attribute == 'ids' or attribute == 'resolution' or attribute == 'media_type' or attribute == 'hdr' or attribute == 'title' or attribute == 'year'):
                            delattr(element, attribute)
                    episodes += [element]
                # add element to collection
                data = {'movies': movies, 'shows': shows, 'seasons': seasons, 'episodes': episodes}
                response = post('https://api.trakt.tv/sync/history',json.dumps(data, default=lambda o: o.__dict__))
                if not self in classes.ignore.ignored:
                    classes.ignore.ignored += [self]
            except Exception as e:
                ui_print("trakt error: couldnt ignore item: " + str(e), debug=ui_settings.debug)

        def remove(self):
            global current_user
            try:
                ignoreuser = library.ignore.user
                user = None
                for plexuser in users:
                    if plexuser[0] == ignoreuser:
                        user = plexuser
                        break
                if user == None:
                    print("[trakt] error: Could not find trakt ignore service user: '"+ignoreuser+"'. Make sure this trakt user exists.")
                    return
                current_user = user
                ui_print('[trakt] un-ignoring item: ' + self.query() + " for user: '" + ignoreuser + "'")
                element = copy.deepcopy(self)
                data = []
                shows = []
                movies = []
                seasons = []
                episodes = []
                if element.type == 'show':
                    if hasattr(element, 'Seasons'):
                        for season in element.Seasons:
                            for attribute in season.__dict__.copy():
                                if not (attribute == 'ids' or attribute == 'episodes' or attribute == 'number'):
                                    delattr(season, attribute)
                    else:
                        ui_print("[trakt] error: couldnt find seasons in show object", debug=ui_settings.debug)
                    # remove unwanted attributes from element
                    element.seasons = element.Seasons
                    for ids in element.ids.__dict__.copy():
                        value = getattr(element.ids, ids)
                        if not value:
                            delattr(element.ids, ids)
                    for attribute in element.__dict__.copy():
                        if not (attribute == 'ids' or attribute == 'seasons' or attribute == 'title' or attribute == 'year'):
                            delattr(element, attribute)
                    shows += [element]
                elif element.type == 'season':
                    if hasattr(element, 'seasons'):
                        for episode in element.episodes:
                            for attribute in episode.__dict__.copy():
                                if not (attribute == 'ids' or attribute == 'number'):
                                    delattr(episode, attribute)
                    # remove unwanted attributes from element
                    for ids in element.ids.__dict__.copy():
                        value = getattr(element.ids, ids)
                        if not value:
                            delattr(element.ids, ids)
                    for attribute in element.__dict__.copy():
                        if not (attribute == 'ids' or attribute == 'episodes' or attribute == 'title' or attribute == 'year'):
                            delattr(element, attribute)
                    seasons += [element]
                elif element.type == 'movie':
                    # remove unwanted attributes from element
                    for ids in element.ids.__dict__.copy():
                        value = getattr(element.ids, ids)
                        if not value:
                            delattr(element.ids, ids)
                    for attribute in element.__dict__.copy():
                        if not (attribute == 'ids' or attribute == 'resolution' or attribute == 'media_type' or attribute == 'hdr' or attribute == 'title' or attribute == 'year'):
                            delattr(element, attribute)
                    movies += [element]
                elif element.type == 'episode':
                    # remove unwanted attributes from element
                    for ids in element.ids.__dict__.copy():
                        value = getattr(element.ids, ids)
                        if not value:
                            delattr(element.ids, ids)
                    for attribute in element.__dict__.copy():
                        if not (attribute == 'ids' or attribute == 'resolution' or attribute == 'media_type' or attribute == 'hdr' or attribute == 'title' or attribute == 'year'):
                            delattr(element, attribute)
                    episodes += [element]
                # add element to collection
                data = {'movies': movies, 'shows': shows, 'seasons': seasons, 'episodes': episodes}
                response = post('https://api.trakt.tv/sync/history/remove',json.dumps(data, default=lambda o: o.__dict__))
                if self in classes.ignore.ignored:
                    classes.ignore.ignored.remove(self)
            except Exception as e:
                ui_print("trakt error: couldnt un-ignore item: " + str(e), debug=ui_settings.debug)

        def check(self):
            global current_user
            try:
                ignoreuser = library.ignore.user
                user = None
                for plexuser in users:
                    if plexuser[0] == ignoreuser:
                        user = plexuser
                        break
                if user == None:
                    print("[trakt] error: Could not find trakt ignore service user: '"+ignoreuser+"'. Make sure this trakt user exists.")
                    return False
                current_user = user
                history = library.ignore.history()
                if self.type == "movie":
                    if self in history:
                        if not self in  classes.ignore.ignored:
                            classes.ignore.ignored += [self]
                        return True
                if self.type == "episode":
                    for show in history:
                        if show.type == "show":
                            for season in show.Seasons:
                                for episode in season.Episodes:
                                    if episode == self:
                                        if not self in  classes.ignore.ignored:
                                            classes.ignore.ignored += [self]
                                        return True
                if self.type == "show":
                    match = next((x for x in history if x == self), None)
                    if match == None:
                        return False
                    if not len(match.Seasons) == len(self.Seasons):
                        return False
                    for season in self.Seasons:
                        matching_season = next((x for x in match.Seasons if x == season), None)
                        if len(season.Episodes) == len(matching_season.Episodes):
                            return False
                    if not self in  classes.ignore.ignored:
                        classes.ignore.ignored += [self]
                    return True
                if self.type == "season":
                    for show in history:
                        if show.type == "show":
                            for season in show.Seasons:
                                if season == self:
                                    if not self in  classes.ignore.ignored:
                                        classes.ignore.ignored += [self]
                                    return True
                return False
            except Exception as e:
                ui_print("[trakt] error: couldnt check ignore status for item: " + str(e), debug=ui_settings.debug)
                return False
    
        def history():
            data = []
            history = []
            try:
                if not library.ignore.last_check == None:
                    if time.time() - library.ignore.last_check < 20:
                        return library.ignore.watched
                library.ignore.last_check = time.time()
                response = get("https://api.trakt.tv/sync/watched/shows")
                data += response[0]
                response = get("https://api.trakt.tv/sync/watched/movies")
                data += response[0]
                for element in data:
                    if hasattr(element, 'show'):
                        element.show.type = 'show'
                        element.show.user = library.ignore.user
                        element.show.guid = element.show.ids.trakt
                        element.show.EID = setEID(element.show)
                        element.show.Seasons = []
                        for season_ in element.seasons:
                            season_.parentYear = element.show.year
                            season_.parentTitle = element.show.title
                            season_.parentGuid = element.show.guid
                            season_.parentEID = element.show.EID
                            element.show.Seasons += [season(season_)]
                        leafCount = 0
                        for season_ in element.show.Seasons:
                            leafCount += season_.leafCount
                        element.show.leafCount = leafCount
                        history.append(classes.media(element.show))
                    elif hasattr(element, 'movie'):
                        element.movie.type = 'movie'
                        element.movie.user = library.ignore.user
                        element.movie.guid = element.movie.ids.trakt
                        element.movie.EID = setEID(element.movie)
                        history.append(classes.media(element.movie))
                library.ignore.watched = history
                return history
            except Exception as e:
                ui_print("[trakt] error: couldnt check ignore status for item: " + str(e), debug=ui_settings.debug)
                return None

def aliases(self,lan):
    global current_user
    ctrs = []
    for l in lan_ctr:
        if lan == l[0]:
            ctrs = l[1]
    aliases = []
    if len(users) > 0:
        current_user = users[0]
        type = ("shows" if self.type in ["show","season","episode"] else "movies")
        response, header = get('https://api.trakt.tv/'+type+'/' + str(self.ids.trakt) + '/aliases')
        if not response == None:
            if len(response) > 0:
                for alias in response:
                    if alias.country in ctrs:
                        aliases += [alias.title]
    return aliases

def translations(self,lan):
    global current_user
    translations = []
    if not lan == 'en':
        if len(users) > 0:
            current_user = users[0]
            type = ("shows" if self.type in ["show","season","episode"] else "movies")
            response, header = get('https://api.trakt.tv/'+type+'/' + str(self.ids.trakt) + '/translations/'+lan)
            if not response == None:
                if len(response) > 0:
                    for alias in response:
                        translations += [alias.title]
    return translations
    
def search(query, type):
    global current_user
    current_user = users[0]
    if type == 'all':
        response, header = get('https://api.trakt.tv/search/movie,show?query=' + str(query))
    elif type == 'movie':
        response, header = get('https://api.trakt.tv/search/movie?query=' + str(query))
    elif type == 'tv':
        response, header = get('https://api.trakt.tv/search/show?query=' + str(query))
    elif type == 'imdb':
        response, header = get('https://api.trakt.tv/search/imdb?query=' + str(query))
    elif type == 'tmdb':
        response, header = get('https://api.trakt.tv/search/tmdb?query=' + str(query))
    elif type == 'tvdb':
        response, header = get('https://api.trakt.tv/search/tvdb?query=' + str(query))
    return response

def match(self):
    global current_user
    current_user = users[0]
    if self.type == "season":
        if hasattr(self,"parentEID"):
            for EID in self.parentEID:
                type = "show"
                service,query = EID.split('://')
                response, header = get('https://api.trakt.tv/search/' + service + '/' + query + '?type=' + type + '&extended=full,episodes')
                try:
                    response[0].show.type = 'show'
                    response[0].show.guid = response[0].show.ids.trakt
                    trakt_show = show(response[0].show)
                    for trakt_season in trakt_show.Seasons:
                        if trakt_season == self:
                            return trakt_season
                    ui_print("couldnt find season in matched show",ui_settings.debug)
                    return None
                except:
                    continue
    elif hasattr(self,"EID"):
        for EID in self.EID:
            type = self.type
            service,query = EID.split('://')
            response, header = get('https://api.trakt.tv/search/' + service + '/' + query + '?type=' + type + '&extended=full,episodes')
            try:
                if type == 'movie':
                    response[0].movie.type = 'movie'
                    response[0].movie.guid = response[0].movie.ids.trakt
                    return movie(response[0].movie)
                elif type == 'show':
                    response[0].show.type = 'show'
                    response[0].show.guid = response[0].show.ids.trakt
                    return show(response[0].show)
                elif type == 'episode':
                    response[0].episode.type = 'episode'
                    response[0].episode.guid = response[0].episode.ids.trakt
                    return episode(response[0].episode)
            except:
                continue
    return None