#import modules
from base import *
from ui.ui_print import *
import releases

base_url = "http://127.0.0.1:9117"
api_key = ""
name = "jackett"
resolver_timeout = '1'
filter = "!status:failing,test:passed"
session = requests.Session()

def setup(cls, new=False):
    from settings import settings_list
    from scraper.services import active
    settings = []
    for category, allsettings in settings_list:
        for setting in allsettings:
            if setting.cls == cls:
                settings += [setting]
    if settings == []:
        if not cls.name in active:
            active += [cls.name]
    back = False
    if not new:
        while not back:
            print("0) Back")
            indices = []
            for index, setting in enumerate(settings):
                print(str(index + 1) + ') ' + setting.name)
                indices += [str(index + 1)]
            print()
            if settings == []:
                print("Nothing to edit!")
                print()
                time.sleep(3)
                return
            choice = input("Choose an action: ")
            if choice in indices:
                settings[int(choice) - 1].input()
                if not cls.name in active:
                    active += [cls.name]
                back = True
            elif choice == '0':
                back = True
    else:
        print()
        indices = []
        for setting in settings:
            if setting.name == "Jackett API Key" or setting.name == "Jackett Base URL":
                setting.setup()
                if not cls.name in active:
                    active += [cls.name]

def scrape(query, altquery):
    from scraper.services import active
    global base_url
    scraped_releases = []
    if 'jackett' in active:
        if base_url.endswith('/'):
            base_url = base_url[:-1]
        url = base_url + '/api/v2.0/indexers/' + filter + '/results?apikey=' + api_key + '&Query=' + query
        try:
            response = session.get(url, timeout=60)
        except requests.exceptions.Timeout:
            ui_print('[jackett] error: jackett request timed out. Reduce the number of jackett indexers, make sure your indexers are healthy and enable the jackett setting "CORS".')
            return []
        except :
            ui_print('[jackett] error: jackett couldnt be reached. Make sure your jackett base url is correctly formatted (default: http://localhost:9117).')
            return []
        if not response.status_code == 200:
            if response.status_code in [401,403]:
                ui_print('[jackett] error '+str(response.status_code)+': it seems your api key is not working.')
            else:
                ui_print('[jackett] error '+str(response.status_code)+': it seems jackett is reachable, but jackett returned an internal error.')
            return []
        try:
            response = json.loads(response.content, object_hook=lambda d: SimpleNamespace(**d))
        except:
            ui_print('[jackett] error: jackett didnt return any data.')
            return []
        for result in response.Results[:]:
            result.Title = result.Title.replace(' ', '.')
            result.Title = result.Title.replace(':', '').replace("'", '')
            result.Title = regex.sub(r'\.+', ".", result.Title)
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
        results = [None] * len(response.Results[:200])
        threads = []
        # start thread for each remaining release
        for index, result in enumerate(response.Results[:200]):
            t = Thread(target=multi_init, args=(resolve, result, results, index))
            threads.append(t)
            try:
                t.start()
            except:
                ui_print("[jackett] error: couldnt start resolver thread - retrying.")
                time.sleep(1)
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
        link = session.get(result.Link, allow_redirects=False, timeout=float(resolver_timeout))
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
