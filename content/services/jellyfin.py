#import modules
from base import *
#import parent modules
from content import classes
from ui.ui_print import *

name = 'Jellyfin'
session = requests.Session()
api_key = ''

def logerror(response):
    if not response.status_code == 200 and hasattr(response,"content") and len(str(response.content)) > 0:
        ui_print("jellyfin error: " + str(response.content), debug=ui_settings.debug)
    if response.status_code == 401:
        ui_print("jellyfin error: (401 unauthorized): api token does not seem to work. check your jellyfin settings.")

def get(url, timeout=30):
    try:
        headers = {"X-MediaBrowser-Token": api_key}
        response = session.get(url, timeout=timeout, headers=headers)
        logerror(response)
        response = json.loads(response.content, object_hook=lambda d: SimpleNamespace(**d))
        return response
    except Exception as e:
        ui_print("jellyfin error: (json exception): " + str(e), debug=ui_settings.debug)
        return None

def post(url, data):
    try:
        headers = {"X-MediaBrowser-Token": api_key}
        response = session.post(url, data=data, headers=headers)
        logerror(response)
        response = json.loads(response.content, object_hook=lambda d: SimpleNamespace(**d))
        return response
    except Exception as e:
        ui_print("jellyfin error: (json exception): " + str(e), debug=ui_settings.debug)
        return None

class library():
    name = 'Jellyfin Library'
    url = 'http://localhost:8096'

    def setup(cls, new=False):
        from settings import settings_list
        if new:
            print()
            settings = []
            for category, allsettings in settings_list:
                for setting in allsettings:
                    settings += [setting]
            if len(api_key) == 0:
                print('Please specify your jellyfin api key:')
                print()
                for setting in settings:
                    if setting.name == 'Jellyfin API Key':
                        setting.setup()
                print()
            for setting in settings:
                if setting.name == 'Jellyfin server address':
                    setting.setup()
                    print()
            classes.library.active = [library.name]
        else:
            classes.library.setup(library)

    class refresh(classes.refresh):

        name = 'Jellyfin Libraries'

        def setup(cls, new=False):
            ui_cls("Options/Settings/Library Services/Library update services")
            from settings import settings_list
            settings = []
            for category, allsettings in settings_list:
                for setting in allsettings:
                    settings += [setting]
            if len(api_key) == 0:
                print("It looks like you havent setup a jellyfin api key. Please set up a jellyfin api key first.")
                print()
                for setting in settings:
                    if setting.name == "Jellyfin API Key":
                        setting.setup()
            working = False
            while not working:
                try:
                    headers = {"X-MediaBrowser-Token": api_key}
                    response = session.get(library.url  + '/System/Info',headers=headers)
                    while response.status_code == 401:
                        print("It looks like your jellyfin api key did not work.")
                        print()
                        for setting in settings:
                            if setting.name == "Jellyfin API Key":
                                setting.setup()
                        headers = {"X-MediaBrowser-Token": api_key}
                        response = session.get(library.url  + '/System/Info',headers=headers)
                    working = True
                except:
                    print("It looks like your jellyfin server could not be reached at '" + library.url + "'")
                    print()
                    for setting in settings:
                        if setting.name == "Jellyfin server address":
                            setting.setup()
                    print()
            if not new:
                back = False
                jellysettings = []
                for setting in settings:
                    if setting.name == "Jellyfin API Key" or setting.name == "Jellyfin server address":
                        jellysettings += [setting]
                while not back:
                    print("0) Back")
                    indices = []
                    for i,setting in enumerate(jellysettings):
                        print(str(i+1) + ") " + setting.name)
                        indices += str(i+1)
                    print()
                    choice2 = input("Choose an action")
                    if choice2 == '0':
                        back = True
                    elif choice2 in indices:
                        jellysettings[int(choice2)-1].setup()
            else:
                back = False
                while not back:
                    if not library.refresh.name in classes.refresh.active:
                        classes.refresh.active += [library.refresh.name]
                        print()
                        print("Successfully added jellyfin!")
                        print()
                        time.sleep(3)
                    return

        def __new__(cls, element):
            try:
                ui_print('[jellyfin] refreshing all libraries')
                url = library.url + '/Library/Refresh'
                response = post(url,"")
            except:
                print("[jellyfin] error: couldnt refresh libraries")

    def __new__(self):
        #not implemented yet
        list = []
        ui_print('[jellyfin] getting entire jellyfin library ...')
        url = library.url + '/users'
        response = get(url)
        for user in response:
            url = library.url + '/users/' + user.Id + '/Items?Recursive=true&fields=AirTime,CanDelete,CanDownload,ChannelInfo,Chapters,ChildCount,CumulativeRunTimeTicks,CustomRating,DateCreated,DateLastMediaAdded,DisplayPreferencesId,Etag,ExternalUrls,Genres,HomePageUrl,ItemCounts,MediaSourceCount,MediaSources,OriginalTitle,Overview,ParentId,Path,People,PlayAccess,ProductionLocations,ProviderIds,PrimaryImageAspectRatio,RecursiveItemCount,Settings,ScreenshotImageTags,SeriesPrimaryImage,SeriesStudio,SortName,SpecialEpisodeNumbers,Studios,BasicSyncInfo,SyncInfo,Taglines,Tags,RemoteTrailers,MediaStreams,SeasonUserData,ServiceName,ThemeSongIds,ThemeVideoIds,ExternalEtag,PresentationUniqueKey,InheritedParentalRatingValue,ExternalSeriesId,SeriesPresentationUniqueKey,DateLastRefreshed,DateLastSaved,RefreshState,ChannelImage,EnableMediaSourceDisplay,Width,Height,ExtraIds,LocalTrailerCount,IsHD,SpecialFeatureCount'
            response = get(url)
            response
        ui_print('done')
        if hasattr(response, 'MediaContainer'):
            if hasattr(response.MediaContainer, 'Metadata'):
                for element in response.MediaContainer.Metadata:
                    list += [classes.media(element)]
        else:
            ui_print(
                "[jellyfin error]: couldnt reach local jellyfin server at server address: " + library.url + " - or this library really is empty.")
        if len(list) == 0:
            ui_print(
                "[jellyfin error]: Your library seems empty. To prevent unwanted behaviour, no further downloads will be started. If your library really is empty, please add at least one media item manually.")
        return list

# Multiprocessing watchlist method
def multi_init(cls, obj, result, index):
    result[index] = cls(obj)
