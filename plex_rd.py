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
        active = ['Plex','Trakt','Overseerr']
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
    class watchlist(watchlist):
        autoremove = "movie"
        def __init__(self) -> None:
            ui.print('getting all plex watchlists ...')
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
            if hasattr(item,'user'):
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
            ui.print("updating all plex watchlists ...",debug=ui_settings.debug)
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
                                    ui.print('item: "' + entry.title + '" found in '+ user[0] +'`s plex watchlist')
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
                    return released.days > 0
            except Exception as e:
                ui.print("plex error: (attr exception): " + str(e),debug=ui_settings.debug)
                return False
        def available(self):
            if len(trakt.users) > 0:
                try:
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
                except Exception as e:
                    ui.print("plex error: (attr exception): " + str(e),debug=ui_settings.debug)
                    return False
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
            try:
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
            except Exception as e:
                ui.print("plex error: (attr exception): " + str(e),debug=ui_settings.debug)
                return False
        def collected(self,list):
            try:
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
            except Exception as e:
                ui.print("plex error: (attr exception): " + str(e),debug=ui_settings.debug)
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
                    if not season.collected(list) and not season.watched() and season.released() and not season.downloading():
                        for episode in season.Episodes[:]:
                            if episode.collected(list) or episode.watched() or not episode.released() or episode.downloading():
                                season.Episodes.remove(episode)
                    else:
                        Seasons.remove(season)
                    if len(season.Episodes) == 0 and season in Seasons:
                        Seasons.remove(season)
                return Seasons
            return []
        def downloading(self):
            return self in debrid.downloading
        def download(self,retries=1,library=[],parentReleases=[]):
            i = 0
            refresh = False
            self.Releases = []
            if self.type == 'movie':
                if self.released() and not self.watched() and not self.downloading():
                    if len(self.uncollected(library)) > 0:
                        tic = time.perf_counter()
                        while len(self.Releases) == 0 and i <= retries:
                            self.Releases += scraper(self.query())
                            i += 1
                        if self.debrid_download():
                            refresh = True
                            if plex.watchlist.autoremove == "both" or plex.watchlist.autoremove == "movie":
                                plex.watchlist.remove([],self)
                            toc = time.perf_counter()
                            ui.print('took ' + str(round(toc-tic,2)) + 's')
                        else:
                            self.watch()
            elif self.type == 'show':
                if self.released() and not self.watched():
                    self.Seasons = self.uncollected(library)
                    if len(self.Seasons) > 0:
                        tic = time.perf_counter()
                        if len(self.Seasons) > 1:
                            self.Releases += scraper(self.query())
                            parentReleases = copy.deepcopy(self.Releases)
                            if len(self.Seasons) > 3:
                                if self.debrid_download():
                                    refresh = True
                                    for season in self.Seasons[:]:
                                        for episode in season.Episodes[:]:
                                            for file in self.Releases[0].files:
                                                if file.match == episode.files()[0]:
                                                    season.Episodes.remove(episode)
                                                    break
                                        if len(season.Episodes) == 0:
                                            self.Seasons.remove(season)
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
                        for result in results:
                            if result:
                                refresh = True
                        if refresh and (plex.watchlist.autoremove == "both" or plex.watchlist.autoremove == "show"):
                            plex.watchlist.remove([],self)
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
            if debrid.download(self,stream=True):
                return True
            if not self.type == 'show' and debrid.uncached == 'true':
                if debrid.download(self,stream=False):
                    debrid.downloading += [self]
                    return True
            return False
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
                        self.leafCount = response.MediaContainer.totalSize
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
        check = []
        def refresh(section):
            ui.print('refreshing library section '+section+' ...')
            url = plex.library.url + '/library/sections/' + section + '/refresh?X-Plex-Token=' + plex.users[0][1]
            plex.session.get(url)
            ui.print('done')
        def __new__(self):
            list = []
            if not plex.library.check == [['']] and not plex.library.check == []:
                ui.print('getting plex library section/s "'+','.join(x[0] for x in plex.library.check) +'" ...')
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
                                    section_response += [plex.media(element)]
                    if len(section_response) == 0:
                        ui.print("plex error: couldnt reach local plex library section '"+section[0]+"' at server address: " + plex.library.url + " - or this library really is empty.")  
                    else:
                        list += section_response
                ui.print('done')
            else:
                ui.print('getting entire plex library ...')
                url = plex.library.url + '/library/all?X-Plex-Token='+ plex.users[0][1]
                response = plex.get(url)
                ui.print('done')
                if hasattr(response,'MediaContainer'):
                    if hasattr(response.MediaContainer,'Metadata'):
                        for element in response.MediaContainer.Metadata:
                            list += [plex.media(element)]
                else:
                    ui.print("plex error: couldnt reach local plex server at server address: " + plex.library.url + " - or this library really is empty.")    
            if len(list) == 0:
                ui.print("plex error: Your library seems empty. To prevent unwanted behaviour, no further downloads will be started. If your library really is empty, please add at least one media item manually.") 
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
            ui.print("plex error: couldnt match content to plex media type, because the plex library is empty. Please add at least one movie and one show!")
            return []
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
    lists = []
    users = []
    current_user = ["",""]
    session = requests.Session()
    def setup(self):
        back = False
        settings = []
        for category, allsettings in ui.settings_list:
            for setting in allsettings:
                if setting.cls == self or setting.name.startswith(self.name):
                    settings += [setting]
        ui.cls("Options/Settings/Content Services/Content Services/Trakt")
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
                    print("You can define which trakt lists should be monitored by plex_debrid. This includes public lists and your trakt users watchlists.")
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
                            if not user[0] in trakt.lists:
                                print(str(i+1) + ') add ' + user[0] + "'s trakt watchlist")
                                indices += [str(i+1)]
                                add_user += [user[0]]
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
                            trakt.lists += [add_user[int(choice)-2] + "'s watchlist"]
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
    class watchlist(watchlist):
        def __init__(self):
            if len(trakt.lists) > 0:
                ui.print('getting all trakt lists ...')
            self.data = []
            for list in trakt.lists:
                public = True
                for user in trakt.users:
                    if list == user[0] + "'s watchlist":
                        public = False
                        break
                trakt.current_user = user
                if not public:
                    watchlist_shows, header = trakt.get('https://api.trakt.tv/users/me/watchlist/shows')
                    watchlist_movies, header = trakt.get('https://api.trakt.tv/users/me/watchlist/movies')
                    for element in watchlist_shows:
                        element.show.type = 'show'
                        element.show.user = user
                        if not element.show in self.data:
                            self.data.append(element.show)
                    for element in watchlist_movies:
                        element.movie.type = 'movie'
                        element.movie.user = user
                        if not element.movie in self.data:
                            self.data.append(element.movie)
                else:
                    watchlist_shows, header = trakt.get('https://api.trakt.tv'+list+'/items/shows')
                    watchlist_movies, header = trakt.get('https://api.trakt.tv'+list+'/items/movies')
                    for element in watchlist_shows:
                        element.show.type = 'show'
                        element.show.user = user
                        if not element.show in self.data:
                            self.data.append(element.show)
                    for element in watchlist_movies:
                        element.movie.type = 'movie'
                        element.movie.user = user
                        if not element.movie in self.data:
                            self.data.append(element.movie)
            ui.print('done')
        def sync(self,other:plex.watchlist,library):
            add = []
            for element in self.data:
                try:
                    result = plex.match("imdb-"+element.ids.imdb,element.type,library=library)
                    if result == []:
                        result = plex.match("tmdb-"+str(element.ids.tmdb),element.type,library=library)
                    if result == []:
                        result = plex.match("tvdb-"+str(element.ids.tvdb),element.type,library=library)
                    result[0].trakt = element
                except:
                    ui.print('couldnt add item: "' + element.title + '" - no plex match found!',debug=ui_settings.debug)
                    result = []
                if not result == []:
                    add += result
            for element in add:
                if not element in other:
                    other.data.append(element)
        def update(self):
            if len(trakt.lists) > 0:
                ui.print('updating all trakt lists ...',debug=ui_settings.debug)
            refresh = False
            for list in trakt.lists:
                public = True
                for user in trakt.users:
                    if list == user[0] + "'s watchlist":
                        public = False
                        break
                trakt.current_user = user
                if not public:
                    watchlist_shows, header = trakt.get('https://api.trakt.tv/users/me/watchlist/shows')
                    watchlist_movies, header = trakt.get('https://api.trakt.tv/users/me/watchlist/movies')
                    for element in watchlist_shows:
                        element.show.type = 'show'
                        element.show.user = user
                        if not element.show in self.data:
                            refresh = True
                            ui.print('item: "' + element.show.title + '" found in ' + trakt.current_user[0]+ "'s trakt watchlist.")
                            self.data.append(element.show)
                    for element in watchlist_movies:
                        element.movie.type = 'movie'
                        element.movie.user = user
                        if not element.movie in self.data:
                            refresh = True
                            ui.print('item: "' + element.movie.title + '" found in ' + trakt.current_user[0]+ "'s trakt watchlist.")
                            self.data.append(element.movie)
                else:
                    watchlist_shows, header = trakt.get('https://api.trakt.tv'+list+'/items/shows')
                    watchlist_movies, header = trakt.get('https://api.trakt.tv'+list+'/items/movies')
                    for element in watchlist_shows:
                        element.show.type = 'show'
                        element.show.user = user
                        if not element.show in self.data:
                            refresh = True
                            ui.print('item: "' + element.show.title + '" found in public trakt list "' + list + '".')
                            self.data.append(element.show)
                    for element in watchlist_movies:
                        element.movie.type = 'movie'
                        element.movie.user = user
                        if not element.movie in self.data:
                            refresh = True
                            ui.print('item: "' + element.movie.title + '" found in public trakt list "' + list + '".')
                            self.data.append(element.movie)
            if len(trakt.lists) > 0:
                ui.print('done',debug=ui_settings.debug)
            if refresh:
                return True
            return False
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
            trakt.current_user = user
            trakt.post('https://api.trakt.tv/sync/watchlist/remove',json.dumps(data, default=lambda o: o.__dict__))
    class media:
        def available(self):
            trakt.current_user = trakt.users[0]
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
    def get(url): 
        try :
            response = overseerr.session.get(url, headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36', 'Content-type' : "application/json", "X-Api-Key" : overseerr.api_key})
            response = json.loads(response.content, object_hook=lambda d: SimpleNamespace(**d))
        except :
            response = None
        return response
    def post(url, data):
        try :
            response = overseerr.session.post(url, headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36', 'Content-type' : "application/json", "X-Api-Key" : overseerr.api_key}, data = data)
            response = json.loads(response.content, object_hook=lambda d: SimpleNamespace(**d))
        except :
            response = None
        return response
    class requests(watchlist):
        def __init__(self):
            self.data = []
            if len(overseerr.users) > 0 and len(overseerr.api_key) > 0:
                ui.print('getting all overseerr requests ...')
                try:
                    response = overseerr.get(overseerr.base_url + '/api/v1/request')
                    for element in response.results:
                        if not element in self.data and (element.requestedBy.displayName in overseerr.users or overseerr.users == ['all']) and [str(element.status)] in overseerr.allowed_status:
                            self.data.append(element)
                except:
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
                ui.print('updating all overseerr requests ...',debug=ui_settings.debug)
                refresh = False
                try:
                    response = overseerr.get(overseerr.base_url + '/api/v1/request')
                    for element in response.results:
                        if not element in self.data and (element.requestedBy.displayName in overseerr.users or overseerr.users == ['all']) and [str(element.status)] in overseerr.allowed_status:
                            ui.print('found new overseerr request by user "' + element.requestedBy.displayName + '".')
                            refresh = True
                            self.data.append(element)
                    ui.print('done',debug=ui_settings.debug)
                    if refresh:
                        return True
                except:
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
    def download(element:plex.media,stream=True,query='',force=False):
        if stream:
            debrid.check(element,force=force)
            cached_releases = copy.deepcopy(element.Releases)
            for release in cached_releases:
                element.Releases = [release,]
                if len(debrid.tracker) > 0:
                    for t,s in debrid.tracker:
                        if regex.search(t,release.source,regex.I):
                            release.cached = s
                for service in debrid.services():
                    if service.short in release.cached:
                        if service.download(element,stream=stream,query=query,force=force):
                            return True
        else:
            scraped_releases = copy.deepcopy(element.Releases)
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
                                return True
                    else:
                        if service.download(element,stream=stream,query=query,force=force):
                            return True
        return False
    #Check Method:
    def check(element:plex.media,force=False):
        for service in debrid.services():
            service.check(element,force=force)
        releases.sort(element.Releases)
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
        def download(element:plex.media,stream=True,query='',force=False):
            cached = element.Releases
            if query == '':
                query = element.query()
            if regex.search(r'(S[0-9][0-9])',query):
                query = regex.split(r'(S[0-9]+)',query) 
                season_number = regex.search(r'([0-9]+)',query[1]).group()
                query[1] = '(S'+season_number+'|SEASON.'+str(int(season_number))+')'
                query = query[0] + '[0-9]*.*' + query[1] + query[2]
            wanted = [query]
            if not isinstance(element,releases):
                wanted = element.files()
            for release in cached[:]:
                #if release matches query
                if regex.match(r'('+ query.replace('.','\.').replace("\.*",".*") + ')',release.title,regex.I) or force:
                    if stream:
                        release.size = 0
                        for version in release.files:
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
                if not release.hash == '':
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
        def download(element:plex.media,stream=True,query='',force=False):
            cached = element.Releases
            if query == '':
                query = element.query()
            if regex.search(r'(S[0-9][0-9])',query):
                query = regex.split(r'(S[0-9]+)',query)
                season_number = regex.search(r'([0-9]+)',query[1]).group()
                query[1] = '(S'+season_number+'|SEASON.0?'+str(int(season_number))+')' 
                query = query[0] + '[0-9]*.*' + query[1] + query[2]
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
                if not release.hash == '':
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
        def download(element:plex.media,stream=True,query='',force=False):
            cached = element.Releases
            if query == '':
                query = element.query()
            if regex.search(r'(S[0-9][0-9])',query):
                query = regex.split(r'(S[0-9]+)',query)
                season_number = regex.search(r'([0-9]+)',query[1]).group()
                query[1] = '(S'+season_number+'|SEASON.0?'+str(int(season_number))+')' 
                query = query[0] + '[0-9]*.*' + query[1] + query[2]
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
                if not release.hash == '':
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
        def download(element:plex.media,stream=True,query='',force=False):
            cached = element.Releases
            if query == '':
                query = element.query()
            if regex.search(r'(S[0-9][0-9])',query):
                query = regex.split(r'(S[0-9]+)',query)
                season_number = regex.search(r'([0-9]+)',query[1]).group()
                query[1] = '(S'+season_number+'|SEASON.0?'+str(int(season_number))+')' 
                query = query[0] + '[0-9]*.*' + query[1] + query[2]
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
                if not release.hash == '':
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
        self.hash       = ''
        if len(self.download)> 0:
            if regex.search(r'(?<=btih:).*?(?=&)',str(self.download[0]),regex.I):
                self.hash   = regex.findall(r'(?<=btih:).*?(?=&)',str(self.download[0]),regex.I)[0]            
        self.cached     = []
        self.title_deviation = 0
        self.wanted = 0
        self.unwanted = 0
    #Define when releases are Equal 
    def __eq__(self, other):
        return self.title == other.title
    #Sort Method
    class sort:
        unwanted = ['sample']
        multiple_versions_trigger = ""
        ranking= [
            [
                "(1080|720|480)(?=p|i)",
                "title",
                "number",
                "1"
            ],
            [
                "(.*)",
                "wanted",
                "number",
                "1"
            ],
            [
                "(.*)",
                "unwanted",
                "number",
                "0"
            ],
            [
                "(1337x)",
                "source",
                "text",
                "0"
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
                "title_deviation",
                "number",
                "0"
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
    class rename:
        deleteChars = ['.',':','(',')','`','´',',','!','?',' - ',"'","\u200b"]
        dotChars = [' ']#,'/']
        replaceChars = [['&','and'],['ü','ue'],['ä','ae'],['ö','oe'],['ß','ss'],['é','e'],['è','e']]
        def __new__(self,string):
            for specialChar in self.deleteChars:
                string = string.replace(specialChar, '')
            for specialChar in self.dotChars:
                string = string.replace(specialChar, '.')
            for specialChar,repl in self.replaceChars:
                string = string.replace(specialChar,repl)
            string = regex.sub(r'\.+',".",string)
            return string    
    #Print Method
    def print(scraped_releases):
        if __name__ == "__main__":
            longest_file = 0
            longest_cached = 0
            longest_title = 0
            longest_size = 0
            longest_index = 0
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
                if len(str(index+1)) > longest_index:
                    longest_index = len(str(index+1))
            for index,release in enumerate(scraped_releases):
                print(str(index+1)+") "+' ' * (longest_index-len(str(index+1)))+"title: " + release.title + ' ' * (longest_title-len(release.title)) + " | size: " + str(release.printsize) + ' ' * (longest_size-len(str(release.printsize))) + " | cached: " + '/'.join(release.cached) + ' ' * (longest_cached-len('/'.join(release.cached))) + " | files: " + release.file + ' ' * (longest_file-len(release.file)) + " | source: " + release.source )
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
    def __new__(cls,query):
        ui.print('done')
        ui.print('scraping sources for query "' + query + '" ...')
        scrapers = scraper.services()
        scraped_releases = []
        results = [None] * len(scrapers)
        threads = []
        for index,scraper_ in enumerate(scrapers):
            t = Thread(target=scrape, args=(scraper_,query,results,index))
            threads.append(t)
            t.start()
        # wait for the threads to complete
        for t in threads:
            t.join()
        for result in results:
            if not result == []:
                scraped_releases += result
        if regex.search(r'(S[0-9]+)',query) or not query.endswith('.'):
            if not query.endswith('.'):
                altquery = [query,'(S[0-9]+|Season.[0-9]+)','']
            else:
                altquery = regex.split(r'(S[0-9]+)',query) 
                season_number = regex.search(r'([0-9]+)',altquery[1]).group()
                altquery[1] = '(S'+season_number+'|SEASON.'+str(int(season_number))+')'
            for release in scraped_releases:
                deviation = regex.search(r'(?<=' + altquery[0] + ')(.*?)(?=' + altquery[1] + altquery[2] + ')',release.title,regex.I)
                if not deviation == None:
                    if len(deviation.group()) <= 1:
                        release.title_deviation = 0
                    elif len(deviation.group()) > 6:
                        release.title_deviation = 2
                    else:
                        release.title_deviation = 1
                elif not query.endswith('.'):
                    release.title_deviation = 2
                else:
                    release.title_deviation = 0
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
                        if regex.match(r'('+ altquery.replace('.','\.').replace("\.*",".*") + ')',result.title,regex.I):
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
                            if regex.match(r'('+ altquery.replace('.','\.').replace("\.*",".*") + ')',title,regex.I):
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
    class jackett(services):
        base_url = "http://127.0.0.1:9117"
        api_key = ""
        name = "jackett"
        indexers = []
        categories = []
        filters = []
        session = requests.Session()
        def __new__(cls,query):
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
                altquery = copy.deepcopy(query)
                if regex.search(r'(S[0-9]+)',altquery):
                    altquery = regex.split(r'(S[0-9]+)',altquery) 
                    altquery = altquery[0] + '[0-9]*.*' + altquery[1] + altquery[2]
                url = scraper.jackett.base_url + '/api/v2.0/indexers/' + filter + '/results?apikey=' + scraper.jackett.api_key + '&Query=' + query + tags
                response = scraper.jackett.session.get(url)
                if response.status_code == 200:
                    response = json.loads(response.content, object_hook=lambda d: SimpleNamespace(**d))
                    for result in response.Results[:]:
                        result.Title = result.Title.replace(' ','.')
                        if regex.match(r'('+ altquery.replace('.','\.').replace("\.*",".*") + ')',result.Title,regex.I):
                            if not result.MagnetUri == None:
                                if not result.Tracker == None and not result.Size == None:
                                    scraped_releases += [releases('[jackett: '+str(result.Tracker)+']','torrent',result.Title,[],float(result.Size)/1000000000,[result.MagnetUri])]
                                elif not result.Tracker == None:
                                    scraped_releases += [releases('[jackett: '+str(result.Tracker)+']','torrent',result.Title,[],1,[result.MagnetUri])]
                                elif not result.Size == None:
                                    scraped_releases += [releases('[jackett: unnamed]','torrent',result.Title,[],float(result.Size)/1000000000,[result.MagnetUri])]
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
                        if not result == []:
                            scraped_releases += result
            return scraped_releases
        def resolve(result):
            scraped_releases = []
            try:
                link = scraper.jackett.session.get(result.Link,allow_redirects=False,timeout=0.5)
                if regex.search(r'(?<=btih:).*?(?=&)',str(link.headers['Location']),regex.I):
                    if not result.Tracker == None and not result.Size == None:
                        scraped_releases += [releases('[jackett: '+str(result.Tracker)+']','torrent',result.Title,[],float(result.Size)/1000000000,[link.headers['Location']])]
                    elif not result.Tracker == None:
                        scraped_releases += [releases('[jackett: '+str(result.Tracker)+']','torrent',result.Title,[],1,[link.headers['Location']])]
                    elif not result.Size == None:
                        scraped_releases += [releases('[jackett: unnamed]','torrent',result.Title,[],float(result.Size)/1000000000,[link.headers['Location']])]
                return scraped_releases
            except:
                return scraped_releases
    class prowlarr(services):
        base_url = "http://127.0.0.1:9696"
        api_key = ""
        name = "prowlarr"
        session = requests.Session()
        def __new__(cls,query):
            scraped_releases = []
            if 'prowlarr' in scraper.services.active:
                altquery = copy.deepcopy(query)
                if regex.search(r'(S[0-9]+)',altquery):
                    altquery = regex.split(r'(S[0-9]+)',altquery) 
                    altquery = altquery[0] + '[0-9]*.*' + altquery[1] + altquery[2]
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
                                        scraped_releases += [releases('[prowlarr: '+str(result.indexer)+']','torrent',result.title,[],float(result.size)/1000000000,[result.magnetUrl])]
                                    elif not result.indexer == None:
                                        scraped_releases += [releases('[prowlarr: '+str(result.indexer)+']','torrent',result.title,[],1,[result.magnetUrl])]
                                    elif not result.size == None:
                                        scraped_releases += [releases('[prowlarr: unnamed]','torrent',result.title,[],float(result.size)/1000000000,[result.magnetUrl])]
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
                if regex.search(r'(?<=btih:).*?(?=&)',str(link.headers['Location']),regex.I):
                    if not result.indexer == None and not result.size == None:
                        scraped_releases += [releases('[prowlarr: '+str(result.indexer)+']','torrent',result.title,[],float(result.size)/1000000000,[link.headers['Location']])]
                    elif not result.indexer == None:
                        scraped_releases += [releases('[prowlarr: '+str(result.indexer)+']','torrent',result.title,[],1,[link.headers['Location']])]
                    elif not result.size == None:
                        scraped_releases += [releases('[prowlarr: unnamed]','torrent',result.title,[],float(result.size)/1000000000,[link.headers['Location']])]
                return scraped_releases
            except:
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
        #get entire plex_watchlist
        plex_watchlist = plex.watchlist()
        #get entire trakt_watchlist, match content to plex media type and add to monitored list
        trakt_watchlist = trakt.watchlist()
        trakt_watchlist.sync(plex_watchlist,library)
        #get all overseerr request, match content to plex media type and add to monitored list
        overseerr_requests = overseerr.requests()
        overseerr_requests.sync(plex_watchlist,library)
        if len(plex_watchlist) == 0:
            ui.print('checking new content ... done' )
        else:
            ui.print('checking new content ...')
            for element in plex_watchlist:
                element.download(library=library)
            ui.print('done')
        while not stop():   
            if plex_watchlist.update() or overseerr_requests.update() or trakt_watchlist.update():
                library = plex.library()
                trakt_watchlist.sync(plex_watchlist,library)
                overseerr_requests.sync(plex_watchlist,library)
                if len(library) == 0:
                    break
                ui.print('checking new content ...')
                for element in plex_watchlist:
                    element.download(library=library)
                ui.print('done')
            elif timeout_counter >= regular_check:
                #get entire plex_watchlist
                plex_watchlist = plex.watchlist()
                #get entire trakt_watchlist, match content to plex media type and add to monitored list
                trakt_watchlist = trakt.watchlist()
                trakt_watchlist.sync(plex_watchlist,library)
                #get all overseerr request, match content to plex media type and add to monitored list
                overseerr_requests = overseerr.requests()
                overseerr_requests.sync(plex_watchlist,library)
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
    version = ['1.1',"Content Services have been updated. Overseerr is now an available content service.",['Content Services',]]
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
        def __init__(self,name,prompt,cls,key,required=False,entry="",test=None,help="",hidden=False,subclass=False,oauth=False,moveable=True,preflight=False):
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
        def input(self):
            if self.moveable:
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
            setting('Content Services',[''],content.services,'active',entry="content service",subclass=True,moveable=False),
            setting('Plex users',['Please provide a name for this Plex user: ','Please provide the Plex token for this Plex user: '],plex,'users',required=True,preflight=True,entry="user",help="Please create a plex user by providing a name and a token. To find the plex token for this user, open your favorite browser, log in to this plex account and visit 'https://plex.tv/devices.xml'. Pick a 'token' from one of the listed devices.",hidden=True),
            setting('Trakt users',['Please provide a name for this Trakt user: ','Please open your favorite browser, log into this Trakt user and open "https://trakt.tv/activate". Enter this code: '],trakt,'users',entry="user",oauth=True,hidden=True),
            setting('Trakt lists',[''],trakt,'lists',hidden=True),
            setting('Plex server address','Please enter your Plex server address: ',plex.library,'url',hidden=True),
            setting('Plex "movies" library','Please enter the section number of the "movies" library, that should be refreshed after a movie download. To find the section number, go to "https://app.plex.tv", open your "movies" library and look for the "source=" parameter in the url. Please enter the section number: ',plex.library,'movies',required=True,hidden=True),
            setting('Plex "shows" library','Please enter the section number of the "shows" library, that should be refreshed after a show download. To find the section number, go to "https://app.plex.tv", open your "shows" library and look for the "source=" parameter in the url. Please enter the section number:  ',plex.library,'shows',required=True,hidden=True),
            setting('Plex library check',['Please specify a library section number that should be checked for existing content before download: '],plex.library,'check',hidden=True,entry="section",help='By default, your entire library (including plex shares) is checked for existing content before a download is started. This setting allows you limit this check to specific library sections. To find a section number, go to "https://app.plex.tv", open your the library you want to include in the check and look for the "source=" parameter in the url.'),
            setting('Plex auto remove','Please choose which media type/s should be removed from your watchlist after successful download ("movie","show","both" or "none"): ',plex.watchlist,'autoremove',hidden=True,help='By default, movies are removed from your watchlist after a successful download. In this setting you can choose to automatically remove shows, shows and movies or nothing.'),
            setting('Overseerr users',['Please choose a user: '],overseerr,'users',entry="user",help="Please specify which users requests should be downloaded by plex_debrid.",hidden=True),
            setting('Overseerr API Key','Please specify your Overseerr API Key: ',overseerr,'api_key',hidden=True),
            setting('Overseerr Base URL','Please specify your Overseerr base URL: ',overseerr,'base_url',hidden=True),
            ]
        ],
        ['Scraper',[
            setting('Sources',[''],scraper.services,'active',entry="source",subclass=True,preflight=True),
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
            setting('Special character renaming',['Please specify a character or string that should be replaced: ','Please specify with what character or string it should be replaced: '],releases.rename,'replaceChars',entry="rule",help='By default, spaces in plex media titles are replaced by dots and the following character/s are removed: "' + '","'.join(releases.rename.deleteChars) + '". In this setting you can specify a character or a string that should be replaced by nothing, some other character or a string.'),
            #setting('Multiple versions trigger','Please specify your multiple versions trigger: ',releases.sort,'multiple_versions_trigger',help='This setting allows you to download more than one release every time you add a movie or show. If the selected release regex-matches the specified trigger, the next, best release that doesnt match this trigger will be downloaded aswell. Example: You want to download both HDR and non-HDR versions of your content - type "(HDR)."'),
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
            setting('Uncached Release Download','Please enter "true" or "false": ',debrid,'uncached',help='Please specify wether uncached releases should be added to your debrid service, if no cached releases were found.'),
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
            #setting('Debrid Link API Key','Please enter your Debrid Link API Key: ',debrid.debridlink,'api_key',hidden=True),
            setting('Debrid Link API Key','Please open your favorite browser, log into your debridlink account and open "https://debrid-link.fr/device". Enter this code: ',debrid.debridlink,'api_key',hidden=True,oauth=True),
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
        print('/_/               /_____/                                ')
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
            elif string.endswith('...') and __name__ == "__main__":
                print('[' + str(datetime.datetime.now()) + '] ' + string, end=' ')
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
        print('Press Enter to return to the main menu.')
        print()
        query = input("Enter a query: ")
        if query == '':
            return
        print()
        obj = releases('','','',[],0,[])
        scraped_releases = scraper(query.replace(' ','.'))
        if len(scraped_releases) > 0:
            obj.Releases = scraped_releases
            debrid.check(obj,force=True)
            print()
            print("0) Back")
            releases.print(scraped_releases)
            print()
            print("Type 'auto' to automatically download the first cached release.")
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
        elif not settings['version'][0] == ui_settings.version[0]:
            ui.update(settings,ui_settings.version)
            updated = True
        for category, load_settings in ui.settings_list:
            for setting in load_settings:
                if setting.name in settings:
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
