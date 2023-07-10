from base import *
from content import classes
from ui.ui_print import *

name = "Mdblist"
settings = []
lists = {}
api_key = ''
_data = []

def setup_api_key(self):
    setting = self.settings[0]
    in_loop = True
    while in_loop:
        ui_cls("Options/Settings/Content Services/Content Services/" + self.name + "/API Key")
        key = input("Input your mdblist api key (0 to return back):")
        if key == "0":
            return
        setting.entry = key
        response = requests.get(f"https://mdblist.com/api/lists/user/?apikey={key}")
        if not response.ok:
            print(f"{response['error']} Please try again.")
        else:
            in_loop = False
    self.api_key = key

def setup_lists(self):
    response = requests.get(f"https://mdblist.com/api/lists/user/?apikey={self.api_key}")
    response = json.loads(response.text)

    while True:
        ui_cls("Options/Settings/Content Services/Content Services/" + self.name + "/lists")
        print("0) Back")
        print("1) Add")
        print("2) Remove")
        choice = input("Do you wish to add or remove lists:")
        match choice:
            case "1":
                while True:
                    ui_cls("Options/Settings/Content Services/Content Services/" + self.name + "/lists")
                    print("0) Back")
                    i = 0
                    list_dict = {}
                    for item in response:
                        value = { str(item["id"]):item["name"] }
                        if not str(item["id"]) in self.lists.keys():
                            name = item["name"]
                            print(f"{i + 1}) {name}")
                            list_dict.update({i: value})
                            i += 1
                    try:
                        choice = int(input("Choose list to add: "))
                        if choice == 0:
                            break
                        elif choice > len(response):
                            continue
                        else:
                            # self.lists[str(list_dict[choice - 1])] = list_dict[choice - 1]
                            self.lists.update(list_dict[choice - 1])
                    except(ValueError):
                        continue
            case "2":
                while True:
                    ui_cls("Options/Settings/Content Services/Content Services/" + self.name + "/lists")
                    print("0) Back")
                    i = 0
                    list_array = []
                    for id in self.lists:
                        name = self.lists[id]
                        print(f"{i + 1}) {name}")
                        list_array.append(id)
                        i += 1
                    try:
                        choice = int(input("Choose list to remove:"))
                        if choice == 0:
                            break
                        elif choice > len(self.lists):
                            continue
                        else:
                            id = list_array[choice - 1]
                            self.lists.pop(id)
                    except(ValueError):
                        continue
            case "0":
                break

def get(url):
    key = api_key
    response = requests.get(f"{url}/?apikey={key}")
    return json.loads(response.text)

def setup(self, new=False):
    from settings import settings_list
    for _, allsettings in settings_list:
        for setting in allsettings:
            if not setting in self.settings:
                if setting.cls == self:
                    self.settings += [setting]
    if not new:
        while True:
            if self.api_key:
                ui_cls("Options/Settings/Content Services/Content Services/" + self.name)
                print("0) Back")
                indices = []
                for index, setting in enumerate(settings):
                    print(str(index + 1) + ') ' + setting.name)
                    indices += [str(index + 1)]
                print()
                choice = input("Choose an action: ")
                match choice:
                    case "1":
                        setup_api_key(self)
                    case "2":
                        setup_lists(self)
                    case "0":
                        break
            else:
                setup_api_key(self)
                setup_lists(self)
                break

class watchlist(classes.watchlist):
    global _data
    refresh = False
    data = []

    def __init__(self):
        global settings
        try:
            if len(lists) >= 0:
                ui_print('[mdb] getting all lists ...')
        except:
            ui_print('[mdb] oops, you dont have mdb lists setup!')
            return

    def remove(self, item):
        from content.services.plex import users, library, current_library
        url = library.url
        _, token = users[0]
        if library.name == "Plex Library":
            for _section in library.check:
                if type(_section) is list:
                    _section = _section[0]
                headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
                response = requests.get(f"{url}/library/sections/{_section}/all?X-Plex-Token={token}", headers=headers)
                content = json.loads(response.text)
                for _item in content['MediaContainer']['Metadata']:
                    if _item['title'] == item.title:
                        for _media in item.watchlist.data:
                            item.watchlist.data.remove(_media)

    def update(self):
        for id in lists:
            list_items = get(f"https://mdblist.com/api/lists/{id}/items")
            threads = self.split_lists_to_threads(list_items)
            for t in threads:
                t.join()
        return self.refresh

    def split_lists_to_threads(self, lst):
        thread_count = os.cpu_count() // 2
        chunk_size = len(lst) // thread_count
        sublists = [lst[i:i+chunk_size] for i in range(0, len(lst), chunk_size)]

        threads = []
        for sublist in sublists:
            thread = Thread(target=self.multi_update, args=(sublist,))
            threads.append(thread)
            thread.start()

        return threads

    def multi_update(self, lst):
        from content.services.plex import current_library
        from content.services.trakt import show, movie, get as trakt_get

        for item in lst:
            try:
                match item['mediatype']:
                    case "show":
                        response = trakt_get(f"https://api.trakt.tv/search/imdb/{item['imdb_id']}?extended=full,type=show")[0][0]
                        _media_item = show(response.show)
                        _media_item.type = "show"
                    case "movie":
                        response = trakt_get(f"https://api.trakt.tv/search/imdb/{item['imdb_id']}?extended=full,type=movie")[0][0]
                        _media_item = movie(response.movie)
                        _media_item.type = "movie"
                if any(hasattr(x, "EID") and not x.EID[0] == _media_item.EID[0] for x in current_library):
                    self.data.append(_media_item)
                    ui_print(f"[mdb] {_media_item.type.capitalize()} \"{_media_item.title}\" found!")
                    self.refresh = True
            except IndexError or AttributeError:
                ui_print(f"[mdb error] Could not find {item['mediatype']} with imdb id: {item['imdb_id']}!", debug=ui_settings.debug)
            except Exception as e:
                ui_print("[mdb error]: (exception): " + str(e), debug=ui_settings.debug)