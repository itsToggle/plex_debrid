# import modules
from base import *
from ui.ui_print import *
import releases

name = "orionoid"
token = ''
client_id = "GPQJBFGJKAHVFM37LJDNNLTHKJMXEAJJ"

default_opts = [["limitcount", "5"], ["sortvalue", "popularity"], [
    "streamtype", "torrent"], ["filename", "true"]]

session = custom_session()


def get(url):
    try:
        response = session.get(url, timeout=60)
        response = json.loads(
            response.content, object_hook=lambda d: SimpleNamespace(**d))
        return response
    except:
        return None


def oauth(code=""):
    if code == "":
        response = get('https://api.orionoid.com?keyapp=' +
                       client_id+'&mode=user&action=authenticate')
        return response.data.code, response.data.code
    else:
        response = None
        while response == None:
            response = get('https://api.orionoid.com?keyapp=' +
                           client_id+'&mode=user&action=authenticate&code=' + code)
            if not hasattr(response, 'data'):
                response = None
            time.sleep(5)
        return response.data.token


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
            if setting.name == "Orionoid API Key":
                setting.setup()
                if not cls.name in active:
                    active += [cls.name]


def scrape(query, altquery):
    from scraper.services import active
    if altquery == "(.*)":
        altquery = query
    type = ("show" if regex.search(
        r'(S[0-9]|complete|S\?[0-9])', altquery, regex.I) else "movie")
    opts = []
    for opt in default_opts:
        opts += ['='.join(opt)]
    opts = '&'.join(opts)
    if type == "show":
        s = (regex.search(r'(?<=S)([0-9]+)', altquery, regex.I).group()
             if regex.search(r'(?<=S)([0-9]+)', altquery, regex.I) else None)
        e = (regex.search(r'(?<=E)([0-9]+)', altquery, regex.I).group()
             if regex.search(r'(?<=E)([0-9]+)', altquery, regex.I) else None)
        if s == None or int(s) == 0:
            s = 1
        opts += '&numberseason=' + str(int(s))
        if not e == None and not int(e) == 0:
            opts += '&numberepisode=' + str(int(e))
    scraped_releases = []
    if regex.search(r'(tt[0-9]+)', altquery, regex.I):
        query = regex.search(r'(tt[0-9]+)', altquery, regex.I).group()
    if not 'orionoid' in active:
        return scraped_releases
    if regex.search(r'(tt[0-9]+)', query, regex.I):
        url = 'https://api.orionoid.com?token='+token + \
            '&mode=stream&action=retrieve&type=' + \
            type+'&idimdb='+query[2:] + '&' + opts
    else:
        url = 'https://api.orionoid.com?token='+token + \
            '&mode=stream&action=retrieve&type='+type+'&query='+query + '&' + opts
    response = get(url)
    if not hasattr(response, "data") or (hasattr(response, "data") and not hasattr(response.data, "streams")):
        try:
            ui_print('[orionoid] error: ' + response.result.message)
        except:
            ui_print('[orionoid] error: unknown error')
        return scraped_releases
    match = "None"
    try:
        if hasattr(response.data, "movie"):
            match = response.data.movie.meta.title + \
                ' ' + str(response.data.movie.meta.year)
        elif hasattr(response.data, "show"):
            match = response.data.show.meta.title + \
                ' ' + str(response.data.show.meta.year)
        ui_print("[orionoid] matched query: '" + query + "' to " + type + " '" + match + "' - found " + str(
            response.data.count.total) + " releases (total), retrieved " + str(response.data.count.retrieved), ui_settings.debug)
    except:
        None
    for result in response.data.streams:
        try:
            title = result.file.name.replace(' ', '.')
            size = (float(result.file.size) /
                    1000000000 if not result.file.size == None else 0)
            links = result.links
            seeds = (result.stream.seeds if not result.stream.seeds == None else 0)
            source = (
                result.stream.source if not result.stream.source == None else "unknown")
            scraped_releases += [releases.release(
                '[orionoid: '+source+']', 'torrent', title, [], size, links, seeds)]
        except:
            continue
    return scraped_releases
