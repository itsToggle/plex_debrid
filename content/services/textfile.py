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
                with open(library.ignore.path + "ignored.txt",'r') as f:
                    lines = f.read()
                with open(library.ignore.path + "ignored.txt",'a') as f:
                    if not self.query() + '\n' in lines:
                        f.write(self.query() + '\n')
                f.close()
                if not self in classes.ignore.ignored:
                    classes.ignore.ignored += [self]
            except Exception as e:
                ui_print("[local ignore list] error: couldnt ignore item: " + str(e), debug=ui_settings.debug)

        def remove(self):
            try:
                with open(library.ignore.path + "ignored.txt", "r") as f:
                    lines = f.readlines()
                with open(library.ignore.path + "ignored.txt", "w") as f:
                    for line in lines:
                        if self.query().lower() + '\n' == line.lower() or self.query().lower() == line.lower() or self.query().lower()[:-1] == line.lower():
                            continue
                        f.write(line)
                f.close()
                if self in classes.ignore.ignored:
                    classes.ignore.ignored.remove(self)
            except Exception as e:
                ui_print("[local ignore list] error: couldnt un-ignore item: " + str(e), debug=ui_settings.debug)

        def check(self):
            try:
                if os.path.exists(library.ignore.path + "ignored.txt"):
                    with open(library.ignore.path + "ignored.txt") as f:
                        ignored = f.readlines()
                    f.close()
                    for line in ignored:
                        if self.query().lower() + '\n' == line.lower() or self.query().lower() == line.lower() or self.query().lower()[:-1] == line.lower():
                            if not self in classes.ignore.ignored:
                                classes.ignore.ignored += [self]
                            return True
                    return False
                return False
            except Exception as e:
                ui_print("[local ignore list] error: couldnt check ignore status for item: " + str(e), debug=ui_settings.debug)
                return False
    
def match(self):
    return None
