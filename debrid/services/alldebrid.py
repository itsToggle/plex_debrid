#import modules
from base import *
from ui.ui_print import *
import releases

# (required) Name of the Debrid service
name = "All Debrid"
short = "AD"
# (required) Authentification of the Debrid service, can be oauth aswell. Create a setting for the required variables in the ui.settings_list. For an oauth example check the trakt authentification.
api_key = ""
# Define Variables
session = requests.Session()

def setup(cls, new=False):
    from debrid.services import setup
    setup(cls,new)

# Error Log
def logerror(response):
    if not response.status_code == 200:
        ui_print("[alldebrid] error "+str(response.status_code)+": " + str(response.content), debug=ui_settings.debug)
    if 'error' in str(response.content):
        try:
            response2 = json.loads(response.content, object_hook=lambda d: SimpleNamespace(**d))
            ui_print("[alldebrid] error "+str(response.status_code)+": " + response2.data[0].error.message)
        except:
            try:
                response2 = json.loads(response.content, object_hook=lambda d: SimpleNamespace(**d))
                ui_print("[alldebrid] error "+str(response.status_code)+": " + response2.error.message)
            except:
                ui_print("[alldebrid] error "+str(response.status_code)+": unknown error")
    if response.status_code == 401:
        ui_print("[alldebrid] error: 401: alldebrid api key does not seem to work. check your alldebrid settings.")

# Get Function
def get(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36',
        'authorization': 'Bearer ' + api_key}
    try:
        response = session.get(url + '&agent=plex_debrid', headers=headers)
        logerror(response)
        response = json.loads(response.content, object_hook=lambda d: SimpleNamespace(**d))
    except Exception as e:
        ui_print("[alldebrid] error: (json exception): " + str(e), debug=ui_settings.debug)
        response = None
    return response

# Post Function
def post(url, data):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36',
        'authorization': 'Bearer ' + api_key}
    try:
        response = session.post(url, headers=headers, data=data)
        logerror(response)
        response = json.loads(response.content, object_hook=lambda d: SimpleNamespace(**d))
    except Exception as e:
        ui_print("[alldebrid] error: (json exception): " + str(e), debug=ui_settings.debug)
        response = None
    return response

# (required) Download Function.
def download(element, stream=True, query='', force=False):
    cached = element.Releases
    if query == '':
        query = element.deviation()
    for release in cached[:]:
        # if release matches query
        if regex.match(r'(' + query + ')', release.title, regex.I) or force:
            if stream:
                # This request will add the torrent to the magnets directory of webdav. For shows, we're done after this.
                url = 'https://api.alldebrid.com/v4/magnet/instant?magnets[]=' + release.download[0]
                response = get(url)
                instant = False
                try:
                    instant = response.data.magnets[0].instant
                    if element.type != 'movie':
                        return True
                except:
                    continue
                if instant:
                    url = 'https://api.alldebrid.com/v4/magnet/upload?magnets[]=' + release.download[0]
                    response = get(url)
                    torrent_id = response.data.magnets[0].id
                    url = 'https://api.alldebrid.com/v4/magnet/status?id=' + str(torrent_id)
                    response = get(url)
                    total_size = response.data.magnets.size
                    torrent_files = response.data.magnets.links
                    torrent_links = []
                    for file in torrent_files:
                        torrent_links += [file.link]
                    if len(torrent_links) > 0:
                        rate_limit = 1 / 12
                        success = False
                        saved_links = []
                        files_response = requests.get("https://uptobox.com/api/link/info?fileCodes=" + ",".join(link.split("uptobox.com/")[1] for link in torrent_links), timeout=5000)
                        if not files_response.status_code == 200:
                            pass
                        files_data = json.loads(files_response.content)
                        files = files_data["data"]["list"]
                        for f in files:
                            # if file doesn't look like a video, ignore it
                            if "error" in f or f["file_name"].endswith(".nfo") or f["file_name"].endswith(".srt") or f["file_name"].endswith(".txt") or f["file_name"].endswith("png"):
                                continue
                            # if file is too small it's probably a sample or trailer, so ignore it
                            if int(f["file_size"]) <= 0.6 * total_size:
                                continue
                            link = "https://uptobox.com/" + f["file_code"]
                            url = 'https://api.alldebrid.com/v4/link/unlock?link=' + requests.utils.quote(link)
                            response = get(url)
                            if not response.status == 'success':
                                success = False
                                break
                            saved_links += [requests.utils.quote(link)]
                            success = True
                            time.sleep(rate_limit)
                        if success:
                            saved_links = '&links[]='.join(saved_links)
                            url = 'https://api.alldebrid.com/v4/user/links/save?links[]=' + saved_links
                            response = get(url)
                            ui_print('[alldebrid] adding cached release: ' + release.title)
                            url = 'https://api.alldebrid.com/v4/magnet/delete?id=' + str(torrent_id)
                            ui_print("[alldebrid] deleted torrent since links have been saved: " + str(torrent_id))
                            return True
                        else:
                            # delete failed torrent
                            return False
                    else:
                        # delete failed torrent
                        return False
            else:
                # Uncached Download Method for AllDebrid
                url = 'https://api.alldebrid.com/v4/magnet/upload?magnets[]=' + release.download[0]
                response = get(url)
                ui_print('[alldebrid] adding uncached release: ' + release.title)
                return True
    return False
    # (required) Check Function

def check(element, force=False):
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
        response = get(
            'https://api.alldebrid.com/v4/magnet/instant?magnets[]=' + '&magnets[]='.join(hashes[:200]))
        for i, release in enumerate(element.Releases):
            try:
                instant = response.data.magnets[i].instant
                if instant:
                    release.cached += ['AD']
                    # release.wanted = 0
                    # release.unwanted = 0
            except:
                continue