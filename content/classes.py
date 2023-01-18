from base import *

import releases
import debrid
import scraper
from ui.ui_print import *

class watchlist(Sequence):
    def __init__(self, other):
        self.data = other

    def __getitem__(self, index):
        return self.data[index]

    def __len__(self):
        return len(self.data)

    def __eq__(self, other):
        return len(self) == len(other)

    def __add__(self,other):
        return watchlist(self.data + other.data)

    def remove(self, item):
        self.data.remove(item)

    def add(self, item, user):
        self.data.append(item)

class library:

    active = []

    def setup(cls, new=False):
        from settings import settings_list
        settings = []
        for category, allsettings in settings_list:
            for setting in allsettings:
                if setting.cls == cls or setting.name.startswith(cls.name):
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
                    if not cls.name in library.active:
                        library.active = [cls.name]
                    back = True
                elif choice == '0':
                    back = True
        else:
            print()
            indices = []
            for setting in settings:
                setting.setup()
                if not cls.name in library.active:
                    library.active = [cls.name]

    def __new__(cls):
        activeservices = []
        for servicename in library.active:
            for service in cls.__subclasses__():
                if service.name == servicename:
                    activeservices += [service]
        return activeservices

class refresh:
    
    active = []

    def setup(cls, new=False):
        from settings import settings_list
        settings = []
        for category, allsettings in settings_list:
            for setting in allsettings:
                if setting.cls == cls or setting.name.startswith(cls.name):
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
                    if not cls.name in refresh.active:
                        refresh.active = [cls.name]
                    back = True
                elif choice == '0':
                    back = True
        else:
            print()
            indices = []
            for setting in settings:
                setting.setup()
                if not cls.name in refresh.active:
                    refresh.active = [cls.name]

    def __new__(cls):
        activeservices = []
        for servicename in refresh.active:
            for service in cls.__subclasses__():
                if service.name == servicename:
                    activeservices += [service]
        return activeservices

class ignore:
    
    active = []
    ignored = []

    def setup(cls, new=False):
        from settings import settings_list
        settings = []
        for category, allsettings in settings_list:
            for setting in allsettings:
                if setting.cls == cls or setting.name.startswith(cls.name):
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
                    if not cls.name in ignore.active:
                        ignore.active += [cls.name]
                    back = True
                elif choice == '0':
                    back = True
        else:
            print()
            indices = []
            for setting in settings:
                setting.setup()
                if not cls.name in ignore.active:
                    ignore.active += [cls.name]
    
    def __new__(cls):
        activeservices = []
        for servicename in ignore.active:
            for service in cls.__subclasses__():
                if service.name == servicename:
                    activeservices += [service]
        return activeservices

    def add(self):
        for service in ignore():
            ui_print("ignoring item of type '" + self.__module__ + "' on service '" + service.__module__ + "'",ui_settings.debug)
            self.match(service.__module__)
            service.add(self)
    
    def remove(self):
        for service in ignore():
            ui_print("un-ignoring item of type '" + self.__module__ + "' on service '" + service.__module__ + "'",ui_settings.debug)
            self.match(service.__module__)
            service.remove(self)
    
    def check(self):
        check = False
        for service in ignore():
            self.match(service.__module__)
            if service.check(self):
                check = True
        return check

class media:
    
    ignore_queue = []
    downloaded_versions = []

    def __init__(self, other):
        self.__dict__.update(other.__dict__)

    def __eq__(self, other) -> bool:
        try:
            if type(other) == type(None):
                if type(self) == type(None):
                    return True
                return False
            if not self.type == other.type:
                return False
            if self.type == 'movie' or self.type == 'show':
                if hasattr(self,"EID") and hasattr(other,"EID"):
                    for EID in self.EID:
                        if EID in other.EID:
                            return True
                    return False
                return self.guid == other.guid
            elif self.type == 'season':
                if hasattr(self,"parentEID") and hasattr(other,"parentEID"):
                    for EID in self.parentEID:
                        if EID in other.parentEID and self.index == other.index:
                            return True
                    return False
                return self.parentGuid == other.parentGuid and self.index == other.index
            elif self.type == 'episode':
                if hasattr(self,"grandparentEID") and hasattr(other,"grandparentEID"):
                    for EID in self.grandparentEID:
                        if EID in other.grandparentEID and self.parentIndex == other.parentIndex and self.index == other.index:
                            return True
                    return False
                return self.grandparentGuid == other.grandparentGuid and self.parentIndex == other.parentIndex and self.index == other.index
        except:
            return False

    def __repr__(self):
        return str(self.__dict__)

    def match(self,service):
        if not hasattr(self,"services"):
            self.services = [self.__module__]
        if self.type == "show":
            for season in self.Seasons:
                if not hasattr(season,"services"):
                    season.services = [self.__module__]
                for episode in season.Episodes:
                    if not hasattr(episode,"services"):
                        episode.services = [self.__module__]
        if self.type == "season":
            for episode in self.Episodes:
                if not hasattr(episode,"services"):
                    episode.services = [self.__module__]
        if not service in self.services:
            query = "unknown"
            try:
                query = self.query()
            except:
                try:
                    query = self.EID[0]
                except:
                    query = "unknown"
            if not service == "content.services.textfile":
                ui_print("matching item: '"+query+"' of service '" + self.__module__ + "' to service '" + service + "'",ui_settings.debug)
            match = sys.modules[service].match(self)
            if match == None:
                return False
            delattr(match,'watchlist')
            if self.type in ["movie","episode"]:
                delattr(match,"guid")
                if hasattr(match,"year"):
                    if match.year == None:
                        delattr(match,"year")
                self.__dict__.update(match.__dict__)
                self.services += [service]
                return True
            elif self.type == "show":
                for season in match.Seasons[:]:
                    if not season in self.Seasons:
                        match.Seasons.remove(season)
                    elif self.services != ["content.services.overseerr"]:
                        matching_season = next((x for x in self.Seasons if x == season), None)
                        for episode in season.Episodes:
                            if not episode in matching_season.Episodes:
                                season.Episodes.remove(episode)
                if self.services != ["content.services.overseerr"]:
                    for season in match.Seasons:
                        matching_season = next((x for x in self.Seasons if x == season), None)
                        if not matching_season == None:
                            for episode in season.Episodes:
                                matching_episode = next((x for x in matching_season.Episodes if x == episode), None)
                                if not matching_episode == None:
                                    delattr(episode,"guid")
                                    matching_episode.__dict__.update(episode.__dict__)
                            season.__dict__.update(matching_season.__dict__)
                    delattr(match,"guid")
                else:
                    for season in match.Seasons:
                        if not hasattr(season,'services'):
                            season.services = [self.__module__]
                        for episode in season.Episodes:
                            if not hasattr(episode,'services'):
                                episode.services = [self.__module__]
                self.__dict__.update(match.__dict__)
                self.services += [service]
                for season in self.Seasons:
                    season.services += [service]
                    for episode in season.Episodes:
                        episode.services += [service]
                return True
            elif self.type == "season":
                for episode in match.Episodes[:]:
                    if not episode in self.Episodes:
                        match.Episodes.remove(episode)
                for episode in match.Episodes:
                    matching_episode = next((x for x in self.Episodes if x == episode), None)
                    if not matching_episode == None:
                        episode.__dict__.update(matching_episode.__dict__)
                self.__dict__.update(match.__dict__)
                self.services += [service]
                for episode in self.Episodes:
                    episode.services += [service]
                return True

    def query(self,title=""):
        if title == "":
            if self.type == 'movie':
                title = releases.rename(self.title)
            elif self.type == 'show':
                title = releases.rename(self.title)
            elif self.type == 'season':
                title = releases.rename(self.parentTitle)
            elif self.type == 'episode':
                title = releases.rename(self.grandparentTitle)
        if self.type == 'movie':
            title = title.replace('.' + str(self.year), '')
            return title + '.' + str(self.year)
        elif self.type == 'show':
            title = title.replace('.' + str(self.year), '')
            return title
        elif self.type == 'season':
            title = title.replace('.' + str(self.parentYear), '')
            return title + '.S' + str("{:02d}".format(self.index)) + '.'
        elif self.type == 'episode':
            title = title.replace('.' + str(self.grandparentYear), '')
            return title + '.S' + str("{:02d}".format(self.parentIndex)) + 'E' + str("{:02d}".format(self.index)) + '.'
    
    def anime_query(self,title=""):
        if title == "":
            if self.type == 'movie':
                title = releases.rename(self.title)
            elif self.type == 'show':
                title = releases.rename(self.title)
            elif self.type == 'season':
                title = releases.rename(self.parentTitle)
            elif self.type == 'episode':
                title = releases.rename(self.grandparentTitle)
        if self.type == 'movie':
            title = title.replace('.' + str(self.year), '')
            return title.replace('.',' ') + ' ' + str(self.year)
        elif self.type == 'show':
            title = title.replace('.' + str(self.year), '')
            return title.replace('.',' ')
        elif self.type == 'season':
            title = title.replace('.' + str(self.parentYear), '')
            return title.replace('.',' ') + ' ' + str(self.anime_season) + ' '
        elif self.type == 'episode':
            title = title.replace('.' + str(self.grandparentYear), '')
            return title.replace('.',' ') + ' ' + str(self.anime_count)

    def aliases(self,lan='en'):
        if len(sys.modules['content.services.trakt'].users) > 0:
            if not hasattr(self,"alternate_titles"):
                self.alternate_titles = []
            self.match('content.services.trakt')
            aliases = sys.modules['content.services.trakt'].aliases(self,lan)
            translations = sys.modules['content.services.trakt'].translations(self,lan)
            if not len(translations) == 0 and not len(aliases) == 0:
                aliases = translations + aliases
            elif not len(translations) == 0:
                aliases = translations
            if (lan == 'en' or len(aliases) == 0) and not releases.rename(self.title) in self.alternate_titles:
                aliases.insert(0,self.title)
            elif not releases.rename(self.title) in self.alternate_titles:
                aliases += [self.title]
            for title in aliases:
                if title == None or title == []:
                    continue
                title = releases.rename(title)
                if hasattr(self,"scraping_adjustment"):
                    for operator, value in self.scraping_adjustment:
                        if operator == "add text before title":
                            title_ = value + title
                        elif operator == "add text after title":
                            title_ = title + value
                        if not title_ in self.alternate_titles:
                            self.alternate_titles += [title_]
                else:
                    if not title in self.alternate_titles:
                        self.alternate_titles += [title]
            if self.type == "show":
                if hasattr(self,'Seasons'):
                    for season in self.Seasons:
                        season.alternate_titles = self.alternate_titles
                        if hasattr(season,'Episodes'):
                            for episode in season.Episodes:
                                episode.alternate_titles = self.alternate_titles
        else:
            title = releases.rename(self.title)
            if not hasattr(self,"alternate_titles"):
                self.alternate_titles = []
            if hasattr(self,"scraping_adjustment"):
                for operator, value in self.scraping_adjustment:
                    if operator == "add text before title":
                        title_ = value + title
                    elif operator == "add text after title":
                        title_ = title + value
                    if not title_ in self.alternate_titles:
                        self.alternate_titles += [title_]
            else:
                self.alternate_titles = [title]
            if self.type == "show":
                if hasattr(self,'Seasons'):
                    for season in self.Seasons:
                        season.alternate_titles = self.alternate_titles
                        if hasattr(season,'Episodes'):
                            for episode in season.Episodes:
                                episode.alternate_titles = self.alternate_titles
    
    def deviation(self):
        self.versions()
        if not self.isanime():
            if hasattr(self,'alternate_titles'):
                title = '(' + '|'.join(self.alternate_titles) + ')'
            else:
                if self.type == 'movie':
                    title = releases.rename(self.title)
                elif self.type == 'show':
                    title = releases.rename(self.title)
                elif self.type == 'season':
                    title = releases.rename(self.parentTitle)
                elif self.type == 'episode':
                    title = releases.rename(self.grandparentTitle)
            escape_chars = ['[',']']
            for char in escape_chars:
                title = title.replace(char,'\\'+char)
            if self.type == 'movie':
                title = title.replace('.' + str(self.year), '')
                return '[^A-Za-z0-9]*(' + title + ':?.)\(?\[?(' + str(self.year) + '|' + str(self.year - 1) + '|' + str(self.year + 1) + ')'
            elif self.type == 'show':
                title = title.replace('.' + str(self.year), '')
                return '[^A-Za-z0-9]*(' + title + ':?.)(series.)?((\(?' + str(self.year) + '\)?.)|(complete.)|(seasons?.[0-9]+.[0-9]?[0-9]?.?)|(S[0-9]+.S?[0-9]?[0-9]?.?)|(S[0-9]+E[0-9]+))'
            elif self.type == 'season':
                title = title.replace('.' + str(self.parentYear), '')
                return '[^A-Za-z0-9]*(' + title + ':?.)(series.)?(\(?' + str(self.parentYear) + '\)?.)?(season.' + str(self.index) + '.|season.' + str("{:02d}".format(self.index)) + '.|S' + str("{:02d}".format(self.index)) + '.)'
            elif self.type == 'episode':
                title = title.replace('.' + str(self.grandparentYear), '')
                return '[^A-Za-z0-9]*(' + title + ':?.)(series.)?(\(?' + str(self.grandparentYear) + '\)?.)?(S' + str("{:02d}".format(self.parentIndex)) + 'E' + str("{:02d}".format(self.index)) + '.)'
        else:
            if hasattr(self,'alternate_titles'):
                title = '(' + '|'.join(self.alternate_titles) + ')'
            else:
                if self.type == 'movie':
                    title = releases.rename(self.title)
                elif self.type == 'show':
                    title = releases.rename(self.title)
                elif self.type == 'season':
                    title = releases.rename(self.parentTitle)
                elif self.type == 'episode':
                    title = releases.rename(self.grandparentTitle)
            escape_chars = ['[',']']
            for char in escape_chars:
                title = title.replace(char,'\\'+char)
            if self.type == 'movie':
                title = title.replace('.' + str(self.year), '')
                return '(.*?)(' + title + '.)(.*?)(' + str(self.year) + '|' + str(self.year - 1) + '|' + str(self.year + 1) + ')'
            elif self.type == 'show':
                title = title.replace('.' + str(self.year), '')
                return '(.*?)(' + title + '.)(.*?)('+self.anime_count+'|complete)'
            elif self.type == 'season':
                title = title.replace('.' + str(self.parentYear), '')
                return '(.*?)(' + title + '.)(.*?)(season.' + str(self.index) + '|season.' + str("{:02d}".format(self.index)) + '|S?' + str("{:02d}".format(self.index)) + '|'+str(self.index)+'|'+self.anime_count+')'
            elif self.type == 'episode':
                title = title.replace('.' + str(self.grandparentYear), '')
                return '(.*?)(' + title + '.)(.*?)(S' + str("{:02d}".format(self.parentIndex)) + '.?E' + str("{:02d}".format(self.index)) + '|'+self.anime_count+')'

    def isanime(self):
        if 'anime' in self.genre():
            if self.type == "show":
                self.anime_count = 0
                if hasattr(self,'Seasons'):
                    for season in self.Seasons:
                        season.genres = ['anime']
                        season.anime_season = (str(self.anime_count + 1) if self.anime_count == 0 else str(self.anime_count))
                        if hasattr(season,'Episodes'):
                            for episode in season.Episodes:
                                self.anime_count += 1
                                episode.genres = ['anime']
                                episode.anime_count = str(self.anime_count)
                        season.anime_count = '-0*(' + str(self.anime_count) + '|' + str(self.anime_count+1) + ')'
                        season.anime_season = season.anime_season + '-' + str(self.anime_count)
                self.anime_count = '-0*(' + str(self.anime_count) + '|' + str(self.anime_count+1) + ')'
            return True
        return False
    
    def genre(self):
        genres = []
        if hasattr(self,'genres'):
            if not self.genres == None:
                for gen in self.genres:
                    genres += [gen]
        if hasattr(self,"Genre"):
            if not self.Genre == None:
                for gen in self.Genre:
                    genres += [gen.slug]
        return genres
        
    def versions(self):
        versions = []
        for version in releases.sort.versions:
            versions += [releases.sort.version(version[0], version[1], version[2], version[3])]
        for version in versions[:]:
            missing = False
            if self.type == "movie" or self.type == "episode":
                if self.query() + ' [' + version.name + ']' in media.downloaded_versions:
                    versions.remove(version)
            elif self.type == 'show':
                for season in self.Seasons:
                    for episode in season.Episodes:
                        if not episode.query() + ' [' + version.name + ']' in media.downloaded_versions:
                            missing = True
                            break
                    if missing == True:
                        break
                if not missing:
                    versions.remove(version)            
            elif self.type == 'season':
                for episode in self.Episodes:
                    if not episode.query() + ' [' + version.name + ']' in media.downloaded_versions:
                        missing = True
                        break
                if not missing:
                    versions.remove(version)   
        if self in media.ignore_queue:
            match = next((x for x in media.ignore_queue if self == x), None)
            self.ignored_count = match.ignored_count
        for version in versions[:]:
            if not version.applies(self):
                versions.remove(version)
        return versions

    def version_missing(self):
        all_versions = []
        if self in media.ignore_queue:
            match = next((x for x in media.ignore_queue if self == x), None)
            self.ignored_count = match.ignored_count
        for version in releases.sort.versions:
            all_versions += [releases.sort.version(version[0], version[1], version[2], version[3])]
        for version in all_versions[:]:
            if not version.applies(self):
                all_versions.remove(version)
        return (len(self.versions()) > 0) and not (len(self.versions()) == len(all_versions))

    def watch(self):
        names = []
        retries = 0
        for version in self.versions():
            names += [version.name]
            for trigger in version.triggers:
                if trigger[0] == "retries" and trigger[1] == "<=":
                    if int(float(trigger[2])) > retries:
                        retries = int(float(trigger[2]))
        if retries == 0:
            return
        if not self in media.ignore_queue:
            self.ignored_count = 1
            media.ignore_queue += [self]
            ui_print('retrying download in 30min for item: ' + self.query() + ' - version/s [' + '],['.join(names) + '] - attempt ' + str(self.ignored_count) + '/' + str(retries))
        else:
            match = next((x for x in media.ignore_queue if self == x), None)
            if match.ignored_count < retries:
                match.ignored_count += 1
                ui_print('retrying download in 30min for item: ' + self.query() + ' - version/s [' + '],['.join(names) + '] - attempt ' + str(match.ignored_count) + '/' + str(retries))
            else:
                media.ignore_queue.remove(match)
                ignore.add(self)

    def unwatch(self):
        ignore.remove(self)

    def watched(self):
        return ignore.check(self)

    def released(self):
        try:
            released = datetime.datetime.today() - datetime.datetime.strptime(self.originallyAvailableAt,'%Y-%m-%d')
            if self.type == 'movie':
                if released.days >= -30 and released.days <= 60:
                    if self.available():
                        return True
                    else:
                        return False
                return released.days > 0
            else:
                if released.days >= -1 and released.days <= 1:
                    if self.available():
                        return True
                    else:
                        return False
                return released.days >= 0
        except Exception as e:
            ui_print("media error: (attr exception): " + str(e), debug=ui_settings.debug)
            return False

    def available(self):
        import content.services.plex as plex
        import content.services.trakt as trakt
        import content.services.overseerr as overseerr
        if (self.watchlist == plex.watchlist and len(trakt.users) > 0) or self.watchlist == trakt.watchlist:
            if self.watchlist == plex.watchlist:
                self.match('content.services.trakt')
            trakt_match = self
            if not trakt_match == None:
                trakt.current_user = trakt.users[0]
                try:
                    if trakt_match.type == 'show':
                        return datetime.datetime.utcnow() > datetime.datetime.strptime(trakt_match.first_aired,'%Y-%m-%dT%H:%M:%S.000Z')
                    elif trakt_match.type == 'movie':
                        release_date = None
                        releases, header = trakt.get(
                            'https://api.trakt.tv/movies/' + str(trakt_match.ids.trakt) + '/releases/')
                        for release in releases:
                            if release.release_type == 'digital' or release.release_type == 'physical' or release.release_type == 'tv':
                                if release_date == None:
                                    release_date = release.release_date
                                elif datetime.datetime.strptime(release_date,'%Y-%m-%d') > datetime.datetime.strptime(release.release_date, '%Y-%m-%d'):
                                    release_date = release.release_date
                        # If no release date was found, select the theatrical release date + 2 Month delay
                        if release_date == None:
                            for release in releases:
                                if release_date == None:
                                    release_date = release.release_date
                                elif datetime.datetime.strptime(release_date,'%Y-%m-%d') > datetime.datetime.strptime(release.release_date, '%Y-%m-%d'):
                                    release_date = release.release_date
                            release_date = datetime.datetime.strptime(release_date,'%Y-%m-%d') + datetime.timedelta(days=60)
                            release_date = release_date.strftime("%Y-%m-%d")
                        # Get trakt 'Latest HD/4k Releases' Lists to accept early releases
                        match = False
                        if trakt.early_releases == "true":
                            trakt_lists, header = trakt.get(
                                'https://api.trakt.tv/movies/' + str(trakt_match.ids.trakt) + '/lists/personal/popular')
                            for trakt_list in trakt_lists:
                                if regex.search(r'(latest|new).*?(releases)', trakt_list.name, regex.I):
                                    match = True
                        # if release_date and delay have passed or the movie was released early
                        return datetime.datetime.utcnow() > datetime.datetime.strptime(release_date,'%Y-%m-%d') or match
                    elif trakt_match.type == 'season':
                        try:
                            return datetime.datetime.utcnow() > datetime.datetime.strptime(trakt_match.first_aired,'%Y-%m-%dT%H:%M:%S.000Z')
                        except:
                            return True
                    elif trakt_match.type == 'episode':
                        return datetime.datetime.utcnow() > datetime.datetime.strptime(trakt_match.first_aired,'%Y-%m-%dT%H:%M:%S.000Z')
                except:
                    return False
        try:
            released = datetime.datetime.today() - datetime.datetime.strptime(self.originallyAvailableAt,'%Y-%m-%d')
            if released.days < 0:
                return False
            return True
        except:
            return False

    def collect(self):
        for refresh_service in refresh():
            if refresh_service.__module__ == self.__module__ or (self.__module__ in ["content.services.trakt","releases","content.services.overseerr","content.services.plex"] and refresh_service.__module__ in ["content.services.plex","content.services.jellyfin"]):
                refresh_service(self)
            elif self.__module__ in ["content.services.plex","content.services.overseerr"] and refresh_service.__module__ == "content.services.trakt":
                try:
                    self.match('content.services.trakt')
                    refresh_service(self)
                except:
                    ui_print("[trakt] error: adding item to trakt collection failed")
            else:
                ui_print("error: library update service could not be determined",ui_settings.debug)

    def collected(self, list):
        import content.services.plex as plex
        import content.services.trakt as trakt
        import content.services.overseerr as overseerr
        if self.type in ["movie","show"]:
            if self in list:
                if self.type == "movie":
                    return True
                match = next((x for x in list if x == self), None)
                if not hasattr(match, 'leafCount'):
                    return False
                if match.leafCount == self.leafCount:
                    return True
            return False
        if self.type == "season":
            for show in list:
                if show.type == "show":
                    for season in show.Seasons:
                        if self == season:
                            if season.leafCount == self.leafCount:
                                return True
                            return False
            return False
        if self.type == "episode":
            for show in list:
                if show.type == "show":
                    for season in show.Seasons:
                        for episode in season.Episodes:
                            if self == episode:
                                return True
            return False
    
    def uncollected(self, list):
        if self.type == 'movie':
            if not self.collected(list):
                return [self]
        elif self.type == 'show':
            if self.collected(list) and not self.version_missing():
                return []
            Seasons = copy.deepcopy(self.Seasons)
            for season in Seasons[:]:
                if (not season.collected(list) or season.version_missing()) and not season.watched() and season.released() and not season.downloading():
                    for episode in season.Episodes[:]:
                        if (episode.collected(list) and not episode.version_missing()) or episode.watched() or not episode.released() or episode.downloading():
                            season.Episodes.remove(episode)
                else:
                    if season in Seasons:
                        Seasons.remove(season)
                if len(season.Episodes) == 0 and season in Seasons:
                    Seasons.remove(season)
            return Seasons
        return []

    def downloading(self):
        if hasattr(self, "version"):
            return [self.query() + ' [' + self.version.name + ']'] in debrid.downloading
        else:
            return False

    def download(self, retries=0, library=[], parentReleases=[]):
        import content.services.plex as plex
        import content.services.trakt as trakt
        import content.services.overseerr as overseerr
        current_module = sys.modules[__name__]
        refresh_ = False
        i = 0
        self.Releases = []
        if self.type == 'movie':
            if (len(self.uncollected(library)) > 0 or self.version_missing()) and len(self.versions()) > 0:
                if self.released() and not self.watched() and not self.downloading():
                    if not hasattr(self,"year") or self.year == None:
                        ui_print("error: media item has no release year.")
                        return
                    tic = time.perf_counter()
                    alternate_years = [self.year, self.year - 1, self.year + 1]
                    langs = []
                    for version in self.versions():
                        if not version.lang in langs and not version.lang == 'en':
                            self.aliases(version.lang)
                            langs += [version.lang]
                    self.aliases('en')
                    for year in alternate_years:
                        i = 0
                        while len(self.Releases) == 0 and i <= retries:
                            for title in self.alternate_titles:
                                self.Releases += scraper.scrape(self.query(title).replace(str(self.year), str(year)),self.deviation())
                                if len(self.Releases) > 0:
                                    break
                            i += 1
                        if not len(self.Releases) == 0:
                            self.year = year
                            break
                    imdb_scraped = False
                    if len(self.Releases) <= 10:
                        imdb_scraped = True
                        if hasattr(self,"EID"):
                            for EID in self.EID:
                                if EID.startswith("imdb"):
                                    service,query = EID.split('://')
                                    self.Releases += scraper.scrape(query,self.deviation())
                    debrid_downloaded, retry = self.debrid_download()
                    if not imdb_scraped and (not debrid_downloaded or retry):
                        if debrid_downloaded:
                            refresh_ = True
                        if hasattr(self,"EID"):
                            for EID in self.EID:
                                if EID.startswith("imdb"):
                                    service,query = EID.split('://')
                                    self.Releases += scraper.scrape(query,self.deviation())
                                    debrid_downloaded, retry = self.debrid_download()
                    if debrid_downloaded:
                        refresh_ = True
                        if not retry and (self.watchlist.autoremove == "both" or self.watchlist.autoremove == "movie"):
                            self.watchlist.remove([], self)
                        toc = time.perf_counter()
                        ui_print('took ' + str(round(toc - tic, 2)) + 's')
                    if retry:
                        self.watch()
        elif self.type == 'show':
            if self.released() and (not self.collected(library) or self.version_missing()) and not self.watched() and len(self.versions()) > 0:
                self.isanime()
                self.Seasons = self.uncollected(library)
                # if there are uncollected episodes
                if len(self.Seasons) > 0:
                    tic = time.perf_counter()
                    langs = []
                    for version in self.versions():
                        if not version.lang in langs and not version.lang == 'en':
                            self.aliases(version.lang)
                            langs += [version.lang]
                    self.aliases('en')
                    imdb_scraped = False
                    # if there is more than one uncollected season
                    if len(self.Seasons) > 1:
                        if self.isanime():
                            for title in self.alternate_titles:
                                self.Releases += scraper.scrape(self.anime_query(title), self.deviation())
                                if len(self.Releases) > 0:
                                    break
                        else:
                            for title in self.alternate_titles:
                                self.Releases += scraper.scrape(self.query(title), self.deviation())
                                if len(self.Releases) > 0:
                                    break
                        if len(self.Releases) <= 10:
                            imdb_scraped = True
                            if hasattr(self,"EID"):
                                for EID in self.EID:
                                    if EID.startswith("imdb"):
                                        service,query = EID.split('://')
                                        self.Releases += scraper.scrape(query,self.deviation())
                        parentReleases = copy.deepcopy(self.Releases)
                        # if there are more than 3 uncollected seasons, look for multi-season releases before downloading single-season releases
                        if len(self.Seasons) > 3:
                            # gather file information on scraped, cached releases
                            debrid.check(self)
                            multi_season_releases = []
                            season_releases = [None] * len(self.Seasons)
                            minimum_episodes = len(self.files()) / 2
                            season_queries = []
                            for season in self.Seasons:
                                season_queries += [season.deviation()]
                            season_queries_str = '(' + ')|('.join(season_queries) + ')'
                            if self.isanime():
                                for release in self.Releases:
                                    if regex.search(self.anime_count,release.title,regex.I):
                                        multi_season_releases += [release]
                            for release in self.Releases:
                                match = regex.match(season_queries_str, release.title, regex.I)
                                for version in release.files:
                                    if isinstance(version.wanted, int):
                                        # if a multi season pack contains more than half of all uncollected episodes, accept it as a multi-season-pack.
                                        if version.wanted > minimum_episodes:
                                            multi_season_releases += [release]
                                            break
                                            # if the release is a single-season pack, find out the quality
                                        if match:
                                            for index, season_query in enumerate(season_queries):
                                                if regex.match(season_query, release.title, regex.I):
                                                    if version.wanted >= len(self.Seasons[index].files()) and \
                                                            season_releases[index] == None:
                                                        quality = regex.search('(2160|1080|720|480)(?=p|i)',release.title, regex.I)
                                                        if quality:
                                                            quality = int(quality.group())
                                                        else:
                                                            quality = 0
                                                        season_releases[index] = quality
                                                        break
                            # if there are eligible multi-season packs
                            if len(multi_season_releases) > 0:
                                download_multi_season_release = False
                                # if one of the shows seasons cant be downloaded as a single-season pack, download the multi-season pack.
                                for season_release in season_releases:
                                    if season_release == None:
                                        download_multi_season_release = True
                                        break
                                # if all seasons of the show could also be downloaded as single-season packs, compare the quality of the best ranking multi season pack with the lowest quality of the single season packs.
                                if not download_multi_season_release:
                                    season_quality = min(season_releases)
                                    quality = regex.search('(2160|1080|720|480)(?=p|i)',multi_season_releases[0].title, regex.I)
                                    if quality:
                                        quality = int(quality.group())
                                    else:
                                        quality = 0
                                    if quality >= season_quality:
                                        download_multi_season_release = True
                                # if either not all seasons can be downloaded as single-season packs or the single season packs are of equal or lower quality compared to the multi-season packs, download the multi season packs.
                                if download_multi_season_release:
                                    self.Releases = multi_season_releases
                                    debrid_downloaded, retry = self.debrid_download()
                                    if not imdb_scraped and (not debrid_downloaded or retry):
                                        if debrid_downloaded:
                                            refresh_ = True
                                        if hasattr(self,"EID"):
                                            for EID in self.EID:
                                                if EID.startswith("imdb"):
                                                    service,query = EID.split('://')
                                                    self.Releases += scraper.scrape(query,self.deviation())
                                                    debrid_downloaded, retry = self.debrid_download()
                                    if debrid_downloaded:
                                        refresh_ = True
                                        if not retry:
                                            if self.isanime():
                                                self.Seasons = []
                                            else:
                                                for season in self.Seasons[:]:
                                                    for episode in season.Episodes[:]:
                                                        for file in self.Releases[0].files:
                                                            if hasattr(file, 'match'):
                                                                if file.match == episode.files()[0]:
                                                                    season.Episodes.remove(episode)
                                                                    break
                                                    if len(season.Episodes) == 0:
                                                        self.Seasons.remove(season)
                    # Download all remaining seasons by starting a thread for each season.
                    results = [None] * len(self.Seasons)
                    threads = []
                    # start thread for each season
                    for index, Season in enumerate(self.Seasons):
                        t = Thread(target=download, args=(Season, library, parentReleases, results, index))
                        threads.append(t)
                        t.start()
                    # wait for the threads to complete
                    for t in threads:
                        t.join()
                    retry = False
                    for index, result in enumerate(results):
                        if result == None:
                            continue
                        if result[0]:
                            refresh_ = True
                        if result[1]:
                            retry = True
                    if not retry and (self.watchlist.autoremove == "both" or self.watchlist.autoremove == "show"):
                        self.watchlist.remove([], self)
                    toc = time.perf_counter()
                    ui_print('took ' + str(round(toc - tic, 2)) + 's')
        elif self.type == 'season':
            imdb_scraped = False
            altquery = self.deviation()
            for release in parentReleases:
                if regex.match(r'(' + altquery + ')', release.title, regex.I):
                    self.Releases += [release]
            if not len(self.Episodes) <= self.leafCount / 2:
                debrid_downloaded, retry = self.debrid_download()
                if debrid_downloaded:
                    return True, retry
                else:
                    self.Releases = []
                if self.isanime():
                    for title in self.alternate_titles:
                        self.Releases += scraper.scrape(self.anime_query(title), self.deviation())
                        if len(self.Releases) > 0:
                            break
                while len(self.Releases) == 0 and i <= retries:
                    for title in self.alternate_titles:
                        self.Releases += scraper.scrape(self.query(title), self.deviation())
                        if len(self.Releases) > 0:
                            break
                    i += 1
                if len(self.Releases) <= 5:
                    imdb_scraped = True
                    if hasattr(self,"parentEID"):
                        for EID in self.parentEID:
                            if EID.startswith("imdb"):
                                service,query = EID.split('://')
                                self.Releases += scraper.scrape(query,self.deviation())
            debrid_downloaded, retry = self.debrid_download()
            if not imdb_scraped and (not debrid_downloaded or retry):
                if debrid_downloaded:
                    refresh_ = True
                if hasattr(self,"parentEID"):
                    for EID in self.parentEID:
                        if EID.startswith("imdb"):
                            service,query = EID.split('://')
                            self.Releases += scraper.scrape(query,self.deviation())
                            debrid_downloaded, retry = self.debrid_download()
            if not debrid_downloaded or retry:
                if debrid_downloaded:
                    refresh_ = True
                for title in self.alternate_titles:
                    self.Releases += scraper.scrape(self.query()[:-1])
                    if len(self.Releases) > 0:
                        break
                if len(self.Releases) <= 5 and not imdb_scraped:
                    if hasattr(self,"parentEID"):
                        for EID in self.parentEID:
                            if EID.startswith("imdb"):
                                service,query = EID.split('://')
                                self.Releases += scraper.scrape(query)
                for episode in self.Episodes:
                    downloaded, retry = episode.download(library=library, parentReleases=self.Releases)
                    if downloaded:
                        refresh_ = True
                    if retry:
                        episode.watch()
                return refresh_, retry
            else:
                return True, retry
        elif self.type == 'episode':
            altquery = self.deviation()
            for release in parentReleases:
                if regex.match(r'(' + altquery + ')', release.title, regex.I):
                    self.Releases += [release]
            debrid_downloaded, retry = self.debrid_download()
            if not debrid_downloaded or retry:
                if debrid_downloaded:
                    refresh_ = True
                if self.isanime():
                    for title in self.alternate_titles:
                        self.Releases += scraper.scrape(self.anime_query(title), self.deviation())
                        if len(self.Releases) > 0:
                            break
                for title in self.alternate_titles:
                    self.Releases = scraper.scrape(self.query(title), self.deviation())
                    if len(self.Releases) > 0:
                        break
                debrid_downloaded, retry = self.debrid_download()
                if debrid_downloaded:
                    refresh_ = True
                return refresh_, retry
            return True, retry
        if refresh_:
            self.collect()

    def downloaded(self):
        if self.type == "movie" or self.type == "episode":
            media.downloaded_versions += [self.query() + ' [' + self.version.name + ']']
        elif self.type == 'show':
            filemode = False
            for season in self.Seasons:
                for episode in season.Episodes:
                    for file in self.Releases[0].files:
                        if hasattr(file, 'match'):
                            if file.match == episode.files()[0]:
                                episode.version = self.version
                                episode.downloaded()
                                filemode = True
                                break
            if not filemode:
                for season in self.Seasons:
                    season.version = self.version
                    season.downloaded()
        elif self.type == 'season':
            for episode in self.Episodes:
                episode.version = self.version
                episode.downloaded()

    def debrid_download(self):
        if len(self.Releases) > 0:
            ui_print("checking cache status for scraped releases on: [" + "],[".join(debrid.services.active) + "] ...")
        debrid.check(self)
        if len(self.Releases) > 0:
            ui_print("done")
        scraped_releases = copy.deepcopy(self.Releases)
        downloaded = []
        if len(scraped_releases) > 0:
            for version in self.versions():
                debrid_uncached = True
                for rule in version.rules:
                    if rule[0] == "cache status" and rule[1] == 'requirement' and rule[2] == "cached":
                        debrid_uncached = False
                self.version = version
                self.Releases = copy.deepcopy(scraped_releases)
                releases.sort(self.Releases, self.version)
                if debrid.download(self, stream=True):
                    self.downloaded()
                    downloaded += [True]
                elif not self.type == 'show' and debrid_uncached:  # change to version definition of cache status
                    if debrid.download(self, stream=False):
                        self.downloaded()
                        debrid.downloading += [self.query() + ' [' + self.version.name + ']']
                        downloaded += [True]
                    else:
                        downloaded += [False]
                else:
                    downloaded += [False]
        return True in downloaded, (False in downloaded or len(downloaded) == 0)

    def files(self):
        files = []
        if self.type == 'movie':
            files = ['(mkv|mp4)']
        elif self.type == 'show':
            for season in self.Seasons:
                for episode in season.Episodes:
                    files += episode.files()
        elif self.type == 'season':
            for episode in self.Episodes:
                files += episode.files()
        elif self.type == 'episode':
            files += ['S' + str("{:02d}".format(self.parentIndex)) + 'E' + str("{:02d}".format(self.index)) + '']
        return files

def download(cls, library, parentReleases, result, index):
    result[index] = cls.download(library=library, parentReleases=parentReleases)
