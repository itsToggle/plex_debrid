# plex_debrid
Plex/Emby/Jellyfin/Infuse torrent streaming through Debrid Services, using Plex Discover Watchlists, Trakt lists and Overseerr.

Using content services like plex discover, trakt and overseerr, your personal media server users can add movies/shows to their watchlist and they become available to stream in seconds.

### In Action:

![ezgif com-gif-maker](https://user-images.githubusercontent.com/71379623/185643627-45217303-75d8-4c9d-8c8b-41bb2e27fd87.gif)


### Description:

plex_debrid provides an easy way to add media content to your debrid service/s, which becomes instantly watchable when mounting your debrid service with a personal media server like plex/emby/jellyfin/infuse. The plex watchlists, trakt watchlists and overseer-requests of specified users are constantly checked for newly added movies/shows and newly released episodes of watchlisted shows. Once new content is found, torrent indexers are scraped for the best, cached release on selected debrid services. The torrent is then added to a suitable debrid service and a library refresh is performed to make the newly added content available. 

**For any debrid-cached content (movies, one-season tv shows or even multi-season tv shows) the entire process from watchlisting content to watching it takes about 10-20 seconds.**

This is a work in progress, and im not a professional programmer. shits not ready! Feel free to check it out though, I will continously improve the speed, reliability and user-friendlyness.

### Features:
- Compatible with any OS (Mac, Linux, Windows, Android, FreeBSD, ...)
- Gathering new content **every 5s** from:
   - <img src="https://app.plex.tv/desktop/favicon.ico" height="16"> **[Plex Watchlists](https://plex.tv/)**
   - <img src="https://walter.trakt.tv/hotlink-ok/public/favicon.ico" height="16"> **[Trakt public lists, watchlists and collections](https://trakt.tv/)**
   - <img src="https://hotio.dev/webhook-avatars/overseerr.png" height="16"> **[Overseerr Requests](https://overseerr.dev/)**
- Checking and maintaining your library for:
   - <img src="https://app.plex.tv/desktop/favicon.ico" height="16"> **[Plex Library](https://plex.tv/)**
   - <img src="https://walter.trakt.tv/hotlink-ok/public/favicon.ico" height="16"> **[Trakt Collection](https://trakt.tv/)**
- Determining precise release dates and times, checking for early releases of movies
- Scraping Releases from:
   - <img src="https://user-images.githubusercontent.com/27040483/28728094-99f3e3f6-73c7-11e7-8f8d-28912dc6ac0d.png" height="16"> **[Jackett](https://github.com/Jackett/Jackett)**
   - <img src="https://prowlarr.com/img/favicon-32x32.png" height="16"> **[Prowlarr](https://github.com/Prowlarr/Prowlarr)**
   - <img src="https://progsoft.net/images/rarbg-icon-648af4dcc6ec63ee49d6c050af63d2547c74d46c.png" height="16"> **[RARBG](https://rarbg.to/)**
   - <img src="https://1337x.to/favicon.ico" height="16"> **[1337X](https://1337x.to/)**
- Sorting and selecting scraped releases by completely customizable rules
- Selecting multiple versions of your requested content (e.g. HDR and SDR versions) by completely customizable rules
- Checking for cached releases and adding them to:
   - <img src="https://fcdn.real-debrid.com/0818/favicons/favicon.ico" height="16"> **[RealDebrid](https://real-debrid.com/)**
   - <img src="https://www.premiumize.me/favicon-16x16.png" height="16"> **[Premiumize](https://www.premiumize.me/)**
   - <img src="https://cdn.alldebrid.com/lib/images/default/favicon.png" height="16"> **[AllDebrid](https://alldebrid.com/)**
   - <img src="https://cdn.debrid-link.com/favicon.ico?i=2" height="16"> **[DebridLink](https://debrid-link.com/)**
   - <img src="https://app.put.io/assets/favicon-32x32.png" height="16"> **[PUT.io (no check for cached releases)](https://put.io/)**
- Refreshing your personal media server libraries to make the content available to watch for:
   - <img src="https://app.plex.tv/desktop/favicon.ico" height="16"> **[Plex](https://plex.tv/)**

## Setup:
For linux, mac and windows, the setup process does not require any additional preparation. For different operating systems, check out the information the fine people linked here have gathered:
<details>
  <summary><b><u>Help for your OS</u></b></summary>
  
  - **[FreeBSD (u/TheNicestRichtofen)](https://www.reddit.com/r/Piracy/comments/v5zpj7/comment/ibnikqh/?utm_source=share&utm_medium=web2x&context=3)**
  - **[Android](https://github.com/itsToggle/plex_debrid/tree/android)**
</details>

### 1) :open_file_folder: Mount your debrid services:

*For this download automation to work, you need to mount at least one debrid service as a virtual drive. I highly recommend using RealDebrid, as this service will recieve updates and new features from plex_debrid first.*
>
><details>
>  <summary><b><u><img src="https://fcdn.real-debrid.com/0818/favicons/favicon.ico" height="16"> Mounting RealDebrid</u></b></summary>
>  
>  Realdebrid has now implement support for WebDav, which makes it mountable with official rclone software.
>  
>  I do still recomend using my fork, since realdebrids WebDav does not allow for torrent file deletion through rclone and they limit the amount of torrents displayed to 200. They do claim the torrent file deletion works with other webdav mount programs, but i have not been able to test this yet. It also seems that the official realdebrid webdav is still slower and more bandwidth heavy than my rclone fork, because mounting the webdav leads to frequent re-discovering of already downloaded content. 
>  
>  **Mounting with my fork:**
>  
>  1. Install my rclone fork: https://github.com/itsToggle/rclone_rd
>  2. configure rclone by running the command 'rclone config' (could be './rclone config' and depending on your os, the filename could be './rclone-linux' or similar. If you get a permission denied error (linux & macos), run 'sudo chmod u+x rclone-linux', adjusted to the filename.)
>  3. create a new remote by typing 'n'
>  4. give your remote a name (e.g. 'your-remote')
>  5. choose '47) realdebrid' as your remote type
>  6. follow the rest of the prompted instructions, choose 'no advaced configuration'
>  7. You can mount your newly created remote by running the command 'rclone cmount your-remote: X: --dir-cache-time 10s --vfs-cache-mode full' (replace 'your-remote' with your remote name, replace X with a drive letter of your choice e.g 'X','Y','Z',...)
>  8. If you are running my rclone fork on Linux, replace "cmount" with "mount" in the command above.
>  9. You've successfuly created a virtual drive of your debrid service!
>  
>  *You can run rclone as a background service by adding the mounting tag '--no-console' (Windows) or '--deamon' (Linux, Mac, etc)*
> 
>  **Mounting with official rclone software (WebDav)**
>  
>  1. Install the official rclone software: https://github.com/rclone/rclone or my fork: https://github.com/itsToggle/rclone_rd
>  2. configure rclone by running the command 'rclone config' (could be './rclone config' depending on your os)
>  3. create a new remote by typing 'n'
>  4. give your remote a name (e.g. 'your-remote')
>  5. choose '45) WebDav' as your remote type
>  6. enter 'https://dav.real-debrid.com/' as the server url
>  7. choose option '5) (other)'
>  8. enter your realdebrid user name as your user name
>  9. choose option 'y) yes, enter in my own password'
>  10. enter your webdav password (available in your account settings) as the password
>  11. You can mount your newly created remote by running the command 'rclone mount your-remote:torrents X: --dir-cache-time 10s --vfs-cache-mode full' (replace 'your-remote' with your remote name, replace X with a drive letter of your choice e.g 'X','Y','Z',...)
>  12. You've successfuly created a virtual drive of your debrid service!
> 
>  *You can run rclone as a background service by adding the mounting tag '--no-console' (Windows) or '--deamon' (Linux, Mac, etc)*
></details>
>
><details>
>  <summary><b><u><img src="https://www.premiumize.me/favicon-16x16.png" height="16"> Mounting Premiumize</u></b></summary>
>  
>  1. Install the official rclone software: https://github.com/rclone/rclone or my fork: https://github.com/itsToggle/rclone_rd
>  2. configure rclone by running the command 'rclone config' (could be './rclone config' depending on your os)
>  3. create a new remote by typing 'n'
>  4. give your remote a name (e.g. 'your-remote')
>  5. choose '46) premiumize' as your remote type
>  6. follow the rest of the prompted instructions, choose 'no advaced configuration'
>  7. You can mount your newly created remote by running the command 'rclone mount your-remote: X: --dir-cache-time 10s --vfs-cache-mode full' (replace 'your-remote' with your remote name, replace X with a drive letter of your choice e.g 'X','Y','Z',...)
>  8. You've successfuly created a virtual drive of your debrid service!
>  
>  *You can run rclone as a background service by adding the mounting tag '--no-console' (Windows) or '--deamon' (Linux, Mac, etc)*
></details>
>
><details>
>  <summary><b><u><img src="https://cdn.alldebrid.com/lib/images/default/favicon.png" height="16"> Mounting AllDebrid</u></b></summary>
>  
>  1. Install the official rclone software: https://github.com/rclone/rclone or my fork: https://github.com/itsToggle/rclone_rd
>  2. configure rclone by running the command 'rclone config' (could be './rclone config' depending on your os)
>  3. create a new remote by typing 'n'
>  4. give your remote a name (e.g. 'your-remote')
>  5. choose '42) WebDav' as your remote type
>  6. enter 'https://alldebrid.com/webdav/' as the server url
>  7. choose option '5) (other)'
>  8. enter an api key as your user name
>  9. choose option 'y) yes, enter in my own password'
>  10. enter 'eeeee' as the password
>  11. You can mount your newly created remote by running the command 'rclone mount your-remote:links X: --dir-cache-time 10s --vfs-cache-mode full' (replace 'your-remote' with your remote name, replace X with a drive letter of your choice e.g 'X','Y','Z',...)
>  12. You've successfuly created a virtual drive of your debrid service!
>  13. You will only be able to watch content from the "links" and "history" folder, not the "magnet" folder. The "links" folder is recommended and the one used in the mounting command above.
>  
>  *You can run rclone as a background service by adding the mounting tag '--no-console' (Windows) or '--deamon' (Linux, Mac, etc)*
></details>
>
><details>
>  <summary><b><u><img src="https://cdn.debrid-link.com/favicon.ico?i=2" height="16"> Mounting DebridLink</u></b></summary>
>  
>  1. Install the official rclone software: https://github.com/rclone/rclone or my fork: https://github.com/itsToggle/rclone_rd
>  2. configure rclone by running the command 'rclone config' (could be './rclone config' depending on your os)
>  3. create a new remote by typing 'n'
>  4. give your remote a name (e.g. 'your-remote')
>  5. choose '42) WebDav' as your remote type
>  6. enter 'https://webdav.debrid.link' as the server url
>  7. choose option '5) (other)'
>  8. enter your debrid-link user name as your user name
>  9. choose option 'y) yes, enter in my own password'
>  10. enter your "passkey" (Available in your account) as the password
>  11. You can mount your newly created remote by running the command 'rclone mount your-remote X: --dir-cache-time 10s --vfs-cache-mode full' (replace 'your-remote' with your remote name, replace X with a drive letter of your choice e.g 'X','Y','Z',...)
>  12. You've successfuly created a virtual drive of your debrid service!
>  
>  *You can run rclone as a background service by adding the mounting tag '--no-console' (Windows) or '--deamon' (Linux, Mac, etc)*
></details>
>
><details>
>  <summary><b><u><img src="https://app.put.io/assets/favicon-32x32.png" height="16"> Mounting PUT.io</u></b></summary>
>  
>  Here is a nicely written article from the put.io team on how to mount put.io using rclone:
>  
>  http://help.put.io/en/articles/3480094-plex-rclone
>  
>You can mount your newly created remote by running the command 'rclone mount your-remote X: --dir-cache-time 10s --vfs-cache-mode full' (replace 'your-remote' with your remote name, replace X with a drive letter of your choice e.g 'X','Y','Z',...)
>  
>  *You can run rclone as a background service by adding the mounting tag '--no-console' (Windows) or '--deamon' (Linux, Mac, etc)*
></details>

### 2) :tv: Setup your personal media server:

*To stream content from your newly mounted virtual drive, its recommended to set up a personal media server like plex, emby or jellyfin. These services allow you to stream your content from outside your local network. You will have the best expirience when using plex, since you dont need any 3rd party website to download new content - you can simply add new movies/shows to your watchlist from inside any plex client app, wait a few seconds and then watch it (see the gif above). If you prefer emby or jellyfin as your personal media server, the only way to add new content is via trakt (for now). A different approach is to use media players like Infuse to access the mounted files, which too relies on trakt to add new content.*

><details>
>  <summary><b><u><img src="https://app.plex.tv/desktop/favicon.ico" height="16"> Setting up Plex:</u></b></summary>
>  
>  1. Create a plex 'movie' library of the mounted virtual drive or add the virtual drive to an existing 'movie' library.
>  2. Create a plex 'shows' library of the mounted virtual drive or add the virtual drive to an existing 'shows' library.
>  3. *If you are running rclone on a Linux based OS and Plex cant find your mounted virtual drive, try adding the mounting tag '--allow-other'*
>  4. *Recommendation: disable 'video preview thumbnails', ~disable 'intro detection'~, disable the scheduled task 'perfom extensive media analysis' to reduce the download traffic*
>  5. You and your home users can now stream cached torrents from your debrid service/s!
>  
>  </details>

more personal media server setup instructions to come soon.

### 3) :page_facing_up: Setup plex_debrid:

*The plex_debrid script can be run as a docker container (dockerized version) or by simply executing it with python 3 (standard version).*

><details>
>  <summary><b><u>Standard Version:</u></b></summary>
>  
>  0. Clone this repository with git or click on "code" (top right) and then "download zip" 
>  1. Run the script!
>  2. The script will guide you through the initial setup and the next steps. When setting up plex_debrid, you will be prompted to choose the 3 main services that this script connects:
>  3. Pick and setup at least one **content service** which plex_debrid should monitor for new content
>  4. Pick and setup a **library service**, which plex_debrid will use to determine your current media collection.
>  5. Pick and setup at least one **debrid service**, which plex_debrid will use to download content.
>  3. You're done!
>  4. Choose option '1' to run the download automation. Choose option '2' to explore or edit the Settings or open the "settings.json" file the script creates after the first run.
>  5. Read the rest of the README!
>  
></details>
>
><details>
>  <summary><b><u>Dockerized Version:</u></b></summary>
>  
>  0. Clone this repository with git or click on "code" (top right) and then "download zip" 
>  1. Run 'docker build -t plex_debrid .'
>  2. Run 'docker run -ti plex_debrid'
>  3. The script will guide you through the initial setup and the next steps. When setting up plex_debrid, you will be prompted to choose the 3 main services that this script connects:
>  4. Pick and setup at least one **content service** which plex_debrid should monitor for new content
>  5. Pick and setup a **library service**, which plex_debrid will use to determine your current media collection.
>  6. Pick and setup at least one **debrid service**, which plex_debrid will use to download content.
>  7. You're done!
>  8. Choose option '1' to run the download automation. Choose option '2' to explore or edit the Settings or open the "settings.json" file the script creates after the first run.
>  9. Read the rest of the README!
>  
></details>

## Usage:

*plex_debrid can be setup in a bunch of different ways, which this readme wont be able to cover. Feel free to ask any questions in the "discussions" section of this respository.*

### :tv: Content Services:

*The services that plex_debrid can monitor for new content.*

><details>
>  <summary><b><u><img src="https://app.plex.tv/desktop/favicon.ico" height="16"> Plex watchlists:</u></b></summary>
>  
>  - The Plex Watchlist and the Discover feature are only available for accounts that are linked to an email address - so no managed accounts.
>  - To allow content download from inside any plex client by yourself and other users, create a new user by navigation to '/Settings/Content Services/Plex/Plex users/Edit/Add user'.
>  - You and the users you've added can now browse the Discover part of Plex and download content by adding it to the Plex Watchlist.
>  - If you want to delete something from your Plex server, make sure that you've removed it from your Watchlist first. Otherwise the script will see that its in your watchlist and not on your server and will simply download it again.
>  - By default, movies that you add to your Plex Watchlist are removed automatically once they are downloaded and shows stay in the Watchlist, because only shows that are in the Watchlist are monitored for newly released episodes. You can change which media type/s should be automatically removed from your watchlist by navigating to '/Settings/Content Services/Plex/Plex auto remove'
>  - The script tries its best to avoid downloading unwanted (e.g. sample) files. If samples still show up on plex, you can create a .plexignore file and add it to the mounts parent directory (more info [here](https://support.plex.tv/articles/201381883-special-keyword-file-folder-exclusion/)).
>  - The Plex Watchlist of your specified users will polled for changes every 5 seconds, which is when it will try to find newly added content. 
>  - The Plex Watchlist will be updated entirely every 30 minutes, which is when it will try to find newly released episodes from watchlisted series. This is only done every 30 minutes, because building the whole watchlist can take more than a minute, depending on the amount of shows you have in there.
>  - If you dont want to download a specific episode or season of a show, navigate to that show in the discovery feature and mark the episodes/seasons that you want to ignore as 'watched'. The watch status inside the discovery feature is not connected to the watch status inside your libraries (by default).
>  - When some plex watchlisted content could repeatedly not be downloaded, it will be marked as 'watched' in the Discovery feature of the first specified user. This will cause the scraper to ignore the content, until its marked as 'unwatched' again.
>  - You can connect plex_debrid to trakt.tv to get more accurate release dates and times for your content.
>  - You can explore and remove ignored content in the main menu.
>
></details>
>
><details>
>  <summary><b><u><img src="https://walter.trakt.tv/hotlink-ok/public/favicon.ico" height="16"> Trakt watchlists, collections and public lists:</u></b></summary>
>  
>  - To connect the script to trakt, navigate to '/Settings/Content Services/Trakt/Trakt users/Edit/Add user'. You can add an unlimited amount of users.
>  - To monitor and download your users trakt watchlists, collections or public lists, navigate to '/Settings/Content Services/Trakt/Trakt lists'. By default, no trakt list is monitored for new content.
>  - Only movies and entire shows in the watchlists, public lists and collections are downloaded. Not single seasons or episodes (for now).
>  - The trakt watchlists of specified users is updated every 5s.
>  - Shows in the trakt collections of specified users are checked for newly released episodes every 30min.
>  - Public lists are updated every 30min.
>
></details>
>
><details>
>  <summary><b><u><img src="https://hotio.dev/webhook-avatars/overseerr.png" height="16"> Overseerr requests:</u></b></summary>
> 
>  - You can connect plex_debrid to overseerr to instantly and automatically download approved requests from selected users.
>  - To connect the script to overseerr, navigate to '/Settings/Content Services/Overseerr'. 
>  - By default, all approved requests from all overseerr users are downloaded by plex_debrid. To limit this feature to specific users, navigate to '/Settings/Content Services/Overseerr/Overseerr users'
>
></details>

### :open_file_folder: Library Service

*The services that plex_debrid can use to determine your current media collection.*

><details>
>  <summary><b><u><img src="https://app.plex.tv/desktop/favicon.ico" height="16"> Plex library:</u></b></summary>
>  
>  - To use your plex library as your library service, navigate to '/Settings/Library Service/Change library service/'
>  - If you choose your plex library as your library service, your *entire* Plex Library (including shares) is checked before downloading anything and the script will avoid duplicate downloads. To limit this library check to specific library sections, navigate to '/Settings/Library Service/Edit library service/Plex library check/Edit'
>
></details>
>
><details>
>  <summary><b><u><img src="https://walter.trakt.tv/hotlink-ok/public/favicon.ico" height="16"> Trakt collection:</u></b></summary>
>  
>  - To use one of your trakt users collections as your library service, navigate to '/Settings/Library Service/Change library service/'
>  - If you choose your trakt collection as your library service, your *entire* trakt collection is checked before downloading anything and the script will avoid duplicate downloads.
>  - Once content is downloaded, plex_debrid will mark it as collected for the specified trakt user. 
>
></details>

### :magnet: Debrid Services and Scraper Settings

*The services that plex_debrid can use to find and download torrents.*

><details>
>  <summary><b><u>Integrating your favorite torrent indexers:</u></b></summary>
>  
>  - The only legacy scrapers currently integrated are for rarbg.to and 1337x.to 
>  - Its recommended to install "jackett", a program that wraps a huge amount of torrent indexers (https://github.com/Jackett/Jackett). Once installed and setup, you can enable jackett by navigating to '/Settings/Scraper/Sources/Edit/Add source/jackett'. Once enabled, you can delete the legacy scrapers, since jackett can handle both 1337x and rarbg.
>  - If you prefer Prowlarr over Jackett, you are able to integrate prowlarr in the same way as jackett. Prowlarr has stricted rate limits than jackett for some indexers (e.g. 1337x), which could cause plex_debrid to timeout the request to prowlarr and therefore find less releases than jackett.
>  - You can now choose to use a specific debrid service for a specific torrent tracker by navigating to "/Settings/Debrid Services/Tracker specific Debrid Services". This comes in handy if you are using a private tracker that forces you to use a debrid service that will seed your torrents (e.g. debridlink,put.io).
>
></details>
>
><details>
>  <summary><b><u>Debrid service and download automation settings:</u></b></summary>
>  
>  - You can add more than one debrid service and change the order in which they should be checked for cached releases by navigating to '/Settings/Debrid Services/Edit'.
>  - In order to scrape for a movie/show, plex_debrid renames the movie/show title. by default, some special characters are removed and spaces are replaced with dots. You can edit the replacement of other special characters (for example replacing '&' with 'and', etc.) by navigating to '/Settings/Scraper/Special character renaming'
>  - If you don't want the main menu to show when you start the script and run the download automation right away, you can define this in the 'UI Settings' section of the 'Settings' menu. You can return to the main menu at any time by typing 'exit'.
>
></details>
>
><details>
>  <summary><b><u>Downloading multiple versions:</u></b></summary>
>  
>  - You can download multiple versions of your requested content (e.g. HDR and SDR versions, or a version for each resolution) by adding an unlimited amount of completely customizable version definitions
>  - You can add these version definition by navigating to "/Settings/Scraper Settings/Multiple Versions/Edit"
>  - You can negate the version definitions by adding a "!" as the first character
>  - Example: to download 2160p, 1080p and 720p releases, add the following versions: "(2160p)", "(1080p)" and "(720p)"
>  - Example: to download HDR and non-HDR releases, add the following versions: "(\.HDR\.)" and "!(\.HDR\.)"
>
></details>
>
><details>
>  <summary><b><u>How releases are scraped</u></b></summary>
>  
>  The scraping of movies is pretty simple, there is not a lot to explain.
>  
>  When scraping for shows however, the scraper follows the steps below:
>  - If more than 1 season is to be downloaded, the scraper searches for releases with the following query: 'some.show' - which usually returns all releases related to that show.
>    - If more than 3 seasons are to be downloaded, the scraper looks for multi-season packs within the already scraped releases and tries to download one.
>    - The scraper then looks for single-season packs for the remaining seasons within the already scraped releases.
>    - If not all seasons could be downloaded, the scraper specifically searches for the missing seasons with the following query: 'some.show.S0X.'
>  - If less than one entire season is to be downloaded or episodes are still missing, the scraper searches for releases with the following query: 'some.show.S0X' which usually returns all episodes and partial releases of that season.
>    - If missing episodes are found within the already scraped releases, they are downloaded.
>    - If there are still episodes missing, the scraper will look for the individual episodes with the following query: 'some.show.S0XE0X.'
>  
>  All that is done to minimize the amount of calls made to torrent indexers and to fetch the most episodes at once. The process is done via multiprosing to speed things up.
>  plex_debrid accepts releases whos title deviates a bit from the original search-query. This allows plex_debrid to download a release named "some.show.2018.season.1.S01", when the original search query was "some.show.S01". This usually works fine, but it does lead to problems when downloading shows which have similar titles like "NCIS" and "NCIS: Los Angeles". Im not sure how to find a good compromise solution.
></details>
><details>
>  <summary><b><u>Sorting and selecting scraped releases:</u></b></summary>
>  
>  The scrapers usually provide a whole bunch of releases. 
>  Adding them all to your debrid services would clutter your library and slow things down. This is why this script automatically sorts the releases by completely customizable rules and picks the best one. The script provides some pretty ok rules by default.
>  
>  You can define a minimum and maximum release size to filter out any unwanted releases. By default, the minimum release size is 100MB.
>  
>  The sorting is done by providing an unlimited number of sorting 'rules'. Rules can be added, edited, delted or moved. The first rule has the highest priority, the last one the lowest. 
>
>  Each rule consist of:
>  - a regex match group that defines what we are looking for. Check out regexr.com to try out some regex match definitions.
>  - an attribute definition that defines which attribute of the release we want to look in (can be the title, the source, or the size, or other special attributes that arent described further)
>  - an interpretation method. This can be either:
>    - "number" : the first regex match group will be interpreted as an integer and releases will be ranked by this number.
>    - "text" : we will give each release a rank accoring to which match group its in.
>  - lastly we define wheter to rank the releases in ascending or descending order.
>
>  You can test out your current sorting rules by manually scraping for releases from the main menu. The returned releases are sorted by your current rules. If you follow the 'scraping steps' from the section above, you will be able to tell which releases would be automatically downloaded with your current settings.
>
>  Lets make some rules: 
>
>  <details>
>    <summary><b><u>Example resolution sorting:</u></b></summary>
>
>  We want to download releases up to our prefered resolution of 1080p.
>  For this, we will choose the following setup:
>  - regex definition: "(1080|720|480)(?=p)" - This is one match group, that matches either "1080", "720" or "480", followed by the letter "p". This is a typical Resolution definition of releases.
>  - attribute definition: "title" - we want to look for this inside the release title
>  - interpretation method: "number" - we want to sort the releases by the highest number to the lowest number
>  - ascending/descending: "1" - 1 means descending. We want to sort the releases in decending order to get the highest resolution release.
>
>  </details>
>
>  <details>
>    <summary><b><u>Example codec sorting:</u></b></summary>
>
>  We want to download releases that use the x265 Codec, rather then the x264 codec. 
>  For this, we will choose the following setup:
>  - regex definition: "(h.?265|x.?265)|(h.?264|x.?264)" - These are two match groups, that match typical codec descriptions in the release titles
>  - attribute definition: "title" - we want to look for this inside the release title
>  - interpretation method: "text" - by choosing this, we define that the releases should be sorted by the match group they are in.
>  - ascending/descending: "1" - 1 means descending. Descending in this context means, that the First matchgroup is preffered over the second matchgroup, and both are prefered over a release that doesnt match.
>
>  </details>
>
>  <details>
>    <summary><b><u>Example release exclusion:</u></b></summary>
>
>  We don't want to download releases that are HDR or 3D. For this rule to ne effective, we need to make it our first rule.
>  For this, we will choose the following setup:
>  - regex definition: "(\\.HDR\\.|\\.3D\\.)"
>  - attribute definition: "title" - we want to look for this inside the release title
>  - interpretation method: "text" - by choosing this, we define that the releases should be sorted by the match group they are in.
>  - ascending/descending: "0" - 0 means ascending. Ascending in this context means, that releases that don't match are prefered over releases that do.
>
>  </details>
>
>  <details>
>    <summary><b><u>Example size sorting:</u></b></summary>
>
>  We want to sort or releases by size - this should be implemented as one of the last rules.
>  For this, we will choose the following setup:
>  - regex definition: "(.*)" - This is one match group that simply matches everything.
>  - attribute definition: "size" - we want to look for this inside the release size
>  - interpretation method: "number" - by choosing number, we define that the release size should be interpreted as a number.
>  - ascending/descending: "0" - 0 means ascending. We want to select the smallest release.
>
>  </details>
>
>  <details>
>    <summary><b><u>Example seeders sorting:</u></b></summary>
>
>  We want to sort or releases by the number of seeders.
>  For this, we will choose the following setup:
>  - regex definition: "(.*)" - This is one match group that simply matches everything.
>  - attribute definition: "seeders" - we want to look for this inside the releases seeders attribute
>  - interpretation method: "number" - by choosing number, we define that the releases number of seeders should be interpreted as a number.
>  - ascending/descending: "1" - 0 means descending. We want to select the release with the most seeders.
>
>  </details>
>
></details>

## Limitations:

><details>
>  <summary><b><u>Plex Limitations:</u></b></summary>
>  
>  - If plex is chosen as the library service, trakt and overseerr content needs to be matched to the plex media type. In order to accurate match content from Overseerr and Trakt to Plex, its neccessary to have at least one movie and one show inside a library thats visible by plex_debrid. Thats because in order to accurately match content, a search by imdb/tmdb/tvdb ID is necessary - which currently only works by requesting a "Fix Match" call to an existing library item. Until Plex allows a universal search by ID, this is the best I can do.
>  - plex_debrid cannot destinguish between a truly empty library and a library that couldnt be reached because its offline (or not reachable for any other reason). In order to avoid unwanted behaviour, the script simply stops running whenever an empty library is encountered. You will need to manually add at least one media item to the libraries visible by plex_debrid, before the download automation can run savely.
>  - The plex discover api only provides release dates, not precise release times. Its recommended to connect the script to trakt.tv, which enables plex_debrid to find more accurate release dates and even find out if movies can be downloaded before their actual release date.
>
></details>
>
><details>
>  <summary><b><u>Scraping Limitations:</u></b></summary>
>  
>  - plex_debrid accepts releases whos title deviates a bit from the original search-query. This allows plex_debrid to download a release named "some.show.2018.season.1.S01", when the original search query was "some.show.S01". This usually works fine, but it does lead to problems when downloading shows which have similar titles like "NCIS" and "NCIS: Los Angeles". Im not sure how to find a good compromise solution.
>
></details>

## Buy me a beer/coffee? :)

I've written this automation because it's a hell of a lot of fun and because I've wanted a setup like this for a while. The continuation of this project does **not**, in any way, depend on monetary contributions. If you do want to buy me a beer/coffee, feel free to use my real-debrid [affiliate link](http://real-debrid.com/?id=5708990) or send a virtual beverage via [PayPal](https://www.paypal.com/paypalme/oidulibbe) :)

If you are thinking of moving your plex server to a VPS or dedicated remote server, consider checking out netcup.de - if you contact me, I can provide you with an affiliate coupon that will get you (and me ;) ) up to 3 months free hosting.
