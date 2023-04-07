#import modules
from base import *
from ui.ui_print import *
import releases

# (required) Name of the Debrid service
name = "Premiumize"
short = "PM"
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
        ui_print("[premiumize] error: " + str(response.content), debug=ui_settings.debug)
    if 'error' in str(response.content):
        response2 = json.loads(response.content, object_hook=lambda d: SimpleNamespace(**d))
        ui_print("[premiumize] error: " + response2.message)
    if response.status_code == 401:
        ui_print(
            "[premiumize] error: (401 unauthorized): premiumize api key does not seem to work. check your premiumize settings.")

# Get Function
def get(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36',
        'accept': 'application/json'}
    try:
        response = session.get(url + '&apikey=' + api_key, headers=headers)
        logerror(response)
        response = json.loads(response.content, object_hook=lambda d: SimpleNamespace(**d))
    except Exception as e:
        ui_print("[premiumize] error: (json exception): " + str(e), debug=ui_settings.debug)
        response = None
    return response

# Post Function
def post(url, data):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36',
        'accept': 'application/json', 'Content-Type': 'multipart/form-data'}
    try:
        response = session.post(url + '?apikey=' + api_key + data,
                                                    headers=headers, data={})
        logerror(response)
        response = json.loads(response.content, object_hook=lambda d: SimpleNamespace(**d))
    except Exception as e:
        ui_print("[premiumize] error: (json exception): " + str(e), debug=ui_settings.debug)
        response = None
    return response

# (required) Download Function.
def download(element, stream=True, query='', force=False):
    cached = element.Releases
    if query == '':
        query = element.deviation()
    for release in cached[:]:
        # if release matches query
        if regex.match(r'(' + query + ')', release.title,
                        regex.I) or force:
            if stream:
                # Cached Download Method for premiumize
                url = "https://www.premiumize.me/api/cache/check?items[]=" + release.download[0]
                response = get(url)
                if not response.response[0]:
                    continue
                url = "https://www.premiumize.me/api/transfer/create"
                data = '&src=' + release.download[0]
                response = post(url, data)
                if response.status == 'success':
                    ui_print('[premiumize] adding cached release: ' + release.title)
                    return True
            else:
                # Uncached Download Method for premiumize
                url = "https://www.premiumize.me/api/transfer/create"
                data = '&src=' + release.download[0]
                response = post(url, data)
                if response.status == 'success':
                    ui_print('[premiumize] adding uncached release: ' + release.title)
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
            'https://www.premiumize.me/api/cache/check?items[]=' + '&items[]='.join(hashes[:200]))
        for i, release in enumerate(element.Releases):
            try:
                instant = response.response[i]
                if instant:
                    release.cached += ['PM']
                    # release.wanted = 0
                    # release.unwanted = 0
            except:
                continue