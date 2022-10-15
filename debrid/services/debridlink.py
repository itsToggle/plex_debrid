#import modules
from base import *
from ui.ui_print import *
import releases
# (required) Name of the Debrid service
name = "Debrid Link"
short = "DL"
# (required) Authentification of the Debrid service, can be oauth aswell. Create a setting for the required variables in the ui.settings_list. For an oauth example check the trakt authentification.
api_key = ""
client_id = "0KLCzpbPTCsWZtQ9Ad0aZA"
# Define Variables
session = requests.Session()

def setup(cls, new=False):
    from debrid.services import setup
    setup(cls,new)

# Error Log
def logerror(response):
    if not response.status_code == 200:
        ui_print("[debridlink] error: " + str(response.content), debug=ui_settings.debug)
    if 'error' in str(response.content):
        try:
            response2 = json.loads(response.content, object_hook=lambda d: SimpleNamespace(**d))
            if not response2.error == 'authorization_pending':
                ui_print("[debridlink] error: " + response2.error)
        except:
            ui_print("[debridlink] error: unknown error")
    if response.status_code == 401:
        ui_print(
            "[debridlink] error: (401 unauthorized): debridlink api key does not seem to work. check your debridlink settings.")

# Get Function
def get(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Authorization': 'Bearer ' + api_key}
    try:
        response = session.get(url, headers=headers)
        logerror(response)
        response = json.loads(response.content, object_hook=lambda d: SimpleNamespace(**d))
    except Exception as e:
        ui_print("debridlink error: (json exception): " + str(e), debug=ui_settings.debug)
        response = None
    return response

# Post Function
def post(url, data):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Authorization': 'Bearer ' + api_key}
    try:
        response = session.post(url, headers=headers, data=data)
        logerror(response)
        response = json.loads(response.content, object_hook=lambda d: SimpleNamespace(**d))
    except Exception as e:
        ui_print("debridlink error: (json exception): " + str(e), debug=ui_settings.debug)
        response = None
    return response

# Oauth Method
def oauth(code=""):
    if code == "":
        response = post('https://debrid-link.fr/api/oauth/device/code',
                                            'client_id=' + client_id)
        return response.device_code, response.user_code
    else:
        response = None
        while response == None:
            response = post('https://debrid-link.fr/api/oauth/token',
                                                'client_id=' + client_id + '&code=' + code + '&grant_type=http%3A%2F%2Foauth.net%2Fgrant_type%2Fdevice%2F1.0')
            if hasattr(response, 'error'):
                response = None
            time.sleep(1)
        return response.access_token

# (required) Download Function.
def download(element, stream=True, query='', force=False):
    cached = element.Releases
    if query == '':
        query = element.deviation()
    for release in cached[:]:
        # if release matches query
        if regex.match(r'(' + query.replace('.', '\.').replace("\.*", ".*") + ')', release.title,
                        regex.I) or force:
            if stream:
                # Cached Download Method for debridlink
                hashstring = regex.findall(r'(?<=btih:).*?(?=&)', str(release.download[0]), regex.I)[0]
                url = 'https://debrid-link.fr/api/v2/seedbox/cached?url=' + hashstring
                response = get(url)
                try:
                    if hasattr(response.value, hashstring.lower()):
                        url = 'https://debrid-link.fr/api/v2/seedbox/add'
                        response = post(url, 'url=' + hashstring + '&async=true')
                        if response.success:
                            ui_print('[debridlink] adding cached release: ' + release.title)
                            return True
                except:
                    continue
            else:
                # Uncached Download Method for debridlink
                try:
                    url = 'https://debrid-link.fr/api/v2/seedbox/add'
                    response = post(url, 'url=' + release.download[0] + '&async=true')
                    if response.success:
                        ui_print('[debridlink] adding uncached release: ' + release.title)
                        return True
                except:
                    continue
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
            'https://debrid-link.fr/api/v2/seedbox/cached?url=' + ','.join(hashes[:200]))
        for i, release in enumerate(element.Releases):
            try:
                if hasattr(response.value, release.hash.lower()):
                    release.cached += ['DL']
                    # release.wanted = 0
                    # release.unwanted = 0
            except:
                continue