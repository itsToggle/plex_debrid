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
                        print()
                        choice = input("Choose a list: ")
                        if choice == '0':
                            back = True
                        elif choice == '1':
                            print(
                                "To add a public list, please enter the lists url in the format shown by this example: (Example URL: '/users/giladg/lists/latest-releases') ")
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
        time.sleep(1)
    except:
        response = None
    return response

def oauth(code=""):
    if code == "":
        response = post('https://api.trakt.tv/oauth/device/code', json.dumps({'client_id': client_id}))
        return response.device_code, response.user_code
    else:
        response = None
        while response == None:
            response = post('https://api.trakt.tv/oauth/device/token', json.dumps(
                {'code': code, 'client_id': client_id, 'client_secret': client_secret}))
            time.sleep(1)
        return response.access_token

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
            current_user = user
            if list_type == "watchlist":
                try:
                    watchlist_items, header = get(
                        'https://api.trakt.tv/users/me/watchlist/movies,shows?extended=full')
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
            else:
                try:
                    watchlist_items, header = get(
                        'https://api.trakt.tv' + list + '/items/movies,shows?extended=full')
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
        if len(lists) > 0:
            ui_print('[trakt] updating all trakt watchlists ...', debug=ui_settings.debug)
        refresh = False
        new_watchlist = []
        for list in lists:
            public = True
            for user in users:
                if list == user[0] + "'s watchlist":
                    public = False
                    break
            current_user = user
            if not public:
                try:
                    watchlist_items, header = get(
                        'https://api.trakt.tv/users/me/watchlist/movies,shows?extended=full')
                    for element in watchlist_items:
                        if hasattr(element, 'show'):
                            element.show.type = 'show'
                            element.show.user = user
                            element.show.guid = element.show.ids.trakt
                            if not element.show in self.data:
                                refresh = True
                                ui_print(
                                    '[trakt] item: "' + element.show.title + '" found in ' + current_user[
                                        0] + "'s trakt watchlist.")
                                self.data.append(show(element.show))
                            new_watchlist += [element.show]
                        elif hasattr(element, 'movie'):
                            element.movie.type = 'movie'
                            element.movie.user = user
                            element.movie.guid = element.movie.ids.trakt
                            if not element.movie in self.data:
                                refresh = True
                                ui_print(
                                    '[trakt] item: "' + element.movie.title + '" found in ' + current_user[
                                        0] + "'s trakt watchlist.")
                                self.data.append(movie(element.movie))
                            new_watchlist += [element.movie]
                except Exception as e:
                    ui_print("[trakt error]: (exception): " + str(e), debug=ui_settings.debug)
                    continue
        for element in self.data[:]:
            if not element in new_watchlist:
                self.data.remove(element)
        if len(lists) > 0:
            ui_print('done', debug=ui_settings.debug)
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

class season(classes.media):
    def __init__(self, other):
        self.watchlist = watchlist
        self.__dict__.update(other.__dict__)
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
            episode_.parentIndex = self.index
            self.Episodes += [episode(episode_)]
        self.leafCount = len(self.Episodes)

class episode(classes.media):
    def __init__(self, other):
        self.watchlist = watchlist
        self.__dict__.update(other.__dict__)
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
            print('Please choose the trakt user whos trakt collection should be maintained by plex_debrid.')
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
        collection_movies, header = get('https://api.trakt.tv/sync/collection/movies?extended=metadata')
        collection_shows, header = get('https://api.trakt.tv/sync/collection/shows?extended=metadata')
        watchlist_items += collection_movies
        watchlist_items += collection_shows
        for element in watchlist_items:
            if hasattr(element, 'show'):
                element.show.type = 'show'
                element.show.user = library.user
                element.show.guid = element.show.ids.trakt
                element.show.Seasons = []
                for season_ in element.seasons:
                    season_.parentYear = element.show.year
                    season_.parentTitle = element.show.title
                    season_.parentGuid = element.show.guid
                    element.show.Seasons += [season(season_)]
                leafCount = 0
                for season_ in element.show.Seasons:
                    leafCount += season_.leafCount
                    collection.append(season_)
                    for episode in season_.Episodes:
                        collection.append(episode)
                element.show.leafCount = leafCount
                collection.append(classes.media(element.show))
            elif hasattr(element, 'movie'):
                element.movie.type = 'movie'
                element.movie.user = library.user
                element.movie.guid = element.movie.ids.trakt
                collection.append(classes.media(element.movie))
        ui_print('done')
        return collection

    def add(original_element):
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
            if hasattr(element, 'seasons'):
                for season in element.seasons:
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
        data = {'movies': movies, 'shows': shows}
        response = post('https://api.trakt.tv/sync/collection',
                                json.dumps(data, default=lambda o: o.__dict__))
        ui_print('[trakt] item: ' + element.title + ' added to ' + library.user[0] + "'s collection")
        sys.stdout.flush()

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

def match(query, service, type):
    global current_user
    current_user = users[0]
    if service == 'imdb':
        response, header = get(
            'https://api.trakt.tv/search/imdb/' + str(query) + '?type=' + type + '&extended=full,episodes')
    elif service == 'tmdb':
        response, header = get(
            'https://api.trakt.tv/search/tmdb/' + str(query) + '?type=' + type + '&extended=full,episodes')
    elif service == 'tvdb':
        response, header = get(
            'https://api.trakt.tv/search/tvdb/' + str(query) + '?type=' + type + '&extended=full,episodes')
    try:
        if type == 'movie':
            response[0].movie.type = 'movie'
            response[0].movie.guid = response[0].movie.ids.trakt
            return movie(response[0].movie)
        elif type == 'show':
            response[0].show.type = 'show'
            response[0].show.guid = response[0].show.ids.trakt
            return show(response[0].show)
        elif type == 'season':
            response[0].season.type = 'season'
            response[0].season.guid = response[0].season.ids.trakt
            return season(response[0].season)
        elif type == 'episode':
            response[0].episode.type = 'episode'
            response[0].episode.guid = response[0].episode.ids.trakt
            return episode(response[0].episode)
    except:
        return None
