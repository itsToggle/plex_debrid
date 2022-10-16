#import modules
from base import *
from ui.ui_print import *
import releases

# (required) Name of the Debrid service
name = "PUT.io"
short = "PUT"
# (required) Authentification of the Debrid service, can be oauth aswell. Create a setting for the required variables in the ui.settings_list. For an oauth example check the trakt authentification.
api_key = ""
client_id = "5843"
# Define Variables
session = requests.Session()

def setup(cls, new=False):
    from debrid.services import setup
    setup(cls,new)

# Error Log
def logerror(response):
    if not response.status_code == 200:
        ui_print("[put.io] error: " + str(response.content), debug=ui_settings.debug)
    if 'error' in str(response.content) and not response.status_code == 200:
        try:
            response2 = json.loads(response.content, object_hook=lambda d: SimpleNamespace(**d))
            ui_print("[put.io] error: " + response2.error_message)
        except:
            ui_print("[put.io] error: unknown error")
    if response.status_code == 401:
        ui_print(
            "[put.io] error: (401 unauthorized): put.io api key does not seem to work. check your put.io settings.")

# Get Function
def get(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36',
        'Content-Type': 'application/x-www-form-urlencoded', 'Authorization': 'Bearer ' + api_key}
    try:
        response = session.get(url, headers=headers)
        logerror(response)
        response = json.loads(response.content, object_hook=lambda d: SimpleNamespace(**d))
    except Exception as e:
        ui_print("[put.io] error: (json exception): " + str(e), debug=ui_settings.debug)
        response = None
    return response

# Post Function
def post(url, data):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36',
        'Content-Type': 'application/x-www-form-urlencoded', 'Authorization': 'Bearer ' + api_key}
    try:
        response = session.post(url, headers=headers, data=data)
        logerror(response)
        response = json.loads(response.content, object_hook=lambda d: SimpleNamespace(**d))
    except Exception as e:
        ui_print("[put.io] error: (json exception): " + str(e), debug=ui_settings.debug)
        response = None
    return response

# Oauth Method
def oauth(code=""):
    # I used the swaggerhub oauth redirection url for creating a put.io app, as putio doesnt provide a general redirection url :)
    if code == "":
        response = get('https://api.put.io/v2/oauth2/oob/code?app_id=' + client_id)
        return response.code, response.code
    else:
        response = None
        while response == None:
            response = get('https://api.put.io/v2/oauth2/oob/code/' + code)
            if not hasattr(response, 'oauth_token'):
                response = None
            elif response.oauth_token == None:
                response = None
            time.sleep(1)
        return response.oauth_token

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
                # Cached Download Method for put.io
                url = 'https://api.put.io/v2/transfers/add'
                response = post(url, 'url=' + release.download[0])
                try:
                    if hasattr(response, 'transfer'):
                        ui_print('[put.io] adding release: ' + release.title)
                        return True
                    else:
                        continue
                except:
                    continue
            else:
                # Uncached Download Method for put.io
                try:
                    url = 'https://api.put.io/v2/transfers/add'
                    response = post(url, 'url=' + release.download[0])
                    if hasattr(response, 'transfer'):
                        ui_print('[put.io] adding release: ' + release.title)
                        return True
                    else:
                        continue
                except:
                    continue
    return False
    # (required) Check Function

def check(element, force=False):
    # there is no official check method for putio.
    force