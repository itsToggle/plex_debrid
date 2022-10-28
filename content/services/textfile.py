#import modules
from base import *
#import parent modules
from content import classes
from ui.ui_print import *

name = 'Local Text File'

class library():
    name = 'Local Media List'

    class ignore(classes.ignore):

        name = 'Local Ignore List'
        path = ''
        
        def add(self):
            try:
                #No method implemented yet
                if not self in classes.ignore.ignored:
                    classes.ignore.ignored += [self]
            except Exception as e:
                ui_print("plex error: couldnt ignore item: " + str(e), debug=ui_settings.debug)

        def remove(self):
            try:
                #No method implemented yet
                if self in classes.ignore.ignored:
                    classes.ignore.ignored.remove(self)
            except Exception as e:
                ui_print("plex error: couldnt un-ignore item: " + str(e), debug=ui_settings.debug)

        def check(self):
            try:
                #No method implemented yet
                if self.type == 'movie' or self.type == 'episode':
                    if hasattr(self, 'viewCount'):
                        if self.viewCount > 0:
                            if not self in classes.ignore.ignored:
                                classes.ignore.ignored += [self]
                            return True
                else:
                    if hasattr(self, 'viewedLeafCount'):
                        if self.viewedLeafCount >= self.leafCount:
                            if not self in classes.ignore.ignored:
                                classes.ignore.ignored += [self]
                            return True
                return False
            except Exception as e:
                ui_print("[plex] error: couldnt check ignore status for item: " + str(e), debug=ui_settings.debug)
                return False
    
def match(self):
    return None
