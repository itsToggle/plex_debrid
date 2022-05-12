#Import Modules
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
 
#Plex Class
class plex:
    session = requests.Session()  
    users = []
    headers = {'Content-Type':'application/json','Accept':'application/json'}
    def get(url):
        try:
            response = plex.session.get(url,headers=plex.headers)
            response = json.loads(response.content, object_hook=lambda d: SimpleNamespace(**d))
            return response
        except:
            return None
    def post(url,data):
        try:
            response = plex.session.post(url,data=data,headers=plex.headers)
            response = json.loads(response.content, object_hook=lambda d: SimpleNamespace(**d))
            return response
        except:
            return None
    class watchlist:
        def __init__(self,list) -> None:
            pass
        def __new__(self,old=[]):
            if old == []:
                print('[' + str(datetime.datetime.now()) + '] updating entire plex watchlist ...', end = ' ')
                sys.stdout.flush()
            watchlist_entries = []
            try:
                for user in plex.users:
                    url = 'https://metadata.provider.plex.tv/library/sections/watchlist/all?X-Plex-Token=' + user[1]
                    response = plex.get(url)
                    if hasattr(response.MediaContainer,'Metadata'):
                        for entry in response.MediaContainer.Metadata:
                            entry.user = user
                            if not entry in old:
                                if entry.type == 'show':
                                    watchlist_entries += [plex.show(entry)]
                                if entry.type == 'movie':
                                    watchlist_entries += [plex.movie(entry)]
            except:
                if old == []:
                    print('done')
                    sys.stdout.flush()
                print('[' + str(datetime.datetime.now()) + '] plex error: could not reach plex')
                sys.stdout.flush()
            if old == []:
                print('done')
                sys.stdout.flush()
            return watchlist_entries
        def remove(item):
            print('[' + str(datetime.datetime.now()) + '] item: "' + item.title + '" removed from '+ item.user[0] +'`s plex watchlist')
            sys.stdout.flush()
            url = 'https://metadata.provider.plex.tv/actions/removeFromWatchlist?ratingKey=' + item.ratingKey + '&X-Plex-Token=' + item.user[1]
            response = plex.session.put(url,data={'ratingKey':item.ratingKey})
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
                return releases.rename(self.title) + '.' + str(self.year)
            elif self.type == 'show':
                return releases.rename(self.title)
            elif self.type == 'season':
                return releases.rename(self.parentTitle) + '.S' + str("{:02d}".format(self.index)) + '.'
            elif self.type == 'episode':
                return releases.rename(self.grandparentTitle) + '.S' + str("{:02d}".format(self.parentIndex)) + 'E' + str("{:02d}".format(self.index))+ '.'
        def released(self):
            return datetime.datetime.today() > datetime.datetime.strptime(self.originallyAvailableAt,'%Y-%m-%d')
        def watch(self):
            if self.type == 'movie' or self.type == 'show':
                print('ignoring item: ' + self.title)
                sys.stdout.flush()
            elif self.type == 'season':
                print('ignoring item: ' + self.title + 'S' + str("{:02d}".format(self.index)))
                sys.stdout.flush()
            elif self.type == 'episode':
                print('ignoring item: ' + self.title + 'S' + str("{:02d}".format(self.parentIndex)) + 'E' + str("{:02d}".format(self.index)))
                sys.stdout.flush()
            url = 'https://metadata.provider.plex.tv/actions/scrobble?identifier=tv.plex.provider.metadata&key='+self.ratingKey+'&X-Plex-Token='+ plex.users[0][1]
            plex.get(url)
        def watched(self):
            if self.type == 'movie' or self.type == 'episode':
                return self.viewCount > 0
            else:
                return self.viewedLeafCount == self.leafCount
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
                    if not season.collected(list):
                        for episode in season.Episodes[:]:
                            if episode.collected(list):
                                season.Episodes.remove(episode)
                    else:
                        Seasons.remove(season)
                    if len(season.Episodes) == 0:
                        Seasons.remove(season)
                return Seasons
            return []
        def download(self,retries=1):
            i = 0
            refresh = False
            self.Releases = []
            library = plex.library()
            if self.type == 'movie':
                if self.released() and not self.watched():
                    if len(self.uncollected(library)) > 0:
                        while len(self.Releases) == 0 and i <= retries:
                            self.Releases += releases.scrape(self.query())
                            i += 1
                        if self.debrid_download():
                            refresh = True
                            plex.watchlist.remove(self)
            elif self.type == 'show':
                if self.released() and not self.watched():
                    for season in self.uncollected(library):
                        if season.download():
                            refresh = True
            elif self.type == 'season':
                if self.released() and not self.watched():
                    for episode in self.Episodes[:]:
                        if not episode.released() or episode.watched():
                            self.Episodes.remove(episode)
                    for episode in self.Episodes:
                        if not len(self.Episodes) <= self.leafCount/2:
                            while len(self.Releases) == 0 and i <= retries:
                                self.Releases += releases.scrape(self.query())
                                i += 1
                        if not self.debrid_download():
                            self.Releases += releases.scrape(self.query()[:-1])
                            for episode in self.Episodes:
                                if episode.download(retries=1):
                                    refresh = True
                                else:
                                    episode.watch()
                            if refresh:
                                return True
                        else:
                            return True
            elif self.type == 'episode':
                if self.released() and not self.watched():
                    while len(self.Releases) == 0 and i <= retries:
                        altquery = self.query()
                        if regex.search(r'(S[0-9][0-9])',altquery):
                            altquery = regex.split(r'(S[0-9]+)',altquery) 
                            altquery = altquery[0] + '[0-9]*.*' + altquery[1] + altquery[2]
                        for release in self.Parent.Releases:
                            if regex.match(r'('+altquery+')',release.title,regex.I):
                                self.Releases += [release]
                        if self.debrid_download():
                            return True
                        else:
                            self.Releases = releases.scrape(self.query())
                        i += 1
                    return self.debrid_download()
            if refresh:
                debrid.monitor()
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
    class season(media):
        def __init__(self,other,parent):
            self.__dict__.update(other.__dict__)
            self.Episodes = []
            self.Parent = parent
            while len(self.Episodes) < self.leafCount:
                url = 'https://metadata.provider.plex.tv/library/metadata/'+self.ratingKey+'/children?includeUserState=1&X-Plex-Container-Size=200&X-Plex-Container-Start='+str(len(self.Episodes))+'&X-Plex-Token='+plex.users[0][1]
                response = plex.get(url)
                for episode in response.MediaContainer.Metadata:
                    self.Episodes += [plex.episode(episode,self)]        
    class episode(media):
        def __init__(self,other,parent):
            self.__dict__.update(other.__dict__)
            self.Parent = parent
    class show(media):
        def __init__(self, ratingKey):
            if not isinstance(ratingKey,str):
                self.__dict__.update(ratingKey.__dict__)
                ratingKey = ratingKey.ratingKey
                token = self.user[1]
            else:
                token = plex.users[0][1]
            url = 'https://metadata.provider.plex.tv/library/metadata/'+ratingKey+'?includeUserState=1&X-Plex-Token='+token
            response = plex.get(url)
            self.__dict__.update(response.MediaContainer.Metadata[0].__dict__)
            self.Seasons = []
            url = 'https://metadata.provider.plex.tv/library/metadata/'+ratingKey+'/children?includeUserState=1&X-Plex-Container-Size=200&X-Plex-Container-Start=0&X-Plex-Token='+token
            response = plex.get(url)
            for season in response.MediaContainer.Metadata:
                if not season.index == 0:
                    self.Seasons += [plex.season(season,self)]
    class movie(media):
        def __init__(self, ratingKey):
            if not isinstance(ratingKey,str):
                self.__dict__.update(ratingKey.__dict__)
                ratingKey = ratingKey.ratingKey
            url = 'https://metadata.provider.plex.tv/library/metadata/'+ratingKey+'?includeUserState=1&X-Plex-Token='+plex.users[0][1]
            response = plex.get(url)
            self.__dict__.update(response.MediaContainer.Metadata[0].__dict__)            
    class library:
        url = 'http://localhost:32400'
        movies = '1'
        shows = '2'
        def refresh(section):
            print('[' + str(datetime.datetime.now()) + '] refreshing library section '+section+' ...', end=' ')
            sys.stdout.flush()
            url = plex.library.url + '/library/sections/' + section + '/refresh?X-Plex-Token=' + plex.users[0][1]
            plex.session.get(url)
            print('done')
            sys.stdout.flush()
        def __new__(self):
            url = plex.library.url + '/library/all?X-Plex-Token='+ plex.users[0][1]
            list = []
            response = plex.get(url)
            for element in response.MediaContainer.Metadata:
                list += [plex.media(element)]
            return list
    def search(query):
        query = query.replace(' ','%20')
        url = 'https://metadata.provider.plex.tv/library/search?query='+query+'&limit=30&searchTypes=movies%2Ctv&includeMetadata=1&X-Plex-Token='+plex.users[0][1]
        response = plex.get(url)
        return response.MediaContainer.SearchResult    
#Debrid Class 
class debrid:
    api_key = ""
    #Define Variables
    session = requests.Session()
    #Get Function
    def get(url): 
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36', 'authorization' : 'Bearer ' + debrid.api_key , 'Connection' : 'close'}
        try :
            response = debrid.session.get(url, headers = headers)
            response = json.loads(response.content, object_hook=lambda d: SimpleNamespace(**d))
        except :
            response = None
        return response
    #Post Function
    def post(url, data):
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36', 'authorization' : 'Bearer ' + debrid.api_key , 'Connection' : 'close'}
        try :
            response = debrid.session.post(url, headers = headers, data = data)
            try:
                response = json.loads(response.content, object_hook=lambda d: SimpleNamespace(**d))
            except :
                response = None
            #time.sleep(1)
        except :
            response = None
        return response
    #Delete Function
    def delete(url):
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36', 'authorization' : 'Bearer ' + debrid.api_key , 'Connection' : 'close'}
        try :
            requests.delete(url, headers = headers)
            time.sleep(1)
        except :
            None
        return None
    #Object classes
    class file:
        def __init__(self,id,name,size):
            self.id = id
            self.name = name
            self.size = size
        def __eq__(self, other):
            return self.id == other.id 
    #Check Function
    def download(element:plex.media,stream=True,query=''):
        cached = element.Releases
        if query == '':
            query = element.query()
        if stream:
            mode = 'cached'
        else:
            mode = 'uncached'
        print('[' + str(datetime.datetime.now()) + '] checking debrid for '+mode+' releases ...', end = ' ')
        sys.stdout.flush()
        if regex.search(r'(S[0-9][0-9])',query):
            query = regex.split(r'(S[0-9]+)',query) 
            query = query[0] + '[0-9]*.*' + query[1] + query[2]
        for release in cached[:]:
            #if release matches query
            if regex.match(r'('+ query.replace('.','\.') + ')',release.title,regex.I):
                if stream:
                    release.size = 0
                    files = []
                    cached_ids = []
                    subtitles = []
                    if regex.search(r'(?<=btih:).*?(?=&)',str(release.download[0]),regex.I):
                        hashstring = regex.findall(r'(?<=btih:).*?(?=&)',str(release.download[0]),regex.I)[0]
                        #get cached file ids
                        response = debrid.get('https://api.real-debrid.com/rest/1.0/torrents/instantAvailability/' + hashstring)
                        if hasattr(response, hashstring.lower()):
                            if hasattr(getattr(response, hashstring.lower()),'rd'):
                                for cashed_version in getattr(response, hashstring.lower()).rd:
                                    for file in cashed_version.__dict__:
                                        debrid_file = debrid.file(file,getattr(cashed_version,file).filename,getattr(cashed_version,file).filesize)
                                        if not debrid_file in files:
                                            files.append(debrid_file)
                                #remove unwanted files from selection
                                for file in files[:]:
                                    if file.name.endswith('.rar') or file.name.endswith('.exe') or file.name.endswith('.txt'):
                                        files.remove(file)
                                    if file.name.endswith('.srt'):
                                        subtitles += [file.id]
                                #check if there are cached files available
                                if not files == []:
                                    for file in files:
                                        cached_ids += [file.id]
                                #post magnet to real debrid
                                try:
                                    response = debrid.post('https://api.real-debrid.com/rest/1.0/torrents/addMagnet',{'magnet' : str(release.download[0])})
                                    torrent_id = str(response.id)
                                except:
                                    continue
                                #If cached files are available, post the file selection to get the download links
                                if len(cached_ids) > 0:
                                    response = debrid.post('https://api.real-debrid.com/rest/1.0/torrents/selectFiles/' + torrent_id , {'files' : str(','.join(cached_ids))})    
                                    response = debrid.get('https://api.real-debrid.com/rest/1.0/torrents/info/' + torrent_id)
                                    if len(response.links) == len(cached_ids):
                                        release.download = response.links
                                    elif not len(response.links) == len(cached_ids) and len(subtitles) > 0:
                                        for subtitle in subtitles:
                                            cached_ids.remove(subtitle)
                                        debrid.delete('https://api.real-debrid.com/rest/1.0/torrents/delete/' + torrent_id)
                                        try:
                                            response = debrid.post('https://api.real-debrid.com/rest/1.0/torrents/addMagnet',{'magnet' : str(release.download[0])})
                                            torrent_id = str(response.id)
                                        except:
                                            continue
                                        response = debrid.post('https://api.real-debrid.com/rest/1.0/torrents/selectFiles/' + torrent_id , {'files' : str(','.join(cached_ids))})    
                                        response = debrid.get('https://api.real-debrid.com/rest/1.0/torrents/info/' + torrent_id)
                                        if len(response.links) == len(cached_ids):
                                            release.download = response.links
                                        else:
                                            debrid.delete('https://api.real-debrid.com/rest/1.0/torrents/delete/' + torrent_id)
                                            continue
                                    else:
                                        debrid.delete('https://api.real-debrid.com/rest/1.0/torrents/delete/' + torrent_id)
                                        continue
                                    #delete the torrent
                                    debrid.delete('https://api.real-debrid.com/rest/1.0/torrents/delete/' + torrent_id)
                                    if len(release.download) > 0:
                                        for link in release.download:
                                            try:
                                                response = debrid.post('https://api.real-debrid.com/rest/1.0/unrestrict/link', {'link' : link})
                                            except:
                                                break
                                        print('done')
                                        sys.stdout.flush()
                                        print('[' + str(datetime.datetime.now()) + '] streaming release: ' + release.title)
                                        sys.stdout.flush()
                                        return True
                                else:
                                    debrid.delete('https://api.real-debrid.com/rest/1.0/torrents/delete/' + torrent_id)
                        print('done')
                        sys.stdout.flush()
                        return False
                    else:
                        if len(release.download) > 0:
                            for link in release.download:
                                try:
                                    response = debrid.post('https://api.real-debrid.com/rest/1.0/unrestrict/link', {'link' : link})
                                except:
                                    break
                            print('done')
                            sys.stdout.flush()
                            print('[' + str(datetime.datetime.now()) + '] streaming release: ' + release.title)
                            sys.stdout.flush()
                            return True
                else:
                    print('done')
                    sys.stdout.flush()
                    print('[' + str(datetime.datetime.now()) + '] adding uncached release to debrid: '+ release.title)
                    sys.stdout.flush()
                    response = debrid.post('https://api.real-debrid.com/rest/1.0/torrents/addMagnet',{'magnet':release.download[0]})
                    debrid.post('https://api.real-debrid.com/rest/1.0/torrents/selectFiles/' + str(response.id), {'files':'all'})
                    return True
        print('done')
        sys.stdout.flush()
        return False
    #Monitor Function
    def monitor():
        response = debrid.get('https://api.real-debrid.com/rest/1.0/torrents')
        if not response == None and isinstance(response,list):
            for torrent in response:
                if torrent.status == 'downloaded':
                    torrent.Releases = [releases('[debrid]','hoster',torrent.filename,None,None,torrent.links),]
                    debrid.download(torrent,query=torrent.filename)
                    debrid.delete('https://api.real-debrid.com/rest/1.0/torrents/delete/' + str(torrent.id))
        elif hasattr(response,'error'):
            print('[' + str(datetime.datetime.now()) + '] debrid error: ' + str(response.error))
            sys.stdout.flush()
        else:
            print('[' + str(datetime.datetime.now()) + '] debrid error: could not get content')
            sys.stdout.flush()
    #Collected Method
    def collected(query):
        collected = False
        altquery = copy.deepcopy(query)
        if regex.search(r'(S[0-9][0-9])',altquery):
            altquery = regex.split(r'(S[0-9]+)',altquery) 
            altquery = altquery[0] + '[0-9]*.*' + altquery[1] + altquery[2]
        try:
            files = os.listdir(debrid.mount.destination) 
            for file in files:
                if regex.match(r'('+altquery+')',file,regex.I):
                    collected = True
        except:
            collected = False
        return collected
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
    #Scrape Classes
    class scrape: 
        def __new__(cls,query):
            print ('done')
            print('[' + str(datetime.datetime.now()) + '] scraping sources for query "' + query + '" ...' , end = ' ')
            sys.stdout.flush()
            scraped_releases = []
            scraped_releases += releases.scrape.rarbg(query)
            scraped_releases += releases.scrape.x1337(query)
            releases.sort(scraped_releases)
            print('done - found ' + str(len(scraped_releases)) + ' releases')
            sys.stdout.flush()
            return scraped_releases       
        class rarbg:
            token = 'r05xvbq6ul'
            session = requests.Session()
            def __new__(cls,query):
                altquery = copy.deepcopy(query)
                if regex.search(r'(S[0-9][0-9])',altquery):
                    altquery = regex.split(r'(S[0-9]+)',altquery) 
                    altquery = altquery[0] + '[0-9]*.*' + altquery[1] + altquery[2]
                scraped_releases = []
                headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
                response = None
                retries = 0
                while not hasattr(response, "torrent_results") and retries < 5:
                    if regex.search(r'(tt[0-9]+)',query,regex.I):
                        url = 'https://torrentapi.org/pubapi_v2.php?mode=search&search_imdb=' + str(query) + '&ranked=0&category=52;51;50;49;48;45;44;41;17;14&token=' + releases.scrape.rarbg.token + '&limit=100&format=json_extended&app_id=fuckshit'
                    else:
                        url = 'https://torrentapi.org/pubapi_v2.php?mode=search&search_string=' + str(query) + '&ranked=0&category=52;51;50;49;48;45;44;41;17;14&token=' + releases.scrape.rarbg.token + '&limit=100&format=json_extended&app_id=fuckshit'
                    try:
                        response = releases.scrape.rarbg.session.get(url, headers = headers)
                        if len(response.content) > 10:
                            response = json.loads(response.content, object_hook=lambda d: SimpleNamespace(**d))
                            if hasattr(response, "error"):
                                if 'Invalid token' in response.error:
                                    print('[' + str(datetime.datetime.now()) + '] rarbg error: ' + response.error)
                                    sys.stdout.flush()
                                    print('[' + str(datetime.datetime.now()) + '] fetching new token ...')
                                    sys.stdout.flush()
                                    url = 'https://torrentapi.org/pubapi_v2.php?get_token=get_token&app_id=fuckshit'
                                    response = releases.scrape.rarbg.session.get(url, headers = headers)
                                    if len(response.content) > 5:
                                        response = json.loads(response.content, object_hook=lambda d: SimpleNamespace(**d))
                                        releases.scrape.rarbg.token = response.token 
                                    else:
                                        print('[' + str(datetime.datetime.now()) + '] rarbg error: could not fetch new token')
                                        sys.stdout.flush()
                                elif hasattr(response, "rate_limit"):
                                    retries += -1
                    except:
                        response = None
                        print('[' + str(datetime.datetime.now()) + '] rarbg error: exception')
                        sys.stdout.flush()
                    retries += 1
                    time.sleep(2+random.randint(0, 3))
                if hasattr(response, "torrent_results"):
                    for result in response.torrent_results:
                        if regex.match(r'('+ altquery.replace('.','\.') + ')',result.title,regex.I):
                            release = releases('[rarbg]','torrent',result.title,[],float(result.size)/1000000000,[result.download])
                            scraped_releases += [release]   
                return scraped_releases 
        class x1337:
            session = requests.Session()
            def __new__(cls,query):
                altquery = copy.deepcopy(query)
                if regex.search(r'(S[0-9][0-9])',altquery):
                    altquery = regex.split(r'(S[0-9]+)',altquery) 
                    altquery = altquery[0] + '[0-9]*.*' + altquery[1] + altquery[2]
                scraped_releases = []
                headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
                url = 'https://1337x.to/search/' + str(query) + '/1/'
                try:
                    response = releases.scrape.x1337.session.get(url, headers = headers)
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
                                response = releases.scrape.x1337.session.get( 'https://1337x.to'+link, headers = headers)
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
                    print('[' + str(datetime.datetime.now()) + '] 1337x error: exception')
                    sys.stdout.flush()
                return scraped_releases
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
    #Query Method
    def query(element:plex.media):
        queries = []
        if element.type == 'movie':
            title = releases.rename(element.title)
            queries = [title + '.' + str(element.year)]
        if element.type == 'show':
            title = releases.rename(element.title)
            for season in element.Seasons:
                episode_queries = []
                for episode in season.Episodes:
                    episode_queries += [title + '.S' + str("{:02d}".format(season.index)) + 'E' + str("{:02d}".format(episode.index))+ '.']
                season_query = title + '.S' + str("{:02d}".format(season.index)) + '.'
                queries += [[season_query,episode_queries],]
        return queries
#Script Class
class download_script:   
    def run(): 
        ui.cls()    
        timeout = 10
        regular_check = 1800
        timeout_counter = 0
        old_watchlist = plex.watchlist()
        if len(old_watchlist) == 0:
            print('[' + str(datetime.datetime.now()) + '] checking new content ... done' )
            sys.stdout.flush()
        else:
            print('[' + str(datetime.datetime.now()) + '] checking new content ...', end=' ')
            sys.stdout.flush()
            printed = False
            for element in old_watchlist:
                if element.download():
                    printed = True
            if not printed:
                print('done')
        while True:   
            watchlist = plex.watchlist(old=old_watchlist)
            if len(watchlist) > 0:
                print('[' + str(datetime.datetime.now()) + '] checking new content ...', end=' ')
                sys.stdout.flush()
                printed = False
                for element in watchlist:
                    if element.download():
                        printed = True
                if not printed:
                    print('done')
                old_watchlist = plex.watchlist()
            elif timeout_counter >= regular_check:
                old_watchlist = plex.watchlist()
                timeout_counter = 0
                if len(old_watchlist) == 0:
                    print('[' + str(datetime.datetime.now()) + '] checking new content ... done' )
                    sys.stdout.flush()
                else:
                    print('[' + str(datetime.datetime.now()) + '] checking new content ...', end=' ')
                    sys.stdout.flush()
                    printed = False
                    for element in old_watchlist:
                        if element.download():
                            printed = True
                    if not printed:
                        print('done')
            else:
                debrid.monitor()
                timeout_counter += timeout
            time.sleep(timeout)
#Ui Preference Class:
class ui_settings:
    run_directly = "true"
#Ui Class
class ui:
    class option:
        def __init__(self,name,cls,key):
            self.name = name
            self.cls = cls
            self.key = key
        def input(self):
            func = getattr(self.cls,self.key)
            func()
    class setting:
        def __init__(self,name,prompt,cls,key,required=False):
            self.name = name
            self.prompt = prompt
            self.cls = cls
            self.key = key
            self.required = required
        def input(self):
            print('Current ' + self.name + ': "' + str(getattr(self.cls,self.key)) + '"')
            print()
            print('0) Back')
            print('1) Edit')
            print()
            choice = input('Choose an action: ')
            if choice == '1':
                if isinstance(getattr(self.cls,self.key),list):
                    lists = getattr(self.cls,self.key)
                    print()
                    print('0) Back')
                    print('1) Add entry')
                    if len(lists) > 0:
                        print('2) Edit entries')
                    print()
                    choice = input('Choose an action: ')
                    if choice == '1':
                        edit = []
                        for prompt in self.prompt:
                            edit += [input(prompt)]
                        lists += [edit]
                        setattr(self.cls,self.key,lists)
                        return True
                    if choice == '2':
                        print()
                        print('0) Back')
                        indices = []
                        for index,entry in enumerate(lists):
                            print(str(index+1)+') Edit entry ' + str(index+1) + ': ' + str(entry))
                            indices += [str(index+1)]
                        print()
                        index = input('Choose an entry: ')
                        back3 = False
                        while not back3:
                            if index == '0':
                                back3 = True
                            if index in indices:
                                print()
                                print('Entry '+index+': ' + str(lists[int(index)-1]))
                                print()
                                print('0) Back')
                                print('1) Edit')
                                print('2) Delete')
                                if len(lists) > 1:
                                    print('3) Move')
                                print()
                                choice = input('Choose an action: ')
                                back2 = False
                                while not back2:
                                    print()
                                    if choice == '0':
                                        back2 = True
                                    if choice == '1':
                                        edit = []
                                        for k,prompt in enumerate(self.prompt):
                                            edit += [input(prompt + '- currently "'+lists[int(index)-1][k]+'": ')]
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
                                            choice = input('Move entry ' + index + ' to: ')
                                            if choice == '0':
                                                back = True
                                            if choice in indices:
                                                lists.insert(int(choice)-1,lists[int(index)-1])
                                                del lists[int(index)-1]
                                                setattr(self.cls,self.key,lists)
                                                return True
                                

                else:        
                    console_input = input(self.prompt)
                    setattr(self.cls,self.key,console_input)
                    return True
        def setup(self):
            if isinstance(getattr(self.cls,self.key),list):
                edit = []
                print(self.name + ' - current value: ' + str(getattr(self.cls,self.key)))
                print()
                lists = getattr(self.cls,self.key)
                for prompt in self.prompt:
                    edit += [input(prompt)]
                lists = [edit,]
                setattr(self.cls,self.key,lists)
            else:
                print(self.name + ' - current value: ' + str(getattr(self.cls,self.key)))
                print()
                console_input = input(self.prompt)
                setattr(self.cls,self.key,console_input)
        def set(self,value):
            setattr(self.cls,self.key,value)
        def get(self):
            return getattr(self.cls,self.key)
    settings_list = [
        ['Real Debrid Settings', [
            setting('Real Debrid API Key','Please enter your Real Debrid API Key: ',debrid,'api_key',required=True),
            ]
        ],
        ['Plex Settings',[
            setting('Plex users',['Please provide a name for this Plex user: ','Please provide the Plex token for this Plex user: '],plex,'users',required=True),
            setting('Plex server address','Please enter your Plex server address: ',plex.library,'url',required=True),
            setting('Plex "movies" library','Please enter the section number of the "movies" library, that should be refreshed after a movie download: ',plex.library,'movies',required=True),
            setting('Plex "shows" library','Please enter the section number of the "shows" library, that should be refreshed after a show download: ',plex.library,'shows',required=True)
            ]
        ],
        ['Scraper Settings',[
            setting('Release sorting',['Please specify what this sorting rule should to look for by providing one or more regex match group(s): ','Please specify in which release attribute ("title","source" or "size") this sorting rule should search: ','Please specify if the match should be interpreted as a number or as text ("number" or "text")','Please specify in which order the releases should be by ranked by this sorting rule ("0" = ascending or "1" = descending): '],releases.sort,'ranking'),
            ]
        ],
        ['UI Settings',[
            setting('Show Menu on Startup','Please enter "true" or "false": ',ui_settings,'run_directly'),
            ]
        ]

    ]
    def cls(path=''):
        os.system('cls' if os.name=='nt' else 'clear')
        ui.logo(path=path)
    def logo(path=''):
        print('           __                        __')
        print('    ____  / /__  _  __     _________/ /')
        print('   / __ \/ / _ \| |/_/    / ___/ __  / ')
        print('  / /_/ / /  __/>  <     / /  / /_/ /  ')
        print(' / .___/_/\___/_/|_|____/_/   \__,_/   ')
        print('/_/               /_____/              ')
        print()
        print(path)
        print()
    def settings():
        list = ui.settings_list
        ui.cls('Options/Settings/')
        print('0) Back')
        for index,category in enumerate (list):
            print(str(index+1) + ') ' + category[0])
        print()
        choice = input('Choose an action: ')
        if choice == '0':
            ui.options()
        else:
            ui.cls('Options/Settings/'+list[int(choice)-1][0]+'/')
            print('0) Back')
            for index,setting in enumerate (list[int(choice)-1][1]):
                print(str(index+1) + ') ' + setting.name)
            print()
            choice2 = input('Choose an action: ')
            for index,setting in enumerate (list[int(choice)-1][1]):
                if choice2 == str(index+1):
                    ui.cls('Options/Settings/'+list[int(choice)-1][0]+'/'+setting.name)
                    setting.input()
                    ui.settings()
            ui.settings()
    def options():
        list = [
            ui.option('Run',download_script,'run'),
            ui.option('Settings',ui,'settings'),
            ui.option('Save current settings',ui,'save'),
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
        ui.options()
    def setup():
        if os.path.exists('.\settings.json'):
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
    def load():
        with open('settings.json', 'r') as f:
            settings = json.loads(f.read())
        for category, load_settings in ui.settings_list:
            for setting in load_settings:
                setting.set(settings[setting.name])
    def run():
        if ui.setup():
            ui.options()
        else:
            ui.load()
            download_script.run()

#TODO
#season scrape like episode scrape with parent release check
#multiprocessing for watchlist creation and element download
#downloading boolean for element to check if in realdebrid uncached torrents

ui.run()