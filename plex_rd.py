#Import Modules
try:
    import os
    import requests
    import json
    import time
    import datetime
    from types import SimpleNamespace
    import regex
    regex.DEFAULT_VERSION = regex.VERSION1
    from bs4 import BeautifulSoup
    import sys
    import copy
    import random
    from threading import Thread
    from collections.abc import Sequence
    import six
    import hashlib
    import base64
    import itertools
except Exception as e:
    print("python error: (module import exception): ")
    print(e)
    print("Make sure you have installed this python module.")
    print("You need to install 'pip' (https://pip.pypa.io/en/stable/installation/) and run the command 'pip install "+e.name+"'.")
    input("Press any key to exit")
    exit()
#Provider Class
class content:
    #Servies Class
    class services:
        active = ['Plex','Trakt','Overseerr']
        def setup(cls,new=False):
            settings = []
            for category, allsettings in ui.settings_list:
                for setting in allsettings:
                    if setting.cls == cls or setting.name == cls.name + ' auto remove':
                        settings += [setting]
            back = False
            if not new:
                while not back:
                    print("0) Back")
                    indices = []
                    for index, setting in enumerate(settings):
                        print(str(index+1) + ') ' + setting.name)
                        indices += [str(index+1)]
                    print()
                    choice = input("Choose an action: ")
                    if choice in indices:
                        settings[int(choice)-1].input()
                        if not cls.name in content.services.active:
                            content.services.active += [cls.name]
                        back = True
                    elif choice == '0':
                        back = True
            else:
                print()
                indices = []
                for setting in settings:
                    if not setting.name == cls.name + ' auto remove':
                        setting.setup()
                        if not cls.name in content.services.active:
                            content.services.active += [cls.name]      
        def __new__(cls):
            activeservices = []
            for servicename in content.services.active:
                for service in cls.__subclasses__():
                    if service.name == servicename:
                        activeservices += [service]
            return activeservices
    #Libraries Class
    class libraries:
        active = []
        def setup(cls,new=False):
            settings = []
            for category, allsettings in ui.settings_list:
                for setting in allsettings:
                    if setting.cls == cls or setting.name.startswith(cls.name):
                        settings += [setting]
            back = False
            if not new:
                while not back:
                    print("0) Back")
                    indices = []
                    for index, setting in enumerate(settings):
                        print(str(index+1) + ') ' + setting.name)
                        indices += [str(index+1)]
                    print()
                    choice = input("Choose an action: ")
                    if choice in indices:
                        settings[int(choice)-1].input()
                        if not cls.name in content.libraries.active:
                            content.libraries.active = [cls.name]
                        back = True
                    elif choice == '0':
                        back = True
            else:
                print()
                indices = []
                for setting in settings:
                    setting.setup()
                    if not cls.name in content.libraries.active:
                        content.libraries.active = [cls.name]      
        def __new__(cls):
            activeservices = []
            for servicename in content.libraries.active:
                for service in cls.__subclasses__():
                    if service.name == servicename:
                        activeservices += [service]
            return activeservices
    #Watchlist Class
    class watchlist(Sequence):
        def __init__(self,other):
            self.data = other
        def __getitem__(self, index):
            return self.data[index]
        def __len__(self):
            return len(self.data)
        def __eq__(self, other):
            return len(self) == len(other)
        def remove(self,item):
            self.data.remove(item)
        def add(self,item,user):
            self.data.append(item)
    #Media Class
    class media:
        ignore_queue = []
        downloaded_versions = []
        def __init__(self,other):
            self.__dict__.update(other.__dict__)
        def __eq__(self, other) -> bool:
            try:
                if not self.type == other.type:
                    return False
                if self.type == 'movie' or self.type == 'show':
                    return self.guid == other.guid
                elif self.type == 'season':
                    return self.parentGuid == other.parentGuid and self.index == other.index
                elif self.type == 'episode':
                    return self.grandparentGuid == other.grandparentGuid and self.parentIndex == other.parentIndex and self.index == other.index
            except:
                return False
        def __repr__(self):
            return str(self.__dict__)
        def query(self):
            if self.type == 'movie':
                title = releases.rename(self.title)
                title = title.replace('.'+str(self.year),'')
                return title + '.' + str(self.year)
            elif self.type == 'show':
                title = releases.rename(self.title)
                title = title.replace('.'+str(self.year),'')
                return title
            elif self.type == 'season':
                title = releases.rename(self.parentTitle) 
                title = title.replace('.'+str(self.parentYear),'')
                return title + '.S' + str("{:02d}".format(self.index)) + '.'
            elif self.type == 'episode': 
                title = releases.rename(self.grandparentTitle) 
                title = title.replace('.'+str(self.grandparentYear),'')
                return title + '.S' + str("{:02d}".format(self.parentIndex)) + 'E' + str("{:02d}".format(self.index))+ '.'
        def deviation(self):
            if self.type == 'movie':
                title = releases.rename(self.title)
                title = title.replace('.'+str(self.year),'')
                return '(' + title + '.)(' + str(self.year) + '|' + str(self.year - 1) + '|' + str(self.year + 1) + ')'
            elif self.type == 'show':
                title = releases.rename(self.title)
                title = title.replace('.'+str(self.year),'')
                return '(' + title + '.)((' + str(self.year) + '.)|(complete.)|(seasons?.[0-9]+.[0-9]?[0-9]?.?)|(S[0-9]+.[0-9]?[0-9]?.?)|(S[0-9]+E[0-9]+))'
            elif self.type == 'season':
                title = releases.rename(self.parentTitle) 
                title = title.replace('.'+str(self.parentYear),'')
                return '(' + title + '.)(' + str(self.parentYear) + '.)?(season.[0-9]+.)?' + '(S' + str("{:02d}".format(self.index)) + '.)'
            elif self.type == 'episode': 
                title = releases.rename(self.grandparentTitle) 
                title = title.replace('.'+str(self.grandparentYear),'')
                return '(' + title + '.)(' + str(self.grandparentYear) + '.)?(S' + str("{:02d}".format(self.parentIndex)) + 'E' + str("{:02d}".format(self.index))+ '.)'
        def versions(self):
            versions = []
            for version in releases.sort.versions:
                versions += [releases.sort.version(version[0],version[1],version[2],version[3])]
            for version in versions[:]:
                if self.query() + ' [' + version.name + ']' in content.media.downloaded_versions:
                    versions.remove(version)
            return versions
        def watch(self):
            if not self in content.media.ignore_queue:
                self.ignored_count = 1
                content.media.ignore_queue += [self]
                ui.print('retrying download in 30min for item: ' + self.query() + ' - attempt '+str(self.ignored_count)+'/48')
            else:
                match = next((x for x in content.media.ignore_queue if self == x),None)
                if match.ignored_count < 48:
                    match.ignored_count += 1
                    ui.print('retrying download in 30min for item: ' + self.query() + ' - attempt '+str(match.ignored_count)+'/48')
                else:
                    content.media.ignore_queue.remove(match)
                    if content.libraries.active == ['Plex Library']:
                        try:
                            ui.print('[plex] ignoring item: ' + self.query())
                            url = 'https://metadata.provider.plex.tv/actions/scrobble?identifier=tv.plex.provider.metadata&key='+self.ratingKey+'&X-Plex-Token='+ plex.users[0][1]
                            plex.get(url)
                            if not self in plex.ignored:
                                plex.ignored += [self]
                        except Exception as e:
                            ui.print("plex error: couldnt ignore item: " + str(e),debug=ui_settings.debug)
                    elif content.libraries.active == ['Trakt Collection']:
                        pass
        def unwatch(self):
            if content.libraries.active == ['Plex Library']:
                try:
                    url = 'https://metadata.provider.plex.tv/actions/unscrobble?identifier=tv.plex.provider.metadata&key='+self.ratingKey+'&X-Plex-Token='+ plex.users[0][1]
                    plex.get(url)
                    plex.ignored.remove(self)
                except Exception as e:
                    ui.print("plex error: couldnt un-ignore item: " + str(e),debug=ui_settings.debug)
            elif content.libraries.active == ['Trakt Collection']:
                pass
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
                    if released.days >= 0 and released.days <= 1:
                        if self.available():
                            return True
                        else:
                            return False
                    return released.days >= 0
            except Exception as e:
                ui.print("media error: (attr exception): " + str(e),debug=ui_settings.debug)
                return False
        def available(self):
            if (self.watchlist == plex.watchlist and len(trakt.users) > 0) or self.watchlist == trakt.watchlist :
                if self.watchlist == plex.watchlist:
                    try:
                        for guid in self.Guid:
                            service,guid = guid.id.split('://')
                            trakt_match = trakt.match(guid,service,self.type)
                            if not trakt_match == None:
                                break
                    except Exception as e:
                        ui.print("plex error: (attr exception): " + str(e),debug=ui_settings.debug)
                        return True
                else:
                    trakt_match = self
                if not trakt_match == None:
                    trakt.current_user = trakt.users[0]
                    try:
                        if trakt_match.type == 'show':
                            return datetime.datetime.utcnow() > datetime.datetime.strptime(trakt_match.first_aired,'%Y-%m-%dT%H:%M:%S.000Z')
                        elif trakt_match.type == 'movie':
                            release_date = None
                            releases, header = trakt.get('https://api.trakt.tv/movies/'+ str(trakt_match.ids.trakt) +'/releases/')
                            for release in releases:
                                if release.release_type == 'digital' or release.release_type == 'physical' or release.release_type == 'tv':
                                    if release_date == None:
                                        release_date = release.release_date
                                    elif datetime.datetime.strptime(release_date,'%Y-%m-%d') > datetime.datetime.strptime(release.release_date,'%Y-%m-%d'):
                                        release_date = release.release_date
                            #If no release date was found, select the theatrical release date + 2 Month delay
                            if release_date == None:
                                for release in releases:
                                    if release_date == None:
                                        release_date = release.release_date
                                    elif datetime.datetime.strptime(release_date,'%Y-%m-%d') > datetime.datetime.strptime(release.release_date,'%Y-%m-%d'):
                                        release_date = release.release_date
                                release_date = datetime.datetime.strptime(release_date,'%Y-%m-%d') + datetime.timedelta(days=60)
                                release_date = release_date.strftime("%Y-%m-%d")
                            #Get trakt 'Latest HD/4k Releases' Lists to accept early releases
                            trakt_lists, header = trakt.get('https://api.trakt.tv/movies/'+ str(trakt_match.ids.trakt) +'/lists/personal/popular')
                            match = False
                            for trakt_list in trakt_lists:
                                if regex.search(r'(latest|new).*?(releases)',trakt_list.name,regex.I):
                                    match = True
                            #if release_date and delay have passed or the movie was released early
                            return datetime.datetime.utcnow() > datetime.datetime.strptime(release_date,'%Y-%m-%d') or match
                        elif trakt_match.type == 'season':
                            return datetime.datetime.utcnow() > datetime.datetime.strptime(trakt_match.first_aired,'%Y-%m-%dT%H:%M:%S.000Z')
                        elif trakt_match.type == 'episode':
                            return datetime.datetime.utcnow() > datetime.datetime.strptime(trakt_match.first_aired,'%Y-%m-%dT%H:%M:%S.000Z')
                    except:
                        return False
            elif self.type == 'movie':
                released = datetime.datetime.today() - datetime.datetime.strptime(self.originallyAvailableAt,'%Y-%m-%d')
                if released.days < 0:
                    return False
            return True  
        def watched(self):
            if content.libraries.active == ['Plex Library']:
                try:
                    if self.type == 'movie' or self.type == 'episode':
                        if hasattr(self,'viewCount'):
                            if self.viewCount > 0:
                                if not self in plex.ignored:
                                    plex.ignored += [self]
                                return True
                    else:
                        if hasattr(self, 'viewedLeafCount'):
                            if self.viewedLeafCount >= self.leafCount:
                                if not self in plex.ignored:
                                    plex.ignored += [self]
                                return True
                    return False
                except Exception as e:
                    ui.print("plex error: (attr exception): " + str(e),debug=ui_settings.debug)
                    return False
            elif content.libraries.active == ['Trakt Collection']:
                return False
        def collected(self,list):
            if self.watchlist == plex.watchlist and content.libraries.active == ['Plex Library']:
                try:
                    if self.type == 'show' or self.type == 'season':
                        match = next((x for x in list if x == self),None)
                        if not hasattr(match,'leafCount'):
                            return False
                        if match.leafCount == self.leafCount:
                            return True
                        return False
                    else:
                        return self in list
                except Exception as e:
                    ui.print("plex error: (plex to plex library check exception): " + str(e),debug=ui_settings.debug)
                    return False
            elif self.watchlist == trakt.watchlist and content.libraries.active == ['Plex Library']:
                try:
                    if self.type in ['movie','show']:
                        if hasattr(self.ids,'imdb'):
                            result = plex.match("imdb-"+self.ids.imdb,self.type,library=list)
                        elif hasattr(self.ids,'tmdb'):
                            result = plex.match("tmdb-"+str(self.ids.tmdb),self.type,library=list)
                        elif hasattr(self.ids,'tvdb'):
                            result = plex.match("tvdb-"+str(self.ids.tvdb),self.type,library=list)
                        if hasattr(self,'Seasons'):
                            for season in self.Seasons:
                                matching_season = next((x for x in result[0].Seasons if x.index == season.index),None)
                                if hasattr(matching_season,'viewedLeafCount'):
                                    season.viewedLeafCount = matching_season.viewedLeafCount
                                if hasattr(matching_season,'ratingKey'):
                                    season.ratingKey = matching_season.ratingKey
                                season.parentGuid = result[0].guid
                                for episode in season.Episodes:
                                    if hasattr(matching_season,'Episodes'):
                                        matching_episode = next((x for x in matching_season.Episodes if x.index == episode.index),None)
                                        if hasattr(matching_episode,'viewCount'):
                                            episode.viewCount = matching_episode.viewCount
                                        if hasattr(matching_episode,'ratingKey'):
                                            episode.ratingKey = matching_episode.ratingKey
                                    episode.grandparentGuid = result[0].guid
                        if hasattr(result[0],'viewCount'):
                            self.viewCount = result[0].viewCount
                        if hasattr(result[0],'viewedLeafCount'):
                            self.viewedLeafCount = result[0].viewedLeafCount
                        if hasattr(result[0],'ratingKey'):
                            self.ratingKey = result[0].ratingKey
                        return content.media.collected(result[0],list)
                    elif self.type == 'season':
                        match = next((x for x in list if x == self),None)
                        if not hasattr(match,'leafCount'):
                            return False
                        if match.leafCount == self.leafCount:
                            return True
                        return False
                    elif self.type == 'episode':
                        return self in list
                except Exception as e:
                    ui.print("trakt error: (trakt to plex library check exception): " + str(e),debug=ui_settings.debug)
                    return False
            elif self.watchlist == trakt.watchlist and content.libraries.active == ['Trakt Collection']:
                try:
                    if self.type == 'show' or self.type == 'season':
                        match = next((x for x in list if x == self),None)
                        if not hasattr(match,'leafCount'):
                            return False
                        if match.leafCount == self.leafCount:
                            return True
                        return False
                    else:
                        return self in list
                except Exception as e:
                    ui.print("trakt error: (trakt to trakt library check exception): " + str(e),debug=ui_settings.debug)
                    return False
            elif self.watchlist == plex.watchlist and content.libraries.active == ['Trakt Collection']:
                try:
                    if self.type in ['movie','show']:
                        for guid in self.Guid:
                            service,guid = guid.id.split('://')
                            trakt_match = trakt.match(guid,service,self.type)
                            if trakt_match:
                                break
                        if hasattr(self,'Seasons'):
                            for season in self.Seasons:
                                season.parentGuid = trakt_match.guid
                                for episode in season.Episodes:
                                    episode.grandparentGuid = trakt_match.guid
                            self.seasons = trakt_match.Seasons
                        self.ids = trakt_match.ids
                        return content.media.collected(trakt_match,list)        
                    elif self.type == 'season':
                        match = next((x for x in list if x == self),None)
                        if not hasattr(match,'leafCount'):
                            return False
                        if match.leafCount == self.leafCount:
                            return True
                        return False
                    else:
                        return self in list
                except Exception as e:
                    ui.print("trakt error: (plex to trakt library check exception): " + str(e),debug=ui_settings.debug)
                    return False
            else:
                ui.print("library check error: (no library check performed): " + str(e),debug=ui_settings.debug)
                return False
        def uncollected(self,list):
            if self.type == 'movie':
                if not self.collected(list):
                    return [self]
            elif self.type == 'show':
                if self.collected(list) and not (len(self.versions()) > 0 and not len(self.versions()) == len(releases.sort.versions)):
                    return []
                Seasons = copy.deepcopy(self.Seasons)
                for season in Seasons[:]:
                    if (not season.collected(list) or (len(season.versions()) > 0 and not len(season.versions()) == len(releases.sort.versions))) and not season.watched() and season.released() and not season.downloading():
                        for episode in season.Episodes[:]:
                            if (episode.collected(list) and not (len(episode.versions()) > 0 and not len(episode.versions()) == len(releases.sort.versions))) or episode.watched() or not episode.released() or episode.downloading():
                                season.Episodes.remove(episode)
                    else:
                        Seasons.remove(season)
                    if len(season.Episodes) == 0 and season in Seasons:
                        Seasons.remove(season)
                return Seasons
            return []
        def downloading(self):
            if hasattr(self,"version"):
                return [self.query() + ' [' + self.version.name + ']'] in debrid.downloading
            else:
                return False
        def download(self,retries=0,library=[],parentReleases=[]):
            refresh = False
            i=0
            self.Releases = []
            if self.type == 'movie':
                if len(self.uncollected(library)) > 0 or (len(self.versions()) > 0 and not len(self.versions()) == len(releases.sort.versions)):
                    if self.released() and not self.watched() and not self.downloading():
                        tic = time.perf_counter()
                        alternate_years = [self.year, self.year - 1, self.year + 1]
                        for year in alternate_years:
                            i = 0
                            while len(self.Releases) == 0 and i <= retries:
                                self.Releases += scraper(self.query().replace(str(self.year),str(year)),self.deviation())
                                i += 1
                            if not len(self.Releases) == 0:
                                self.year = year
                                break
                        debrid_downloaded, retry = self.debrid_download()
                        if debrid_downloaded:
                            refresh = True
                            if not retry and (self.watchlist.autoremove == "both" or self.watchlist.autoremove == "movie"):
                                self.watchlist.remove([],self)
                            toc = time.perf_counter()
                            ui.print('took ' + str(round(toc-tic,2)) + 's')
                        if retry:
                            self.watch()
            elif self.type == 'show':
                if self.released() and (not self.collected(library) or (len(self.versions()) > 0 and not len(self.versions()) == len(releases.sort.versions))) and not self.watched():
                    self.Seasons = self.uncollected(library)
                    #if there are uncollected episodes
                    if len(self.Seasons) > 0:
                        tic = time.perf_counter()
                        #if there is more than one uncollected season
                        if len(self.Seasons) > 1:
                            self.Releases += scraper(self.query(),self.deviation())
                            parentReleases = copy.deepcopy(self.Releases)
                            #if there are more than 3 uncollected seasons, look for multi-season releases before downloading single-season releases
                            if len(self.Seasons) > 3:
                                #gather file information on scraped, cached releases
                                debrid.check(self)
                                multi_season_releases = []
                                season_releases = [None] * len(self.Seasons)
                                minimum_episodes = len(self.files())/2
                                season_queries = []
                                for season in self.Seasons:
                                    season_queries += [season.deviation()]
                                season_queries_str = '(' + ')|('.join(season_queries) + ')'
                                for release in self.Releases:
                                    match = regex.match(season_queries_str,release.title,regex.I)
                                    for version in release.files:
                                        if isinstance(version.wanted,int):
                                            #if a multi season pack contains more than half of all uncollected episodes, accept it as a multi-season-pack.
                                            if version.wanted > minimum_episodes:
                                                multi_season_releases += [release]
                                                break   
                                            #if the release is a single-season pack, find out the quality
                                            if match:
                                                for index,season_query in enumerate(season_queries):
                                                    if regex.match(season_query,release.title,regex.I):
                                                        if version.wanted >= len(self.Seasons[index].files()) and season_releases[index] == None:
                                                            quality = regex.search('(2160|1080|720|480)(?=p|i)',release.title,regex.I)
                                                            if quality:
                                                                quality = int(quality.group())
                                                            else:
                                                                quality = 0
                                                            season_releases[index] = quality
                                                            break
                                #if there are eligible multi-season packs
                                if len(multi_season_releases) > 0:
                                    download_multi_season_release = False
                                    #if one of the shows seasons cant be downloaded as a single-season pack, download the multi-season pack.
                                    for season_release in season_releases:
                                        if season_release == None:
                                            download_multi_season_release = True
                                            break
                                    #if all seasons of the show could also be downloaded as single-season packs, compare the quality of the best ranking multi season pack with the lowest quality of the single season packs.
                                    if not download_multi_season_release:
                                        season_quality = min(season_releases)
                                        quality = regex.search('(2160|1080|720|480)(?=p|i)',multi_season_releases[0].title,regex.I)
                                        if quality:
                                            quality = int(quality.group())
                                        else:
                                            quality = 0
                                        if quality >= season_quality:
                                            download_multi_season_release = True
                                    #if either not all seasons can be downloaded as single-season packs or the single season packs are of equal or lower quality compared to the multi-season packs, download the multi season packs.
                                    if download_multi_season_release:
                                        self.Releases = multi_season_releases
                                        debrid_downloaded, retry = self.debrid_download()
                                        if debrid_downloaded:
                                            refresh = True
                                            if not retry:
                                                for season in self.Seasons[:]:
                                                    for episode in season.Episodes[:]:
                                                        for file in self.Releases[0].files:
                                                            if hasattr(file,'match'):
                                                                if file.match == episode.files()[0]:
                                                                    season.Episodes.remove(episode)
                                                                    break
                                                    if len(season.Episodes) == 0:
                                                        self.Seasons.remove(season)
                        #Download all remaining seasons by starting a thread for each season.
                        results = [None] * len(self.Seasons)
                        threads = []
                        #start thread for each season
                        for index,Season in enumerate(self.Seasons):
                            t = Thread(target=download, args=(Season,library,parentReleases,results,index))
                            threads.append(t)
                            t.start()
                        # wait for the threads to complete
                        for t in threads:
                            t.join()
                        retry = False
                        for index,result in enumerate(results):
                            if result[0]:
                                refresh = True
                            if result[1]:
                                retry = True
                        if not retry and (self.watchlist.autoremove == "both" or self.watchlist.autoremove == "show"):
                            self.watchlist.remove([],self)
                        toc = time.perf_counter()
                        ui.print('took ' + str(round(toc-tic,2)) + 's')
            elif self.type == 'season':
                altquery = self.deviation()
                for release in parentReleases:
                    if regex.match(r'('+altquery+')',release.title,regex.I):
                        self.Releases += [release]
                if not len(self.Episodes) <= self.leafCount/2:
                    debrid_downloaded, retry = self.debrid_download()
                    if debrid_downloaded:
                        return True, retry
                    else:
                        self.Releases = []
                    while len(self.Releases) == 0 and i <= retries:
                        self.Releases += scraper(self.query(),self.deviation())
                        i += 1
                debrid_downloaded, retry = self.debrid_download()
                if not debrid_downloaded or retry:
                    self.Releases += scraper(self.query()[:-1])
                    for episode in self.Episodes:
                        downloaded, retry = episode.download(library=library,parentReleases=self.Releases)
                        if downloaded:
                            refresh = True
                        if retry:
                            episode.watch()
                    if refresh:
                        return True, retry
                    return False, retry
                else:
                    return True, retry
            elif self.type == 'episode':
                while len(self.Releases) == 0 and i <= retries:
                    altquery = self.deviation()
                    for release in parentReleases:
                        if regex.match(r'('+altquery+')',release.title,regex.I):
                            self.Releases += [release]
                    debrid_downloaded, retry = self.debrid_download()
                    if debrid_downloaded:
                        return True, retry
                    else:
                        self.Releases = scraper(self.query(),self.deviation())
                    i += 1
                return self.debrid_download()
            if refresh and content.libraries.active == [plex.library.name]:
                if self.type == 'movie':
                    plex.library.refresh(plex.library.movies)
                elif self.type == 'show':
                    plex.library.refresh(plex.library.shows)
                return True
            elif refresh and content.libraries.active == [trakt.library.name]:
                trakt.library.add(self)
        def downloaded(self):
            content.media.downloaded_versions += [self.query() + ' [' + self.version.name + ']']
            if self.type == 'show':
                for season in self.Seasons:
                    season.version = self.version
                    season.downloaded()
            if self.type == 'season':
                for episode in self.Episodes:
                    episode.version = self.version
                    episode.downloaded()
        def debrid_download(self):
            debrid.check(self)
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
                    releases.sort(self.Releases,self.version)
                    if debrid.download(self,stream=True):
                        self.downloaded()
                        downloaded += [True]
                    elif not self.type == 'show' and debrid_uncached: #change to version definition of cache status
                        if debrid.download(self,stream=False):
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
                files = [self.query()]
            elif self.type == 'show':
                for season in self.Seasons:
                    for episode in season.Episodes:
                        files += episode.files()
            elif self.type == 'season':
                for episode in self.Episodes:
                    files += episode.files()
            elif self.type == 'episode':
                files += ['S' + str("{:02d}".format(self.parentIndex)) + 'E' + str("{:02d}".format(self.index))+ '']
            return files
#Plex Class
class plex(content.services):
    name = 'Plex'
    session = requests.Session()  
    users = []
    headers = {'Content-Type':'application/json','Accept':'application/json'}
    ignored = []
    def logerror(response):
        if not response.status_code == 200:
            ui.print("Plex error: " + str(response.content),debug=ui_settings.debug)
        if response.status_code == 401:
            ui.print("plex error: (401 unauthorized): user token does not seem to work. check your plex user settings.")
    def get(url,timeout=30):
        try:
            response = plex.session.get(url,headers=plex.headers,timeout=timeout)
            plex.logerror(response)
            response = json.loads(response.content, object_hook=lambda d: SimpleNamespace(**d))
            return response
        except Exception as e:
            ui.print("plex error: (json exception): " + str(e),debug=ui_settings.debug)
            return None
    def post(url,data):
        try:
            response = plex.session.post(url,data=data,headers=plex.headers)
            plex.logerror(response)
            response = json.loads(response.content, object_hook=lambda d: SimpleNamespace(**d))
            return response
        except Exception as e:
            ui.print("plex error: (json exception): " + str(e),debug=ui_settings.debug)
            return None
    class watchlist(content.watchlist):
        autoremove = "movie"
        def __init__(self) -> None:
            if len(plex.users) > 0:
                ui.print('[plex] getting all watchlists ...')
            self.data = []
            try:
                for user in plex.users:
                    url = 'https://metadata.provider.plex.tv/library/sections/watchlist/all?X-Plex-Token=' + user[1]
                    response = plex.get(url)
                    if hasattr(response,'MediaContainer'):
                        if hasattr(response.MediaContainer,'Metadata'):
                            for entry in response.MediaContainer.Metadata:
                                entry.user = [user]
                                if not entry in self.data:
                                    if entry.type == 'show':
                                        self.data += [plex.show(entry)]
                                    if entry.type == 'movie':
                                        self.data += [plex.movie(entry)]
                                else:
                                    element = next(x for x in self.data if x == entry)
                                    if not user in element.user:
                                        element.user += [user]
                self.data.sort(key=lambda s: s.watchlistedAt,reverse=True)
            except Exception as e:
                ui.print('done') 
                ui.print("[plex error]: (watchlist exception): " + str(e),debug=ui_settings.debug)
                ui.print('[plex error]: could not reach plex')
            if len(plex.users) > 0:
                ui.print('done')        
        def remove(self,item):
            if hasattr(item,'user'):
                if isinstance(item.user[0],list):
                    for user in item.user:
                        ui.print('[plex] item: "' + item.title + '" removed from '+ user[0] +'`s watchlist')
                        url = 'https://metadata.provider.plex.tv/actions/removeFromWatchlist?ratingKey=' + item.ratingKey + '&X-Plex-Token=' + user[1]
                        response = plex.session.put(url,data={'ratingKey':item.ratingKey})
                    if not self == []:
                        self.data.remove(item)
                else:
                    ui.print('[plex] item: "' + item.title + '" removed from '+ item.user[0] +'`s watchlist')
                    url = 'https://metadata.provider.plex.tv/actions/removeFromWatchlist?ratingKey=' + item.ratingKey + '&X-Plex-Token=' + item.user[1]
                    response = plex.session.put(url,data={'ratingKey':item.ratingKey})
                    if not self == []:
                        self.data.remove(item)
        def add(self,item,user):
            ui.print('[plex] item: "' + item.title + '" added to '+ user[0] +'`s watchlist')
            url = 'https://metadata.provider.plex.tv/actions/addToWatchlist?ratingKey=' + item.ratingKey + '&X-Plex-Token=' + user[1]
            response = plex.session.put(url,data={'ratingKey':item.ratingKey})
            if item.type == 'show':
                self.data.append(plex.show(item.ratingKey))
            elif item.type == 'movie':
                self.data.append(plex.movie(item.ratingKey))
        def update(self):
            if len(plex.users) > 0:
                ui.print("[plex] updating all watchlists ...",debug=ui_settings.debug)
            update = False
            new_watchlist = []
            try:
                for user in plex.users:
                    url = 'https://metadata.provider.plex.tv/library/sections/watchlist/all?X-Plex-Token=' + user[1]
                    response = plex.get(url)
                    if hasattr(response,'MediaContainer'):
                        if hasattr(response.MediaContainer,'Metadata'):
                            for entry in response.MediaContainer.Metadata:
                                entry.user = [user]
                                if not entry in self.data:
                                    ui.print('[plex] item: "' + entry.title + '" found in '+ user[0] +'`s watchlist')
                                    update = True
                                    if entry.type == 'show':
                                        self.data += [plex.show(entry)]
                                    if entry.type == 'movie':
                                        self.data += [plex.movie(entry)]
                                else:
                                    element = next(x for x in self.data if x == entry)
                                    if not user in element.user:
                                        element.user += [user]
                            new_watchlist += response.MediaContainer.Metadata
                for entry in self.data[:]:
                    if not entry in new_watchlist:
                        self.data.remove(entry)
                self.data.sort(key=lambda s: s.watchlistedAt,reverse=True)
            except Exception as e:
                ui.print('done') 
                ui.print("[plex error]: (watchlist exception): " + str(e),debug=ui_settings.debug)
                ui.print('[plex error]: could not reach plex')
            if len(plex.users) > 0:
                ui.print('done') 
            return update       
    class season(content.media):
        def __init__(self,other):
            self.watchlist = plex.watchlist
            self.__dict__.update(other.__dict__)
            self.Episodes = []
            while len(self.Episodes) < self.leafCount:
                url = 'https://metadata.provider.plex.tv/library/metadata/'+self.ratingKey+'/children?includeUserState=1&X-Plex-Container-Size=200&X-Plex-Container-Start='+str(len(self.Episodes))+'&X-Plex-Token='+plex.users[0][1]
                response = plex.get(url)
                if not response == None:
                    if hasattr(response,'MediaContainer'):
                        if hasattr(response.MediaContainer,'Metadata'):
                            for episode in response.MediaContainer.Metadata:
                                episode.grandparentYear = self.parentYear
                                self.Episodes += [plex.episode(episode)] 
                        self.leafCount = response.MediaContainer.totalSize
                else: 
                    time.sleep(1)
    class episode(content.media):
        def __init__(self,other):
            self.watchlist = plex.watchlist
            self.__dict__.update(other.__dict__)
    class show(content.media):
        def __init__(self, ratingKey):
            self.watchlist = plex.watchlist
            if not isinstance(ratingKey,str):
                self.__dict__.update(ratingKey.__dict__)
                ratingKey = ratingKey.ratingKey
                if isinstance(self.user[0],list):
                    token = self.user[0][1]
                else:
                    token = self.user[1]
            else:
                if ratingKey.startswith('plex://'):
                    ratingKey = ratingKey.split('/')[-1]
                token = plex.users[0][1]
            success = False
            while not success:
                url = 'https://metadata.provider.plex.tv/library/metadata/'+ratingKey+'?includeUserState=1&X-Plex-Token='+token
                response = plex.get(url)
                if not response == None:
                    self.__dict__.update(response.MediaContainer.Metadata[0].__dict__)
                    self.Seasons = []
                    url = 'https://metadata.provider.plex.tv/library/metadata/'+ratingKey+'/children?includeUserState=1&X-Plex-Container-Size=200&X-Plex-Container-Start=0&X-Plex-Token='+token
                    response = plex.get(url)
                    if not response == None:
                        if hasattr(response,'MediaContainer'):
                            if hasattr(response.MediaContainer,'Metadata'):
                                for Season in response.MediaContainer.Metadata[:]:
                                    if Season.index == 0:
                                        response.MediaContainer.Metadata.remove(Season)
                                results = [None] * len(response.MediaContainer.Metadata)
                                threads = []
                                #start thread for each season
                                for index,Season in enumerate(response.MediaContainer.Metadata):
                                    Season.parentYear = self.year
                                    t = Thread(target=multi_init, args=(plex.season,Season,results,index))
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
    class movie(content.media):
        def __init__(self, ratingKey):
            self.watchlist = plex.watchlist
            if not isinstance(ratingKey,str):
                self.__dict__.update(ratingKey.__dict__)
                ratingKey = ratingKey.ratingKey
            elif ratingKey.startswith('plex://'):
                ratingKey = ratingKey.split('/')[-1]
            url = 'https://metadata.provider.plex.tv/library/metadata/'+ratingKey+'?includeUserState=1&X-Plex-Token='+plex.users[0][1]
            response = plex.get(url)
            self.__dict__.update(response.MediaContainer.Metadata[0].__dict__)            
    class library(content.libraries):
        name = 'Plex Library'
        url = 'http://localhost:32400'
        movies = '1'
        shows = '2'
        check = []
        def setup(cls, new=False):
            if new:
                print()
                settings = []
                for category, allsettings in ui.settings_list:
                    for setting in allsettings:
                        settings += [setting]
                if len(plex.users) == 0:
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
                    elif setting.name == 'Plex "movies" library':
                        setting.setup()
                        print()
                    elif setting.name == 'Plex "shows" library':
                        setting.setup()
                        print()
                content.libraries.active = [plex.library.name]
            else:
                content.libraries.setup(plex.library)
        class refresh:
            def poll(self):
                try:
                    refreshing = True
                    while refreshing:
                        refreshing = False
                        url = plex.library.url + '/library/sections/?X-Plex-Token=' + plex.users[0][1]
                        response = plex.get(url)
                        for section in response.MediaContainer.Directory:
                            if section.refreshing:
                                refreshing = True
                        time.sleep(1)
                    return True
                except Exception as e:
                    ui.print(str(e),debug=ui_settings.debug)
                    return True
            def call(section):
                time.sleep(2)
                plex.library.refresh.poll(None)
                url = plex.library.url + '/library/sections/' + section + '/refresh?X-Plex-Token=' + plex.users[0][1]
                plex.session.get(url)
            def __new__(cls,section):
                ui.print('refreshing library section '+section+'')
                t = Thread(target=multi_init, args=(plex.library.refresh.call,section,[None],0))
                t.start()
        def __new__(self):
            list = []
            if not plex.library.check == [['']] and not plex.library.check == []:
                ui.print('[plex] getting plex library section/s "'+','.join(x[0] for x in plex.library.check) +'" ...')
                types = ['1','2','3','4']
                for section in plex.library.check:
                    if section[0] == '':
                        continue
                    section_response = []
                    for type in types:
                        url = plex.library.url + '/library/sections/'+section[0]+'/all?type='+type+'&X-Plex-Token='+ plex.users[0][1]
                        response = plex.get(url)
                        if hasattr(response,'MediaContainer'):
                            if hasattr(response.MediaContainer,'Metadata'):
                                for element in response.MediaContainer.Metadata:
                                    section_response += [content.media(element)]
                    if len(section_response) == 0:
                        ui.print("[plex error]: couldnt reach local plex library section '"+section[0]+"' at server address: " + plex.library.url + " - or this library really is empty.")  
                    else:
                        list += section_response
                ui.print('done')
            else:
                ui.print('[plex] getting entire plex library ...')
                url = plex.library.url + '/library/all?X-Plex-Token='+ plex.users[0][1]
                response = plex.get(url)
                ui.print('done')
                if hasattr(response,'MediaContainer'):
                    if hasattr(response.MediaContainer,'Metadata'):
                        for element in response.MediaContainer.Metadata:
                            list += [content.media(element)]
                else:
                    ui.print("[plex error]: couldnt reach local plex server at server address: " + plex.library.url + " - or this library really is empty.")    
            if len(list) == 0:
                ui.print("[plex error]: Your library seems empty. To prevent unwanted behaviour, no further downloads will be started. If your library really is empty, please add at least one media item manually.") 
            return list
    def search(query,library=[]):
        query = query.replace(' ','%20')
        url = 'https://metadata.provider.plex.tv/library/search?query='+query+'&limit=20&searchTypes=movies%2Ctv&includeMetadata=1&X-Plex-Token='+plex.users[0][1]
        response = plex.get(url)
        try:
            return response.MediaContainer.SearchResult    
        except:
            return []
    def match(query,type,library=[]):
        if not library == []:
            for element in library:
                if element.type == type:
                    some_local_media = element
                    break
        else:
            ui.print("[plex error]: couldnt match content to plex media type, because the plex library is empty. Please add at least one movie and one show!")
            return []
        if type == 'movie':
            agent = 'tv.plex.agents.movie'
        else:
            agent = 'tv.plex.agents.series'
        url = plex.library.url + '/library/metadata/'+some_local_media.ratingKey+'/matches?manual=1&title='+query+'&agent='+agent+'&language=en-US&X-Plex-Token='+plex.users[0][1]
        response = plex.get(url)
        try:
            match = response.MediaContainer.SearchResult[0]
            if match.type == 'show':
                return [plex.show(match.guid)]
            elif match.type == 'movie':
                return [plex.movie(match.guid)] 
        except:
            return [] 
#Trakt Class
class trakt(content.services):
    name = 'Trakt'
    client_id = "0183a05ad97098d87287fe46da4ae286f434f32e8e951caad4cc147c947d79a3"
    client_secret = "87109ed53fe1b4d6b0239e671f36cd2f17378384fa1ae09888a32643f83b7e6c"
    lists = []
    users = []
    current_user = ["",""]
    session = requests.Session()
    def setup(self,new=False):
        back = False
        settings = []
        for category, allsettings in ui.settings_list:
            for setting in allsettings:
                if setting.cls == self or setting.name == self.name + ' auto remove':
                    settings += [setting]
        ui.cls("Options/Settings/Content Services/Content Services/Trakt")
        if not new:
            while not back:
                print("0) Back")
                indices = []
                for index, setting in enumerate(settings):
                    print(str(index+1) + ') ' + setting.name)
                    indices += [str(index+1)]
                print()
                choice = input("Choose an action: ")
                if choice in indices:
                    if settings[int(choice)-1].name == "Trakt lists":
                        print()
                        print("You can define which trakt lists should be monitored by plex_debrid. This includes public lists and your trakt users watchlists and collections.")
                        print()
                        print('Currently monitored trakt lists: "'+str(trakt.lists)+'"')
                        print()
                        print('0) Back')
                        print('1) Add list')
                        if len(trakt.lists) > 0:
                            print('2) Remove list')
                        print()
                        choice = input('Choose an action: ')
                        print()
                        if choice == '1':
                            print("Choose a trakt list that should be monitored by plex_debrid.")
                            print()
                            i=1
                            indices = []
                            add_user = []
                            print('0) Back')
                            print('1) add public list')
                            for user in trakt.users:
                                if not user[0] + "'s watchlist" in trakt.lists:
                                    print(str(i+1) + ') add ' + user[0] + "'s watchlist")
                                    indices += [str(i+1)]
                                    add_user += [user[0] + "'s watchlist"]
                                    i+=1
                                if not user[0] + "'s collection" in trakt.lists:
                                    print(str(i+1) + ') add ' + user[0] + "'s collection")
                                    indices += [str(i+1)]
                                    add_user += [user[0] + "'s collection"]
                                    i+=1
                            print()
                            choice = input("Choose a list: ")
                            if choice == '0':
                                back = True
                            elif choice == '1':
                                print("To add a public list, please enter the lists url in the format shown by this example: (Example URL: '/users/giladg/lists/latest-releases') ")
                                print()
                                url = input("Please enter the public list url: ")
                                working = False
                                trakt.current_user = trakt.users[0]
                                if trakt.current_user[1] == "":
                                    print("Please add at least one trakt user before adding a trakt list!")
                                    time.sleep(5)
                                    return False
                                response,header = trakt.get('https://api.trakt.tv' + url + '/items')
                                while response == None:
                                    print()
                                    print("Looks like that url didnt work. Please enter the lists url in the format shown by this example: (Example URL: '/users/giladg/lists/latest-releases') ")
                                    print()
                                    url = input("Please enter the public list url: ")
                                    response,header = trakt.get('https://api.trakt.tv' + url)
                                trakt.lists += [url]
                                return True
                            elif choice in indices:
                                trakt.lists += [add_user[int(choice)-2]]
                                return True
                        elif choice == '2':
                            indices = []
                            print("Choose a list to remove.")
                            print()
                            print('0) Back')
                            for index,list in enumerate(trakt.lists):
                                print(str(index+1) + ') ' + list)
                                indices += [str(index+1)]
                            print()
                            choice = input("Choose a list: ")
                            if choice == '0':
                                back = True
                            elif choice in indices:
                                trakt.lists.remove(trakt.lists[int(choice)-1])
                                return True
                    else:
                        settings[int(choice)-1].input()
                    back = True
                elif choice == '0':
                    back = True
        else:
            print('Please add at least one trakt user:')
            for setting in settings:
                if setting.name == 'Trakt users':
                    setting.setup()
            trakt.lists = [trakt.users[0][0] + "'s watchlist"]
    def logerror(response):
        if not response.status_code == 200:
            ui.print("[trakt] error: " + str(response.content),debug=ui_settings.debug)
        if response.status_code == 401:
            ui.print("[trakt] error: (401 unauthorized): trakt api key for user '"+trakt.current_user[0]+"' does not seem to work. Consider re-authorizing plex_debrid for this trakt user.")
    def get(url): 
        try :
            response = trakt.session.get(url, headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36', 'Content-type' : "application/json", "trakt-api-key" : trakt.client_id, "trakt-api-version" : "2", "Authorization" : "Bearer " + trakt.current_user[1]})
            trakt.logerror(response)
            header = response.headers
            response = json.loads(response.content, object_hook=lambda d: SimpleNamespace(**d))
        except :
            response = None
            header = None
        return response, header
    def post(url, data):
        try :
            response = trakt.session.post(url, headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36', 'Content-type' : "application/json", "trakt-api-key" : trakt.client_id, "trakt-api-version" : "2", "Authorization" : "Bearer " + trakt.current_user[1]}, data = data)
            trakt.logerror(response)
            response = json.loads(response.content, object_hook=lambda d: SimpleNamespace(**d))
            time.sleep(1)
        except :
            response = None
        return response
    def oauth(code=""):
        if code == "":
            response = trakt.post('https://api.trakt.tv/oauth/device/code',json.dumps({'client_id':trakt.client_id}))
            return response.device_code, response.user_code
        else:
            response = None
            while response == None:
                response = trakt.post('https://api.trakt.tv/oauth/device/token',json.dumps({'code': code, 'client_id':trakt.client_id, 'client_secret':trakt.client_secret}))
                time.sleep(1)
            return response.access_token       
    class watchlist(content.watchlist):
        autoremove = "movie"
        def __init__(self):
            if len(trakt.lists) > 0:
                ui.print('[trakt] getting all trakt lists ...')
            self.data = []
            for list in trakt.lists:
                list_type = "public"
                for user in trakt.users:
                    if list == user[0] + "'s watchlist":
                        list_type = "watchlist"
                        break
                    if list == user[0] + "'s collection":
                        list_type = "collection"
                        break
                trakt.current_user = user
                if list_type == "watchlist":
                    try:
                        watchlist_items, header = trakt.get('https://api.trakt.tv/users/me/watchlist/movies,shows?extended=full')
                        for element in watchlist_items:
                            if hasattr(element,'show'):
                                element.show.type = 'show'
                                element.show.user = user
                                element.show.guid = element.show.ids.trakt
                                if not element.show in self.data:
                                    self.data.append(trakt.show(element.show))
                            elif hasattr(element,'movie'):
                                element.movie.type = 'movie'
                                element.movie.user = user
                                element.movie.guid = element.movie.ids.trakt
                                if not element.movie in self.data:
                                    self.data.append(trakt.movie(element.movie))
                    except Exception as e:
                        ui.print("[trakt error]: (exception): " + str(e),debug=ui_settings.debug)
                        continue
                elif list_type == "collection":
                    try:
                        watchlist_items,header = trakt.get('https://api.trakt.tv/sync/collection/shows?extended=full')
                        for element in watchlist_items:
                            if hasattr(element,'show'):
                                element.show.type = 'show'
                                element.show.user = user
                                element.show.guid = element.show.ids.trakt
                                if not element.show in self.data:
                                    self.data.append(trakt.show(element.show))
                    except Exception as e:
                        ui.print("[trakt error]: (exception): " + str(e),debug=ui_settings.debug)
                        continue
                else:
                    try:
                        watchlist_items, header = trakt.get('https://api.trakt.tv'+list+'/items/movies,shows?extended=full')
                        for element in watchlist_items:
                            if hasattr(element,'show'):
                                element.show.type = 'show'
                                element.show.user = user
                                element.show.guid = element.show.ids.trakt
                                if not element.show in self.data:
                                    self.data.append(trakt.show(element.show))
                            elif hasattr(element,'movie'):
                                element.movie.type = 'movie'
                                element.movie.user = user
                                element.movie.guid = element.movie.ids.trakt
                                if not element.movie in self.data:
                                    self.data.append(trakt.movie(element.movie))
                    except Exception as e:
                        ui.print("[trakt error]: (exception): " + str(e),debug=ui_settings.debug)
                        continue
            ui.print('done')
        def update(self):
            if len(trakt.lists) > 0:
                ui.print('[trakt] updating all trakt watchlists ...',debug=ui_settings.debug)
            refresh = False
            new_watchlist = []
            for list in trakt.lists:
                public = True
                for user in trakt.users:
                    if list == user[0] + "'s watchlist":
                        public = False
                        break
                trakt.current_user = user
                if not public:
                    try:
                        watchlist_items, header = trakt.get('https://api.trakt.tv/users/me/watchlist/movies,shows?extended=full')
                        for element in watchlist_items:
                            if hasattr(element,'show'):
                                element.show.type = 'show'
                                element.show.user = user
                                element.show.guid = element.show.ids.trakt
                                if not element.show in self.data:
                                    refresh = True
                                    ui.print('[trakt] item: "' + element.show.title + '" found in ' + trakt.current_user[0]+ "'s trakt watchlist.")
                                    self.data.append(trakt.show(element.show))
                                new_watchlist += [element.show]
                            elif hasattr(element,'movie'):
                                element.movie.type = 'movie'
                                element.movie.user = user
                                element.movie.guid = element.movie.ids.trakt
                                if not element.movie in self.data:
                                    refresh = True
                                    ui.print('[trakt] item: "' + element.movie.title + '" found in ' + trakt.current_user[0]+ "'s trakt watchlist.")
                                    self.data.append(trakt.movie(element.movie))
                                new_watchlist += [element.movie]
                    except Exception as e:
                        ui.print("[trakt error]: (exception): " + str(e),debug=ui_settings.debug)
                        continue
            for element in self.data[:]:
                if not element in new_watchlist:
                    self.data.remove(element)
            if len(trakt.lists) > 0:
                ui.print('done',debug=ui_settings.debug)
            if refresh:
                return True
            return False
        def remove(self,original_element):
            element = copy.deepcopy(original_element)
            user = copy.deepcopy(element.user)
            data = []
            shows = []
            movies = []
            if element.type == 'tv':
                for ids in element.ids.__dict__.copy():
                    value = getattr(element.ids,ids)
                    if not value:
                        delattr(element.ids,ids)
                for attribute in element.__dict__.copy():
                    if not (attribute == 'ids' or attribute == 'seasons' or attribute == 'title' or attribute == 'year'):
                        delattr(element,attribute)
                ui.print('[trakt] item: "' + element.title + '" removed from '+user[0]+'`s watchlist')
                shows += [element]
            elif element.type == 'movie':
                for ids in element.ids.__dict__.copy():
                    value = getattr(element.ids,ids)
                    if not value:
                        delattr(element.ids,ids)
                for attribute in element.__dict__.copy():
                    if not (attribute == 'ids' or attribute == 'title' or attribute == 'year'):
                        delattr(element,attribute)
                ui.print('[trakt] item: "' + element.title + '" removed from '+user[0]+'`s watchlist')
                movies += [element]
            data = {'movies':movies,'shows':shows}
            trakt.current_user = user
            trakt.post('https://api.trakt.tv/sync/watchlist/remove',json.dumps(data, default=lambda o: o.__dict__))
    class season(content.media):
        def __init__(self,other):
            self.watchlist = trakt.watchlist
            self.__dict__.update(other.__dict__)
            self.Episodes = []
            if hasattr(self,'ids.trakt'):
                self.guid = self.ids.trakt
            else:
                self.guid = None
            try:
                if hasattr(self,'first_aired'):
                    if not self.first_aired == None:
                        self.originallyAvailableAt = datetime.datetime.strptime(self.first_aired,'%Y-%m-%dT%H:%M:%S.000Z').strftime('%Y-%m-%d')
                    else:
                        self.originallyAvailableAt = datetime.datetime.utcnow().strftime('%Y-%m-%d')
                else:
                    self.originallyAvailableAt = datetime.datetime.utcnow().strftime('%Y-%m-%d')
            except:
                self.originallyAvailableAt = datetime.datetime.utcnow().strftime('%Y-%m-%d')
            self.index = self.number
            self.type = 'season'
            for episode in self.episodes:
                episode.grandparentYear = self.parentYear
                episode.grandparentTitle = self.parentTitle
                episode.grandparentGuid = self.parentGuid
                episode.parentIndex = self.index
                self.Episodes += [trakt.episode(episode)]
            self.leafCount = len(self.Episodes)
    class episode(content.media):
        def __init__(self,other):
            self.watchlist = trakt.watchlist
            self.__dict__.update(other.__dict__)
            if hasattr(self,'ids.trakt'):
                self.guid = self.ids.trakt
            else:
                self.guid = None
            try:
                if hasattr(self,'first_aired'):
                    if not self.first_aired == None:
                        self.originallyAvailableAt = datetime.datetime.strptime(self.first_aired,'%Y-%m-%dT%H:%M:%S.000Z').strftime('%Y-%m-%d')
                    else:
                        self.originallyAvailableAt = datetime.datetime.utcnow().strftime('%Y-%m-%d')
                else:
                    self.originallyAvailableAt = datetime.datetime.utcnow().strftime('%Y-%m-%d')
            except:
                self.originallyAvailableAt = datetime.datetime.utcnow().strftime('%Y-%m-%d')
            self.index = self.number
            self.type = 'episode'
    class show(content.media):
        def __init__(self,other):
            self.watchlist = trakt.watchlist
            self.__dict__.update(other.__dict__)
            self.Seasons = []
            self.guid = self.ids.trakt
            try:
                self.originallyAvailableAt = datetime.datetime.strptime(self.first_aired,'%Y-%m-%dT%H:%M:%S.000Z').strftime('%Y-%m-%d')
            except:
                self.originallyAvailableAt = datetime.datetime.utcnow().strftime('%Y-%m-%d')
            response, header = trakt.get('https://api.trakt.tv/shows/' + str(self.ids.trakt) + '/seasons?extended=episodes,full')
            leafCount = 0
            for season in response:
                if not season.number == 0:
                    season.parentYear = self.year
                    season.parentTitle = self.title
                    season.parentGuid = self.guid
                    self.Seasons += [trakt.season(season)]
            for season in self.Seasons:
                leafCount += season.leafCount
            self.leafCount = leafCount
    class movie(content.media):
        def __init__(self,other):
            self.watchlist = trakt.watchlist
            try:
                self.originallyAvailableAt = other.released
                delattr(other,'released')
            except:
                self.originallyAvailableAt = datetime.datetime.utcnow().strftime('%Y-%m-%d')
            self.__dict__.update(other.__dict__)
    class library(content.libraries):
        name = 'Trakt Collection'
        user = []
        def setup(cls, new=False):
            print()
            traktuser = []
            for category, allsettings in ui.settings_list:
                for setting in allsettings:
                    if setting.name == 'Trakt users':
                        traktuser = setting
            if len(trakt.users) == 0:
                print('Please set up a trakt user first:')
                print()
                traktuser.setup()
                print()
            back = False
            while not back:
                print('Please choose the trakt user whos trakt collection should be maintained by plex_debrid.')
                print()
                indices = []
                for index,user in enumerate(trakt.users):
                    print(str(index+1) + ') ' + user[0] + "'s trakt collection")
                    indices += [str(index+1)]
                print()
                choice = input("Choose a trakt users collection: ")
                if choice in indices:
                    trakt.library.user = trakt.users[int(choice)-1]
                    content.libraries.active = [trakt.library.name]
                    back = True
        def __new__(self):
            trakt.current_user = trakt.library.user
            ui.print('[trakt] getting '+trakt.current_user[0]+ "'s" + ' entire trakt collection ...')
            watchlist_items = []
            collection = []
            collection_movies,header = trakt.get('https://api.trakt.tv/sync/collection/movies?extended=metadata')
            collection_shows,header = trakt.get('https://api.trakt.tv/sync/collection/shows?extended=metadata')
            watchlist_items += collection_movies
            watchlist_items += collection_shows
            for element in watchlist_items:
                if hasattr(element,'show'):
                    element.show.type = 'show'
                    element.show.user = trakt.library.user
                    element.show.guid = element.show.ids.trakt
                    element.show.Seasons = []
                    for season in element.seasons:
                        season.parentYear = element.show.year
                        season.parentTitle = element.show.title
                        season.parentGuid = element.show.guid
                        element.show.Seasons += [trakt.season(season)]
                    leafCount = 0
                    for season in element.show.Seasons:
                        leafCount += season.leafCount
                        collection.append(season)
                        for episode in season.Episodes:
                            collection.append(episode)
                    element.show.leafCount = leafCount
                    collection.append(content.media(element.show))
                elif hasattr(element,'movie'):
                    element.movie.type = 'movie'
                    element.movie.user = trakt.library.user
                    element.movie.guid = element.movie.ids.trakt
                    collection.append(content.media(element.movie))
            ui.print('done')
            return collection
        def add(original_element):
            element = copy.deepcopy(original_element)
            data = []
            shows = []
            movies = []
            #determine release quality
            try:
                if len(element.Releases) == 0:
                    element.Releases += [element.Seasons[0].Releases[0]]
                resolution = regex.search(r'(2160|1080|720)(?=p)',element.Releases[0].title,regex.I)
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
                hdr = regex.search(r'(HDR)',element.Releases[0].title,regex.I)
            except:
                hdr = False
            if hdr:
                hdr = 'hdr10'
            #add release quality to element
            if element.type == 'show':
                if hasattr(element,'seasons'):
                    for season in element.seasons:
                        for attribute in season.__dict__.copy():
                            if not (attribute == 'ids' or attribute == 'episodes' or attribute == 'number'):
                                delattr(season,attribute)
                        for episode in season.episodes:
                            if hdr:
                                episode.media_type = 'digital'
                                episode.resolution = resolution
                                episode.hdr = hdr
                            else:
                                episode.media_type = 'digital'
                                episode.resolution = resolution
                else:
                    ui.print("[trakt] error: couldnt find seasons in show object",debug=ui_settings.debug)
                #remove unwanted attributes from element
                for ids in element.ids.__dict__.copy():
                    value = getattr(element.ids,ids)
                    if not value:
                        delattr(element.ids,ids)
                for attribute in element.__dict__.copy():
                    if not (attribute == 'ids' or attribute == 'seasons' or attribute == 'title' or attribute == 'year'):
                        delattr(element,attribute)
                shows += [element]
            elif element.type == 'movie':
                if hdr:
                    element.media_type = 'digital'
                    element.resolution = resolution
                    element.hdr = hdr
                else:
                    element.media_type = 'digital'
                    element.resolution = resolution
                #remove unwanted attributes from element
                for ids in element.ids.__dict__.copy():
                    value = getattr(element.ids,ids)
                    if not value:
                        delattr(element.ids,ids)
                for attribute in element.__dict__.copy():
                    if not (attribute == 'ids' or attribute == 'resolution' or attribute == 'media_type' or attribute == 'hdr' or attribute == 'title' or attribute == 'year'):
                        delattr(element,attribute)
                movies += [element]
            #add element to collection
            data = {'movies':movies,'shows':shows}
            response = trakt.post('https://api.trakt.tv/sync/collection',json.dumps(data, default=lambda o: o.__dict__))
            ui.print('[trakt] item: ' + element.title + ' added to ' + trakt.library.user[0] + "'s collection")
            sys.stdout.flush()
    def search(query,type):
        trakt.current_user = trakt.users[0]
        if type == 'all':
            response, header = trakt.get('https://api.trakt.tv/search/movie,show?query=' + str(query))
        elif type == 'movie':
            response, header = trakt.get('https://api.trakt.tv/search/movie?query=' + str(query))
        elif type == 'tv':
            response, header = trakt.get('https://api.trakt.tv/search/show?query=' + str(query))
        elif type == 'imdb':
            response, header = trakt.get('https://api.trakt.tv/search/imdb?query=' + str(query))
        elif type == 'tmdb':
            response, header = trakt.get('https://api.trakt.tv/search/tmdb?query=' + str(query))
        elif type == 'tvdb':
            response, header = trakt.get('https://api.trakt.tv/search/tvdb?query=' + str(query))
        return response
    def match(query,service,type):
        trakt.current_user = trakt.users[0]
        if service == 'imdb':
            response, header = trakt.get('https://api.trakt.tv/search/imdb/' + str(query) + '?type=' + type + '&extended=full,episodes')
        elif service == 'tmdb':
            response, header = trakt.get('https://api.trakt.tv/search/tmdb/' + str(query) + '?type=' + type + '&extended=full,episodes')
        elif service == 'tvdb':
            response, header = trakt.get('https://api.trakt.tv/search/tvdb/' + str(query) + '?type=' + type + '&extended=full,episodes')
        try:
            if type == 'movie':
                response[0].movie.type = 'movie'
                response[0].movie.guid = response[0].movie.ids.trakt
                return trakt.movie(response[0].movie)
            elif type == 'show':
                response[0].show.type = 'show'
                response[0].show.guid = response[0].show.ids.trakt
                return trakt.show(response[0].show)
            elif type == 'season':
                response[0].season.type = 'season'
                response[0].season.guid = response[0].season.ids.trakt
                return trakt.season(response[0].season)
            elif type == 'episode':
                response[0].episode.type = 'episode'
                response[0].episode.guid = response[0].episode.ids.trakt
                return trakt.episode(response[0].episode)
        except:
            return None
#Overseer Class
class overseerr(content.services):
    name = 'Overseerr'
    base_url = "http://localhost:5055"
    users = ['all']
    allowed_status = [['2'],]
    api_key = ""
    session = requests.Session()
    def setup(self):
        ui.cls("Options/Settings/Content Services/Content Services/Overseerr")
        working_key = False
        working_url = False
        if len(plex.users) == 0:
            print('Looks like you havent connected plex_debrid to plex! Please setup at least one plex user.')
            time.sleep(3)
            return
        try:
            response = overseerr.session.get(overseerr.base_url + '/api/v1/request',headers={"X-Api-Key" : overseerr.api_key},timeout=0.5)
            if response.status_code == 200:
                working_key = True
                working_url = True
            else:
                working_key = False
                working_url = True
        except:
            working_url = False
        while not working_url:
            if overseerr.base_url == "http://localhost:5055":
                print("Looks like overseerr couldn't be reached under the default base url ('"+overseerr.base_url+"').") 
            else:
                print("Looks like overseerr couldn't be reached under the current base url ('"+overseerr.base_url+"').") 
            print("Please make sure overseerr is running and try again, or provide your overseerr base URL below:")
            print()
            overseerr.base_url = input("Please provide your overseerr base URL (or press enter to retry default: 'http://localhost:5055'): ")
            if overseerr.base_url == "":
                overseerr.base_url = "http://localhost:5055"
            working_key = False
            working_url = False
            try:
                response = overseerr.session.get(overseerr.base_url + '/api/v1/request',headers={"X-Api-Key" : overseerr.api_key},timeout=0.5)
                if response.status_code == 200:
                    working_key = True
                    working_url = True
                else:
                    working_key = False
                    working_url = True
            except:
                working_url = False
        while not working_key:
            if overseerr.api_key == "":
                print("To setup overseerr, please provide your overseerr API Key. Press enter to return to the main menu.")
            else:
                print("Looks like your current API Key ('"+overseerr.api_key+"') doesnt work.") 
            print()
            overseerr.api_key = input("Please enter your overseerr API Key: ")
            if overseerr.api_key == "":
                return
            working_key = False
            working_url = False
            try:
                response = overseerr.session.get(overseerr.base_url + '/api/v1/request',headers={"X-Api-Key" : overseerr.api_key},timeout=0.5)
                if response.status_code == 200:
                    working_key = True
                    working_url = True
                else:
                    working_key = False
                    working_url = True
            except:
                working_url = False
        settings = []
        for category, allsettings in ui.settings_list:
            for setting in allsettings:
                if setting.cls == self or setting.name.startswith(self.name):
                    settings += [setting]
        response = overseerr.get(overseerr.base_url + '/api/v1/user')
        users = response.results
        new_users = []
        for user in users:
            if not user.displayName in overseerr.users:
                new_users += [user.displayName]
        back = False
        ui.cls("Options/Settings/Content Services/Content Services/Overseerr")
        while not back:
            print("0) Back")
            indices = []
            for index, setting in enumerate(settings):
                print(str(index+1) + ') ' + setting.name)
                indices += [str(index+1)]
            print()
            choice = input("Choose an action: ")
            if choice in indices:
                if settings[int(choice)-1].name == "Overseerr users":
                    print()
                    print("You can define which users approved requests should be downloaded by plex_debrid.")
                    print()
                    print('Currently monitored Overseerr users: "'+str(overseerr.users)+'"')
                    print()
                    print('0) Back')
                    print('1) Always monitor all users')
                    print('2) Add user')
                    if len(overseerr.users) > 0 and not overseerr.users == ['all']:
                        print('3) Remove user')
                    print()
                    choice = input('Choose an action: ')
                    print()
                    if choice == '1':
                        overseerr.users = ['all']
                        return True
                    elif choice == '2':
                        print("Choose which users approved requests should be downloaded by plex_debrid. Type 'all' to add all currently listed users.")
                        print()
                        i=0
                        indices = []
                        add_user = []
                        print('0) Back')
                        for user in users:
                            if not user.displayName in overseerr.users:
                                print(str(i+1) + ') ' + user.displayName)
                                indices += [str(i+1)]
                                add_user += [user.displayName]
                                i+=1
                        print()
                        choice = input("Choose a user: ")
                        if choice == '0':
                            back = True
                        elif choice == 'all':
                            overseerr.users += new_users
                            return True
                        elif choice in indices:
                            overseerr.users += [add_user[int(choice)-1]]
                            return True
                    elif choice == '3':
                        indices = []
                        print("Choose a user to remove.")
                        print()
                        print('0) Back')
                        for index,user in enumerate(overseerr.users):
                            print(str(index+1) + ') ' + user)
                            indices += [str(index+1)]
                        print()
                        choice = input("Choose a user: ")
                        if choice == '0':
                            back = True
                        elif choice in indices:
                            overseerr.users.remove(overseerr.users[int(choice)-1])
                            return True
                else:
                    settings[int(choice)-1].input()
                back = True
            elif choice == '0':
                back = True
    def logerror(response):
        if not response.status_code == 200:
            ui.print("[overseerr] error: " + str(response.content),debug=ui_settings.debug)
        if response.status_code == 401:
            ui.print("[overseerr] error: (401 unauthorized): overserr api key does not seem to work.")
    def get(url): 
        try :
            response = overseerr.session.get(url, headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36', 'Content-type' : "application/json", "X-Api-Key" : overseerr.api_key})
            overseerr.logerror(response)
            response = json.loads(response.content, object_hook=lambda d: SimpleNamespace(**d))
        except :
            response = None
        return response
    def post(url, data):
        try :
            response = overseerr.session.post(url, headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36', 'Content-type' : "application/json", "X-Api-Key" : overseerr.api_key}, data = data)
            overseerr.logerror(response)
            response = json.loads(response.content, object_hook=lambda d: SimpleNamespace(**d))
        except :
            response = None
        return response
    class requests(content.watchlist):
        def __init__(self):
            self.data = []
            if len(overseerr.users) > 0 and len(overseerr.api_key) > 0:
                ui.print('[overseerr] getting all overseerr requests ...')
                try:
                    response = overseerr.get(overseerr.base_url + '/api/v1/request')
                    for element in response.results:
                        if not element in self.data and (element.requestedBy.displayName in overseerr.users or overseerr.users == ['all']) and [str(element.status)] in overseerr.allowed_status:
                            self.data.append(element)
                except:
                    ui.print('[overseerr] error: looks like overseerr couldnt be reached. Turn on debug printing for more info.')
                    self.data = []
                ui.print('done')
        def sync(self,other:plex.watchlist,library):
            add = []
            for element in self.data:
                result = []
                try:
                    if not element.media.tmdbId == None:
                        match_id = 'tmdb-'+str(element.media.tmdbId)
                    elif not element.media.tvdbId == None:
                        match_id = 'tvdb-'+str(element.media.tvdbId)
                    if element.type == 'movie':
                        result = plex.match(match_id,'movie',library = library)
                    elif element.type == 'tv':
                        result = plex.match(match_id,'show',library = library)
                except:
                    result = []
                if not result == []:
                    add += result
            for element in add:
                if not element in other:
                    other.data.append(element)
        def update(self):
            if len(overseerr.users) > 0 and len(overseerr.api_key) > 0:
                ui.print('[overseerr] updating all overseerr requests ...',debug=ui_settings.debug)
                refresh = False
                try:
                    response = overseerr.get(overseerr.base_url + '/api/v1/request')
                    for element in response.results:
                        if not element in self.data and (element.requestedBy.displayName in overseerr.users or overseerr.users == ['all']) and [str(element.status)] in overseerr.allowed_status:
                            ui.print('[overseerr] found new overseerr request by user "' + element.requestedBy.displayName + '".')
                            refresh = True
                            self.data.append(element)
                    for element in self.data[:]:
                        if not element in response.results:
                            self.data.remove(element)
                    ui.print('done',debug=ui_settings.debug)
                    if refresh:
                        return True
                except:
                    ui.print('done',debug=ui_settings.debug)
                    return False
            return False
#Debrid Class 
class debrid:
    tracker = []
    downloading = []
    uncached = 'true'
    #Service Class:
    class services:
        active = []
        def setup(cls,new=False):
            settings = []
            for category, allsettings in ui.settings_list:
                for setting in allsettings:
                    if setting.cls == cls:
                        settings += [setting]
            back = False
            if not new:
                while not back:
                    print()
                    print("0) Back")
                    indices = []
                    for index, setting in enumerate(settings):
                        print(str(index+1) + ') ' + setting.name)
                        indices += [str(index+1)]
                    print()
                    choice = input("Choose an action: ")
                    if choice in indices:
                        settings[int(choice)-1].setup()
                        if not cls.name in debrid.services.active:
                            debrid.services.active += [cls.name]
                        back = True
                    elif choice == '0':
                        back = True
            else:
                print()
                indices = []
                for setting in settings:
                    setting.setup()
                    if not cls.name in debrid.services.active:
                        debrid.services.active += [cls.name]      
        def __new__(cls):
            activeservices = []
            for servicename in debrid.services.active:
                for service in cls.__subclasses__():
                    if service.name == servicename:
                        activeservices += [service]
            return activeservices
    #Download Method:
    def download(element:content.media,stream=True,query='',force=False):
        downloaded_files = []
        if stream:
            cached_releases = copy.deepcopy(element.Releases)
            downloaded = False
            for release in cached_releases:
                element.Releases = [release,]
                if len(debrid.tracker) > 0:
                    for t,s in debrid.tracker:
                        if regex.search(t,release.source,regex.I):
                            release.cached = s
                for service in debrid.services():
                    if service.short in release.cached:
                        if service.download(element,stream=stream,query=query,force=force):
                            downloaded = True
                            downloaded_files += element.Releases[0].files
                            break
                if downloaded:
                    break
            if len(element.Releases) > 0:
                element.Releases[0].files = downloaded_files
            return downloaded
        else:
            scraped_releases = copy.deepcopy(element.Releases)
            downloaded = False
            for release in scraped_releases:
                element.Releases = [release,]
                if len(debrid.tracker) > 0:
                    for t,s in debrid.tracker:
                        if regex.search(t,release.source,regex.I):
                            release.cached = s
                for service in debrid.services():
                    if len(release.cached) > 0:
                        if service.short in release.cached:
                            if service.download(element,stream=stream,query=query,force=force):
                                downloaded = True
                                downloaded_files += element.Releases[0].files
                                break
                    else:
                        if service.download(element,stream=stream,query=query,force=force):
                            downloaded = True
                            downloaded_files += element.Releases[0].files
                            break
                if downloaded:
                    break
            if len(element.Releases) > 0:
                element.Releases[0].files = downloaded_files
            return downloaded
    #Check Method:
    def check(element:content.media,force=False):
        for service in debrid.services():
            service.check(element,force=force)
    #RealDebrid class
    class realdebrid(services):
        #(required) Name of the Debrid service
        name = "Real Debrid"
        short = "RD"
        #(required) Authentification of the Debrid service, can be oauth aswell. Create a setting for the required variables in the ui.settings_list. For an oauth example check the trakt authentification.
        api_key = ""
        #Define Variables
        session = requests.Session()
        #Error Log
        def logerror(response):
            if not response.status_code == 200:
                ui.print("[realdebrid] error: " + str(response.content),debug=ui_settings.debug)
            if response.status_code == 401:
                ui.print("[realdebrid] error: (401 unauthorized): realdebrid api key does not seem to work. check your realdebrid settings.")
        #Get Function
        def get(url): 
            headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36', 'authorization' : 'Bearer ' + debrid.realdebrid.api_key}
            try :
                response = debrid.realdebrid.session.get(url, headers = headers)
                debrid.realdebrid.logerror(response)
                response = json.loads(response.content, object_hook=lambda d: SimpleNamespace(**d))
            except Exception as e:
                ui.print("[realdebrid] error: (json exception): " + str(e),debug=ui_settings.debug)
                response = None
            return response
        #Post Function
        def post(url, data):
            headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36', 'authorization' : 'Bearer ' + debrid.realdebrid.api_key}
            try :
                response = debrid.realdebrid.session.post(url, headers = headers, data = data)
                debrid.realdebrid.logerror(response)
                response = json.loads(response.content, object_hook=lambda d: SimpleNamespace(**d))
            except Exception as e:
                ui.print("[realdebrid] error: (json exception): " + str(e),debug=ui_settings.debug)
                response = None
            return response
        #Delete Function
        def delete(url):
            headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36', 'authorization' : 'Bearer ' + debrid.realdebrid.api_key}
            try :
                requests.delete(url, headers = headers)
                #time.sleep(1)
            except Exception as e:
                ui.print("[realdebrid] error: (delete exception): " + str(e),debug=ui_settings.debug)
                None
            return None
        #Object classes
        class file:
            def __init__(self,id,name,size,wanted_list,unwanted_list):
                self.id = id
                self.name = name
                self.size = size
                self.match = ''
                wanted = False
                for key in wanted_list:
                    if regex.search(r'('+key+')',self.name,regex.I):
                        wanted = True
                        self.match = key
                        break
                unwanted = False
                for key in unwanted_list:
                    if regex.search(r'('+key+')',self.name,regex.I) or self.name.endswith('.exe') or self.name.endswith('.txt'):
                        unwanted = True
                        break
                self.wanted = wanted
                self.unwanted = unwanted
            def __eq__(self, other):
                return self.id == other.id 
        class version:
            def __init__(self,files):
                self.files = files
                self.needed = 0
                self.wanted = 0
                self.unwanted = 0
                for file in self.files:
                    if file.wanted:
                        self.wanted += 1
                    if file.unwanted:
                        self.unwanted += 1
        #(required) Download Function. 
        def download(element:content.media,stream=True,query='',force=False):
            cached = element.Releases
            if query == '':
                query = element.deviation()
            wanted = [query]
            if not isinstance(element,releases):
                wanted = element.files()
            for release in cached[:]:
                #if release matches query
                if regex.match(r'('+ query.replace('.','\.').replace("\.*",".*") + ')',release.title,regex.I) or force:
                    if stream:
                        release.size = 0
                        for version in release.files:
                            if hasattr(version,'files'):
                                if len(version.files) > 0 and version.wanted > len(wanted)/2 or force:
                                    cached_ids = []
                                    for file in version.files:
                                        cached_ids += [file.id]
                                    #post magnet to real debrid
                                    try:
                                        response = debrid.realdebrid.post('https://api.real-debrid.com/rest/1.0/torrents/addMagnet',{'magnet' : str(release.download[0])})
                                        torrent_id = str(response.id)
                                    except:
                                        continue
                                    response = debrid.realdebrid.post('https://api.real-debrid.com/rest/1.0/torrents/selectFiles/' + torrent_id , {'files' : str(','.join(cached_ids))})    
                                    response = debrid.realdebrid.get('https://api.real-debrid.com/rest/1.0/torrents/info/' + torrent_id)
                                    if len(response.links) == len(cached_ids):
                                        release.download = response.links
                                    else:
                                        debrid.realdebrid.delete('https://api.real-debrid.com/rest/1.0/torrents/delete/' + torrent_id)
                                        continue
                                    if len(release.download) > 0:
                                        for link in release.download:
                                            try:
                                                response = debrid.realdebrid.post('https://api.real-debrid.com/rest/1.0/unrestrict/link', {'link' : link})
                                            except:
                                                break
                                        release.files = version.files
                                        ui.print('[realdebrid] adding cached release: ' + release.title)
                                        return True
                        ui.print('done')
                        return False
                    else:
                        try:
                            response = debrid.realdebrid.post('https://api.real-debrid.com/rest/1.0/torrents/addMagnet',{'magnet':release.download[0]})
                            time.sleep(0.1)
                            debrid.realdebrid.post('https://api.real-debrid.com/rest/1.0/torrents/selectFiles/' + str(response.id), {'files':'all'})
                            ui.print('[realdebrid] adding uncached release: '+ release.title)
                            return True
                        except:
                            continue
            return False
        #(required) Check Function
        def check(element,force=False):
            if force:
                wanted = ['.*']
            else:
                wanted = element.files()
            unwanted = releases.sort.unwanted
            hashes = []
            for release in element.Releases[:]:
                if len(release.hash) == 40:
                    hashes += [release.hash]
                else:
                    element.Releases.remove(release)
            if len(hashes) > 0:
                response = debrid.realdebrid.get('https://api.real-debrid.com/rest/1.0/torrents/instantAvailability/' + '/'.join(hashes))
                for release in element.Releases:
                    release.files = []
                    if hasattr(response, release.hash.lower()):
                        if hasattr(getattr(response, release.hash.lower()),'rd'):
                            if len(getattr(response, release.hash.lower()).rd) > 0:
                                for cashed_version in getattr(response, release.hash.lower()).rd:
                                    version_files = []
                                    for file in cashed_version.__dict__:
                                        debrid_file = debrid.realdebrid.file(file,getattr(cashed_version,file).filename,getattr(cashed_version,file).filesize,wanted,unwanted)
                                        version_files.append(debrid_file)
                                    release.files += [debrid.realdebrid.version(version_files),]
                                #select cached version that has the most needed, most wanted, least unwanted files and most files overall
                                release.files.sort(key=lambda x: len(x.files), reverse=True)
                                release.files.sort(key=lambda x: x.wanted, reverse=True)
                                release.files.sort(key=lambda x: x.unwanted, reverse=False)
                                release.wanted = release.files[0].wanted
                                release.unwanted = release.files[0].unwanted
                                release.cached += ['RD']
                                continue
    #AllDebrid class
    class alldebrid(services):
        #(required) Name of the Debrid service
        name = "All Debrid"
        short = "AD"
        #(required) Authentification of the Debrid service, can be oauth aswell. Create a setting for the required variables in the ui.settings_list. For an oauth example check the trakt authentification.
        api_key = ""
        #Define Variables
        session = requests.Session()
        #Error Log
        def logerror(response):
            if not response.status_code == 200:
                ui.print("[alldebrid] error: " + str(response.content),debug=ui_settings.debug)
            if 'error' in str(response.content):
                try:
                    response2 = json.loads(response.content, object_hook=lambda d: SimpleNamespace(**d))
                    ui.print("[alldebrid] error: " + response2.data[0].error.message)
                except:
                    try:
                        response2 = json.loads(response.content, object_hook=lambda d: SimpleNamespace(**d))
                        ui.print("[alldebrid] error: " + response2.error.message)
                    except:
                        ui.print("[alldebrid] error: unknown error")
            if response.status_code == 401:
                ui.print("[alldebrid] error: (401 unauthorized): alldebrid api key does not seem to work. check your alldebrid settings.")
        #Get Function
        def get(url): 
            headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36', 'authorization' : 'Bearer ' + debrid.alldebrid.api_key}
            try :
                response = debrid.alldebrid.session.get(url + '&agent=plex_debrid', headers = headers)
                debrid.alldebrid.logerror(response)
                response = json.loads(response.content, object_hook=lambda d: SimpleNamespace(**d))
            except Exception as e:
                ui.print("[alldebrid] error: (json exception): " + str(e),debug=ui_settings.debug)
                response = None
            return response
        #Post Function
        def post(url, data):
            headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36', 'authorization' : 'Bearer ' + debrid.alldebrid.api_key}
            try :
                response = debrid.alldebrid.session.post(url, headers = headers, data = data)
                debrid.alldebrid.logerror(response)
                response = json.loads(response.content, object_hook=lambda d: SimpleNamespace(**d))
            except Exception as e:
                ui.print("[alldebrid] error: (json exception): " + str(e),debug=ui_settings.debug)
                response = None
            return response
        #(required) Download Function. 
        def download(element:content.media,stream=True,query='',force=False):
            cached = element.Releases
            if query == '':
                query = element.deviation()
            for release in cached[:]:
                #if release matches query
                if regex.match(r'('+ query.replace('.','\.').replace("\.*",".*") + ')',release.title,regex.I) or force:
                    if stream:
                        #Cached Download Method for AllDebrid
                        url = 'https://api.alldebrid.com/v4/magnet/instant?magnets[]=' + release.download[0]
                        response = debrid.alldebrid.get(url)
                        instant = False
                        try:
                            instant = response.data.magnets[0].instant
                        except:
                            continue
                        if instant:
                            url = 'https://api.alldebrid.com/v4/magnet/upload?magnets[]='+ release.download[0]
                            response = debrid.alldebrid.get(url)
                            torrent_id = response.data.magnets[0].id
                            url = 'https://api.alldebrid.com/v4/magnet/status?id='+ str(torrent_id)
                            response = debrid.alldebrid.get(url)
                            torrent_files = response.data.magnets.links
                            torrent_links = []
                            for file in torrent_files:
                                torrent_links += [file.link]
                            if len(torrent_links) > 0:
                                rate_limit = 1/12
                                success = False
                                saved_links = []
                                for link in torrent_links:
                                    url = 'https://api.alldebrid.com/v4/link/unlock?link='+ requests.utils.quote(link)
                                    response = debrid.alldebrid.get(url)
                                    if not response.status == 'success':
                                        success = False
                                        break
                                    saved_links += [requests.utils.quote(link)]
                                    success = True
                                    time.sleep(rate_limit)
                                if success:
                                    saved_links = '&links[]='.join(saved_links)
                                    url = 'https://api.alldebrid.com/v4/user/links/save?links[]=' + saved_links
                                    response = debrid.alldebrid.get(url)
                                    ui.print('[alldebrid] adding cached release: ' + release.title)
                                    return True
                                else:
                                    #delete failed torrent
                                    return False
                            else:
                                #delete failed torrent
                                return False
                    else:
                        #Uncached Download Method for AllDebrid
                        url = 'https://api.alldebrid.com/v4/magnet/upload?magnets[]='+ release.download[0]
                        response = debrid.alldebrid.get(url)
                        ui.print('[alldebrid] adding uncached release: '+ release.title)
                        return True
            return False  
        #(required) Check Function
        def check(element,force=False):
            if force:
                wanted = ['.*']
            else:
                wanted = element.files()
            unwanted = releases.sort.unwanted
            hashes = []
            for release in element.Releases[:]:
                if len(release.hash) == 40:
                    hashes += [release.hash]
                else:
                    element.Releases.remove(release)
            if len(hashes) > 0:
                response = debrid.alldebrid.get('https://api.alldebrid.com/v4/magnet/instant?magnets[]=' + '&magnets[]='.join(hashes[:200]))
                for i,release in enumerate(element.Releases):
                    try:
                        instant = response.data.magnets[i].instant
                        if instant:
                            release.cached += ['AD']
                            #release.wanted = 0
                            #release.unwanted = 0
                    except:
                        continue
    #Premiumize class
    class premiumize(services):
        #(required) Name of the Debrid service
        name = "Premiumize"
        short = "PM"
        #(required) Authentification of the Debrid service, can be oauth aswell. Create a setting for the required variables in the ui.settings_list. For an oauth example check the trakt authentification.
        api_key = ""
        #Define Variables
        session = requests.Session()
        #Error Log
        def logerror(response):
            if not response.status_code == 200:
                ui.print("[premiumize] error: " + str(response.content),debug=ui_settings.debug)
            if 'error' in str(response.content):
                response2 = json.loads(response.content, object_hook=lambda d: SimpleNamespace(**d))
                ui.print("[premiumize] error: " + response2.message)
            if response.status_code == 401:
                ui.print("[premiumize] error: (401 unauthorized): premiumize api key does not seem to work. check your premiumize settings.")
        #Get Function
        def get(url): 
            headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36','accept': 'application/json'}
            try :
                response = debrid.premiumize.session.get(url + '&apikey='+ debrid.premiumize.api_key, headers = headers)
                debrid.premiumize.logerror(response)
                response = json.loads(response.content, object_hook=lambda d: SimpleNamespace(**d))
            except Exception as e:
                ui.print("[premiumize] error: (json exception): " + str(e),debug=ui_settings.debug)
                response = None
            return response
        #Post Function
        def post(url, data):
            headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36','accept': 'application/json','Content-Type': 'multipart/form-data'}
            try :
                response = debrid.premiumize.session.post(url + '?apikey='+ debrid.premiumize.api_key + data, headers = headers, data={})
                debrid.premiumize.logerror(response)
                response = json.loads(response.content, object_hook=lambda d: SimpleNamespace(**d))
            except Exception as e:
                ui.print("[premiumize] error: (json exception): " + str(e),debug=ui_settings.debug)
                response = None
            return response
        #(required) Download Function. 
        def download(element:content.media,stream=True,query='',force=False):
            cached = element.Releases
            if query == '':
                query = element.deviation()
            for release in cached[:]:
                #if release matches query
                if regex.match(r'('+ query.replace('.','\.').replace("\.*",".*") + ')',release.title,regex.I) or force:
                    if stream:
                        #Cached Download Method for premiumize
                        url = "https://www.premiumize.me/api/cache/check?items[]=" + release.download[0]
                        response = debrid.premiumize.get(url)
                        if not response.response[0]:
                            continue
                        url = "https://www.premiumize.me/api/transfer/create"
                        data = '&src='+release.download[0]
                        response = debrid.premiumize.post(url,data)
                        if response.status == 'success':
                            ui.print('[premiumize] adding cached release: ' + release.title)
                            return True
                    else:
                        #Uncached Download Method for premiumize
                        url = "https://www.premiumize.me/api/transfer/create"
                        data = '&src='+release.download[0]
                        response = debrid.premiumize.post(url,data)
                        if response.status == 'success':
                            ui.print('[premiumize] adding uncached release: '+ release.title)
                            return True
            return False      
        #(required) Check Function
        def check(element,force=False):
            if force:
                wanted = ['.*']
            else:
                wanted = element.files()
            unwanted = releases.sort.unwanted
            hashes = []
            for release in element.Releases[:]:
                if len(release.hash) == 40:
                    hashes += [release.hash]
                else:
                    element.Releases.remove(release)
            if len(hashes) > 0:
                response = debrid.premiumize.get('https://www.premiumize.me/api/cache/check?items[]=' + '&items[]='.join(hashes[:200]))
                for i,release in enumerate(element.Releases):
                    try:
                        instant = response.response[i]
                        if instant:
                            release.cached += ['PM']
                            #release.wanted = 0
                            #release.unwanted = 0
                    except:
                        continue
    #DebridLink class
    class debridlink(services):
        #(required) Name of the Debrid service
        name = "Debrid Link"
        short = "DL"
        #(required) Authentification of the Debrid service, can be oauth aswell. Create a setting for the required variables in the ui.settings_list. For an oauth example check the trakt authentification.
        api_key = ""
        client_id = "0KLCzpbPTCsWZtQ9Ad0aZA"
        #Define Variables
        session = requests.Session()
        #Error Log
        def logerror(response):
            if not response.status_code == 200:
                ui.print("[debridlink] error: " + str(response.content),debug=ui_settings.debug)
            if 'error' in str(response.content):
                try:
                    response2 = json.loads(response.content, object_hook=lambda d: SimpleNamespace(**d))
                    if not response2.error == 'authorization_pending':
                        ui.print("[debridlink] error: " + response2.error)
                except:
                    ui.print("[debridlink] error: unknown error")
            if response.status_code == 401:
                ui.print("[debridlink] error: (401 unauthorized): debridlink api key does not seem to work. check your debridlink settings.")
        #Get Function
        def get(url): 
            headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36','Content-Type': 'application/x-www-form-urlencoded', 'Authorization' : 'Bearer ' + debrid.debridlink.api_key}
            try :
                response = debrid.debridlink.session.get(url, headers = headers)
                debrid.debridlink.logerror(response)
                response = json.loads(response.content, object_hook=lambda d: SimpleNamespace(**d))
            except Exception as e:
                ui.print("debridlink error: (json exception): " + str(e),debug=ui_settings.debug)
                response = None
            return response
        #Post Function
        def post(url, data):
            headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36','Content-Type': 'application/x-www-form-urlencoded', 'Authorization' : 'Bearer ' + debrid.debridlink.api_key}
            try :
                response = debrid.debridlink.session.post(url, headers = headers, data = data)
                debrid.debridlink.logerror(response)
                response = json.loads(response.content, object_hook=lambda d: SimpleNamespace(**d))
            except Exception as e:
                ui.print("debridlink error: (json exception): " + str(e),debug=ui_settings.debug)
                response = None
            return response
        #Oauth Method
        def oauth(code=""):
            if code == "":
                response = debrid.debridlink.post('https://debrid-link.fr/api/oauth/device/code','client_id='+debrid.debridlink.client_id)
                return response.device_code, response.user_code
            else:
                response = None
                while response == None:
                    response = debrid.debridlink.post('https://debrid-link.fr/api/oauth/token','client_id='+debrid.debridlink.client_id+'&code='+code+'&grant_type=http%3A%2F%2Foauth.net%2Fgrant_type%2Fdevice%2F1.0')
                    if hasattr(response,'error'):
                        response = None
                    time.sleep(1)
                return response.access_token
        #(required) Download Function. 
        def download(element:content.media,stream=True,query='',force=False):
            cached = element.Releases
            if query == '':
                query = element.deviation()
            for release in cached[:]:
                #if release matches query
                if regex.match(r'('+ query.replace('.','\.').replace("\.*",".*") + ')',release.title,regex.I) or force:
                    if stream:
                        #Cached Download Method for debridlink
                        hashstring = regex.findall(r'(?<=btih:).*?(?=&)',str(release.download[0]),regex.I)[0]
                        url = 'https://debrid-link.fr/api/v2/seedbox/cached?url=' + hashstring
                        response = debrid.debridlink.get(url)
                        try:
                            if hasattr(response.value,hashstring.lower()):
                                url = 'https://debrid-link.fr/api/v2/seedbox/add'
                                response = debrid.debridlink.post(url,'url=' + hashstring + '&async=true')
                                if response.success:
                                    ui.print('[debridlink] adding cached release: ' + release.title)
                                    return True
                        except:
                            continue
                    else:
                        #Uncached Download Method for debridlink
                        try:
                            url = 'https://debrid-link.fr/api/v2/seedbox/add'
                            response = debrid.debridlink.post(url,'url=' + release.download[0] + '&async=true')
                            if response.success:
                                ui.print('[debridlink] adding uncached release: '+ release.title)
                                return True
                        except:
                            continue
            return False  
        #(required) Check Function
        def check(element,force=False):
            if force:
                wanted = ['.*']
            else:
                wanted = element.files()
            unwanted = releases.sort.unwanted
            hashes = []
            for release in element.Releases[:]:
                if len(release.hash) == 40:
                    hashes += [release.hash]
                else:
                    element.Releases.remove(release)
            if len(hashes) > 0:
                response = debrid.debridlink.get('https://debrid-link.fr/api/v2/seedbox/cached?url=' + ','.join(hashes[:200]))
                for i,release in enumerate(element.Releases):
                    try:
                        if hasattr(response.value,release.hash.lower()):
                            release.cached += ['DL']
                            #release.wanted = 0
                            #release.unwanted = 0
                    except:
                        continue
    #Putio class
    class putio(services):
        #(required) Name of the Debrid service
        name = "PUT.io"
        short = "PUT"
        #(required) Authentification of the Debrid service, can be oauth aswell. Create a setting for the required variables in the ui.settings_list. For an oauth example check the trakt authentification.
        api_key = ""
        client_id = "5843"
        #Define Variables
        session = requests.Session()
        #Error Log
        def logerror(response):
            if not response.status_code == 200:
                ui.print("[put.io] error: " + str(response.content),debug=ui_settings.debug)
            if 'error' in str(response.content) and not response.status_code == 200:
                try:
                    response2 = json.loads(response.content, object_hook=lambda d: SimpleNamespace(**d))
                    ui.print("[put.io] error: " + response2.error_message)
                except:
                    ui.print("[put.io] error: unknown error")
            if response.status_code == 401:
                ui.print("[put.io] error: (401 unauthorized): put.io api key does not seem to work. check your put.io settings.")
        #Get Function
        def get(url): 
            headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36','Content-Type': 'application/x-www-form-urlencoded', 'Authorization' : 'Bearer ' + debrid.putio.api_key}
            try :
                response = debrid.putio.session.get(url, headers = headers)
                debrid.putio.logerror(response)
                response = json.loads(response.content, object_hook=lambda d: SimpleNamespace(**d))
            except Exception as e:
                ui.print("[put.io] error: (json exception): " + str(e),debug=ui_settings.debug)
                response = None
            return response
        #Post Function
        def post(url, data):
            headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36','Content-Type': 'application/x-www-form-urlencoded', 'Authorization' : 'Bearer ' + debrid.putio.api_key}
            try :
                response = debrid.putio.session.post(url, headers = headers, data = data)
                debrid.putio.logerror(response)
                response = json.loads(response.content, object_hook=lambda d: SimpleNamespace(**d))
            except Exception as e:
                ui.print("[put.io] error: (json exception): " + str(e),debug=ui_settings.debug)
                response = None
            return response
        #Oauth Method
        def oauth(code=""):
            #I used the swaggerhub oauth redirection url for creating a put.io app, as putio doesnt provide a general redirection url :)
            if code == "":
                response = debrid.putio.get('https://api.put.io/v2/oauth2/oob/code?app_id='+debrid.putio.client_id)
                return response.code, response.code
            else:
                response = None
                while response == None:
                    response = debrid.putio.get('https://api.put.io/v2/oauth2/oob/code/'+code)
                    if not hasattr(response,'oauth_token'):
                        response = None
                    elif response.oauth_token == None:
                        response = None
                    time.sleep(1)
                return response.oauth_token
        #(required) Download Function. 
        def download(element:content.media,stream=True,query='',force=False):
            cached = element.Releases
            if query == '':
                query = element.deviation()
            for release in cached[:]:
                #if release matches query
                if regex.match(r'('+ query.replace('.','\.').replace("\.*",".*") + ')',release.title,regex.I) or force:
                    if stream:
                        #Cached Download Method for put.io
                        url = 'https://api.put.io/v2/transfers/add'
                        response = debrid.putio.post(url,'url='+release.download[0])
                        try:
                            if hasattr(response,'transfer'):
                                ui.print('[put.io] adding release: ' + release.title)
                                return True
                            else:
                                continue
                        except:
                            continue
                    else:
                        #Uncached Download Method for put.io
                        try:
                            url = 'https://api.put.io/v2/transfers/add'
                            response = debrid.putio.post(url,'url='+release.download[0])
                            if hasattr(response,'transfer'):
                                ui.print('[put.io] adding release: '+ release.title)
                                return True
                            else:
                                continue
                        except:
                            continue
            return False  
        #(required) Check Function
        def check(element,force=False):
            #there is no official check method for putio.
            force
#Release Class
class releases:   
    #Define release attributes
    def __init__(self, source, type, title, files, size, download,seeders=0):
        self.source     = source
        self.type       = type
        self.title      = title
        self.files      = files
        self.size       = size
        self.download   = download
        self.hash       = ''
        if len(self.download)> 0:
            if regex.search(r'(?<=btih:).*?(?=&)',str(self.download[0]),regex.I):
                self.hash   = regex.findall(r'(?<=btih:).*?(?=&)',str(self.download[0]),regex.I)[0]            
        self.cached     = []
        self.wanted = 0
        self.unwanted = 0
        self.seeders = seeders
        self.resolution = "0"
        if regex.search(r'(2160|1080|720|480)(?=p)',str(self.title),regex.I):
            self.resolution = regex.findall(r'(2160|1080|720|480)(?=p)',str(self.title),regex.I)[0]
    #Define when releases are Equal 
    def __eq__(self, other):
        return self.title == other.title
    #Sort Method
    class sort:
        def setup(cls,new=False):
            back = False
            while not back:
                ui.cls('Options/Settings/Scraper Settings/Versions')
                print("Currently defined versions: [" + '], ['.join(x[0] for x in releases.sort.versions) + ']')
                print()
                print("0) Back")
                print("1) Edit versions")
                print("2) Add version")
                print()
                choice = input("Choose an action: ")
                if choice == '0':
                    back = True
                elif choice == "1":
                    back2 = False
                    while not back2:
                        ui.cls('Options/Settings/Scraper Settings/Versions/Edit')
                        print("0) Back")
                        indices = []
                        for index,version in enumerate(releases.sort.versions):
                            print(str(index+1) + ') Edit version "' + version[0] + '"')
                            indices += [str(index+1)]
                        print()
                        choice2 = input("Choose an action: ")
                        if choice2 in indices:
                            print()
                            default = releases.sort.versions[int(choice2)-1]
                            name = releases.sort.versions[int(choice2)-1][0]
                            releases.sort.version.setup(name,default,new=False)
                        if choice2 == '0':
                            back2 = True
                elif choice == "2":
                    ui.cls('Options/Settings/Scraper Settings/Versions/Add')
                    names = []
                    name = "Id rather be watching the 1999 cinematic masterpiece 'The Mummy'."
                    names += [name]
                    for version in releases.sort.versions[:]:
                        names += [version[0]]
                    while name in names:
                        name = input("Please provide a unique name for this version: ")
                    print()
                    default = copy.deepcopy(releases.sort.versions[0])
                    releases.sort.version.setup(name,default,new=True)
                    releases.sort.versions += [default]
            return
        class version:                
            def setup(name,version_,new=False):
                back = False
                default = version_[3]
                while not back:
                    version_[0] = name
                    if new:
                        ui.cls('Options/Settings/Scraper Settings/Versions/Add')
                        print('Your new version [' + name + '] has been filled with some default rules. You can add new ones or edit the existing rules.')
                    else:
                        ui.cls('Options/Settings/Scraper Settings/Versions/Edit')
                    print()
                    print('Current settigns for version [' + name + ']:')
                    print()
                    print("name     : " + version_[0])
                    print("media    : " + str(version_[1]) + " (not editable yet)")
                    print("required : " + version_[2]  + " (not editable yet)")
                    print()
                    print("0) Back")
                    indices = []
                    l_o = 0
                    l_a = 0
                    l_i = 0
                    l_s = 0
                    for index,rule in enumerate(default):
                        indices += [str(index+1)]
                        if len(str(index + 1)) >= l_i:
                            l_i = len(str(index + 1)) + 1
                        if len(rule[0]) >= l_a:
                            l_a = len(rule[0]) + 1
                        if len(rule[1]) >= l_s:
                            l_s = len(rule[1]) + 1
                        if len(rule[2]) >= l_o:
                            l_o = len(rule[2]) + 1
                    for index,rule in enumerate(default):
                        print(str(index+1) + ')' + ' ' * (l_i - len(str(index + 1))) + rule[0] + ' ' * (l_a - len(rule[0])) + ' ' + rule[1] + ' ' * (l_s - len(rule[1])) + ': ' + ' ' * (l_o - len(rule[2])) + rule[2] + '  ' + rule[3])
                    print()
                    print("Choose a rule to edit or add a new rule by typing 'add'")
                    print("To rename this version, type 'rename'")
                    if len(releases.sort.versions) > 1:
                        print("To delete this version, type 'remove'")
                    print()
                    choice = input("Choose an action: ")
                    print()
                    if choice in indices:
                        releases.sort.version.rule.setup(choice,default,new=False)
                    elif choice == '0':
                        back = True
                    elif choice == 'add':
                        releases.sort.version.rule.setup(choice,default,new=True)
                    elif choice == 'rename':
                        ui.cls('Options/Settings/Scraper Settings/Versions/Add')
                        names = []
                        for version in releases.sort.versions[:]:
                            names += [version[0]]
                        for version in releases.sort.versions[:]:
                            if version[0] == name:
                                break
                        while name in names:
                            name = input("Please provide a unique name for this version: ")
                        version[0] = name
                        print()
                    elif choice == 'remove':
                        if len(releases.sort.versions) > 1:
                            for version in releases.sort.versions[:]:
                                if version[0] == name:
                                    releases.sort.versions.remove(version)
                            back = True
            class rule:
                def setup(choice,default,new=True):
                    back = False
                    while not back:
                        if not new:
                            ui.cls('Options/Settings/Scraper Settings/Versions/Edit')
                            print("Current settings for rule #" + choice +":")
                            print()
                            print("0) Back")
                            print("1) Edit  attribute : " + default[int(choice)-1][0])
                            print("2) Edit  weight    : " + default[int(choice)-1][1])
                            print("3) Edit  operator  : " + default[int(choice)-1][2])
                            if not default[int(choice)-1][0] == "cache status" and not default[int(choice)-1][2] in ["highest","lowest"]:
                                print("4) Edit  value     : " + default[int(choice)-1][3])
                            print()
                            print("Choose a value to edit, move this rule by typing 'move' or delete this rule by typing 'remove' ")
                            print()
                            choice2 = input("Choose an action: ")
                        else:
                            ui.cls('Options/Settings/Scraper Settings/Versions/Add')
                            default += [["","","",""]]
                            choice = str(len(default))
                            choice2 = '1'
                        print()
                        if choice2 == '0':
                            back = True
                        elif choice2 == '1':
                            if not new:
                                print("You cannot change the attribute of an existing rule.")
                                print()
                                time.sleep(2)
                            else:
                                print("Please choose an attribute on which this rule should act.")
                                print()
                                indices = []
                                for index,attribute in enumerate(releases.sort.version.rule.__subclasses__()):
                                    print(str(index+1) + ') ' + attribute.name )
                                    indices += [str(index+1)]
                                print()
                                choice3 = input("Please choose an attribute: ")
                                if choice3 in indices:
                                    default[int(choice)-1][int(choice2)-1] = releases.sort.version.rule.__subclasses__()[int(choice3)-1].name
                                choice2 = '2'
                        if choice2 == '2':
                            print("Please choose a weight for this rule. This rule can either be a requirement or a preference.")
                            print()
                            indices = []
                            for index,attribute in enumerate(releases.sort.version.rule.weights):
                                print(str(index+1) + ') ' + attribute)
                                indices += [str(index+1)]
                            print()
                            choice3 = input("Please choose a weight: ")
                            if choice3 in indices:
                                default[int(choice)-1][int(choice2)-1] = releases.sort.version.rule.weights[int(choice3)-1]
                            if new:
                                choice2 = '3'
                        if choice2 == '3':
                            print("Please choose an operator for this rule.")
                            print()
                            operators = []
                            for subclass in releases.sort.version.rule.__subclasses__():
                                if subclass.name == default[int(choice)-1][0]:
                                    operators = subclass.operators
                                    break
                            indices = []
                            for index,attribute in enumerate(operators):
                                print(str(index+1) + ') ' + attribute)
                                indices += [str(index+1)]
                            print()
                            choice3 = input("Please choose an operator: ")
                            if choice3 in indices:
                                default[int(choice)-1][int(choice2)-1] = subclass.operators[int(choice3)-1]
                            if new and not default[int(choice)-1][0] == "cache status" and not default[int(choice)-1][2] in ["highest","lowest"]:
                                choice2 = '4'
                            elif new:
                                print("New rule added!")
                                time.sleep(2)
                                new = False
                        if choice2 == '4':
                            working = False
                            for subclass in releases.sort.version.rule.__subclasses__():
                                if subclass.name == default[int(choice)-1][0]:
                                    break
                            while not working:
                                print("Please choose a value for this rule. Make sure that the value you enter matches your chosen operator.")
                                print()
                                choice3 = input("Please enter a value: ")
                                if subclass.check(choice3):
                                    working = True
                            default[int(choice)-1][int(choice2)-1] = choice3
                            if new:
                                print("New rule added!")
                                time.sleep(2)
                                new = False
                        if choice2 == 'remove':
                            del default[int(choice)-1]
                            back = True
                        if choice2 == 'move':  
                            print('0) Back')
                            indices = []
                            for i,rule in enumerate(default):
                                print( str(i+1) +') Position '+ str(i+1))
                                indices += [str(i+1)]
                            print()
                            choice3 = input('Move rule #' + choice + ' to: ')
                            if choice in indices:
                                temp = copy.deepcopy(default[int(choice)-1])
                                del default[int(choice)-1]
                                default.insert(int(choice3)-1,temp)
                                back = True
                        print()
                operators = [""]
                weights = ["requirement","preference"]
                def __init__(self,attribute,required,operator,value=None) -> None:
                    self.attribute = attribute
                    self.required = (required == "requirement")
                    self.operator = operator
                    self.value = value
                def apply(self,scraped_releases:list):
                    try:
                        if self.required:
                            if self.operator == "==":
                                for release in scraped_releases[:]:
                                    if not getattr(release,self.attribute) == self.value:
                                        scraped_releases.remove(release)
                                return scraped_releases
                            if self.operator == ">=":
                                for release in scraped_releases[:]:
                                    if not float(getattr(release,self.attribute)) >= float(self.value):
                                        scraped_releases.remove(release)
                                return scraped_releases
                            if self.operator == "<=":
                                for release in scraped_releases[:]:
                                    if not float(getattr(release,self.attribute)) <= float(self.value):
                                        scraped_releases.remove(release)
                                return scraped_releases
                            if self.operator == "highest":
                                scraped_releases.sort(key=lambda s: float(getattr(s,self.attribute)), reverse=True)
                                for release in scraped_releases[:]:
                                    if not float(getattr(release,self.attribute)) == float(getattr(scraped_releases[0],self.attribute)):
                                        scraped_releases.remove(release)
                                return scraped_releases
                            if self.operator == "lowest":
                                scraped_releases.sort(key=lambda s: float(getattr(s,self.attribute)), reverse=False)
                                for release in scraped_releases[:]:
                                    if not float(getattr(release,self.attribute)) == float(getattr(scraped_releases[0],self.attribute)):
                                        scraped_releases.remove(release)
                                return scraped_releases
                            if self.operator == "include":
                                for release in scraped_releases[:]:
                                    if not bool(regex.search(self.value,getattr(release,self.attribute),regex.I)):
                                        scraped_releases.remove(release)
                                return scraped_releases
                            if self.operator == "exclude":
                                for release in scraped_releases[:]:
                                    if bool(regex.search(self.value,getattr(release,self.attribute),regex.I)):
                                        scraped_releases.remove(release)
                                return scraped_releases
                        else:
                            if self.operator == "==":
                                scraped_releases.sort(key=lambda s: (getattr(s,self.attribute) == self.value), reverse=True)
                                return scraped_releases
                            if self.operator == ">=":
                                scraped_releases.sort(key=lambda s: (float(getattr(s,self.attribute)) >= float(self.value)), reverse=True)
                                return scraped_releases
                            if self.operator == "<=":
                                scraped_releases.sort(key=lambda s: (float(getattr(s,self.attribute)) <= float(self.value)), reverse=True)
                                return scraped_releases
                            if self.operator == "highest":
                                scraped_releases.sort(key=lambda s: float(getattr(s,self.attribute)), reverse=True)
                                return scraped_releases
                            if self.operator == "lowest":
                                scraped_releases.sort(key=lambda s: float(getattr(s,self.attribute)), reverse=False)
                                return scraped_releases
                            if self.operator == "include":
                                scraped_releases.sort(key=lambda s: bool(regex.search(self.value,getattr(s,self.attribute),regex.I)), reverse=True)
                                return scraped_releases
                            if self.operator == "exclude":
                                scraped_releases.sort(key=lambda s: bool(regex.search(self.value,getattr(s,self.attribute),regex.I)), reverse=False)
                                return scraped_releases
                    except:
                        ui.print("version rule exception - ignoring this rule")
                        return scraped_releases
                def check(self):
                    return True
            class resolution(rule):
                name = "resolution"
                operators = ["==",">=","<=","highest","lowest"]
                def check(self):
                    try:
                        float(self)
                        return True
                    except:
                        print()
                        print("This value is not in the correct format. Please enter a number (e.g. '420' or '69.69')")
                        print()
                        return False
            class size(rule):
                name = "size"
                operators = ["==",">=","<=","highest","lowest"]
                def apply(self,scraped_releases:list):
                    try:
                        if self.required:
                            if self.operator == "==":
                                for release in scraped_releases[:]:
                                    if not getattr(release,self.attribute) == self.value:
                                        scraped_releases.remove(release)
                                return scraped_releases
                            if self.operator == ">=":
                                for release in scraped_releases[:]:
                                    if not float(getattr(release,self.attribute)) >= float(self.value):
                                        scraped_releases.remove(release)
                                return scraped_releases
                            if self.operator == "<=":
                                for release in scraped_releases[:]:
                                    if not float(getattr(release,self.attribute)) <= float(self.value):
                                        scraped_releases.remove(release)
                                return scraped_releases
                            if self.operator == "highest":
                                scraped_releases.sort(key=lambda s: 5 * round(float(getattr(s,self.attribute))/5), reverse=True)
                                for release in scraped_releases[:]:
                                    if not 5 * round(float(getattr(release,self.attribute))/5) == 5 * round(float(getattr(scraped_releases[0],self.attribute)/5)):
                                        scraped_releases.remove(release)
                                return scraped_releases
                            if self.operator == "lowest":
                                scraped_releases.sort(key=lambda s: 5 * round(float(getattr(s,self.attribute))/5), reverse=False)
                                for release in scraped_releases[:]:
                                    if not 5 * round(float(getattr(release,self.attribute))/5) == 5 * round(float(getattr(scraped_releases[0],self.attribute))/5):
                                        scraped_releases.remove(release)
                                return scraped_releases
                        else:
                            if self.operator == "==":
                                scraped_releases.sort(key=lambda s: (getattr(s,self.attribute) == self.value), reverse=True)
                                return scraped_releases
                            if self.operator == ">=":
                                scraped_releases.sort(key=lambda s: (float(getattr(s,self.attribute)) >= float(self.value)), reverse=True)
                                return scraped_releases
                            if self.operator == "<=":
                                scraped_releases.sort(key=lambda s: (float(getattr(s,self.attribute)) <= float(self.value)), reverse=True)
                                return scraped_releases
                            if self.operator == "highest":
                                scraped_releases.sort(key=lambda s: 5 * round(float(getattr(s,self.attribute))/5), reverse=True)
                                return scraped_releases
                            if self.operator == "lowest":
                                scraped_releases.sort(key=lambda s: 5 * round(float(getattr(s,self.attribute))/5), reverse=False)
                                return scraped_releases
                    except:
                        ui.print("version rule exception - ignoring this rule")
                        return scraped_releases
                def check(self):
                    try:
                        float(self)
                        return True
                    except:
                        print()
                        print("This value is not in the correct format. Please enter a number (e.g. '420' or '69.69')")
                        print()
                        return False
            class seeders(rule):
                name = "seeders"
                operators = ["==",">=","<=","highest","lowest"]
                def check(self):
                    try:
                        float(self)
                        return True
                    except:
                        print()
                        print("This value is not in the correct format. Please enter a number (e.g. '420' or '69.69')")
                        print()
                        return False
            class title(rule):
                name = "title"
                operators = ["==","include","exclude"]
                def check(self):
                    try:
                        regex.search(self,self,regex.I)
                        return True
                    except:
                        print()
                        print("This value is not in the correct format. Please make sure this value is a valid regex expression and no characters are escaped accidentally.")
                        print()
                        return False
            class source(rule):
                name = "source"
                operators = ["==","include","exclude"]
                def check(self):
                    try:
                        regex.search(self,self,regex.I)
                        return True
                    except:
                        print()
                        print("This value is not in the correct format. Please make sure this value is a valid regex expression and no characters are escaped accidentally.")
                        print()
                        return False
            class cache_status(rule):
                name = "cache status"
                operators = ["cached","uncached"]
                def __init__(self,attribute,required,operator,value=None) -> None:
                    self.attribute = "cached"
                    self.required = (required == "requirement")
                    self.operator = operator
                    self.value = value
                def apply(self,scraped_releases:list):
                    try:
                        if self.required:
                            if self.operator == "cached":
                                for release in scraped_releases[:]:
                                    if len(getattr(release,self.attribute)) == 0:
                                        scraped_releases.remove(release)
                                return scraped_releases
                            if self.operator == "uncached":
                                for release in scraped_releases[:]:
                                    if len(getattr(release,self.attribute)) > 0:
                                        scraped_releases.remove(release)
                                return scraped_releases
                        else:
                            if self.operator == "cached":
                                scraped_releases.sort(key=lambda s: len(getattr(s,self.attribute)), reverse=True)
                                return scraped_releases
                            if self.operator == "uncached":
                                scraped_releases.sort(key=lambda s: len(getattr(s,self.attribute)), reverse=False)
                                return scraped_releases
                    except:
                        ui.print("version rule exception - ignoring this rule")
                        return scraped_releases
            def __init__(self,name,media,required,rules) -> None:
                self.name = name
                self.media = media
                self.required = required
                self.rules = rules                
        unwanted = ['sample']
        versions = [
            ["2160p SDR","both","true",[
                ["cache status","requirement","cached",""],
                ["resolution","requirement",">=","2160"],
                ["title","requirement","exclude","(\.DV\.|\.3D\.|\.H?D?.?CAM\.)"],
                ["title","preference","exclude","(\.HDR\.)"],
                ["title","preference","include","(EXTENDED|REMASTERED)"],
                ["size","preference","lowest",""],
                ["seeders","preference","highest",""],
                ["size","requirement",">=","0.1"],
            ]],
            ["1080p SDR","both","true",[
                ["cache status","requirement","cached",""],
                ["resolution","requirement","<=","1080"],
                ["resolution","preference","highest",""],
                ["title","requirement","exclude","(\.DV\.|\.3D\.|\.H?D?.?CAM\.)"],
                ["title","requirement","exclude","(\.HDR\.)"],
                ["title","preference","include","(EXTENDED|REMASTERED)"],
                ["size","preference","lowest",""],
                ["seeders","preference","highest",""],
                ["size","requirement",">=","0.1"],
            ]],
        ]
        always_on_rules = [version.rule("wanted","preference","highest",""),version.rule("unwanted","preference","lowest","")]
        def __new__(self,scraped_releases:list,version:version):
            if len(scraped_releases) > 0:
                for rule in reversed(releases.sort.always_on_rules):
                    rule.apply(scraped_releases)
                for rule in reversed(version.rules):
                    for subrule in releases.sort.version.rule.__subclasses__():
                        if subrule.name == rule[0]:
                            rule = subrule(rule[0],rule[1],rule[2],rule[3])
                            break
                    scraped_releases = rule.apply(scraped_releases)
                ui.print('sorting releases for version [' + version.name + '] ... done - found ' + str(len(scraped_releases)) + ' releases')
            return scraped_releases
    #Rename Method
    class rename:
        replaceChars = [
            ['&','and'],
            ['ü','ue'],
            ['ä','ae'],
            ['ö','oe'],
            ['ß','ss'],
            ['é','e'],
            ['è','e'],
            ['sh!t','shit'],
            ['.',''],
            [':',''],
            ['(',''],
            [')',''],
            ['`',''],
            ['´',''],
            [',',''],
            ['!',''],
            ['?',''],
            [' - ',''],
            ["'",''],
            ["\u200b",''],
            [' ','.']
        ]
        def __new__(self,string):
            string = string.lower()
            for specialChar,repl in self.replaceChars:
                string = string.replace(specialChar.lower(),repl.lower())
            string = regex.sub(r'\.+',".",string)
            return string    
    #torrent2magnet Class:
    class torrent2magnet:
        class BTFailure(Exception):
            pass
        def decode_int(x, f):
            f += 1
            newf = x.find(b"e", f)
            n = int(x[f:newf])
            if six.indexbytes(x, f) == 45:
                if six.indexbytes(x, f + 1) == 48:
                    raise ValueError
            elif six.indexbytes(x, f) == 48 and newf != f + 1:
                raise ValueError
            return (n, newf + 1)
        def decode_string(x, f):
            colon = x.find(b":", f)
            n = int(x[f:colon])
            if six.indexbytes(x, f) == 48 and colon != f + 1:
                raise ValueError
            colon += 1
            return (x[colon : colon + n], colon + n)
        def decode_list(x, f):
            r, f = [], f + 1
            while six.indexbytes(x, f) != 101:
                v, f = releases.torrent2magnet.decode_func[six.indexbytes(x, f)](x, f)
                r.append(v)
            return (r, f + 1)
        def decode_dict(x, f):
            r, f = {}, f + 1
            while six.indexbytes(x, f) != 101:
                k, f = releases.torrent2magnet.decode_string(x, f)
                r[k], f = releases.torrent2magnet.decode_func[six.indexbytes(x, f)](x, f)
            return (r, f + 1)
        decode_func = {}
        decode_func[108] = decode_list
        decode_func[100] = decode_dict
        decode_func[105] = decode_int
        for i in range(48, 59):
            decode_func[i] = decode_string
        def bdecode(x):
            try:
                r, l = releases.torrent2magnet.decode_func[six.indexbytes(x, 0)](x, 0)
            except (IndexError, KeyError, ValueError):
                raise
                raise releases.torrent2magnet.BTFailure("not a valid bencoded string")
            if l != len(x):
                raise releases.torrent2magnet.BTFailure("invalid bencoded value (data after valid prefix)")
            return r
        class Bencached(object):
            __slots__ = ["bencoded"]
            def __init__(self, s):
                self.bencoded = s
        def encode_bencached(x, r):
            r.append(x.bencoded)
        def encode_int(x, r):
            r.extend((b"i", str(x).encode(), b"e"))
        def encode_bool(x, r):
            if x:
                releases.torrent2magnet.encode_int(1, r)
            else:
                releases.torrent2magnet.encode_int(0, r)
        def encode_string(x, r):
            r.extend((str(len(x)).encode(), b":", x))
        def encode_list(x, r):
            r.append(b"l")
            for i in x:
                releases.torrent2magnet.encode_func[type(i)](i, r)
            r.append(b"e")
        def encode_dict(x, r):
            r.append(b"d")
            for k, v in sorted(x.items()):
                r.extend((str(len(k)).encode(), b":", k))
                releases.torrent2magnet.encode_func[type(v)](v, r)
            r.append(b"e")
        encode_func = {}
        encode_func[Bencached] = encode_bencached
        encode_func[int] = encode_int
        encode_func[str] = encode_string
        encode_func[bytes] = encode_string
        encode_func[list] = encode_list
        encode_func[tuple] = encode_list
        encode_func[dict] = encode_dict
        def bencode(x):
            r = []
            releases.torrent2magnet.encode_func[type(x)](x, r)
            return b"".join(r)
        def __new__(cls,x):
            metadata = releases.torrent2magnet.bdecode(x)
            subj = metadata[b'info']
            hashcontents = releases.torrent2magnet.bencode(subj)
            digest = hashlib.sha1(hashcontents).hexdigest()
            return 'magnet:?'\
                    + 'xt=urn:btih:' + digest\
                    + '&dn=' + metadata[b'info'][b'name'].decode()\
                    + '&tr=' + metadata[b'announce'].decode()\
    #Print Method
    def print(scraped_releases):
        if __name__ == "__main__":
            longest_file = 0
            longest_cached = 0
            longest_title = 0
            longest_size = 0
            longest_index = 0
            longest_seeders = 0
            for index,release in enumerate(scraped_releases):
                release.printsize = str(round(release.size, 2))
                release.file = '+' + str(release.wanted) + '/-' + str(release.unwanted)
                if len(release.file) > longest_file:
                    longest_file = len(release.file)
                if len('/'.join(release.cached)) > longest_cached:
                    longest_cached = len('/'.join(release.cached))
                if len(release.title) > longest_title:
                    longest_title = len(release.title)
                if len(str(release.printsize)) > longest_size:
                    longest_size = len(str(release.printsize))
                if len(str(release.seeders)) > longest_seeders:
                    longest_seeders = len(str(release.seeders))
                if len(str(index+1)) > longest_index:
                    longest_index = len(str(index+1))
            for index,release in enumerate(scraped_releases):
                print(str(index+1)+") "+' ' * (longest_index-len(str(index+1)))+"title: " + release.title + ' ' * (longest_title-len(release.title)) + " | size: " + str(release.printsize) + ' ' * (longest_size-len(str(release.printsize))) + " | cached: " + '/'.join(release.cached) + ' ' * (longest_cached-len('/'.join(release.cached))) + " | seeders: " + str(release.seeders) + ' ' * (longest_seeders-len(str(release.seeders))) + " | files: " + release.file + ' ' * (longest_file-len(release.file)) + " | source: " + release.source )
#Scraper Class
class scraper: 
    #Service Class:
    class services:
        active = ['rarbg', '1337x',]
        def setup(cls,new=False):
            settings = []
            for category, allsettings in ui.settings_list:
                for setting in allsettings:
                    if setting.cls == cls:
                        settings += [setting]
            if settings == []:
                if not cls.name in scraper.services.active:
                    scraper.services.active += [cls.name]
            back = False
            if not new:
                while not back:
                    print("0) Back")
                    indices = []
                    for index, setting in enumerate(settings):
                        print(str(index+1) + ') ' + setting.name)
                        indices += [str(index+1)]
                    print()
                    if settings == []:
                        print("Nothing to edit!")
                        print()
                        time.sleep(3)
                        return
                    choice = input("Choose an action: ")
                    if choice in indices:
                        settings[int(choice)-1].setup()
                        if not cls.name in scraper.services.active:
                            scraper.services.active += [cls.name]
                        back = True
                    elif choice == '0':
                        back = True
            else:
                print()
                indices = []
                for setting in settings:
                    setting.setup()
                    if not cls.name in scraper.services.active:
                        scraper.services.active += [cls.name]      
        def __new__(cls):
            activeservices = []
            for servicename in scraper.services.active:
                for service in cls.__subclasses__():
                    if service.name == servicename:
                        activeservices += [service]
            return activeservices
    def __new__(cls,query,altquery="(.*)"):
        ui.print('done')
        ui.print('scraping sources for query "' + query + '" ...')
        ui.print('accepting title that regex match "' + altquery + '" ...',debug=ui_settings.debug)
        scrapers = scraper.services()
        scraped_releases = []
        results = [None] * len(scrapers)
        threads = []
        for index,scraper_ in enumerate(scrapers):
            t = Thread(target=scrape, args=(scraper_,query,altquery,results,index))
            threads.append(t)
            t.start()
        # wait for the threads to complete
        for t in threads:
            t.join()
        for result in results:
            if not result == [] and not result == None:
                scraped_releases += result
        for release in scraped_releases:
            release.title = ''.join([i if ord(i) < 128 else '' for i in release.title])  
        ui.print('done - found ' + str(len(scraped_releases)) + ' releases')
        return scraped_releases       
    class rarbg(services):
        name = "rarbg"
        token = 'r05xvbq6ul'
        session = requests.Session()
        def __new__(cls,query,altquery):
            scraped_releases = []
            if 'rarbg' in scraper.services.active:
                headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
                response = None
                retries = 0
                while not hasattr(response, "torrent_results") and retries < 4:
                    if regex.search(r'(tt[0-9]+)',query,regex.I):
                        url = 'https://torrentapi.org/pubapi_v2.php?mode=search&search_imdb=' + str(query) + '&ranked=0&category=52;51;50;49;48;45;44;41;17;14&token=' + scraper.rarbg.token + '&limit=100&format=json_extended&app_id=fuckshit'
                    else:
                        url = 'https://torrentapi.org/pubapi_v2.php?mode=search&search_string=' + str(query) + '&ranked=0&category=52;51;50;49;48;45;44;41;17;14&token=' + scraper.rarbg.token + '&limit=100&format=json_extended&app_id=fuckshit'
                    try:
                        response = scraper.rarbg.session.get(url, headers = headers)
                        if not response.status_code == 429:
                            response = json.loads(response.content, object_hook=lambda d: SimpleNamespace(**d))
                            if hasattr(response, "error"):
                                if 'Invalid token' in response.error:
                                    ui.print('rarbg error: ' + response.error,debug=ui_settings.debug)
                                    ui.print('fetching new token ...',debug=ui_settings.debug)
                                    url = 'https://torrentapi.org/pubapi_v2.php?get_token=get_token&app_id=fuckshit'
                                    response = scraper.rarbg.session.get(url, headers = headers)
                                    if len(response.content) > 5:
                                        response = json.loads(response.content, object_hook=lambda d: SimpleNamespace(**d))
                                        scraper.rarbg.token = response.token 
                                    else:
                                        ui.print('rarbg error: could not fetch new token',debug=ui_settings.debug)
                                elif hasattr(response, "rate_limit"):
                                    retries += -1
                        else:
                            retries += -1
                    except:
                        response = None
                        ui.print('rarbg error: (parse exception)',debug=ui_settings.debug)
                    retries += 1
                    time.sleep(1+random.randint(0, 2))
                if hasattr(response, "torrent_results"):
                    for result in response.torrent_results:
                        if regex.match(r'('+ altquery.replace('.','\.').replace("\.*",".*") + ')',result.title,regex.I):
                            release = releases('[rarbg]','torrent',result.title,[],float(result.size)/1000000000,[result.download],seeders=result.seeders)
                            scraped_releases += [release]   
            return scraped_releases 
    class x1337(services):
        name = "1337x"
        session = requests.Session()
        def __new__(cls,query,altquery):
            scraped_releases = []
            if '1337x' in scraper.services.active:
                headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
                url = 'https://1337x.to/search/' + str(query) + '/1/'
                try:
                    response = scraper.x1337.session.get(url, headers = headers)
                    soup = BeautifulSoup(response.content, 'html.parser')
                    torrentList = soup.select('a[href*="/torrent/"]')
                    sizeList = soup.select('td.coll-4')
                    seederList = soup.select('td.coll-2')
                    if torrentList:
                        for count,torrent in enumerate(torrentList):
                            title = torrent.getText().strip()
                            title = title.replace(" ",'.')
                            title = regex.sub(r'\.+',".",title)
                            if regex.match(r'('+ altquery.replace('.','\.').replace("\.*",".*") + ')',title,regex.I):
                                link = torrent['href']
                                response = scraper.x1337.session.get( 'https://1337x.to'+link, headers = headers)
                                soup = BeautifulSoup(response.content, 'html.parser')
                                download = soup.select('a[href^="magnet"]')[0]['href']
                                size = sizeList[count].contents[0]
                                seeders = seederList[count].contents[0]
                                if regex.search(r'([0-9]*?\.[0-9])(?= MB)',size,regex.I):
                                    size = regex.search(r'([0-9]*?\.[0-9])(?= MB)',size,regex.I).group()
                                    size = float(float(size) / 1000)
                                elif regex.search(r'([0-9]*?\.[0-9])(?= GB)',size,regex.I):
                                    size = regex.search(r'([0-9]*?\.[0-9])(?= GB)',size,regex.I).group()
                                    size = float(size)
                                else:
                                    size = float(size)
                                scraped_releases += [releases('[1337x]','torrent',title,[],size,[download],seeders=int(seeders))]
                except:
                    response = None
                    ui.print('1337x error: exception')
            return scraped_releases
    class jackett(services):
        base_url = "http://127.0.0.1:9117"
        api_key = ""
        name = "jackett"
        indexers = []
        categories = []
        filters = []
        session = requests.Session()
        def __new__(cls,query,altquery):
            scraped_releases = []
            if 'jackett' in scraper.services.active:
                filter = ""
                tags = ""
                for indexer in scraper.jackett.indexers:
                    if not indexer[0] == '':
                        tags += "&Tracker[]=" + indexer[0]
                for category in scraper.jackett.categories:
                    if not category[0] == '':
                        tags += "&Category[]=" + category[0]
                if not scraper.jackett.filters == []:
                    filters = []
                    for fil in scraper.jackett.filters:
                        if not fil[0] == '':
                            filters += fil
                    if not filters == []:
                        filter = (",").join(filters)
                    else:
                        filter = "all"
                else:
                    filter = "all"
                url = scraper.jackett.base_url + '/api/v2.0/indexers/' + filter + '/results?apikey=' + scraper.jackett.api_key + '&Query=' + query + tags
                try:
                    response = scraper.jackett.session.get(url,timeout=25)
                except:
                    ui.print('jackett error: jackett request timed out.')
                    return []
                if response.status_code == 200:
                    try:
                        response = json.loads(response.content, object_hook=lambda d: SimpleNamespace(**d))
                    except:
                        ui.print('jackett error: jackett didnt return any data.')
                        return []
                    for result in response.Results[:]:
                        result.Title = result.Title.replace(' ','.')
                        if regex.match(r'('+ altquery.replace('.','\.').replace("\.*",".*") + ')',result.Title,regex.I):
                            if not result.MagnetUri == None:
                                if not result.Tracker == None and not result.Size == None:
                                    scraped_releases += [releases('[jackett: '+str(result.Tracker)+']','torrent',result.Title,[],float(result.Size)/1000000000,[result.MagnetUri],seeders=result.Seeders)]
                                elif not result.Tracker == None:
                                    scraped_releases += [releases('[jackett: '+str(result.Tracker)+']','torrent',result.Title,[],1,[result.MagnetUri],seeders=result.Seeders)]
                                elif not result.Size == None:
                                    scraped_releases += [releases('[jackett: unnamed]','torrent',result.Title,[],float(result.Size)/1000000000,[result.MagnetUri],seeders=result.Seeders)]
                                response.Results.remove(result)
                        else:
                            response.Results.remove(result)
                    #Multiprocess resolving of result.Link for remaining releases
                    results = [None] * len(response.Results)
                    threads = []
                    #start thread for each remaining release
                    for index,result in enumerate(response.Results):
                        t = Thread(target=multi_init, args=(scraper.jackett.resolve,result,results,index))
                        threads.append(t)
                        t.start()
                    # wait for the threads to complete
                    for t in threads:
                        t.join()
                    for result in results:
                        if not result == [] and not result == None:
                            scraped_releases += result
            return scraped_releases
        def resolve(result):
            scraped_releases = []
            try:
                link = scraper.jackett.session.get(result.Link,allow_redirects=False,timeout=1)
                if 'Location' in link.headers:
                    if regex.search(r'(?<=btih:).*?(?=&)',str(link.headers['Location']),regex.I):
                        if not result.Tracker == None and not result.Size == None:
                            scraped_releases += [releases('[jackett: '+str(result.Tracker)+']','torrent',result.Title,[],float(result.Size)/1000000000,[link.headers['Location']],seeders=result.Seeders)]
                        elif not result.Tracker == None:
                            scraped_releases += [releases('[jackett: '+str(result.Tracker)+']','torrent',result.Title,[],1,[link.headers['Location']],seeders=result.Seeders)]
                        elif not result.Size == None:
                            scraped_releases += [releases('[jackett: unnamed]','torrent',result.Title,[],float(result.Size)/1000000000,[link.headers['Location']],seeders=result.Seeders)]
                    return scraped_releases
                elif link.headers['Content-Type'] == "application/x-bittorrent":
                    magnet = releases.torrent2magnet(link.content)
                    if not result.Tracker == None and not result.Size == None:
                        scraped_releases += [releases('[jackett: '+str(result.Tracker)+']','torrent',result.Title,[],float(result.Size)/1000000000,[magnet],seeders=result.Seeders)]
                    elif not result.Tracker == None:
                        scraped_releases += [releases('[jackett: '+str(result.Tracker)+']','torrent',result.Title,[],1,[magnet],seeders=result.Seeders)]
                    elif not result.Size == None:
                        scraped_releases += [releases('[jackett: unnamed]','torrent',result.Title,[],float(result.Size)/1000000000,[magnet],seeders=result.Seeders)]
                    return scraped_releases
            except:
                return scraped_releases
    class prowlarr(services):
        base_url = "http://127.0.0.1:9696"
        api_key = ""
        name = "prowlarr"
        session = requests.Session()
        def __new__(cls,query,altquery):
            scraped_releases = []
            if 'prowlarr' in scraper.services.active:
                url = scraper.prowlarr.base_url + '/api/v1/search?query='+query+'&type=search&limit=1000&offset=0'
                headers = {'X-Api-Key': scraper.prowlarr.api_key}
                response = scraper.prowlarr.session.get(url,headers=headers)
                if response.status_code == 200:
                    response = json.loads(response.content, object_hook=lambda d: SimpleNamespace(**d))
                    for result in response[:]:
                        result.title = result.title.replace(' ','.')
                        if regex.match(r'('+ altquery.replace('.','\.').replace("\.*",".*") + ')',result.title,regex.I) and result.protocol == 'torrent':
                            if hasattr(result,'magnetUrl'):
                                if not result.magnetUrl == None:
                                    if not result.indexer == None and not result.size == None:
                                        scraped_releases += [releases('[prowlarr: '+str(result.indexer)+']','torrent',result.title,[],float(result.size)/1000000000,[result.magnetUrl],seeders=result.seeders)]
                                    elif not result.indexer == None:
                                        scraped_releases += [releases('[prowlarr: '+str(result.indexer)+']','torrent',result.title,[],1,[result.magnetUrl],seeders=result.seeders)]
                                    elif not result.size == None:
                                        scraped_releases += [releases('[prowlarr: unnamed]','torrent',result.title,[],float(result.size)/1000000000,[result.magnetUrl],seeders=result.seeders)]
                                    response.remove(result)
                        else:
                            response.remove(result)
                    #Multiprocess resolving of result.Link for remaining releases
                    results = [None] * len(response)
                    threads = []
                    #start thread for each remaining release
                    for index,result in enumerate(response):
                        t = Thread(target=multi_init, args=(scraper.prowlarr.resolve,result,results,index))
                        threads.append(t)
                        t.start()
                    # wait for the threads to complete
                    for t in threads:
                        t.join()
                    for result in results:
                        if not result == []:
                            scraped_releases += result
            return scraped_releases
        def resolve(result):
            scraped_releases = []
            try:
                link = scraper.prowlarr.session.get(result.downloadUrl,allow_redirects=False,timeout=2)
                if 'Location' in link.headers:
                    if regex.search(r'(?<=btih:).*?(?=&)',str(link.headers['Location']),regex.I):
                        if not result.indexer == None and not result.size == None:
                            scraped_releases += [releases('[prowlarr: '+str(result.indexer)+']','torrent',result.title,[],float(result.size)/1000000000,[link.headers['Location']],seeders=result.seeders)]
                        elif not result.indexer == None:
                            scraped_releases += [releases('[prowlarr: '+str(result.indexer)+']','torrent',result.title,[],1,[link.headers['Location']],seeders=result.seeders)]
                        elif not result.size == None:
                            scraped_releases += [releases('[prowlarr: unnamed]','torrent',result.title,[],float(result.size)/1000000000,[link.headers['Location']],seeders=result.seeders)]
                    return scraped_releases
                elif link.headers['Content-Type'] == "application/x-bittorrent":
                    magnet = releases.torrent2magnet(link.content)
                    if not result.indexer == None and not result.size == None:
                        scraped_releases += [releases('[prowlarr: '+str(result.indexer)+']','torrent',result.title,[],float(result.size)/1000000000,[magnet],seeders=result.seeders)]
                    elif not result.indexer == None:
                        scraped_releases += [releases('[prowlarr: '+str(result.indexer)+']','torrent',result.title,[],1,[magnet],seeders=result.seeders)]
                    elif not result.size == None:
                        scraped_releases += [releases('[prowlarr: unnamed]','torrent',result.title,[],float(result.size)/1000000000,[magnet],seeders=result.seeders)]
                    return scraped_releases
            except:
                return scraped_releases
#Multiprocessing scrape method
def scrape(cls:scraper,query,altquery,result,index):
    result[index] = cls(query,altquery)
#Multiprocessing download method
def download(cls:content.media,library,parentReleases,result,index):
    result[index] = cls.download(library=library,parentReleases=parentReleases)
#Multiprocessing watchlist method
def multi_init(cls,obj,result,index):
    result[index] = cls(obj)
#Multiprocessing run method
def run(stop): 
    ui.cls()    
    print("Type 'exit' to return to the main menu.")
    timeout = 5
    regular_check = 1800
    timeout_counter = 0
    library = content.libraries()[0]()
    if len(library) > 0:
        #get entire plex_watchlist
        plex_watchlist = plex.watchlist()
        #get entire trakt_watchlist
        trakt_watchlist = trakt.watchlist()
        #get all overseerr request, match content to plex media type and add to monitored list
        overseerr_requests = overseerr.requests()
        overseerr_requests.sync(plex_watchlist,library)
        ui.print('checking new content ...')
        for iterator in itertools.zip_longest(plex_watchlist,trakt_watchlist):
            for element in iterator:
                if hasattr(element,'download'):
                    element.download(library=library)
        ui.print('done')
        while not stop():   
            if plex_watchlist.update() or overseerr_requests.update() or trakt_watchlist.update():
                library = content.libraries()[0]()
                overseerr_requests.sync(plex_watchlist,library)
                if len(library) == 0:
                    break
                ui.print('checking new content ...')
                for iterator in itertools.zip_longest(plex_watchlist,trakt_watchlist):
                    for element in iterator:
                        if hasattr(element,'download'):
                            element.download(library=library)
                ui.print('done')
            elif timeout_counter >= regular_check:
                #get entire plex_watchlist
                plex_watchlist = plex.watchlist()
                #get entire trakt_watchlist
                trakt_watchlist = trakt.watchlist()
                #get all overseerr request, match content to plex media type and add to monitored list
                overseerr_requests = overseerr.requests()
                overseerr_requests.sync(plex_watchlist,library)
                library = content.libraries()[0]()
                if len(library) == 0:
                    break
                timeout_counter = 0
                ui.print('checking new content ...')
                for iterator in itertools.zip_longest(plex_watchlist,trakt_watchlist):
                    for element in iterator:
                        if hasattr(element,'download'):
                            element.download(library=library)
                ui.print('done')
            else:
                timeout_counter += timeout
            time.sleep(timeout)
#Multiprocessing run class
class download_script:   
    def run():
        if ui.preflight():
            global stop
            stop = False
            t = Thread(target=run, args =(lambda : stop, ))
            t.start()
            while not stop:
                text = input("")
                if text == 'exit':
                    stop = True
                else:
                    print("Type 'exit' to return to the main menu.")
            print("Waiting for the download automation to stop ... ")
            while t.is_alive():
                time.sleep(1)
#Ui Preference Class:
class ui_settings:
    version = ['1.32',"Settings compatible update",[]]
    run_directly = "true"
    debug = "false"
#Ui Class
class ui:
    sameline = False
    class option:
        def __init__(self,name,cls,key):
            self.name = name
            self.cls = cls
            self.key = key
        def input(self):
            func = getattr(self.cls,self.key)
            func()
    class setting:
        def __init__(self,name,prompt,cls,key,required=False,entry="",test=None,help="",hidden=False,subclass=False,oauth=False,moveable=True,preflight=False,radio=False,special=False):
            self.name = name
            self.prompt = prompt
            self.cls = cls
            self.key = key
            self.required = required
            self.entry = entry
            self.test = test
            self.hidden = hidden
            self.subclass = subclass
            self.oauth = oauth
            self.help = help
            self.moveable = moveable
            self.preflight = preflight
            self.radio = radio
            self.special = special
        def input(self):
            if self.special:
                self.cls.setup(self.cls)
                return
            elif self.moveable:
                if not self.help == "":
                    print(self.help)
                    print()
                print('Current ' + self.name + ': "' + str(getattr(self.cls,self.key)) + '"')
                print()
                print('0) Back')
                print('1) Edit')
                print()
                choice = input('Choose an action: ')
            else:
                choice = '1'
            if choice == '1':
                if not isinstance(getattr(self.cls,self.key),list):
                    if self.oauth:
                        device_code, user_code = self.cls.oauth()
                        print(self.prompt + str(user_code))
                        console_input = self.cls.oauth(device_code)
                        setattr(self.cls,self.key,console_input)
                        return True
                    else:
                        console_input = input(self.prompt + '- current value "'+str(getattr(self.cls,self.key))+'": ')
                        setattr(self.cls,self.key,console_input)
                        return True
                else:
                    lists = getattr(self.cls,self.key)
                    if self.radio:
                        print()
                        print('0) Back')
                        if len(lists) > 0:
                            print('1) Change '+self.entry)
                            print('2) Edit '+self.entry)
                        else:
                            print('1) Add '+self.entry)
                        print()
                        choice = input('Choose an action: ')
                    elif self.moveable:
                        print()
                        print('0) Back')
                        print('1) Add '+self.entry)
                        if len(lists) > 0:
                            print('2) Edit '+self.entry+'s')
                        print()
                        choice = input('Choose an action: ')
                    else:
                        choice = '2'
                    if choice == '1':
                        if self.subclass:
                            back = False
                            while not back:
                                print()
                                print('0) Back')
                                services = []
                                indices = []
                                index = 0
                                for service in self.cls.__subclasses__():
                                    if not service.name in getattr(self.cls,self.key) and not '(NOT FUNCTIONAL)' in service.name:
                                        print(str(index+1)+') ' + service.name)
                                        indices += [str(index+1)]
                                        services += [service]
                                        index += 1
                                print()
                                choice = input('Choose a '+self.entry+': ')
                                if choice in indices:
                                    service = services[int(choice)-1]
                                    service.setup(service,new=True)
                                    back = True
                                elif choice == '0':
                                    back = True
                        elif self.oauth:
                            edit = []
                            lists = getattr(self.cls,self.key)
                            for prompt in self.prompt:
                                if "code" in prompt:
                                    device_code, user_code = self.cls.oauth()
                                    print(prompt + str(user_code))
                                    edit += [self.cls.oauth(device_code)]
                                else:
                                    edit += [input(prompt)]
                            lists += [edit]
                            setattr(self.cls,self.key,lists)
                        else:
                            edit = []
                            for prompt in self.prompt:
                                edit += [input(prompt)]
                            lists += [edit]
                            setattr(self.cls,self.key,lists)
                            return True
                    elif choice == '2':
                        if not self.radio:
                            print()
                            print('0) Back')
                            indices = []
                            for index,entry in enumerate(lists):
                                if self.moveable:
                                    print(str(index+1)+') Edit '+self.entry+' ' + str(index+1) + ': ' + str(entry))
                                else:
                                    print(str(index+1)+') ' + str(entry))
                                indices += [str(index+1)]
                            print()
                            index = input('Choose a '+self.entry+': ')
                        else:
                            index = '1'
                            indices = ['1',]
                        back3 = False
                        while not back3:
                            if index == '0':
                                back3 = True
                            if index in indices:
                                if self.moveable and not self.radio:
                                    print()
                                    print(self.entry.capitalize()+' '+index+': ' + str(lists[int(index)-1]))
                                    print()
                                    print('0) Back')
                                    print('1) Edit')
                                    print('2) Delete')
                                    if len(lists) > 1:
                                        print('3) Move')
                                    print()
                                    choice = input('Choose an action: ')
                                else:
                                    choice = '1'
                                back2 = False
                                while not back2:
                                    print()
                                    if choice == '0':
                                        back2 = True
                                        back3 = True
                                    if choice == '1':
                                        if self.subclass:
                                            for service in self.cls.__subclasses__():
                                                if str(lists[int(index)-1]) == service.name:
                                                    service.setup(service)
                                                    return True
                                        elif self.oauth:
                                            edit = []
                                            for prompt in self.prompt:
                                                if "code" in prompt:
                                                    device_code, user_code = self.cls.oauth()
                                                    print(prompt + str(user_code))
                                                    edit += [self.cls.oauth(device_code)]
                                                else:
                                                    edit += [input(prompt)]
                                            lists[int(index)-1] = edit
                                            setattr(self.cls,self.key,lists)
                                            return True
                                        else:
                                            edit = []
                                            for k,prompt in enumerate(self.prompt):
                                                response = input(prompt + '- current value "'+lists[int(index)-1][k]+'": ')
                                                edit += [response]
                                            lists[int(index)-1] = edit
                                            setattr(self.cls,self.key,lists)
                                            return True
                                    if choice == '2':
                                        del lists[int(index)-1]
                                        return True
                                    if choice == '3':
                                        back = False
                                        while not back:
                                            print('0) Back')
                                            for i in indices:
                                                print( i +') Position '+i)
                                            print()
                                            choice = input('Move '+self.entry+' ' + index + ' to: ')
                                            if choice == '0':
                                                back = True
                                            if choice in indices:
                                                temp = copy.deepcopy(lists[int(index)-1])
                                                del lists[int(index)-1]
                                                lists.insert(int(choice)-1,temp)
                                                setattr(self.cls,self.key,lists)
                                                return True                     
        def setup(self):
            if isinstance(getattr(self.cls,self.key),list):
                print()
                working = False
                while not working:
                    if self.subclass:
                        print(self.help)
                        print()
                        services = []
                        indices = []
                        index = 0
                        for service in self.cls.__subclasses__():
                            if not '(NOT FUNCTIONAL)' in service.name and not service.name == 'Overseerr':
                                print(str(index+1)+') ' + service.name)
                                indices += [str(index+1)]
                                services += [service]
                                index += 1
                        print()
                        choice = input('Choose a '+self.entry+': ')
                        if choice in indices:
                            service = services[int(choice)-1]
                            service.setup(service,new=True)
                            working = True
                    else:
                        edit = []
                        print(self.name + ' - current value: ' + str(getattr(self.cls,self.key)))
                        print()
                        if not self.help == '':
                            print(self.help)
                            print()
                        if self.oauth:
                            edit = []
                            lists = getattr(self.cls,self.key)
                            for prompt in self.prompt:
                                if "code" in prompt:
                                    device_code, user_code = self.cls.oauth()
                                    print(prompt + str(user_code))
                                    edit += [self.cls.oauth(device_code)]
                                else:
                                    edit += [input(prompt)]
                            lists += [edit]
                            setattr(self.cls,self.key,lists)
                        else:
                            lists = getattr(self.cls,self.key)
                            for prompt in self.prompt:
                                edit += [input(prompt)]
                            lists = [edit,]
                            setattr(self.cls,self.key,lists)
                        if self.name == 'Plex users':
                            url = 'https://metadata.provider.plex.tv/library/sections/watchlist/all?X-Plex-Token=' + plex.users[0][1]
                            response = plex.session.get(url,headers=plex.headers)
                            if response.status_code == 200:
                                working = True
                            else:
                                print()
                                print("Looks like this plex token does not work. Please enter a valid token.")
                                print()
                        else:
                            working = True
            else:
                working = False
                while not working:
                    print(self.name + ' - current value: ' + str(getattr(self.cls,self.key)))
                    print()
                    if self.oauth:
                        device_code, user_code = self.cls.oauth()
                        print(self.prompt + str(user_code))
                        console_input = self.cls.oauth(device_code)
                        setattr(self.cls,self.key,console_input)
                    else:
                        console_input = input(self.prompt)
                        setattr(self.cls,self.key,console_input)
                    if self.name == 'Real Debrid API Key':
                        url = 'https://api.real-debrid.com/rest/1.0/torrents?limit=2&auth_token=' + console_input
                        response = debrid.realdebrid.session.get(url)
                        if response.status_code == 200:
                            working = True
                        else:
                            print()
                            print("Looks like the api key does not work. Please enter a valid api key.")
                            print()
                    else:
                        working = True
        def set(self,value):
            setattr(self.cls,self.key,value)
        def get(self):
            return getattr(self.cls,self.key)
    settings_list = [
        ['Content Services',[
            setting('Content Services',[''],content.services,'active',entry="content service",subclass=True,moveable=False,required=True,preflight=True,help='Please choose at least one content service that plex_debrid should monitor for new content.'),
            setting('Plex users',['Please provide a name for this Plex user: ','Please provide the Plex token for this Plex user: '],plex,'users',entry="user",help="Please create a plex user by providing a name and a token. To find the plex token for this user, open your favorite browser, log in to this plex account and visit 'https://plex.tv/devices.xml'. Pick a 'token' from one of the listed devices.",hidden=True),
            setting('Plex auto remove','Please choose which media type/s should be removed from your watchlist after successful download ("movie","show","both" or "none"): ',plex.watchlist,'autoremove',hidden=True,help='By default, movies are removed from your watchlist after a successful download. In this setting you can choose to automatically remove shows, shows and movies or nothing.'),
            setting('Trakt users',['Please provide a name for this Trakt user: ','Please open your favorite browser, log into this Trakt user and open "https://trakt.tv/activate". Enter this code: '],trakt,'users',entry="user",oauth=True,hidden=True),
            setting('Trakt lists',[''],trakt,'lists',hidden=True),
            setting('Trakt auto remove','Please choose which media type/s should be removed from your watchlist after successful download ("movie","show","both" or "none"): ',trakt.watchlist,'autoremove',hidden=True,help='By default, movies are removed from your watchlist after a successful download. In this setting you can choose to automatically remove shows, shows and movies or nothing.'),
            setting('Overseerr users',['Please choose a user: '],overseerr,'users',entry="user",help="Please specify which users requests should be downloaded by plex_debrid.",hidden=True),
            setting('Overseerr API Key','Please specify your Overseerr API Key: ',overseerr,'api_key',hidden=True),
            setting('Overseerr Base URL','Please specify your Overseerr base URL: ',overseerr,'base_url',hidden=True),
            ]
        ],
        ['Library Service',[
            setting('Library Service',[''],content.libraries,'active',entry="library service",subclass=True,radio=True,required=True,preflight=True,help='Please choose at least one library service that plex debrid will monitor for existing content.'),
            setting('Trakt library user',[''],trakt.library,'user',hidden=True),
            setting('Plex server address','Please enter your Plex server address: ',plex.library,'url',hidden=True),
            setting('Plex "movies" library','Please enter the section number of the "movies" library, that should be refreshed after a movie download. To find the section number, go to "https://app.plex.tv", open your "movies" library and look for the "source=" parameter in the url. Please enter the section number: ',plex.library,'movies',hidden=True),
            setting('Plex "shows" library','Please enter the section number of the "shows" library, that should be refreshed after a show download. To find the section number, go to "https://app.plex.tv", open your "shows" library and look for the "source=" parameter in the url. Please enter the section number:  ',plex.library,'shows',hidden=True),
            setting('Plex library check',['Please specify a library section number that should be checked for existing content before download: '],plex.library,'check',hidden=True,entry="section",help='By default, your entire library (including plex shares) is checked for existing content before a download is started. This setting allows you limit this check to specific library sections. To find a section number, go to "https://app.plex.tv", open your the library you want to include in the check and look for the "source=" parameter in the url.'),
            ]
        ],
        ['Scraper Settings',[
            setting('Sources',[''],scraper.services,'active',entry="source",subclass=True,preflight=True),
            setting('Versions',[],releases.sort,'versions',special=True,entry="version"),
            setting('Special character renaming',['Please specify a character or string that should be replaced: ','Please specify with what character or string it should be replaced: '],releases.rename,'replaceChars',entry="rule",help='In this setting you can specify a character or a string that should be replaced by nothing, some other character or a string.'),
            setting('Rarbg API Key','The Rarbg API Key gets refreshed automatically, enter the default value: ',scraper.rarbg,'token',hidden=True),
            setting('Jackett Base URL','Please specify your Jackett base URL: ',scraper.jackett,'base_url',hidden=True),
            setting('Jackett API Key','Please specify your Jackett API Key: ',scraper.jackett,'api_key',hidden=True),
            setting('Jackett Indexers',['Please specify a Jackett indexer (Leave blank to scrape all indexers): '],scraper.jackett,'indexers',hidden=True,entry="indexer"),
            setting('Jackett Categories',['Please specify a Jackett torrent category (Leave blank to scrape all categories): '],scraper.jackett,'categories',hidden=True,entry="category"),
            setting('Jackett Filters',['Please specify a Jackett indexer filter (Leave blank to not apply filter): '],scraper.jackett,'categories',hidden=True,entry="filter"),
            setting('Prowlarr Base URL','Please specify your Prowlarr base URL: ',scraper.prowlarr,'base_url',hidden=True),
            setting('Prowlarr API Key','Please specify your Prowlarr API Key: ',scraper.prowlarr,'api_key',hidden=True),
            ]
        ],
        ['Debrid Services', [
            setting('Debrid Services',[''],debrid.services,'active',required=True,preflight=True,entry="service",subclass=True,help='Please setup at least one debrid service: '),
            setting(
                'Tracker specific Debrid Services',
                [
                    'Please specify what tracker to look for by providing a regex match group: ',
                    'Please specify what debrid service should be used for a matching tracker (enter "RD","PM","AD" or "DL"): ',
                ],
                debrid,'tracker',
                entry="rule",
            ),
            setting('Real Debrid API Key','Please enter your Real Debrid API Key: ',debrid.realdebrid,'api_key',hidden=True),
            setting('All Debrid API Key','Please enter your All Debrid API Key: ',debrid.alldebrid,'api_key',hidden=True),
            setting('Premiumize API Key','Please enter your Premiumize API Key: ',debrid.premiumize,'api_key',hidden=True),
            setting('Debrid Link API Key','Please open your favorite browser, log into your debridlink account and open "https://debrid-link.fr/device". Enter this code: ',debrid.debridlink,'api_key',hidden=True,oauth=True),
            setting('Put.io API Key','Please open your favorite browser, log into your put.io account and open "http://put.io/link". Enter this code: ',debrid.putio,'api_key',hidden=True,oauth=True),
            ]
        ],
        ['UI Settings',[
            setting('Show Menu on Startup','Please enter "true" or "false": ',ui_settings,'run_directly'),
            setting('Debug printing','Please enter "true" or "false": ',ui_settings,'debug'),
            setting('version','No snooping around! :D This is for compatability reasons.',ui_settings,'version',hidden=True),
            ]
        ],
    ]
    def cls(path=''):
        os.system('cls' if os.name=='nt' else 'clear')
        ui.logo(path=path)
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
    def print(string:str,debug="true"):
        if debug == "true":
            if string == 'done' and ui.sameline:
                print('done')
                ui.sameline = False
            elif ui.sameline and string.startswith('done'):
                print(string)
                ui.sameline = False
            elif ui.sameline and string.endswith('...'):
                print('done')
                print('[' + str(datetime.datetime.now()) + '] ' + string, end=' ')
                ui.sameline = True
            elif string.endswith('...'):
                print('[' + str(datetime.datetime.now()) + '] ' + string, end=' ')
                ui.sameline = True
            elif not string.startswith('done') and ui.sameline:
                print('done')
                print('[' + str(datetime.datetime.now()) + '] ' + string)
                ui.sameline = False
            elif not string.startswith('done'):
                print('[' + str(datetime.datetime.now()) + '] ' + string)
                ui.sameline = False
            sys.stdout.flush()
    def ignored():
        ui.cls('Options/Ignored Media/')
        if len(plex.ignored) == 0:
            library = content.libraries()[0]()
            if len(library) > 0:
                #get entire plex_watchlist
                plex_watchlist = plex.watchlist()
                #get entire trakt_watchlist
                trakt_watchlist = trakt.watchlist()
                ui.print('checking new content ...')
                for iterator in itertools.zip_longest(plex_watchlist,trakt_watchlist):
                    for element in iterator:
                        if hasattr(element,'uncollected'):
                            element.uncollected(library)
            print()
        print('0) Back')
        indices = []
        for index,element in enumerate(plex.ignored):
            print(str(index+1) + ') ' + element.query())
            indices += [str(index+1)]
        print()
        choice = input('Choose a media item that you want to remove from the ignored list: ')            
        if choice in indices:
            print("Media item: " + plex.ignored[int(choice)-1].query() + ' removed from ignored list.')
            plex.ignored[int(choice)-1].unwatch()
            time.sleep(3)
        ui.options()
    def scrape():
        ui.cls('Options/Scraper/')
        print('Press Enter to return to the main menu.')
        print()
        print("Please choose a version to scrape for: ")
        print()
        obj = releases('','','',[],0,[])
        indices = []
        for index,version in enumerate(releases.sort.versions):
            print(str(index+1) + ') ' + version[0])
            indices += [str(index+1)]
        print(str(index+2) + ') Scrape without defining a version')
        indices += [str(index+2)]
        print()
        choice = input("Choose a version: ")
        if choice in indices and not choice == str(index+2):
            obj.version = releases.sort.version(releases.sort.versions[int(choice)-1][0],releases.sort.versions[int(choice)-1][1],releases.sort.versions[int(choice)-1][2],releases.sort.versions[int(choice)-1][3])
        elif choice == str(index+2):
            obj.version = None
        else:
            return
        ui.cls('Options/Scraper/')
        print('Press Enter to return to the main menu.')
        print()
        query = input("Enter a query: ")
        if query == '':
            return
        print()
        scraped_releases = scraper(query.replace(' ','.'))
        if len(scraped_releases) > 0:
            obj.Releases = scraped_releases
            debrid.check(obj,force=True)
            scraped_releases = obj.Releases
            if not obj.version == None:
                releases.sort(scraped_releases,obj.version)
            print()
            print("0) Back")
            releases.print(scraped_releases)
            print()
            print("Type 'auto' to automatically download the first cached release. Releases were sorted by your first version definition.")
            back = False
            while not back:
                print()
                choice = input("Choose a release to download: ")
                try:
                    if choice == 'auto':
                        release = scraped_releases[0]
                        release.Releases = scraped_releases
                        if debrid.download(release,stream=True,query=query,force=True):
                            back = True
                            time.sleep(3)
                        else:
                            print()
                            print("These releases do not seem to be cached on your debrid services. Add uncached torrent?")
                            print()
                            print("0) Back")
                            print("1) Add uncached torrent")
                            print()
                            choice = input("Choose an action: ")
                            if choice == '1':
                                debrid.download(release,stream=False,query=query,force=True)
                                back = True
                                time.sleep(3)
                    elif int(choice) <= len(scraped_releases) and not int(choice) <= 0:
                        release = scraped_releases[int(choice)-1]
                        release.Releases = [release,]
                        if debrid.download(release,stream=True,query=release.title,force=True):
                            back = True
                            time.sleep(3)
                        else:
                            print()
                            print("This release does not seem to be cached on your debrid services. Add uncached torrent?")
                            print()
                            print("0) Back")
                            print("1) Add uncached torrent")
                            print()
                            choice = input("Choose an action: ")
                            if choice == '1':
                                if debrid.download(release,stream=False,query=query,force=True):
                                    back = True
                                    time.sleep(3)
                                else:
                                    print()
                                    print("There was an error adding this uncached torrent to your debrid service. Choose another release?")
                    elif choice == '0':
                        back = True
                except:
                    back = False
        else:
            print("No releases were found!")
            time.sleep(3)
    def settings():
        back = False
        while not back:
            list = ui.settings_list
            ui.cls('Options/Settings/')
            print('0) Back')
            indices = []
            for index,category in enumerate (list):
                print(str(index+1) + ') ' + category[0])
                indices += [str(index+1)]
            print()
            print('Type "discard" to go back and discard changes.')
            print()
            choice = input('Choose an action: ')
            if choice in indices:
                ui.cls('Options/Settings/'+list[int(choice)-1][0]+'/')
                settings = []
                for index,setting in enumerate(list[int(choice)-1][1]):
                    if not setting.hidden:
                        settings += [setting]
                if len(settings) > 1:
                    print('0) Back')
                    for index,setting in enumerate(settings):
                        if not setting.hidden:
                            print(str(index+1) + ') ' + setting.name)
                    print()
                    choice2 = input('Choose an action: ')
                else:
                    choice2 = '1'
                for index,setting in enumerate (list[int(choice)-1][1]):
                    if choice2 == str(index+1) and not setting.hidden:
                        ui.cls('Options/Settings/'+list[int(choice)-1][0]+'/'+setting.name)
                        setting.input()
            elif choice == '0':
                ui.save()
                back = True
            elif choice == 'discard':
                ui.load(doprint=True)
                back = True
    def options():
        list = [
            ui.option('Run',download_script,'run'),
            ui.option('Settings',ui,'settings'),
            ui.option('Ignored Media',ui,'ignored'),
            ui.option('Scraper',ui,'scrape'),
        ]
        ui.cls('Options/')
        for index,option in enumerate(list):
            print(str(index+1) + ') ' + option.name)
        print()
        print('Type exit to quit.')
        print()
        choice = input('Choose an action: ')
        if choice == 'exit':
            exit()
        for index,option in enumerate(list):
            if choice == str(index+1):
                option.input()
        ui.options()
    def setup():
        if os.path.exists('./settings.json'):
            with open('settings.json', 'r') as f:
                settings = json.loads(f.read())
            if settings['Show Menu on Startup'] == "false":
                return False
            ui.load()
            return True
        else:
            ui.cls('Initial Setup')
            input('Press Enter to continue: ')
            for category, settings in ui.settings_list:
                for setting in settings:
                    if setting.required:
                        ui.cls('Options/Settings/'+category+'/'+setting.name)
                        setting.setup()
            ui.cls('Done!')
            input('Press Enter to continue to the main menu: ')
            ui.save()
            return True
    def save():
        save_settings = {}
        for category, settings in ui.settings_list:
            for setting in settings:
                save_settings[setting.name] = setting.get()
        with open('settings.json', 'w') as f:
            json.dump(save_settings, f,indent=4)
        print('Current settings saved!')
        time.sleep(2)
    def load(doprint=False,updated=False):
        with open('settings.json', 'r') as f:
            settings = json.loads(f.read())
        if 'version' not in settings:
            ui.update(settings,ui_settings.version)
            updated = True
        elif not settings['version'][0] == ui_settings.version[0] and not ui_settings.version[2] == []:
            ui.update(settings,ui_settings.version)
            updated = True
        for category, load_settings in ui.settings_list:
            for setting in load_settings:
                if setting.name in settings and not setting.name == 'version':
                    setting.set(settings[setting.name])
        if doprint:
            print('Last settings loaded!')
            time.sleep(2)
        if updated:
            ui.save()
    def preflight():
        missing = []
        for category,settings in ui.settings_list:
            for setting in settings:
                if setting.preflight:
                    if len(setting.get()) == 0:
                        missing += [setting]
        if len(missing) > 0:
            print()
            print('Looks like your current settings didnt pass preflight checks. Please edit the following setting/s: ')
            for setting in missing:
                print(setting.name + ': Please add at least one ' + setting.entry + '.')
            print()
            input('Press Enter to return to the main menu: ')
            return False
        return True
    def run():
        if ui.setup():
            ui.options()
        else:
            ui.load()
            download_script.run()
            ui.options()
    def update(settings,version):
        ui.cls('/Update ' + version[0] + '/')
        print('There has been an update to plex_debrid, which is not compatible with your current settings:')
        print()
        print(version[1])
        print()
        print('This update will overwrite the following setting/s: ' + str(version[2]))
        print('A backup file (old.json) with your old settings will be created.')
        print()
        input('Press Enter to update your settings:')
        with open("old.json","w+") as f:
            json.dump(settings, f,indent=4)
        for category, load_settings in ui.settings_list:
            for setting in load_settings:
                for setting_name in version[2]:
                    if setting.name == setting_name:
                        settings[setting.name] = setting.get()
                    elif setting.name == 'version':
                        settings[setting.name] = setting.get()

if __name__ == "__main__":
    ui.run()
