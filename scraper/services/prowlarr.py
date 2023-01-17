#import modules
from base import *
from ui.ui_print import *
import releases

base_url = "http://127.0.0.1:9696"
api_key = ""
name = "prowlarr"
session = requests.Session()

def setup(cls, new=False):
    from scraper.services import setup
    setup(cls,new)

def scrape(query, altquery):
    from scraper.services import active
    scraped_releases = []
    if 'prowlarr' in active:
        url = base_url + '/api/v1/search?query=' + query + '&type=search&limit=1000&offset=0'
        headers = {'X-Api-Key': api_key}
        try:
            response = session.get(url, headers=headers)
        except requests.exceptions.Timeout:
            ui_print('[prowlarr] error: prowlarr request timed out. Reduce the number of prowlarr indexers or make sure they are healthy.')
            return []
        except :
            ui_print('[prowlarr] error: prowlarr couldnt be reached. Make sure your prowlarr base url is correctly formatted (default: http://localhost:9696).')
            return []
        if response.status_code == 200:
            try:
                response = json.loads(response.content, object_hook=lambda d: SimpleNamespace(**d))
            except:
                ui_print('[prowlarr] error: prowlarr didnt return any data.')
                return []
            for result in response[:]:
                result.title = result.title.replace(' ', '.')
                result.title = result.title.replace(':', '').replace("'", '')
                result.title = regex.sub(r'\.+', ".", result.title)
                if not altquery == '(.*)':
                    variations = result.title.split('/')
                    variations += result.title.split(']')
                    for variation in variations:
                        if regex.match(r'(' + altquery.replace('.', '\.').replace("\.*", ".*") + ')', variation,regex.I):
                            result.title = variation
                if regex.match(r'(' + altquery.replace('.', '\.').replace("\.*", ".*") + ')', result.title,regex.I) and result.protocol == 'torrent':
                    if hasattr(result, 'magnetUrl'):
                        if not result.magnetUrl == None:
                            if not result.indexer == None and not result.size == None:
                                scraped_releases += [
                                    releases.release('[prowlarr: ' + str(result.indexer) + ']', 'torrent', result.title,[], float(result.size) / 1000000000, [result.magnetUrl],seeders=result.seeders)]
                            elif not result.indexer == None:
                                scraped_releases += [
                                    releases.release('[prowlarr: ' + str(result.indexer) + ']', 'torrent', result.title,[], 1, [result.magnetUrl], seeders=result.seeders)]
                            elif not result.size == None:
                                scraped_releases += [
                                    releases.release('[prowlarr: unnamed]', 'torrent', result.title, [],float(result.size) / 1000000000, [result.magnetUrl],seeders=result.seeders)]
                            response.remove(result)
                else:
                    response.remove(result)
            # Multiprocess resolving of result.Link for remaining releases
            results = [None] * len(response)
            threads = []
            # start thread for each remaining release
            for index, result in enumerate(response):
                t = Thread(target=multi_init, args=(resolve, result, results, index))
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
        link = session.get(result.downloadUrl, allow_redirects=False, timeout=1)
        if 'Location' in link.headers:
            if regex.search(r'(?<=btih:).*?(?=&)', str(link.headers['Location']), regex.I):
                if not result.indexer == None and not result.size == None:
                    scraped_releases += [
                        releases.release('[prowlarr: ' + str(result.indexer) + ']', 'torrent', result.title, [],float(result.size) / 1000000000, [link.headers['Location']],seeders=result.seeders)]
                elif not result.indexer == None:
                    scraped_releases += [
                        releases.release('[prowlarr: ' + str(result.indexer) + ']', 'torrent', result.title, [], 1,[link.headers['Location']], seeders=result.seeders)]
                elif not result.size == None:
                    scraped_releases += [releases.release('[prowlarr: unnamed]', 'torrent', result.title, [],float(result.size) / 1000000000, [link.headers['Location']],seeders=result.seeders)]
            return scraped_releases
        elif link.headers['Content-Type'] == "application/x-bittorrent":
            magnet = releases.torrent2magnet(link.content)
            if not result.indexer == None and not result.size == None:
                scraped_releases += [
                    releases.release('[prowlarr: ' + str(result.indexer) + ']', 'torrent', result.title, [],float(result.size) / 1000000000, [magnet], seeders=result.seeders)]
            elif not result.indexer == None:
                scraped_releases += [
                    releases.release('[prowlarr: ' + str(result.indexer) + ']', 'torrent', result.title, [], 1,[magnet], seeders=result.seeders)]
            elif not result.size == None:
                scraped_releases += [releases.release('[prowlarr: unnamed]', 'torrent', result.title, [],float(result.size) / 1000000000, [magnet],seeders=result.seeders)]
            return scraped_releases
    except:
        ui_print("[prowlarr] error: resolver couldnt get magnet/torrent for release: " + result.title,ui_settings.debug)
        return scraped_releases
    
# Multiprocessing watchlist method
def multi_init(cls, obj, result, index):
    result[index] = cls(obj)
