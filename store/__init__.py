def load(module,variable,doprint="true"):
    from ui.ui_print import ui_print
    from ui.ui_print import ui_settings
    from ui.ui_print import config_dir
    from base import pickle
    from base import os
    cache = []
    try:
        filename = config_dir + '/' + module + "_" + variable + '.pkl'
        if os.path.exists(filename):
            ui_print("["+module+"] reading cached "+variable+" file ...",doprint)
            with open(filename, 'rb') as f:
                cache = pickle.load(f)
            ui_print("done",doprint)
    except:
        ui_print("["+module+"] error: couldnt read cached "+variable+" file.")       
        cache = []
    return cache

def save(cache,module,variable,doprint="true"):
    from ui.ui_print import ui_print
    from ui.ui_print import ui_settings
    from ui.ui_print import config_dir
    from base import pickle
    from base import os
    try:
        filename = config_dir + '/' + module + "_" + variable + '.pkl'
        ui_print("["+module+"] writing cached "+variable+" file ...",doprint)    
        with open(filename, 'wb') as f:
            pickle.dump(cache, f)
        ui_print("done",doprint)
    except:
        ui_print("["+module+"] error: couldnt write cached "+variable+" file.") 
