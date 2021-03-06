# plex_debrid
Plex torrent streaming through Debrid Services, using the new Plex Discover feature, Trakt lists and Overseerr.

**Using the new Plex Discover Feature, your Plex Home users can add movies/shows to their watchlist and they become available to stream in seconds.**

## In Action:

![nice](https://user-images.githubusercontent.com/71379623/178955976-cfd4b7b1-63c8-4940-8f4e-a4d5ebeaeaee.gif)

## Description:

*For this download automation to work, you need to mount your debrid service as a virtual drive. After creating a plex library of this virtual drive, you can stream torrents that are cached on your debrid service without the need to download them first.* 

The plex watchlist (aswell as the trakt watchlist and overseer requests) of specified users are constantly checked for newly added movies/shows and newly released episodes of watchlisted shows.
Once new content is found, torrent indexers are scraped for the best, cached release on selected debrid services. The torrent is then added to a suitable debrid service and a library refresh is performed to make the newly added content available. 

**For any debrid-cached content (movies, one-season tv shows or even multi-season tv shows) the entire process from watchlisting content to watching it takes about 10-20 seconds.**

This is a pre-alpha release. shits not ready! Feel free to check it out though, I will continously improve the speed, reliability and user-friendlyness.

## Features:
- Compatible with any OS (Mac, Linux, Windows, Android, FreeBSD, ...)
- Gathering Content from:
  - <img src="https://app.plex.tv/desktop/favicon.ico" height="16"> **[Plex (updated every 5s)](https://plex.tv/)**
  - <img src="https://hotio.dev/webhook-avatars/overseerr.png" height="16"> **[Overseerr (updated every 5s)](https://overseerr.dev/)**
  - <img src="https://walter.trakt.tv/hotlink-ok/public/favicon.ico" height="16"> **[Trakt (updated every 5s)](https://trakt.tv/)**
- Checking your Plex Library to avoid duplicate downloads
- Determining precise release dates and times, checking for early releases of movies
- Scraping Releases from:
  - <img src="https://user-images.githubusercontent.com/27040483/28728094-99f3e3f6-73c7-11e7-8f8d-28912dc6ac0d.png" height="16"> **[Jackett](https://github.com/Jackett/Jackett)**
  - <img src="https://prowlarr.com/img/favicon-32x32.png" height="16"> **[Prowlarr](https://github.com/Prowlarr/Prowlarr)**
  - <img src="https://progsoft.net/images/rarbg-icon-648af4dcc6ec63ee49d6c050af63d2547c74d46c.png" height="16"> **[RARBG](https://rarbg.to/)**
  - <img src="https://1337x.to/favicon.ico" height="16"> **[1337X](https://1337x.to/)**
- Sorting and selecting scraped releases by completely customizable rules
- Checking for cached releases and adding them to:
  - <img src="https://fcdn.real-debrid.com/0818/favicons/favicon.ico" height="16"> **[RealDebrid](https://real-debrid.com/)**
  - <img src="https://www.premiumize.me/favicon-16x16.png" height="16"> **[Premiumize](https://www.premiumize.me/)**
  - <img src="https://cdn.alldebrid.com/lib/images/default/favicon.png" height="16"> **[AllDebrid](https://alldebrid.com/)**
  - <img src="https://cdn.debrid-link.com/favicon.ico?i=2" height="16"> **[DebridLink](https://debrid-link.com/)**
  - <img src="https://app.put.io/assets/favicon-32x32.png" height="16"> **[PUT.io (no check for cached releases)](https://put.io/)**
- Performing a plex library refresh to make the content available on Plex

### Upcoming Features:
- 'local' downloading of content while streaming (optional)
- adding multiple versions of content (e.g. HDR and non-HDR versions or a version for each resolution etc) (optional)
- tell me your ideas! :)

## Setup:
For linux, mac and windows, the setup process does not require any additional preparation. For different operating systems, check out the information the fine people linked here have gathered:
<details>
  <summary><b><u>Help for your OS</u></b></summary>
  
  - **[FreeBSD (u/TheNicestRichtofen)](https://www.reddit.com/r/Piracy/comments/v5zpj7/comment/ibnikqh/?utm_source=share&utm_medium=web2x&context=3)**
  - **[Android](https://github.com/itsToggle/plex_debrid/tree/android)**
</details>

### 1) Mount your debrid services:

*For this download automation to work, you need to mount at least one debrid service as a virtual drive. I highly recommend using RealDebrid, as this service will recieve updates and new features from plex_debrid first.*

<details>
  <summary><b><u>Mounting RealDebrid</u></b></summary>
  
  Realdebrid has now implement support for WebDav, which means there is technically no need for my rclone fork anymore :)
  
  I do still recomend using my fork, since realdebrids WebDav does not (yet) allow for torrent file deletion through rclone, They do claim the torrent file deletion works with other webdav mount programs, which i have not been able to test yet. They did fix all other issues I mentioned in this repository though, and their WebDav is now just as fast if not faster than my fork. 
  
  **Mounting with my fork:**
  
  1. Install my rclone fork: https://github.com/itsToggle/rclone_rd
  2. configure rclone by running the command 'rclone config' (could be './rclone config' depending on your os)
  3. create a new remote by typing 'n'
  4. give your remote a name (e.g. 'your-remote')
  5. choose '47) realdebrid' as your remote type
  6. follow the rest of the prompted instructions, choose 'no advaced configuration'
  7. You can mount your newly created remote by running the command 'rclone cmount your-remote: X: --dir-cache-time=10s --vfs-cache-mode=full' (replace 'your-remote' with your remote name, replace X with a drive letter of your choice e.g 'X','Y','Z',...)
  8. You've successfuly created a virtual drive of your debrid service!
  
  *You can run rclone as a background service by adding the mounting tag '--no-console' (Windows) or '--deamon' (Linux, Mac, etc)*
  
  **Mounting with official rclone software (WebDav)**
  
  1. Install the official rclone software: https://github.com/rclone/rclone or my fork: https://github.com/itsToggle/rclone_rd
  2. configure rclone by running the command 'rclone config' (could be './rclone config' depending on your os)
  3. create a new remote by typing 'n'
  4. give your remote a name (e.g. 'your-remote')
  5. choose '42) WebDav' as your remote type
  6. enter 'https://dav.real-debrid.com/' as the server url
  7. choose option '5) (other)'
  8. enter your realdebrid user name as your user name
  9. choose option 'y) yes, enter in my own password'
  10. enter your webdav password (available in your account settings) as the password
  11. You can mount your newly created remote by running the command 'rclone mount your-remote X: --dir-cache-time=10s --vfs-cache-mode=full' (replace 'your-remote' with your remote name, replace X with a drive letter of your choice e.g 'X','Y','Z',...)
  12. You've successfuly created a virtual drive of your debrid service!
  
  *You can run rclone as a background service by adding the mounting tag '--no-console' (Windows) or '--deamon' (Linux, Mac, etc)*
</details>

<details>
  <summary><b><u>Mounting Premiumize</u></b></summary>
  
  1. Install the official rclone software: https://github.com/rclone/rclone or my fork: https://github.com/itsToggle/rclone_rd
  2. configure rclone by running the command 'rclone config' (could be './rclone config' depending on your os)
  3. create a new remote by typing 'n'
  4. give your remote a name (e.g. 'your-remote')
  5. choose '46) premiumize' as your remote type
  6. follow the rest of the prompted instructions, choose 'no advaced configuration'
  7. You can mount your newly created remote by running the command 'rclone mount your-remote: X: --dir-cache-time=10s --vfs-cache-mode=full' (replace 'your-remote' with your remote name, replace X with a drive letter of your choice e.g 'X','Y','Z',...)
  8. You've successfuly created a virtual drive of your debrid service!
  
  *You can run rclone as a background service by adding the mounting tag '--no-console' (Windows) or '--deamon' (Linux, Mac, etc)*
</details>

<details>
  <summary><b><u>Mounting AllDebrid</u></b></summary>
  
  1. Install the official rclone software: https://github.com/rclone/rclone or my fork: https://github.com/itsToggle/rclone_rd
  2. configure rclone by running the command 'rclone config' (could be './rclone config' depending on your os)
  3. create a new remote by typing 'n'
  4. give your remote a name (e.g. 'your-remote')
  5. choose '42) WebDav' as your remote type
  6. enter 'https://alldebrid.com/webdav/' as the server url
  7. choose option '5) (other)'
  8. enter an api key as your user name
  9. choose option 'y) yes, enter in my own password'
  10. enter 'eeeee' as the password
  11. You can mount your newly created remote by running the command 'rclone mount your-remote:links X: --dir-cache-time=10s --vfs-cache-mode=full' (replace 'your-remote' with your remote name, replace X with a drive letter of your choice e.g 'X','Y','Z',...)
  12. You've successfuly created a virtual drive of your debrid service!
  13. You will only be able to watch content from the "links" and "history" folder, not the "magnet" folder. The "links" folder is recommended and the one used in the mounting command above.
  
  *You can run rclone as a background service by adding the mounting tag '--no-console' (Windows) or '--deamon' (Linux, Mac, etc)*
</details>

<details>
  <summary><b><u>Mounting DebridLink</u></b></summary>
  
  1. Install the official rclone software: https://github.com/rclone/rclone or my fork: https://github.com/itsToggle/rclone_rd
  2. configure rclone by running the command 'rclone config' (could be './rclone config' depending on your os)
  3. create a new remote by typing 'n'
  4. give your remote a name (e.g. 'your-remote')
  5. choose '42) WebDav' as your remote type
  6. enter 'https://webdav.debrid.link' as the server url
  7. choose option '5) (other)'
  8. enter your debrid-link user name as your user name
  9. choose option 'y) yes, enter in my own password'
  10. enter your "passkey" (Available in your account) as the password
  11. You can mount your newly created remote by running the command 'rclone mount your-remote X: --dir-cache-time=10s --vfs-cache-mode=full' (replace 'your-remote' with your remote name, replace X with a drive letter of your choice e.g 'X','Y','Z',...)
  12. You've successfuly created a virtual drive of your debrid service!
  
  *You can run rclone as a background service by adding the mounting tag '--no-console' (Windows) or '--deamon' (Linux, Mac, etc)*
</details>

<details>
  <summary><b><u>Mounting PUT.io</u></b></summary>
  
  Here is a nicely written article from the put.io team on how to mount put.io using rclone:
  
  http://help.put.io/en/articles/3480094-plex-rclone
  
  *You can run rclone as a background service by adding the mounting tag '--no-console' (Windows) or '--deamon' (Linux, Mac, etc)*
</details>

### 2) Setup Plex:

1. Create a plex 'movie' library of the mounted virtual drive or add the virtual drive to an existing 'movie' library.
2. Create a plex 'shows' library of the mounted virtual drive or add the virtual drive to an existing 'shows' library.
3. *If you are running rclone on a Linux based OS and Plex cant find your mounted virtual drive, try adding the mounting tag '--allow-other'*
4. *Recommendation: disable 'video preview thumbnails', ~disable 'intro detection'~, disable the scheduled task 'perfom extensive media analysis' to reduce the download traffic*
5. You and your home users can now stream cached torrents from your debrid service/s!

### 3) Setup plex_debrid:

*The plex_debrid script can be run as a docker container (dockerized version) or by simply executing it with python 3 (standard version).*

<details>
  <summary><b><u>Standard Version:</u></b></summary>
  
  1. Run the script! (google "how to run a python script" ;) )
  2. The script will guide you through the initial setup.
  3. You're done!
  4. Choose option '1' to run the download automation. Choose option '2' to explore or edit the Settings or open the "settings.json" file the script creates after the first run.
  5. Read the rest of the README!
  
</details>

<details>
  <summary><b><u>Dockerized Version:</u></b></summary>
  
  1. Run 'docker build -t plex_debrid .'
  2. Run 'docker run -ti plex_debrid'
  3. The script will guide you through the initial setup.
  4. You're done!
  5. Choose option '1' to run the download automation. Choose option '2' to explore or edit the Settings or open the "settings.json" file the script creates after the first run.
  6. Read the rest of the README!
  
</details>

## Usage:

<details>
  <summary><b><u>Managing your Plex Content:</u></b></summary>
  
  - The Plex Watchlist and the Discover feature are only available for accounts that are linked to an email address - so no managed accounts.
  - You've already added one user in the initial setup. To allow content download by other users that youve invited to your Plex Home, create a new user by navigation to '/Settings/Content Services/Plex/Plex users/Edit/Add user'.
  - You and the users you've added can now browse the Discover part of Plex and download content by adding it to the Plex Watchlist.
  - By default, your *entire* Plex Library (including shares) is checked before downloading anything and the script will avoid duplicate downloads. To limit this library check to specific library sections, navigate to '/Settings/Content Services/Plex/Plex library check/Edit'
  - If you want to delete something from your Plex server, make sure that you've removed it from your Watchlist first. Otherwise the script will see that its in your watchlist and not on your server and will simply download it again.
  - By default, movies that you add to your Plex Watchlist are removed automatically once they are downloaded and shows stay in the Watchlist, because only shows that are in the Watchlist are monitored for newly released episodes. You can change which media type/s should be automatically removed from your watchlist by navigating to '/Settings/Content Services/Plex/Plex auto remove'
  - The script tries its best to avoid downloading unwanted (e.g. sample) files. If samples still show up on plex, you can create a .plexignore file and add it to the mounts parent directory (more info [here](https://support.plex.tv/articles/201381883-special-keyword-file-folder-exclusion/)).
  - The Plex Watchlist of your specified users will polled for changes every 5 seconds, which is when it will try to find newly added content. 
  - The Plex Watchlist will be updated entirely every 30 minutes, which is when it will try to find newly released episodes from watchlisted series. This is only done every 30 minutes, because building the whole watchlist can take more than a minute, depending on the amount of shows you have in there.
  - If you dont want to download a specific episode or season of a show, navigate to that show in the discovery feature and mark the episodes/seasons that you want to ignore as 'watched'. The watch status inside the discovery feature is not connected to the watch status inside your libraries.
  - When some content could repeatedly not be downloaded, it will be marked as 'watched' in the Discovery feature of the first specified user. This will cause the scraper to ignore the content, until its marked as 'unwatched' again.
  - You can explore and remove ignored content in the main menu.

</details>

<details>
  <summary><b><u>Integrating Trakt:</u></b></summary>
  
  - You can connect plex_debrid to trakt.tv to get more accurate release dates and times for your content. You can also add trakt watchlists from multiple users or public lists to be monitored for new content by plex_debrid.
  - To connect the script to trakt, navigate to '/Settings/Content Services/Trakt/Trakt users/Edit/Add user'. You can add an unlimited amount of users.
  - To monitor and download your users trakt watchlists or public lists, navigate to '/Settings/Content Services/Trakt/Trakt lists'. By default, no trakt watchlist is monitored for new content. The lists will be checked for new content every 5 seconds.
  - To match content from trakt to plex, its neccessary to have at least one movie and one show inside a library thats visible by plex_debrid. Thats because in order to accurately match content, a search by imdb/tmdb/tvdb ID is necessary - which currently only works by requesting a "Fix Match" call to an existing library item.

</details>

<details>
  <summary><b><u>Integrating Overseerr:</u></b></summary>
  
  - You can connect plex_debrid to overseerr to instantly and automatically download approved requests from selected users.
  - To connect the script to overseerr, navigate to '/Settings/Content Services/Overseerr'. 
  - By default, all approved requests from all overseerr users are downloaded by plex_debrid. To limit this feature to specific users, navigate to '/Settings/Content Services/Overseerr/Overseerr users'
  - To match requests from overseerr to plex, its neccessary to have at least one movie and one show inside a library thats visible by plex_debrid. Thats because in order to accurately match content, a search by imdb/tmdb/tvdb ID is necessary - which currently only works by requesting a "Fix Match" call to an existing library item.

</details>

<details>
  <summary><b><u>Integrating your favorite torrent indexers:</u></b></summary>
  
  - The only legacy scrapers currently integrated are for rarbg.to and 1337x.to 
  - Its recommended to install "jackett", a program that wraps a huge amount of torrent indexers (https://github.com/Jackett/Jackett). Once installed and setup, you can enable jackett by navigating to '/Settings/Scraper/Sources/Edit/Add source/jackett'. Once enabled, you can delete the legacy scrapers, since jackett can handle both 1337x and rarbg.
  - If you prefer Prowlarr over Jackett, you are able to integrate prowlarr in the same way as jackett. Prowlarr has stricted rate limits than jackett for some indexers (e.g. 1337x), which could cause plex_debrid to timeout the request to prowlarr and therefore find less releases than jackett.
  - You can now choose to use a specific debrid service for a specific torrent tracker by navigating to "/Settings/Debrid Services/Tracker specific Debrid Services". This comes in handy if you are using a private tracker that forces you to use a debrid service that will seed your torrents (e.g. debridlink).

</details>

<details>
  <summary><b><u>Download Automation Settings:</u></b></summary>
  
  - You can add more than one debrid service and change the order in which they should be checked for cached releases by navigating to '/Settings/Debrid Services/Edit'.
  - In order to scrape for a movie/show, plex_debrid renames the movie/show title. by default, some special characters are removed and spaces are replaced with dots. You can edit the replacement of other special characters (for example replacing '&' with 'and', etc.) by navigating to '/Settings/Scraper/Special character renaming'
  - If you don't want the main menu to show when you start the script and run the download automation right away, you can define this in the 'UI Settings' section of the 'Settings' menu. You can return to the main menu at any time by typing 'exit'.

</details>

<details>
  <summary><b><u>How releases are scraped</u></b></summary>
  
  The scraping of movies is pretty simple, there is not a lot to explain.
  
  When scraping for shows however, the scraper follows the steps below:
  - If more than 1 season is to be downloaded, the scraper searches for releases with the following query: 'some.show' - which usually returns all releases related to that show.
    - If more than 3 seasons are to be downloaded, the scraper looks for multi-season packs within the already scraped releases and tries to download one.
    - The scraper then looks for single-season packs for the remaining seasons within the already scraped releases.
    - If not all seasons could be downloaded, the scraper specifically searches for the missing seasons with the following query: 'some.show.S0X.'
  - If less than one entire season is to be downloaded or episodes are still missing, the scraper searches for releases with the following query: 'some.show.S0X' which usually returns all episodes and partial releases of that season.
    - If missing episodes are found within the already scraped releases, they are downloaded.
    - If there are still episodes missing, the scraper will look for the individual episodes with the following query: 'some.show.S0XE0X.'
  
  All that is done to minimize the amount of calls made to torrent indexers and to fetch the most episodes at once. The process is done via multiprosing to speed things up.
</details>
<details>
  <summary><b><u>Sorting and selecting scraped releases:</u></b></summary>
  
  The scrapers usually provide a whole bunch of releases. 
  Adding them all to your debrid services would clutter your library and slow things down. This is why this script automatically sorts the releases by completely customizable rules and picks the best one. The script provides some pretty ok rules by default.
  
  You can define a minimum and maximum release size to filter out any unwanted releases. By default, the minimum release size is 100MB.
  
  The sorting is done by providing an unlimited number of sorting 'rules'. Rules can be added, edited, delted or moved. The first rule has the highest priority, the last one the lowest. 

  Each rule consist of:
  - a regex match group that defines what we are looking for. Check out regexr.com to try out some regex match definitions.
  - an attribute definition that defines which attribute of the release we want to look in (can be the title, the source, or the size, or other special attributes that arent described further)
  - an interpretation method. This can be either:
    - "number" : the first regex match group will be interpreted as an integer and releases will be ranked by this number.
    - "text" : we will give each release a rank accoring to which match group its in.
  - lastly we define wheter to rank the releases in ascending or descending order.

  You can test out your current sorting rules by manually scraping for releases from the main menu. The returned releases are sorted by your current rules. If you follow the 'scraping steps' from the section above, you will be able to tell which releases would be automatically downloaded with your current settings.

  Lets make some rules: 

  <details>
    <summary><b><u>Example resolution sorting:</u></b></summary>

  We want to download releases up to our prefered resolution of 1080p.
  For this, we will choose the following setup:
  - regex definition: "(1080|720|480)(?=p)" - This is one match group, that matches either "1080", "720" or "480", followed by the letter "p". This is a typical Resolution definition of releases.
  - attribute definition: "title" - we want to look for this inside the release title
  - interpretation method: "number" - we want to sort the releases by the highest number to the lowest number
  - ascending/descending: "1" - 1 means descending. We want to sort the releases in decending order to get the highest resolution release.

  </details>

  <details>
    <summary><b><u>Example codec sorting:</u></b></summary>

  We want to download releases that use the x265 Codec, rather then the x264 codec. 
  For this, we will choose the following setup:
  - regex definition: "(h.?265|x.?265)|(h.?264|x.?264)" - These are two match groups, that match typical codec descriptions in the release titles
  - attribute definition: "title" - we want to look for this inside the release title
  - interpretation method: "text" - by choosing this, we define that the releases should be sorted by the match group they are in.
  - ascending/descending: "1" - 1 means descending. Descending in this context means, that the First matchgroup is preffered over the second matchgroup, and both are prefered over a release that doesnt match.

  </details>

  <details>
    <summary><b><u>Example release exclusion:</u></b></summary>

  We don't want to download releases that are HDR or 3D. For this rule to ne effective, we need to make it our first rule.
  For this, we will choose the following setup:
  - regex definition: "(\\.HDR\\.|\\.3D\\.)"
  - attribute definition: "title" - we want to look for this inside the release title
  - interpretation method: "text" - by choosing this, we define that the releases should be sorted by the match group they are in.
  - ascending/descending: "0" - 0 means ascending. Ascending in this context means, that releases that don't match are prefered over releases that do.

  </details>

  <details>
    <summary><b><u>Example size sorting:</u></b></summary>

  We want to sort or releases by size - this should be implemented as one of the last rules.
  For this, we will choose the following setup:
  - regex definition: "(.*)" - This is one match group that simply matches everything.
  - attribute definition: "size" - we want to look for this inside the release size
  - interpretation method: "number" - by choosing number, we define that the release size should be interpreted as a number.
  - ascending/descending: "0" - 0 means ascending. We want to select the smallest release.

  </details>

</details>

## Limitations:
- The plex discover API only provides a release date, not a release time for new episodes. This makes it hard to determined when to start looking for releases and when to ignore an episode. This script will only download episodes when its been a day since the air-date or if plex shows the episode as availabe on streaming services. It is recommended to connect this script to trakt.tv, to allow for more accurate release dates and times.
- This script is built around the Plex media type. In order to accurate match content from Overseerr and Trakt to Plex, its neccessary to have at least one movie and one show inside a library thats visible by plex_debrid. Thats because in order to accurately match content, a search by imdb/tmdb/tvdb ID is necessary - which currently only works by requesting a "Fix Match" call to an existing library item. Until Plex allows a universal search by ID, this is the best I can do.
- plex_debrid cannot destinguish between a truly empty library and a library that couldnt be reached because its offline (or not reachable for any other reason). In order to avoid unwanted behaviour, the script simply stops running whenever an empty library is encountered. You will need to manually add at least one media item to the libraries visible by plex_debrid, before the download automation can run savely.

## Buy me a beer/coffee? :)

I've written this automation because it's a hell of a lot of fun and because I've wanted a setup like this for a while. The continuation of this project does **not**, in any way, depend on monetary contributions. If you do want to buy me a beer/coffee, feel free to use my real-debrid [affiliate link](http://real-debrid.com/?id=5708990) or send a virtual beverage via [PayPal](https://www.paypal.com/paypalme/oidulibbe) :)

If you are thinking of moving your plex server to a VPS or dedicated remote server, consider checking out netcup.de - if you contact me, I can provide you with an affiliate coupon that will get you (and me ;) ) up to 3 months free hosting.

## Side Project/s:
Ive been working on a little side project that allows you to mock a plex server and fake its responses to your Plex clients. One use-case for this is adding download options to content from plex discover, making the download process even faster than the current plex_debrid script. Other way of downloading content is scraping for releases from the search bar, which allows you to add content thats not on Plex Discover. The initial setup process for this is very complicated and requires 2 PCs (or a VM / VPS), so I wont be releasing this any time soon. I did want to document that this is possible however, if you are interested in how this works let me know.

https://user-images.githubusercontent.com/71379623/178101695-30c2e960-05e0-4af6-b6a4-00af1d13032f.mp4
