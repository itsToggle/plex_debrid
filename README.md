# plex_rd
Plex torrent streaming through RealDebrid, using the new Plex Discover feature.

**Using the new Plex Discover Feature, your Plex Home users can add movies/shows to their watchlist and they become available to stream in seconds.**

## In Action:

![Alt Text](https://i.ibb.co/4SmVGTG/final-6279217a77f1110078928cf3-366957.gif)

## Description:

*This python script makes use of my rclone fork, which allows you to mount the RealDebrid /downloads history as a virtual drive. After creating a plex library of this virtual drive, you can stream torrents that are cached on RealDebrid without the need to download them first.*

The plex watchlist of specified users is constantly checked for newly added movies/shows and newly released episodes of watchlisted shows.
Once new content is found, torrent indexers are scraped for the best, cached release on RealDebrid. The torrent is then added to RealDebrid and a library refresh is performed to make the newly added content available. 

- For a movie or a one-season tv shows this takes about 10 seconds
- For multi-season tv shows this may take a little longer, since all seasons will be added to RealDebrid.

## Setup:

**Pre-Setup:**

1. Install my rclone fork, follow the instructions: https://github.com/itsToggle/rclone_RD
2. Create a plex 'movie' library of the mounted virtual drive or add the mounted virtual drive to an existing 'movie' library.
3. Create a plex 'shows' library of the mounted virtual drive or add the mounted virtual drive to an existing 'shows' library.
4. *Recommendation: disable 'video preview thumbnails', disable 'intro detection', disable the scheduled task 'perfom extensive media analysis' to reduce the download traffic
5. You and your home users can now stream cached torrents from RealDebrid!

**Setup (will make this easier in future versions):**
1. Open the script in your favorite editor
2. In the class 'plex', edit the list 'users'. Give each user that is allowed to download new content a 'name' attribute and provide their plex-token in the 'token' attribute: e.g.: 
**users = [{'name':'admin','token':'your-admin-token'},{'name':'HomeUser1','token':'someones-token'},]**
3. in the subclass 'plex.library', change the variable 'url' to point to your server. e.g.:
**url = 'https://localhost:32400'**
4. in the subclass 'plex.library', change the variable 'movies' to the section number of your movies library. e.g. **movies = '1'**
5. in the subclass 'plex.library', change the variable 'shows' to the section number of your shows library. e.g. **shows = '1'**
6. in the class 'debrid', change the variable 'api_key' to your RealDebrid API key. e.g. **api_key = '...'**
7. Youre done!

## Usage:

- Simply run the script to start. 
- The Plex Watchlist of your specified users will polled for changes every 10 seconds, which is when it will try to find newly added content. 
- It will be updated entirely every 30 minutes, which is when it will try to find newly released episodes from watchlisted series.
- When some content could repeatedly not be downloaded, it will be marked as 'watched' in the Discovery feature of the first specified user. This will cause the scraper to ignore the content, until its marked as 'unwatched' again.
