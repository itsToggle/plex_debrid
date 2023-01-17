#import modules
from base import *
from ui.ui_print import *
import releases

name = "rarbg"
token = 'r05xvbq6ul'
session = requests.Session()

def setup(cls, new=False):
    from scraper.services import setup
    setup(cls,new)

def scrape(query, altquery):
    from scraper.services import active
    global token
    scraped_releases = []
    if 'rarbg' in active:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
        response = None
        retries = 0
        while not hasattr(response, "torrent_results") and retries < 4:
            if regex.search(r'(tt[0-9]+)', query, regex.I):
                url = 'https://torrentapi.org/pubapi_v2.php?mode=search&search_imdb=' + str(
                    query) + '&ranked=0&category=52;51;50;49;48;46;45;44;41;17;14&token=' + token + '&limit=100&format=json_extended&app_id=fuckshit'
            else:
                url = 'https://torrentapi.org/pubapi_v2.php?mode=search&search_string=' + str(
                    query) + '&ranked=0&category=52;51;50;49;48;46;45;44;41;17;14&token=' + token + '&limit=100&format=json_extended&app_id=fuckshit'
            try:
                response = session.get(url, headers=headers)
                if not response.status_code == 429:
                    response = json.loads(response.content, object_hook=lambda d: SimpleNamespace(**d))
                    if hasattr(response, "error"):
                        if 'Invalid token' in response.error:
                            ui_print('rarbg error: ' + response.error, debug=ui_settings.debug)
                            ui_print('fetching new token ...', debug=ui_settings.debug)
                            url = 'https://torrentapi.org/pubapi_v2.php?get_token=get_token&app_id=fuckshit'
                            response = session.get(url, headers=headers)
                            if len(response.content) > 5:
                                response = json.loads(response.content,
                                                        object_hook=lambda d: SimpleNamespace(**d))
                                token = response.token
                            else:
                                ui_print('rarbg error: could not fetch new token', debug=ui_settings.debug)
                        elif hasattr(response, "rate_limit"):
                            retries += 0.1
                else:
                    retries += 0.1
            except:
                response = None
                ui_print('rarbg error: (parse exception)', debug=ui_settings.debug)
            retries += 1
            time.sleep(1 + random.randint(0, 2))
        if hasattr(response, "torrent_results"):
            for result in response.torrent_results:
                if regex.match(r'(' + altquery.replace('.', '\.').replace("\.*", ".*") + ')', result.title,
                                regex.I):
                    release = releases.release('[rarbg]', 'torrent', result.title, [], float(result.size) / 1000000000,
                                        [result.download], seeders=result.seeders)
                    scraped_releases += [release]
    return scraped_releases