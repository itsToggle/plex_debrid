from base import *
from ui.ui_print import *
import releases
#import child modules
from scraper import services

def scrape(query, altquery="(.*)"):
    ui_print('done')
    if regex.search(r'(tt[0-9]+)', query, regex.I):
        ui_print('scraping sources for IMDB ID "' + query + '" ...')
    else:
        ui_print('scraping sources for query "' + query + '" ...')
    ui_print('accepting title that regex match "' + altquery + '" ...', debug=ui_settings.debug)
    scrapers = services.get()
    scraped_releases = []
    results = [None] * len(scrapers)
    threads = []
    for index, scraper_ in enumerate(scrapers):
        t = Thread(target=multi_scrape, args=(scraper_, query, altquery, results, index))
        threads.append(t)
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
    for release in scraped_releases:
        ui_print("found release: " + release.title,debug=ui_settings.debug)
    return scraped_releases

# Multiprocessing scrape method
def multi_scrape(cls, query, altquery, result, index):
    result[index] = cls.scrape(query, altquery)