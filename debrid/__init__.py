from base import *
#import child modules
from debrid import services

tracker = []
downloading = []
uncached = 'true'

# Download Method:
def download(element, stream=True, query='', force=False):
    downloaded_files = []
    if stream:
        cached_releases = copy.deepcopy(element.Releases)
        downloaded = False
        for release in cached_releases:
            element.Releases = [release, ]
            if len(tracker) > 0:
                for t, s in tracker:
                    if regex.search(t, release.source, regex.I):
                        release.cached = s
            for service in services.get():
                if service.short in release.cached:
                    if service.download(element, stream=stream, query=query, force=force):
                        downloaded = True
                        downloaded_files += element.Releases[0].files
                        break
            if downloaded:
                break
        if len(element.Releases) > 0:
            element.Releases[0].files = downloaded_files
        return downloaded
    else:
        scraped_releases = copy.deepcopy(element.Releases)
        downloaded = False
        for release in scraped_releases:
            element.Releases = [release, ]
            if len(tracker) > 0:
                for t, s in tracker:
                    if regex.search(t, release.source, regex.I):
                        release.cached = s
            for service in services.get():
                if len(release.cached) > 0:
                    if service.short in release.cached:
                        if service.download(element, stream=stream, query=query, force=force):
                            downloaded = True
                            downloaded_files += element.Releases[0].files
                            break
                else:
                    if service.download(element, stream=stream, query=query, force=force):
                        downloaded = True
                        downloaded_files += element.Releases[0].files
                        break
            if downloaded:
                break
        if len(element.Releases) > 0:
            element.Releases[0].files = downloaded_files
        return downloaded

# Check Method:
def check(element, force=False):
    for service in services.get():
        service.check(element, force=force)