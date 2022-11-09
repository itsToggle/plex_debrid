#import modules
from base import *
from ui.ui_print import *
import releases

base_url = "http://127.0.0.1:9117"
api_key = ""
name = "jackett"
session = requests.Session()

def setup(cls, new=False):
    from scraper.services import setup
    setup(cls,new)

def scrape(query, altquery):
    from scraper.services import active
    scraped_releases = []
    if 'jackett' in active:
        filter = "all"
        url = base_url + '/api/v2.0/indexers/' + filter + '/results?apikey=' + api_key + '&Query=' + query
        try:
            response = session.get(url, timeout=60)
        except:
            ui_print('[jackett] error: jackett request timed out.')
            return []
        if response.status_code == 200:
            try:
                response = json.loads(response.content, object_hook=lambda d: SimpleNamespace(**d))
            except:
                ui_print('[jackett] error: jackett didnt return any data.')
                return []
            for result in response.Results[:]:
                result.Title = result.Title.replace(' ', '.')
                result.Title = result.Title.replace(':', '').replace("'", '')
                result.Title = regex.sub(r'\.+', ".", result.Title)
                if not altquery == '(.*)':
                    variations = result.Title.split('/')
                    for variation in variations:
                        if regex.match(r'(' + altquery.replace('.', '\.').replace("\.*", ".*") + ')', variation,regex.I):
                            result.Title = variation
                if regex.match(r'(' + altquery.replace('.', '\.').replace("\.*", ".*") + ')', result.Title,regex.I):
                    if not result.MagnetUri == None:
                        if not result.Tracker == None and not result.Size == None:
                            scraped_releases += [
                                releases.release('[jackett: ' + str(result.Tracker) + ']', 'torrent', result.Title, [],float(result.Size) / 1000000000, [result.MagnetUri],seeders=result.Seeders)]
                        elif not result.Tracker == None:
                            scraped_releases += [
                                releases.release('[jackett: ' + str(result.Tracker) + ']', 'torrent', result.Title, [],1, [result.MagnetUri], seeders=result.Seeders)]
                        elif not result.Size == None:
                            scraped_releases += [releases.release('[jackett: unnamed]', 'torrent', result.Title, [],float(result.Size) / 1000000000, [result.MagnetUri],seeders=result.Seeders)]
                        response.Results.remove(result)
                else:
                    response.Results.remove(result)
            # Multiprocess resolving of result.Link for remaining releases
            results = [None] * len(response.Results)
            threads = []
            # start thread for each remaining release
            for index, result in enumerate(response.Results):
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
        link = session.get(result.Link, allow_redirects=False, timeout=1)
        if 'Location' in link.headers:
            if regex.search(r'(?<=btih:).*?(?=&)', str(link.headers['Location']), regex.I):
                if not result.Tracker == None and not result.Size == None:
                    scraped_releases += [
                        releases.release('[jackett: ' + str(result.Tracker) + ']', 'torrent', result.Title, [],float(result.Size) / 1000000000, [link.headers['Location']],seeders=result.Seeders)]
                elif not result.Tracker == None:
                    scraped_releases += [
                        releases.release('[jackett: ' + str(result.Tracker) + ']', 'torrent', result.Title, [], 1,[link.headers['Location']], seeders=result.Seeders)]
                elif not result.Size == None:
                    scraped_releases += [releases.release('[jackett: unnamed]', 'torrent', result.Title, [],float(result.Size) / 1000000000, [link.headers['Location']],seeders=result.Seeders)]
            return scraped_releases
        elif link.headers['Content-Type'] == "application/x-bittorrent":
            magnet = releases.torrent2magnet(link.content)
            if not result.Tracker == None and not result.Size == None:
                scraped_releases += [
                    releases.release('[jackett: ' + str(result.Tracker) + ']', 'torrent', result.Title, [],float(result.Size) / 1000000000, [magnet], seeders=result.Seeders)]
            elif not result.Tracker == None:
                scraped_releases += [
                    releases.release('[jackett: ' + str(result.Tracker) + ']', 'torrent', result.Title, [], 1, [magnet],seeders=result.Seeders)]
            elif not result.Size == None:
                scraped_releases += [
                    releases.release('[jackett: unnamed]', 'torrent', result.Title, [], float(result.Size) / 1000000000,[magnet], seeders=result.Seeders)]
            return scraped_releases
    except:
        ui_print("[jackett] error: resolver couldnt get magnet/torrent for release: " + result.Title,ui_settings.debug)
        return scraped_releases

# Multiprocessing watchlist method
def multi_init(cls, obj, result, index):
    result[index] = cls(obj)