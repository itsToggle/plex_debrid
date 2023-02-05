from base import *
from ui.ui_print import *
import releases
#import child modules
from scraper import services

def scrape(query, altquery="(.*)"):
    ui_print('done')
    scrapers = services.sequential()
    if len(scrapers) == 0:
        scrapers = [services.get()]
    scraped_releases = []
    for sequence in scrapers:
        servicenames = "[" + ",".join(x.name for x in sequence) + "]"
        if regex.search(r'(tt[0-9]+)', query, regex.I):
            ui_print('scraping sources '+servicenames+' for IMDB ID "' + query + '" ...')
        else:
            ui_print('scraping sources '+servicenames+' for query "' + query + '" ...')
        ui_print('accepting titles that regex match "' + altquery + '" ...', debug=ui_settings.debug)
        results = [None] * len(sequence)
        threads = []
        for index, scraper_ in enumerate(sequence):
            t = Thread(target=multi_scrape, args=(scraper_, query, altquery, results, index))
            threads.append(t)
            try:
                t.start()
            except:
                ui_print("error starting new thread (perhaps maximum number of threads reached), will retry in 5 seconds and exit if it fails again.")
                time.sleep(5)
                t.start()
        # wait for the threads to complete
        for t in threads:
            t.join()
        for result in results:
            if not result == [] and not result == None:
                scraped_releases += result
        for release in scraped_releases:
            release.title = ''.join([i if ord(i) < 128 else '' for i in release.title])
        ui_print('done - found ' + str(len(scraped_releases)) + ' releases')
        if len(scraped_releases) > 0:
            break
    return scraped_releases

# Multiprocessing scrape method
def multi_scrape(cls, query, altquery, result, index):
    result[index] = cls.scrape(query, altquery)
