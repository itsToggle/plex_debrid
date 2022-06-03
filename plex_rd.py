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
    import clipboard
    from collections.abc import Sequence
except Exception as e:
    print("python error: (module import exception): ")
    print(e)
    print("Make sure you have installed this python module.")
    print("You need to install 'pip' (https://pip.pypa.io/en/stable/installation/) and run the command 'pip install "+e.name+"'.")
    input("Press any key to exit")
    exit()
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
#Provider Class
class content:
    class services:
        active = ['Plex','Trakt']
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
                        if not cls.name in content.services.active:
                            content.services.active += [cls.name]
                        back = True
                    elif choice == '0':
                        back = True
            else:
                print()
                indices = []
                for setting in settings:
                    setting.input()
                    if not cls.name in content.services.active:
                        content.services.active += [cls.name]      
        def __new__(cls):
            activeservices = []
            for servicename in content.services.active:
                for service in cls.__subclasses__():
                    if service.name == servicename:
                        activeservices += [service]
            return activeservices
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
    def get(url):
        try:
            response = plex.session.get(url,headers=plex.headers)
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
    class watchlist(watchlist):
        def __init__(self) -> None:
            ui.print('updating entire plex watchlist ...')
            self.data = []
            try:
                for user in plex.users:
                    url = 'https://metadata.provider.plex.tv/library/sections/watchlist/all?X-Plex-Token=' + user[1]
                    response = plex.get(url)
                    if hasattr(response,'MediaContainer'):
                        if hasattr(response.MediaContainer,'Metadata'):
                            for entry in response.MediaContainer.Metadata:
                                entry.user = user
                                if not entry in self.data:
                                    if entry.type == 'show':
                                        self.data += [plex.show(entry)]
                                    if entry.type == 'movie':
                                        self.data += [plex.movie(entry)]
            except Exception as e:
                ui.print('done') 
                ui.print("plex error: (watchlist exception): " + str(e),debug=ui_settings.debug)
                ui.print('plex error: could not reach plex')
            ui.print('done')        
        def remove(self,item):
            ui.print('item: "' + item.title + '" removed from '+ item.user[0] +'`s plex watchlist')
            url = 'https://metadata.provider.plex.tv/actions/removeFromWatchlist?ratingKey=' + item.ratingKey + '&X-Plex-Token=' + item.user[1]
            response = plex.session.put(url,data={'ratingKey':item.ratingKey})
            if not self == []:
                self.data.remove(item)
        def add(self,item,user):
            ui.print('item: "' + item.title + '" added to '+ user[0] +'`s plex watchlist')
            url = 'https://metadata.provider.plex.tv/actions/addToWatchlist?ratingKey=' + item.ratingKey + '&X-Plex-Token=' + user[1]
            response = plex.session.put(url,data={'ratingKey':item.ratingKey})
            if item.type == 'show':
                self.data.append(plex.show(item.ratingKey))
            elif item.type == 'movie':
                self.data.append(plex.movie(item.ratingKey))
        def update(self):
            ui.print("updating plex watchlist ...",debug=ui_settings.debug)
            update = False
            try:
                for user in plex.users:
                    url = 'https://metadata.provider.plex.tv/library/sections/watchlist/all?X-Plex-Token=' + user[1]
                    response = plex.get(url)
                    if hasattr(response,'MediaContainer'):
                        if hasattr(response.MediaContainer,'Metadata'):
                            for entry in response.MediaContainer.Metadata:
                                entry.user = user
                                if not entry in self.data:
                                    update = True
                                    if entry.type == 'show':
                                        self.data += [plex.show(entry)]
                                    if entry.type == 'movie':
                                        self.data += [plex.movie(entry)]
            except Exception as e:
                ui.print('done') 
                ui.print("plex error: (watchlist exception): " + str(e),debug=ui_settings.debug)
                ui.print('plex error: could not reach plex')
            ui.print('done') 
            return update       
    class media:
        def __init__(self,other):
            self.__dict__.update(other.__dict__)
        def __eq__(self, other) -> bool:
            if not self.type == other.type:
                return False
            if self.type == 'movie' or self.type == 'show':
                return self.guid == other.guid
            elif self.type == 'season':
                return self.parentGuid == other.parentGuid and self.index == other.index
            elif self.type == 'episode':
                return self.grandparentGuid == other.grandparentGuid and self.parentIndex == other.parentIndex and self.index == other.index
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
        def released(self):
            released = datetime.datetime.today() - datetime.datetime.strptime(self.originallyAvailableAt,'%Y-%m-%d')
            if self.type == 'movie':
                if released.days >= 0 and released.days <= 60:
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
                return released.days > 0
        def available(self):
            if len(trakt.users) > 0:
                for guid in self.Guid:
                    service,guid = guid.id.split('://')
                    trakt_match = trakt.match(guid,service,self.type)
                    if not trakt_match == None:
                        break
                if not trakt_match == None:
                    if self.type == 'movie':
                        return trakt.media.available(trakt_match)
                    elif self.type == 'episode':
                        trakt_match.next_season = self.parentIndex
                        trakt_match.next_episode = self.index
                        return trakt.media.available(trakt_match)
            url = 'https://metadata.provider.plex.tv/library/metadata/'+self.ratingKey+'/availabilities?X-Plex-Token='+plex.users[0][1]
            response = plex.get(url)
            if not response == None:
                if hasattr(response,'MediaContainer'):
                    if response.MediaContainer.size > 0:
                        return True
            return False
        def watch(self):
            ui.print('ignoring item: ' + self.query())
            url = 'https://metadata.provider.plex.tv/actions/scrobble?identifier=tv.plex.provider.metadata&key='+self.ratingKey+'&X-Plex-Token='+ plex.users[0][1]
            plex.get(url)
            if not self in plex.ignored:
                plex.ignored += [self]
        def unwatch(self):
            url = 'https://metadata.provider.plex.tv/actions/unscrobble?identifier=tv.plex.provider.metadata&key='+self.ratingKey+'&X-Plex-Token='+ plex.users[0][1]
            plex.get(url)
            plex.ignored.remove(self)
        def watched(self):
            if self.type == 'movie' or self.type == 'episode':
                if self.viewCount > 0:
                    if not self in plex.ignored:
                        plex.ignored += [self]
                    return True
            else:
                if self.viewedLeafCount == self.leafCount:
                    if not self in plex.ignored:
                        plex.ignored += [self]
                    return True
            return False
        def collected(self,list):
            if self.type == 'show' or self.type == 'season':
                match = next((x for x in list if x == self),None)
                if not hasattr(match,'leafCount'):
                    return False
                if match.leafCount == self.leafCount:
                    return True
                return False
            else:
                if self in list:
                    return True
                return False            
        def uncollected(self,list):
            if self.type == 'movie':
                if not self.collected(list):
                    return [self]
            elif self.type == 'show':
                if self.collected(list):
                    return []
                Seasons = copy.deepcopy(self.Seasons)
                for season in Seasons[:]:
                    if not season.collected(list) and not season.watched() and season.released():
                        for episode in season.Episodes[:]:
                            if episode.collected(list) or episode.watched() or not episode.released():
                                season.Episodes.remove(episode)
                    else:
                        Seasons.remove(season)
                    if len(season.Episodes) == 0:
                        Seasons.remove(season)
                return Seasons
            return []
        def download(self,retries=1,library=[],parentReleases=[]):
            i = 0
            refresh = False
            self.Releases = []
            if self.type == 'movie':
                if self.released() and not self.watched():
                    if len(self.uncollected(library)) > 0:
                        tic = time.perf_counter()
                        while len(self.Releases) == 0 and i <= retries:
                            self.Releases += scraper(self.query())
                            i += 1
                        if self.debrid_download():
                            refresh = True
                            plex.watchlist.remove([],self)
                            toc = time.perf_counter()
                            ui.print('took ' + str(round(toc-tic,2)) + 's')
                        else:
                            self.watch()
            elif self.type == 'show':
                if self.released() and not self.watched():
                    Seasons = self.uncollected(library)
                    if len(Seasons) > 0:
                        tic = time.perf_counter()
                        if len(Seasons) > 1:
                            self.Releases += scraper(self.query())
                        results = [None] * len(Seasons)
                        threads = []
                        #start thread for each season
                        for index,Season in enumerate(Seasons):
                            t = Thread(target=download, args=(Season,library,self.Releases,results,index))
                            threads.append(t)
                            t.start()
                        # wait for the threads to complete
                        for t in threads:
                            t.join()
                        for result in results:
                            if result:
                                refresh = True
                        toc = time.perf_counter()
                        ui.print('took ' + str(round(toc-tic,2)) + 's')
            elif self.type == 'season':
                altquery = self.query()
                if regex.search(r'(S[0-9]+)',altquery):
                    altquery = regex.split(r'(S[0-9]+)',altquery) 
                    altquery = altquery[0] + '[0-9]*.*' + altquery[1] + altquery[2]
                for release in parentReleases:
                    if regex.match(r'('+altquery+')',release.title,regex.I):
                        self.Releases += [release]
                for episode in self.Episodes:
                    if not len(self.Episodes) <= self.leafCount/2:
                        if self.debrid_download():
                            return True
                        else:
                            self.Releases = []
                        while len(self.Releases) == 0 and i <= retries:
                            self.Releases += scraper(self.query())
                            i += 1
                    if not self.debrid_download():
                        self.Releases += scraper(self.query()[:-1])
                        for episode in self.Episodes:
                            if episode.download(library=library,parentReleases=self.Releases):
                                refresh = True
                            else:
                                episode.watch()
                        if refresh:
                            return True
                    else:
                        return True
            elif self.type == 'episode':
                while len(self.Releases) == 0 and i <= retries:
                    altquery = self.query()
                    if regex.search(r'(S[0-9]+)',altquery):
                        altquery = regex.split(r'(S[0-9]+)',altquery) 
                        altquery = altquery[0] + '[0-9]*.*' + altquery[1] + altquery[2]
                    for release in parentReleases:
                        if regex.match(r'('+altquery+')',release.title,regex.I):
                            self.Releases += [release]
                    if self.debrid_download():
                        return True
                    else:
                        self.Releases = scraper(self.query())
                    i += 1
                return self.debrid_download()
            if refresh:
                if self.type == 'movie':
                    plex.library.refresh(plex.library.movies)
                elif self.type == 'show':
                    plex.library.refresh(plex.library.shows)
                return True
        def debrid_download(self):
            if not debrid.download(self,stream=True):
                if not debrid.download(self,stream=False):
                    return False
            return True             
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
    class season(media):
        def __init__(self,other):
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
                else: 
                    time.sleep(1)       
    class episode(media):
        def __init__(self,other):
            self.__dict__.update(other.__dict__)
    class show(media):
        def __init__(self, ratingKey):
            if not isinstance(ratingKey,str):
                self.__dict__.update(ratingKey.__dict__)
                ratingKey = ratingKey.ratingKey
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
    class movie(media):
        def __init__(self, ratingKey):
            if not isinstance(ratingKey,str):
                self.__dict__.update(ratingKey.__dict__)
                ratingKey = ratingKey.ratingKey
            elif ratingKey.startswith('plex://'):
                ratingKey = ratingKey.split('/')[-1]
            url = 'https://metadata.provider.plex.tv/library/metadata/'+ratingKey+'?includeUserState=1&X-Plex-Token='+plex.users[0][1]
            response = plex.get(url)
            self.__dict__.update(response.MediaContainer.Metadata[0].__dict__)            
    class library:
        url = 'http://localhost:32400'
        movies = '1'
        shows = '2'
        def refresh(section):
            ui.print('refreshing library section '+section+' ...')
            url = plex.library.url + '/library/sections/' + section + '/refresh?X-Plex-Token=' + plex.users[0][1]
            plex.session.get(url)
            ui.print('done')
        def __new__(self):
            url = plex.library.url + '/library/all?X-Plex-Token='+ plex.users[0][1]
            list = []
            response = plex.get(url)
            if hasattr(response,'MediaContainer'):
                if hasattr(response.MediaContainer,'Metadata'):
                    for element in response.MediaContainer.Metadata:
                        list += [plex.media(element)]
            else:
                ui.print("plex error: couldnt reach local plex server at server address: " + plex.library.url + " - or your library really is empty.")    
                ui.print("to prevent unwanted behaviour, no further downloads will be started." + plex.library.url) 
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
        if type == 'movie':
            agent = 'tv.plex.agents.movie'
        elif type == 'show':
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
    sync_with_plex = "false"
    users = []
    current_token = ""
    session = requests.Session()
    def get(url): 
        try :
            response = trakt.session.get(url, headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36', 'Content-type' : "application/json", "trakt-api-key" : trakt.client_id, "trakt-api-version" : "2", "Authorization" : "Bearer " + trakt.current_token})
            header = response.headers
            response = json.loads(response.content, object_hook=lambda d: SimpleNamespace(**d))
        except :
            response = None
            header = None
        return response, header
    def post(url, data):
        try :
            response = trakt.session.post(url, headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36', 'Content-type' : "application/json", "trakt-api-key" : trakt.client_id, "trakt-api-version" : "2", "Authorization" : "Bearer " + trakt.current_token}, data = data)
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
    class watchlist(watchlist):
        def __init__(self):
            self.data = []
            for user in trakt.users:
                trakt.current_token = user[1]
                watchlist_shows, header = trakt.get('https://api.trakt.tv/users/me/watchlist/shows')
                watchlist_movies, header = trakt.get('https://api.trakt.tv/users/me/watchlist/movies')
                for element in watchlist_shows:
                    if not element.show in self.data:
                        element.show.type = 'show'
                        element.show.user = user
                        self.data.append(element.show)
                for element in watchlist_movies:
                    if not element.movie in self.data:
                        element.movie.type = 'movie'
                        element.movie.user = user
                        self.data.append(element.movie)
        def sync(self,other:plex.watchlist,library):
            add = []
            for element in self.data:
                try:
                    result = plex.match(element.ids.imdb,element.type,library=library)
                    result[0].trakt = element
                except:
                    result = []
                if not result == []:
                    add += result
            for element in add:
                if not element in other:
                    other.add(element,plex.users[0])
                if element.type == 'movie':
                    self.remove(element.trakt)
        def remove(self,element):
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
                ui.print('item: "' + element.title + '" removed from '+user[0]+'`s trakt watchlist')
                shows += [element]
            elif element.type == 'movie':
                for ids in element.ids.__dict__.copy():
                    value = getattr(element.ids,ids)
                    if not value:
                        delattr(element.ids,ids)
                for attribute in element.__dict__.copy():
                    if not (attribute == 'ids' or attribute == 'title' or attribute == 'year'):
                        delattr(element,attribute)
                ui.print('item: "' + element.title + '" removed from '+user[0]+'`s trakt watchlist')
                movies += [element]
            data = {'movies':movies,'shows':shows}
            trakt.current_token = user[1]
            trakt.post('https://api.trakt.tv/sync/watchlist/remove',json.dumps(data, default=lambda o: o.__dict__))
    class media:
        def available(self):
            trakt.current_token = trakt.users[0][1]
            if self.type == 'show':
                #Determine air-date of next episode
                next_episode, header = trakt.get('https://api.trakt.tv/shows/' + str(self.ids.trakt) + '/seasons/' + str(self.next_season) + '/episodes/' + str(self.next_episode) + '?extended=full')
                #If next episode air-date and delay have passed
                return datetime.datetime.utcnow() > datetime.datetime.strptime(next_episode.first_aired,'%Y-%m-%dT%H:%M:%S.000Z')
            elif self.type == 'movie':
                release_date = None
                releases, header = trakt.get('https://api.trakt.tv/movies/'+ str(self.ids.trakt) +'/releases/')
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
                trakt_lists, header = trakt.get('https://api.trakt.tv/movies/'+ str(self.ids.trakt) +'/lists/personal/popular')
                match = False
                for trakt_list in trakt_lists:
                    if regex.search(r'(latest|new).*?(releases)',trakt_list.name,regex.I):
                        match = True
                #if release_date and delay have passed or the movie was released early
                return datetime.datetime.utcnow() > datetime.datetime.strptime(release_date,'%Y-%m-%d') or match
    def search(query,type):
        trakt.current_token = trakt.users[0][1]
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
        trakt.current_token = trakt.users[0][1]
        if service == 'imdb':
            response, header = trakt.get('https://api.trakt.tv/search/imdb/' + str(query) + '?type=' + type + '&extended=full')
        elif service == 'tmdb':
            response, header = trakt.get('https://api.trakt.tv/search/tmdb/' + str(query) + '?type=' + type + '&extended=full')
        elif service == 'tvdb':
            response, header = trakt.get('https://api.trakt.tv/search/tvdb/' + str(query) + '?type=' + type + '&extended=full')
        try:
            if type == 'movie':
                response[0].movie.type = 'movie'
                return response[0].movie
            else:
                response[0].show.type = 'show'
                return response[0].show
        except:
            return None
#Debrid Class 
class debrid:
    #Service Class:
    class services:
        active = ['Real Debrid']
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
    def download(element:plex.media,stream=True,query='',force=False):
        scraped_releases = copy.deepcopy(element.Releases)
        for release in scraped_releases:
            element.Releases = [release,]
            for service in debrid.services():
                if service.download(element,stream=stream,query=query,force=force):
                    return True
        return False
    #RealDebrid class
    class realdebrid(services):
        #(required) Name of the Debrid service
        name = "Real Debrid"
        #(required) Authentification of the Debrid service, can be oauth aswell. Create a setting for the required variables in the ui.settings_list. For an oauth example check the trakt authentification.
        api_key = ""
        #(required) Method to determine if the service has been setup (for compatability reasons)
        def active(self):
            if not self.api_key == "":
                return True
            return False
        #Define Variables
        session = requests.Session()
        #Error Log
        def logerror(response):
            if not response.status_code == 200:
                ui.print("realdebrid error: " + str(response.content),debug=ui_settings.debug)
            if response.status_code == 401:
                ui.print("realdebrid error: (401 unauthorized): realdebrid api key does not seem to work. check your realdebrid settings.")
        #Get Function
        def get(url): 
            headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36', 'authorization' : 'Bearer ' + debrid.realdebrid.api_key}
            try :
                response = debrid.realdebrid.session.get(url, headers = headers)
                debrid.realdebrid.logerror(response)
                response = json.loads(response.content, object_hook=lambda d: SimpleNamespace(**d))
            except Exception as e:
                ui.print("realdebrid error: (json exception): " + str(e),debug=ui_settings.debug)
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
                ui.print("realdebrid error: (json exception): " + str(e),debug=ui_settings.debug)
                response = None
            return response
        #Delete Function
        def delete(url):
            headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36', 'authorization' : 'Bearer ' + debrid.realdebrid.api_key}
            try :
                requests.delete(url, headers = headers)
                #time.sleep(1)
            except Exception as e:
                ui.print("realdebrid error: (delete exception): " + str(e),debug=ui_settings.debug)
                None
            return None
        #Object classes
        class file:
            def __init__(self,id,name,size,wanted_list,unwanted_list):
                self.id = id
                self.name = name
                self.size = size
                wanted = False
                for key in wanted_list:
                    if regex.search(r'('+key+')',self.name,regex.I):
                        wanted = True
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
                self.wanted = 0
                self.unwanted = 0
                for file in self.files:
                    if file.wanted:
                        self.wanted += 1
                    if file.unwanted:
                        self.unwanted += 1
        #(required) Download Function. 
        def download(element:plex.media,stream=True,query='',force=False):
            cached = element.Releases
            if query == '':
                query = element.query()
            if regex.search(r'(S[0-9][0-9])',query):
                query = regex.split(r'(S[0-9]+)',query) 
                query = query[0] + '[0-9]*.*' + query[1] + query[2]
            unwanted = ['sample']
            wanted = [query]
            if not isinstance(element,releases):
                wanted = element.files()
            for release in cached[:]:
                #if release matches query
                if regex.match(r'('+ query.replace('.','\.') + ')',release.title,regex.I) or force:
                    if stream:
                        release.size = 0
                        files = []
                        subtitles = []
                        if regex.search(r'(?<=btih:).*?(?=&)',str(release.download[0]),regex.I):
                            hashstring = regex.findall(r'(?<=btih:).*?(?=&)',str(release.download[0]),regex.I)[0]
                            #get cached file ids
                            response = debrid.realdebrid.get('https://api.real-debrid.com/rest/1.0/torrents/instantAvailability/' + hashstring)
                            if hasattr(response, hashstring.lower()):
                                if hasattr(getattr(response, hashstring.lower()),'rd'):
                                    for cashed_version in getattr(response, hashstring.lower()).rd:
                                        version_files = []
                                        for file in cashed_version.__dict__:
                                            debrid_file = debrid.realdebrid.file(file,getattr(cashed_version,file).filename,getattr(cashed_version,file).filesize,wanted,unwanted)
                                            version_files.append(debrid_file)
                                        files += [debrid.realdebrid.version(version_files),]
                                    #select cached version that has the most wanted, least unwanted files and least files overall
                                    files.sort(key=lambda x: len(x.files), reverse=False)
                                    files.sort(key=lambda x: x.wanted, reverse=True)
                                    files.sort(key=lambda x: x.unwanted, reverse=False)
                                    #check if there are cached files available
                                    if len(files) > 0:
                                        for version in files:
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
                                                    ui.print('adding cached release: ' + release.title)
                                                    return True
                            ui.print('done')
                            return False
                        else:
                            if len(release.download) > 0:
                                for link in release.download:
                                    try:
                                        response = debrid.realdebrid.post('https://api.real-debrid.com/rest/1.0/unrestrict/link', {'link' : link})
                                    except:
                                        break
                                ui.print('adding cached release: ' + release.title)
                                return True
                    else:
                        try:
                            response = debrid.realdebrid.post('https://api.real-debrid.com/rest/1.0/torrents/addMagnet',{'magnet':release.download[0]})
                            time.sleep(0.1)
                            debrid.realdebrid.post('https://api.real-debrid.com/rest/1.0/torrents/selectFiles/' + str(response.id), {'files':'all'})
                            ui.print('adding uncached release: '+ release.title)
                            return True
                        except:
                            continue
            return False
    #AllDebrid class
    class alldebrid(services):
        #(required) Name of the Debrid service
        name = "All Debrid (NOT FUNCTIONAL)"
        #(required) Authentification of the Debrid service, can be oauth aswell. Create a setting for the required variables in the ui.settings_list. For an oauth example check the trakt authentification.
        api_key = ""
        #(required) Method to determine if the service has been setup (for compatability reasons)
        def active(self):
            if not self.api_key == "":
                return True
            return False
        #Define Variables
        session = requests.Session()
        #Error Log
        def logerror(response):
            if not response.status_code == 200:
                ui.print("alldebrid error: " + str(response.content),debug=ui_settings.debug)
            if response.status_code == 401:
                ui.print("alldebrid error: (401 unauthorized): alldebrid api key does not seem to work. check your alldebrid settings.")
        #Get Function
        def get(url): 
            headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36', 'authorization' : 'Bearer ' + debrid.alldebrid.api_key}
            try :
                response = debrid.alldebrid.session.get(url, headers = headers)
                debrid.alldebrid.logerror(response)
                response = json.loads(response.content, object_hook=lambda d: SimpleNamespace(**d))
            except Exception as e:
                ui.print("alldebrid error: (json exception): " + str(e),debug=ui_settings.debug)
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
                ui.print("alldebrid error: (json exception): " + str(e),debug=ui_settings.debug)
                response = None
            return response
        #(required) Download Function. 
        def download(element:plex.media,stream=True,query='',force=False):
            cached = element.Releases
            if query == '':
                query = element.query()
            if regex.search(r'(S[0-9][0-9])',query):
                query = regex.split(r'(S[0-9]+)',query) 
                query = query[0] + '[0-9]*.*' + query[1] + query[2]
            for release in cached[:]:
                #if release matches query
                if regex.match(r'('+ query.replace('.','\.') + ')',release.title,regex.I) or force:
                    if stream:
                        #Cached Download Method for AllDebrid
                        #...
                        ui.print('adding cached release: ' + release.title)
                        return True
                    else:
                        #Uncached Download Method for AllDebrid
                        #...
                        ui.print('adding uncached release: '+ release.title)
                        return True
            return False  
    #Premiumize class
    class premiumize(services):
        #(required) Name of the Debrid service
        name = "Premiumize (NOT FUNCTIONAL)"
        #(required) Authentification of the Debrid service, can be oauth aswell. Create a setting for the required variables in the ui.settings_list. For an oauth example check the trakt authentification.
        api_key = ""
        #(required) Method to determine if the service has been setup (for compatability reasons)
        def active(self):
            if not self.api_key == "":
                return True
            return False
        #Define Variables
        session = requests.Session()
        #Error Log
        def logerror(response):
            if not response.status_code == 200:
                ui.print("premiumize error: " + str(response.content),debug=ui_settings.debug)
            if response.status_code == 401:
                ui.print("premiumize error: (401 unauthorized): premiumize api key does not seem to work. check your premiumize settings.")
        #Get Function
        def get(url): 
            headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36', 'authorization' : 'Bearer ' + debrid.premiumize.api_key}
            try :
                response = debrid.premiumize.session.get(url, headers = headers)
                debrid.premiumize.logerror(response)
                response = json.loads(response.content, object_hook=lambda d: SimpleNamespace(**d))
            except Exception as e:
                ui.print("premiumize error: (json exception): " + str(e),debug=ui_settings.debug)
                response = None
            return response
        #Post Function
        def post(url, data):
            headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36', 'authorization' : 'Bearer ' + debrid.premiumize.api_key}
            try :
                response = debrid.premiumize.session.post(url, headers = headers, data = data)
                debrid.premiumize.logerror(response)
                response = json.loads(response.content, object_hook=lambda d: SimpleNamespace(**d))
            except Exception as e:
                ui.print("premiumize error: (json exception): " + str(e),debug=ui_settings.debug)
                response = None
            return response
        #(required) Download Function. 
        def download(element:plex.media,stream=True,query='',force=False):
            cached = element.Releases
            if query == '':
                query = element.query()
            if regex.search(r'(S[0-9][0-9])',query):
                query = regex.split(r'(S[0-9]+)',query) 
                query = query[0] + '[0-9]*.*' + query[1] + query[2]
            for release in cached[:]:
                #if release matches query
                if regex.match(r'('+ query.replace('.','\.') + ')',release.title,regex.I) or force:
                    if stream:
                        #Cached Download Method for premiumize
                        #...
                        ui.print('adding cached release: ' + release.title)
                        return True
                    else:
                        #Uncached Download Method for premiumize
                        #...
                        ui.print('adding uncached release: '+ release.title)
                        return True
            return False      
    #DebridLink class
    class debridlink(services):
        #(required) Name of the Debrid service
        name = "Debrid Link (NOT FUNCTIONAL)"
        #(required) Authentification of the Debrid service, can be oauth aswell. Create a setting for the required variables in the ui.settings_list. For an oauth example check the trakt authentification.
        api_key = ""
        #(required) Method to determine if the service has been setup (for compatability reasons)
        def active(self):
            if not self.api_key == "":
                return True
            return False
        #Define Variables
        session = requests.Session()
        #Error Log
        def logerror(response):
            if not response.status_code == 200:
                ui.print("debridlink error: " + str(response.content),debug=ui_settings.debug)
            if response.status_code == 401:
                ui.print("debridlink error: (401 unauthorized): debridlink api key does not seem to work. check your debridlink settings.")
        #Get Function
        def get(url): 
            headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36', 'authorization' : 'Bearer ' + debrid.debridlink.api_key}
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
            headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36', 'authorization' : 'Bearer ' + debrid.debridlink.api_key}
            try :
                response = debrid.debridlink.session.post(url, headers = headers, data = data)
                debrid.debridlink.logerror(response)
                response = json.loads(response.content, object_hook=lambda d: SimpleNamespace(**d))
            except Exception as e:
                ui.print("debridlink error: (json exception): " + str(e),debug=ui_settings.debug)
                response = None
            return response
        #(required) Download Function. 
        def download(element:plex.media,stream=True,query='',force=False):
            cached = element.Releases
            if query == '':
                query = element.query()
            if regex.search(r'(S[0-9][0-9])',query):
                query = regex.split(r'(S[0-9]+)',query) 
                query = query[0] + '[0-9]*.*' + query[1] + query[2]
            for release in cached[:]:
                #if release matches query
                if regex.match(r'('+ query.replace('.','\.') + ')',release.title,regex.I) or force:
                    if stream:
                        #Cached Download Method for debridlink
                        #...
                        ui.print('adding cached release: ' + release.title)
                        return True
                    else:
                        #Uncached Download Method for debridlink
                        #...
                        ui.print('adding uncached release: '+ release.title)
                        return True
            return False  
#Release Class
class releases:
    #Define release attributes
    def __init__(self, source, type, title, files, size, download):
        self.source     = source
        self.type       = type
        self.title      = title
        self.files      = files
        self.size       = size
        self.download   = download
    #Define when releases are Equal 
    def __eq__(self, other):
        return self.title == other.title
    #Sort Method
    class sort:
        ranking= [
            [
                "(1080|720|480)(?=p)",
                "title",
                "number",
                "1"
            ],
            [
                "(EXTENDED|REMASTERED)",
                "title",
                "text",
                "1"
            ],
            [
                "(h.?265|x.?265)",
                "title",
                "text",
                "1"
            ],
            [
                "(.*)",
                "size",
                "number",
                "0"
            ]
        ]
        def __new__(self,scraped_releases:list):
            try:
                for release in scraped_releases:
                    release.rank = []
                    for group,attribute,type,descending in releases.sort.ranking:
                        search = regex.search(group,str(getattr(release,attribute)),regex.I)
                        if search:
                            if type == 'text':
                                for rank,match in enumerate(search.groups()):
                                    if match:
                                        release.rank += [{attribute+': '+group:len(search.groups())-rank}]
                            if type == 'number':
                                release.rank += [{attribute+': '+group:int(float(search.group()))}]
                        else:
                            release.rank += [{attribute+': '+group:0}]
                index = len(releases.sort.ranking)-1
                for group,attribute,type,descending in reversed(releases.sort.ranking):
                    scraped_releases.sort(key=lambda s: s.rank[index][attribute+': '+group], reverse=int(descending))
                    index += -1
            except Exception as e:
                ui.print("sorting error: (sorting exception): something seems wrong with your sorting rules. Aborted sorting. For details enable debug printing.")
                ui.print("sorting error: (sorting exception): " + str(e),debug=ui_settings.debug)
            return scraped_releases
    #Rename Method
    def rename(string):
        deleteChars = ['.',':','(',')','`','´',',','!','?',' - ',"'","\u200b"]
        dotChars = [' ']#,'/']
        for specialChar in deleteChars:
            string = string.replace(specialChar, '')
        for specialChar in dotChars:
            string = string.replace(specialChar, '.')
        string.replace('&','and').replace('ü','ue').replace('ä','ae').replace('ö','oe').replace('ß','ss').replace('é','e').replace('è','e')
        string = regex.sub(r'\.+',".",string)
        return string    
    #Print Method
    def print(scraped_releases):
        longest_title = 0
        longest_size = 0
        longest_index = 0
        for index,release in enumerate(scraped_releases):
            if len(release.title) > longest_title:
                longest_title = len(release.title)
            if len(str(release.size)) > longest_size:
                longest_size = len(str(release.size))
            if len(str(index+1)) > longest_index:
                longest_index = len(str(index+1))
        for index,release in enumerate(scraped_releases):
            print(str(index+1)+") "+' ' * (longest_index-len(str(index+1)))+"title: " + release.title + ' ' * (longest_title-len(release.title)) + " | size: " + str(release.size) + ' ' * (longest_size-len(str(release.size)))  + " | source: " + release.source)
#Scraper Class
class scraper: 
    #Service Class:
    class services:
        active = ['rarbg', '1337x']
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
    def __new__(cls,query):
        ui.print('done')
        ui.print('scraping sources for query "' + query + '" ...')
        scrapers = scraper.services()
        scraped_releases = []
        results = [[],[],]
        threads = []
        for index,scraper_ in enumerate(scrapers):
            t = Thread(target=scrape, args=(scraper_,query,results,index))
            threads.append(t)
            t.start()
        # wait for the threads to complete
        for t in threads:
            t.join()
        for result in results:
            scraped_releases += result
        releases.sort(scraped_releases)
        ui.print('done - found ' + str(len(scraped_releases)) + ' releases')
        return scraped_releases       
    class rarbg(services):
        name = "rarbg"
        token = 'r05xvbq6ul'
        session = requests.Session()
        def __new__(cls,query):
            scraped_releases = []
            if 'rarbg' in scraper.services.active:
                altquery = copy.deepcopy(query)
                if regex.search(r'(S[0-9]+)',altquery):
                    altquery = regex.split(r'(S[0-9]+)',altquery) 
                    altquery = altquery[0] + '[0-9]*.*' + altquery[1] + altquery[2]
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
                                    ui.print('rarbg error: ' + response.error)
                                    ui.print('fetching new token ...')
                                    url = 'https://torrentapi.org/pubapi_v2.php?get_token=get_token&app_id=fuckshit'
                                    response = scraper.rarbg.session.get(url, headers = headers)
                                    if len(response.content) > 5:
                                        response = json.loads(response.content, object_hook=lambda d: SimpleNamespace(**d))
                                        scraper.rarbg.token = response.token 
                                    else:
                                        ui.print('rarbg error: could not fetch new token')
                                elif hasattr(response, "rate_limit"):
                                    retries += -1
                        else:
                            retries += -1
                    except:
                        response = None
                        ui.print('rarbg error: (parse exception)')
                    retries += 1
                    time.sleep(1+random.randint(0, 2))
                if hasattr(response, "torrent_results"):
                    for result in response.torrent_results:
                        if regex.match(r'('+ altquery.replace('.','\.') + ')',result.title,regex.I):
                            release = releases('[rarbg]','torrent',result.title,[],float(result.size)/1000000000,[result.download])
                            scraped_releases += [release]   
            return scraped_releases 
    class x1337(services):
        name = "1337x"
        session = requests.Session()
        def __new__(cls,query):
            scraped_releases = []
            if '1337x' in scraper.services.active:
                altquery = copy.deepcopy(query)
                if regex.search(r'(S[0-9]+)',altquery):
                    altquery = regex.split(r'(S[0-9]+)',altquery) 
                    altquery = altquery[0] + '[0-9]*.*' + altquery[1] + altquery[2]
                headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
                url = 'https://1337x.to/search/' + str(query) + '/1/'
                try:
                    response = scraper.x1337.session.get(url, headers = headers)
                    soup = BeautifulSoup(response.content, 'html.parser')
                    torrentList = soup.select('a[href*="/torrent/"]')
                    sizeList = soup.select('td.coll-4')
                    if torrentList:
                        for count,torrent in enumerate(torrentList):
                            title = torrent.getText().strip()
                            title = title.replace(" ",'.')
                            title = regex.sub(r'\.+',".",title)
                            if regex.match(r'('+ altquery.replace('.','\.') + ')',title,regex.I):
                                link = torrent['href']
                                response = scraper.x1337.session.get( 'https://1337x.to'+link, headers = headers)
                                soup = BeautifulSoup(response.content, 'html.parser')
                                download = soup.select('a[href^="magnet"]')[0]['href']
                                size = sizeList[count].contents[0]
                                if regex.search(r'([0-9]*?\.[0-9])(?= MB)',size,regex.I):
                                    size = regex.search(r'([0-9]*?\.[0-9])(?= MB)',size,regex.I).group()
                                    size = float(float(size) / 1000)
                                elif regex.search(r'([0-9]*?\.[0-9])(?= GB)',size,regex.I):
                                    size = regex.search(r'([0-9]*?\.[0-9])(?= GB)',size,regex.I).group()
                                    size = float(size)
                                else:
                                    size = float(size)
                                scraped_releases += [releases('[1337x]','torrent',title,[],size,[download])]
                except:
                    response = None
                    ui.print('1337x error: exception')
            return scraped_releases
#Multiprocessing scrape method
def scrape(cls:scraper,query,result,index):
    result[index] = cls(query)
#Multiprocessing download method
def download(cls:plex.media,library,parentReleases,result,index):
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
    library = plex.library()
    if len(library) > 0:
        plex_watchlist = plex.watchlist()
        if trakt.sync_with_plex == "true":
            trakt_watchlist = trakt.watchlist()
            trakt_watchlist.sync(plex_watchlist,library)
            plex_watchlist.update()
        if len(plex_watchlist) == 0:
            ui.print('checking new content ... done' )
        else:
            ui.print('checking new content ...')
            for element in plex_watchlist:
                element.download(library=library)
            ui.print('done')
        while not stop():   
            if plex_watchlist.update():
                library = plex.library()
                if len(library) == 0:
                    break
                ui.print('checking new content ...')
                for element in plex_watchlist:
                    element.download(library=library)
                ui.print('done')
            elif timeout_counter >= regular_check:
                if trakt.sync_with_plex == "true":
                    trakt_watchlist = trakt.watchlist()
                    trakt_watchlist.sync(plex_watchlist,library)
                plex_watchlist = plex.watchlist()
                library = plex.library()
                if len(library) == 0:
                    break
                timeout_counter = 0
                if len(plex_watchlist) == 0:
                    ui.print('checking new content ... done' )
                else:
                    ui.print('checking new content ...')
                    for element in plex_watchlist:
                        element.download(library=library)
                    ui.print('done')
            else:
                timeout_counter += timeout
            time.sleep(timeout)
#Multiprocessing run class
class download_script:   
    def run():
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
        def __init__(self,name,prompt,cls,key,required=False,entry="",test=None,help="",hidden=False,subclass=False,oauth=False,moveable=True):
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
        def input(self):
            if self.moveable:
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
                    clipboard.copy(getattr(self.cls,self.key))
                    console_input = input(self.prompt + '- current value "'+str(getattr(self.cls,self.key))+'" copied to your clipboard: ')
                    setattr(self.cls,self.key,console_input)
                    return True
                else:
                    lists = getattr(self.cls,self.key)
                    if self.moveable:
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
                        back3 = False
                        while not back3:
                            if index == '0':
                                back3 = True
                            if index in indices:
                                if self.moveable:
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
                                                clipboard.copy(lists[int(index)-1][k])
                                                response = input(prompt + '- current value "'+lists[int(index)-1][k]+'" copied to your clipboard: ')
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
                working = False
                while not working:
                    if self.name == 'Plex users':
                        print(self.help)
                        print()
                    if self.subclass:
                        print(self.help)
                        print()
                        services = []
                        indices = []
                        index = 0
                        for service in self.cls.__subclasses__():
                            if not '(NOT FUNCTIONAL)' in service.name:
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
            setting('Content Services',[''],content.services,'active',entry="content service",subclass=True,moveable=False),
            setting('Plex users',['Please provide a name for this Plex user: ','Please provide the Plex token for this Plex user: '],plex,'users',required=True,entry="user",help="Please create a plex user by providing a name and a token. To find the plex token for this user, open your favorite browser, log in to this plex account and visit 'https://plex.tv/devices.xml'. Pick a 'token' from one of the listed devices.",hidden=True),
            setting('Trakt users',['Please provide a name for this Trakt user: ','Please open your favorite browser, log into this Trakt user and open "https://trakt.tv/activate". Enter this code: '],trakt,'users',entry="user",oauth=True,hidden=True),
            setting('Trakt-to-Plex synchronization','Please enter "true" or "false": ',trakt,'sync_with_plex',hidden=True),
            setting('Plex server address','Please enter your Plex server address: ',plex.library,'url',hidden=True),
            setting('Plex "movies" library','Please enter the section number of the "movies" library, that should be refreshed after a movie download: ',plex.library,'movies',required=True,hidden=True),
            setting('Plex "shows" library','Please enter the section number of the "shows" library, that should be refreshed after a show download: ',plex.library,'shows',required=True,hidden=True)
            ]
        ],
        ['Scraper',[
            setting('Sources',[''],scraper.services,'active',entry="source",subclass=True),
            setting(
                'Release sorting',
                [
                    'Please specify what this sorting rule should to look for by providing one or more regex match group(s): ',
                    'Please specify in which release attribute ("title","source" or "size") this sorting rule should search: ',
                    'Please specify if the match should be interpreted as a number or as text ("number" or "text"): ',
                    'Please specify in which order the releases should be by ranked by this sorting rule ("0" = ascending or "1" = descending): ',
                ],
                releases.sort,'ranking',
                entry="rule",
            ),
            setting('Rarbg API Key','The Rarbg API Key gets refreshed automatically, enter the default value: ',scraper.rarbg,'token',hidden=True),
            ]
        ],
        ['Debrid Services', [
            setting('Debrid Services',[''],debrid.services,'active',required=True,entry="service",subclass=True,help='Please setup at least one debrid service (Currently only RealDebrid): '),
            setting('Real Debrid API Key','Please enter your Real Debrid API Key: ',debrid.realdebrid,'api_key',hidden=True),
            setting('All Debrid API Key','Please enter your All Debrid API Key: ',debrid.alldebrid,'api_key',hidden=True),
            setting('Premiumize API Key','Please enter your Premiumize API Key: ',debrid.premiumize,'api_key',hidden=True),
            setting('Debrid Link API Key','Please enter your Debrid Link API Key: ',debrid.debridlink,'api_key',hidden=True),
            ]
        ],
        ['UI Settings',[
            setting('Show Menu on Startup','Please enter "true" or "false": ',ui_settings,'run_directly'),
            setting('Debug printing','Please enter "true" or "false": ',ui_settings,'debug'),
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
        print('/_/               /_____/                                ')
        print()
        print(path)
        print()
    def print(string:str,debug="true"):
        if debug == "true":
            if string == 'done' and ui.sameline:
                print('done')
                ui.sameline = False
            elif ui.sameline and string.startswith('done'):
                print(string)
                ui.sameline = False
            elif string.endswith('...') and __name__ == "__main__":
                print('[' + str(datetime.datetime.now()) + '] ' + string, end=' ')
                sys.stdout.flush()
                ui.sameline = True
            elif not string.startswith('done'):
                print('[' + str(datetime.datetime.now()) + '] ' + string)
                sys.stdout.flush()
    def ignored():
        ui.cls('Options/Ignored Media/')
        if len(plex.ignored) == 0:
            watchlist = plex.watchlist()
            library = plex.library()
            for element in watchlist:
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
        query = input("Enter a query: ")
        print()
        scraped_releases = scraper(query.replace(' ','.'))
        if len(scraped_releases) > 0:
            print()
            print("0) Back")
            releases.print(scraped_releases)
            print()
            print("Type 'auto' to automatically download the first cached release.")
            back = False
            while not back:
                print()
                choice = input("Choose a release to download: ")
                if choice == 'auto':
                    release = scraped_releases[0]
                    release.Releases = scraped_releases
                    if debrid.download(release,stream=True,query=query,force=True):
                        back = True
                        time.sleep(3)
                    else:
                        print()
                        print("These releases do not seem to be cached on realdebrid. Add uncached torrent?")
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
                        print("This release does not seem to be cached on realdebrid. Add uncached torrent?")
                        print()
                        print("0) Back")
                        print("1) Add uncached torrent")
                        print()
                        choice = input("Choose an action: ")
                        if choice == '1':
                            debrid.download(release,stream=False,query=query,force=True)
                            back = True
                            time.sleep(3)
                elif choice == '0':
                    back = True
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
        choice = input('Choose an action: ')
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
            input('Press any key to continue: ')
            for category, settings in ui.settings_list:
                for setting in settings:
                    if setting.required:
                        ui.cls('Options/Settings/'+category+'/'+setting.name)
                        setting.setup()
            ui.cls('Done!')
            input('Press any key to continue to the main menu: ')
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
    def load(doprint=False):
        with open('settings.json', 'r') as f:
            settings = json.loads(f.read())
        for category, load_settings in ui.settings_list:
            for setting in load_settings:
                if setting.name in settings:
                    setting.set(settings[setting.name])
        if doprint:
            print('Last settings loaded!')
            time.sleep(2)
    def run():
        if ui.setup():
            ui.options()
        else:
            ui.load()
            download_script.run()

#TODO
#clean up the messy code
#make things even faster?
#downloading boolean for element to check if in debrid uncached torrents
#Barebones structure for other debrid services added, work on integration
#Add Google Watchlist, IMDB Watchlist, etc

if __name__ == "__main__":
    ui.run()
