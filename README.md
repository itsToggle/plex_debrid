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
   - <img src="https://raw.githubusercontent.com/Fallenbagel/jellyseerr/main/public/android-chrome-512x512.png" height="16"> **[Jellyseerr Requests](https://github.com/Fallenbagel/jellyseerr)**
- Checking and maintaining your library for:
   - <img src="https://app.plex.tv/desktop/favicon.ico" height="16"> **[Plex Library](https://plex.tv/)**
   - <img src="https://walter.trakt.tv/hotlink-ok/public/favicon.ico" height="16"> **[Trakt Collection](https://trakt.tv/)**
- Determining precise release dates and times, checking for early releases of movies
- Scraping Releases from:
   - <img src="https://user-images.githubusercontent.com/27040483/28728094-99f3e3f6-73c7-11e7-8f8d-28912dc6ac0d.png" height="16"> **[Jackett](https://github.com/Jackett/Jackett)**
   - <img src="https://prowlarr.com/img/favicon-32x32.png" height="16"> **[Prowlarr](https://github.com/Prowlarr/Prowlarr)**
   - <img src="https://orionoid.com/web/images/logo/logo256.png" height="16"> **[Orionoid](https://orionoid.com/)**
   - <img src="https://progsoft.net/images/rarbg-icon-648af4dcc6ec63ee49d6c050af63d2547c74d46c.png" height="16"> **[RARBG](https://rarbg.to/)**
   - <img src="https://1337x.to/favicon.ico" height="16"> **[1337X](https://1337x.to/)**
- Defining multiple, completely customizable versions to download (2160p HDR, 1080p SDR, etc)
- Checking for cached releases and adding them to:
   - <img src="https://fcdn.real-debrid.com/0818/favicons/favicon.ico" height="16"> **[RealDebrid](http://real-debrid.com/?id=5708990)**
   - <img src="https://www.premiumize.me/favicon-16x16.png" height="16"> **[Premiumize](https://www.premiumize.me/)**
   - <img src="https://cdn.alldebrid.com/lib/images/default/favicon.png" height="16"> **[AllDebrid](https://alldebrid.com/)**
   - <img src="https://cdn.debrid-link.com/favicon.ico?i=2" height="16"> **[DebridLink](https://debrid-link.com/)**
   - <img src="https://app.put.io/assets/favicon-32x32.png" height="16"> **[PUT.io (no check for cached releases)](https://put.io/)**
- Refreshing your personal media server libraries (fully or partially) to make the content available to watch for:
   - <img src="https://app.plex.tv/desktop/favicon.ico" height="16"> **[Plex](https://plex.tv/)**
   - <img src="https://jellyfin.org/images/favicon.ico" height="16"> **[Jellyfin](https://jellyfin.org/)**
 
### Community

Feel free to ask any questions on github [discussions](https://github.com/itsToggle/plex_debrid/discussions) or create a new [issue](https://github.com/itsToggle/plex_debrid/issues) if you find a bug or have an idea for an improvement.

If github is not your cup of tee, join the plex_debrid [discord server](https://discord.gg/UKkPeRdukx) or find me on [reddit](https://www.reddit.com/user/itsToggle)
 
## Setup:

Aside from this general setup guide, here some step-by-step guides with specific examples for a few different operating systems:

<details>
  <summary><b><u>Step by Step for your OS:</u></b></summary>
  
  - **[Windows (Wiki)](https://github.com/itsToggle/plex_debrid/wiki/Setup-Guides#windows-setup)**
  - **[Linux Server (Wiki)](https://github.com/itsToggle/plex_debrid/wiki/Setup-Guides#linux-server-setup)**
  - **[Linux ARM Server (Wiki)](https://github.com/itsToggle/plex_debrid/wiki/Setup-Guides#linux-arm64-server-setup)**
  - **[FreeBSD (u/TheNicestRichtofen)](https://www.reddit.com/r/Piracy/comments/v5zpj7/comment/ibnikqh/?utm_source=share&utm_medium=web2x&context=3)**
  - **[Android](https://github.com/itsToggle/plex_debrid/tree/android)**
  - **Rooted Nvidia Shield guide from user "b u n n y" up on discord**
</details>

If you want to run plex_debrid on a VPS or Seedbox, please keep in mind that some debrid services block such IP addresses from accessing their servers:
<details>
  <summary><b><u>Help for a VPS/Seedbox Setup</u></b></summary>
  
  - **I do not encourage you to disregard your debrid services code of conduct.**
  - Debrid services like realdebrid block common VPS or Seedbox IP addresses. They do however have a list of whitelisted VPNs, behind which you can run your server. For realdebrid you can find this list on https://real-debrid.com/vpn . You can also use this address to check wether or not your servers IP is blocked by running the commands `curl -4 https://real-debrid.com/vpn | grep blocked` and `curl -6 https://real-debrid.com/vpn | grep blocked`. If you have the option, you can try to request a different IP address from your VPS provider, preferably your own personal IPv4 address which will most likely not be blocked.
</details>


### 1) :open_file_folder: Mount your debrid services:

*For this download automation to work, you need to mount at least one debrid service as a virtual drive. I highly recommend using RealDebrid, as this service will recieve updates and new features from plex_debrid first. Please keep in mind that most debrid services dont allow you to access their service from multiple IP addresses in parallel. This is not an issue if you have a Plex server running, since everything you stream through plex (from any location, no matter how many in parallel) is routed through your servers IP address. While you have your plex server running though, you should not download from your debrid service in any other way than through plex.*

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
>  7. You can mount your newly created remote by running the command 'rclone cmount your-remote: X: --dir-cache-time 10s' (replace 'your-remote' with your remote name, replace 'X' with a drive letter of your choice or replace 'X:' with a destination folder)
>  8. If you are running my rclone fork on Linux, replace "cmount" with "mount" in the command above.
>  9. You've successfuly created a virtual drive of your debrid service!
>  
>  *You can run rclone as a background service by adding the mounting tag '--no-console' (Windows) or '--deamon' (Linux, Mac, etc).*
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
>  11. You can mount your newly created remote by running the command 'rclone mount your-remote:torrents X: --dir-cache-time 10s' (replace 'your-remote' with your remote name, replace X with a drive letter of your choice or replace 'X:' with a destination folder)
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
>  7. You can mount your newly created remote by running the command 'rclone mount your-remote: X: --dir-cache-time 10s' (replace 'your-remote' with your remote name, replace X with a drive letter of your choice or replace 'X:' with a destination folder)
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
>  11. You can mount your newly created remote by running the command 'rclone mount your-remote:links X: --dir-cache-time 10s' (replace 'your-remote' with your remote name, replace X with a drive letter of your choice or replace 'X:' with a destination folder)
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
>  11. You can mount your newly created remote by running the command 'rclone mount your-remote X: --dir-cache-time 10s' (replace 'your-remote' with your remote name, replace X with a drive letter of your choice or replace 'X:' with a destination folder)
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
>You can mount your newly created remote by running the command 'rclone mount your-remote X: --dir-cache-time 10s' (replace 'your-remote' with your remote name, replace X with a drive letter of your choice or replace 'X:' with a destination folder)
>  
>  *You can run rclone as a background service by adding the mounting tag '--no-console' (Windows) or '--deamon' (Linux, Mac, etc)*
></details>

### 2) :tv: Setup your personal media server:

*To stream content from your newly mounted virtual drive, its recommended to set up a personal media server like plex, emby or jellyfin. These services allow you to stream your content from outside your local network. You will have the best expirience when using plex, since you dont need any 3rd party website to download new content - you can simply add new movies/shows to your watchlist from inside any plex client app, wait a few seconds and then watch it (see the gif above). If you prefer emby or jellyfin as your personal media server, the only way to add new content is via trakt and jellyseerr. A different approach is to use media players like Infuse to access the mounted files, which too relies on trakt to add new content.*

><details>
>  <summary><b><u><img src="https://app.plex.tv/desktop/favicon.ico" height="16"> Setting up Plex:</u></b></summary>
>  
>  1. Create a plex 'movie' library of the mounted virtual drive or add the virtual drive to an existing 'movie' library.
>  2. Create a plex 'shows' library of the mounted virtual drive or add the virtual drive to an existing 'shows' library.
>  3. *If you are running rclone on a Linux based OS and Plex cant find your mounted virtual drive, try adding the mounting tag '--allow-other'*
>  4. *Recommendation: disable 'video preview thumbnails', disable the scheduled task 'perfom extensive media analysis' to reduce the download traffic*
>  5. Disable the libary setting "Empty trash after every scan", to make sure that no content is removed accidentaly
>  6. You and your home users can now stream cached torrents from your debrid service/s!
>  
>  **Please keep your libraries metadata agent as the default Plex metadata agent**
>  </details>

### 3) :page_facing_up: Setup plex_debrid:

*The plex_debrid script can be run as a docker container (dockerized version) or by simply executing it with python 3 (standard version).*

><details>
>  <summary><b><u>Standard Version:</u></b></summary>
>  
>  0. Clone this repository with git or click on "code" (top right) and then "download zip" 
>  1. Open a terminal inside the downloaded plex_debrid-main folder. Run `pip install -r requirements.txt` - if you dont have pip yet, install it from https://pypi.org/project/pip/
>  2. Start the script by running `python ./main.py`
>  3. The script will guide you through the initial setup and the next steps. When setting up plex_debrid, you will be prompted to choose the 5 main services that this script connects:
>  4. Pick and setup at least one [**content service**](https://github.com/itsToggle/plex_debrid#tv-content-services) which plex_debrid should monitor for new content
>  5. Pick and setup a [**library collection service**](https://github.com/itsToggle/plex_debrid#open_file_folder-library-collection-service), which plex_debrid will use to determine your current media collection. If you intend to run a plex server, choose plex.
>  6. Pick and setup a [**library update service**](https://github.com/itsToggle/plex_debrid#-library-update-services), which plex_debrid will update/refresh after a successful download. If you intent to run a plex server, choose plex.
>  7. Pick and setup a [**library ignore service**](https://github.com/itsToggle/plex_debrid#eyes-library-ignore-services), which plex_debrid will use to ignore content. If you intent to run a plex server, choose plex.
>  8. Pick and setup at least one [**debrid service**](https://github.com/itsToggle/plex_debrid#arrow_down_small-debrid-services), which plex_debrid will use to download content.
>  9. You're done!
>  10. Choose option '1' to run the download automation. Choose option '2' to explore or edit the Settings or open the "settings.json" file the script creates after the first run. 
>  11. If you dont want the main menu to show when starting the script (for an auto-run setup), navigate to "/Settings/UI Settings/show menu on startup" and set the value to "false".
>  12. Read the rest of the README!
>  
></details>
>
><details>
>  <summary><b><u>Dockerized Version:</u></b></summary>
>   
>  1. Run `docker pull itstoggle/plex_debrid`or visit https://hub.docker.com/repository/docker/itstoggle/plex_debrid.
>  2. Run `docker run -v /path/to/config:/config --net host -ti itstoggle/plex_debrid` . Where `/path/to/config` is the directory path where you want to save your plex_debrid config data.
>  3. The script will guide you through the initial setup and the next steps. When setting up plex_debrid, you will be prompted to choose the 5 main services that this script connects:
>  4. Pick and setup at least one [**content service**](https://github.com/itsToggle/plex_debrid#tv-content-services) which plex_debrid should monitor for new content
>  5. Pick and setup a [**library collection service**](https://github.com/itsToggle/plex_debrid#open_file_folder-library-collection-service), which plex_debrid will use to determine your current media collection. If you intend to run a plex server, choose plex.
>  6. Pick and setup a [**library update service**](https://github.com/itsToggle/plex_debrid#-library-update-services), which plex_debrid will update/refresh after a successful download. If you intent to run a plex server, choose plex.
>  7. Pick and setup a [**library ignore service**](https://github.com/itsToggle/plex_debrid#eyes-library-ignore-services), which plex_debrid will use to ignore content. If you intent to run a plex server, choose plex.
>  8. Pick and setup at least one [**debrid service**](https://github.com/itsToggle/plex_debrid#arrow_down_small-debrid-services), which plex_debrid will use to download content.
>  9. You're done!
>  10. Choose option '1' to run the download automation. Choose option '2' to explore or edit the Settings or open the "settings.json" file the script creates after the first run.
>  11. If you dont want the main menu to show when starting the script (for an auto-run setup), navigate to "/Settings/UI Settings/show menu on startup" and set the value to "false".
>  12. Read the rest of the README!
>  
></details>
 
## Usage:

*plex_debrid can be setup in a bunch of different ways, which this readme wont be able to cover. Feel free to ask any questions in the "discussions" section of this respository or join our discord server.*
 
### :tv: Content Services:

*The services that plex_debrid can monitor for new content. You can pick any combination of services.*

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
>  - You can connect plex_debrid to trakt.tv to get more accurate release dates and times for your content, without needing to actually monitor any of your trakt content.
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
>  - You can connect plex_debrid to overseerr to instantly and automatically download approved requests from selected users. For this to work, you need to connect plex_debrid to either Plex or Trakt, since these services can be used to gather more information on the requested media items.
>  - To connect the script to overseerr, navigate to '/Settings/Content Services/Overseerr'. 
>  - By default, all approved requests from all overseerr users are downloaded by plex_debrid. To limit this feature to specific users, navigate to '/Settings/Content Services/Overseerr/Overseerr users'
>
></details>
>
><details>
>  <summary><b><u><img src="https://raw.githubusercontent.com/Fallenbagel/jellyseerr/main/public/android-chrome-512x512.png" height="16"> Jellyseerr requests:</u></b></summary>
> 
>  - You can connect plex_debrid to jellyseerr to instantly and automatically download approved requests from selected users. For this to work, you need to connect plex_debrid to either Plex or Trakt, since these services can be used to gather more information on the requested media items. Since jellyseer and overseerr use the exact same api endpoints, simply set up jellyseer in the plex_debrid overseerr menu:
>  - To connect the script to jellyseerr, navigate to '/Settings/Content Services/Overseerr'. 
>  - By default, all approved requests from all jellyseerr users are downloaded by plex_debrid. To limit this feature to specific users, navigate to '/Settings/Content Services/Overseerr/Overseerr users'
>
></details>
 
 
### :open_file_folder: Library Collection Service

*The services that plex_debrid can use to determine your current media collection.*

><details>
>  <summary><b><u><img src="https://app.plex.tv/desktop/favicon.ico" height="16"> Plex library:</u></b></summary>
>  
>  - To use your plex library as your library service, navigate to '/Settings/Library Service/Library collection service/Change library service/'
>  - If you choose your plex library as your library service, your *entire* Plex Library (including shares) is checked before downloading anything and the script will avoid duplicate downloads. To limit this library check to specific library sections, navigate to '/Settings/Library Service/Library collectikn service/Edit library service/Plex library check/Edit'
>
></details>
>
><details>
>  <summary><b><u><img src="https://walter.trakt.tv/hotlink-ok/public/favicon.ico" height="16"> Trakt collection:</u></b></summary>
>  
>  - To use one of your trakt users collections as your library service, navigate to '/Settings/Library Service/Library collection service/Change library service/'
>  - If you choose your trakt collection as your library service, your *entire* trakt collection is checked before downloading anything and the script will avoid duplicate downloads. 
>
></details>
 
### 🔁 Library Update Services

*The services that plex_debrid can update/refresh after a successful download. You can add any combination of services.*

><details>
>  <summary><b><u><img src="https://app.plex.tv/desktop/favicon.ico" height="16"> Plex library:</u></b></summary>
>  
>  - To refresh your plex libraries after a succesful download, navigate to '/Settings/Library Service/Library update service/Edit/'
>  - You can add an unlimited amount of libraries to be refreshed
>  - plex_debrid is now capable of only partially scanning your libraries. This feature is currently only available for content that's downloaded through realdebrid.
>
></details>
>
><details>
>  <summary><b><u><img src="https://walter.trakt.tv/hotlink-ok/public/favicon.ico" height="16"> Trakt collection:</u></b></summary>
>  
>  - To mark content as collected on Trakt after it has been successfully downloaded, navigate to '/Settings/Library Service/Library update service/Edit/'
>  - plex_debrid will automatically add the downloaded resolution and other properties of the downloaded media to your trakt collection
>
></details>
>
><details>
>  <summary><b><u><img src="https://jellyfin.org/images/favicon.ico" height="16"> Jellyfin Libraries:</u></b></summary>
>  
>  - To refresh your jellyfin libraries after a succesful download, navigate to '/Settings/Library Service/Library update service/Edit/'
>  - plex_debrid is currently only able to refresh your entire jellyfinlibrary. Partial library scans to come shortly!
>
></details>
 
### :eyes: Library Ignore Services

*The services that plex_debrid will use to ignore content. You can add any combination of services. You can explore the media thats currently ignored from the main plex_debrid menu.*

><details>
>  <summary><b><u><img src="https://app.plex.tv/desktop/favicon.ico" height="16"> Plex Discover Watch Status:</u></b></summary>
>  
>  - To use a plex users plex discover watch status to ignore content, navigate to '/Settings/Library Service/Library ignore services/Edit/'
>
></details>
>
><details>
>  <summary><b><u><img src="https://walter.trakt.tv/hotlink-ok/public/favicon.ico" height="16"> Trakt Watch Status:</u></b></summary>
>  
>  - To use a trakt users trakt watch status to ignore content, navigate to '/Settings/Library Service/Library ignore services/Edit/'
>
></details>
>
><details>
>  <summary><u><b>:clipboard: Local Ignore List:</u></b></summary>
>  
>  - To use a local text file of queries to ignore content, navigate to '/Settings/Library Service/Library ignore services/Edit/'
>
></details>
 
### :magnet: Scraping Services:

*The services that plex_debrid can use to find torrents. You can add any combination of services. By default, only the legacy scrapers (rarbg, 1337x) are enabled. Its highly recommended to connect more scraping services to make sure you find high quality, cached releases.*

>
><details>
>  <summary><b><u><img src="https://progsoft.net/images/rarbg-icon-648af4dcc6ec63ee49d6c050af63d2547c74d46c.png" height="16"><img src="https://1337x.to/favicon.ico" height="16"> legacy scrapers (rarbg, 1337x):</u></b></summary>
>  
>  - The only "legacy" scrapers currently integrated are for rarbg.to and 1337x.to - you can turn these off or on by navigating to '/Settings/Scraper/Sources/Edit/'.
>
></details>
>
><details>
>  <summary><b><u><img src="https://user-images.githubusercontent.com/27040483/28728094-99f3e3f6-73c7-11e7-8f8d-28912dc6ac0d.png" height="16"> jackett (highly recommended):</u></b></summary>
>  
>  - Its recommended to install "jackett", a program that wraps a huge amount of torrent indexers (https://github.com/Jackett/Jackett). Once installed and setup, you can enable jackett by navigating to '/Settings/Scraper/Sources/Edit/Add source/jackett'.
>  - You can now choose to use a specific debrid service for a specific torrent tracker by navigating to "/Settings/Debrid Services/Tracker specific Debrid Services". This comes in handy if you are using a private tracker that forces you to use a debrid service that will seed your torrents (e.g. debridlink,put.io).
>
></details>
>
><details>
>  <summary><b><u><img src="https://prowlarr.com/img/favicon-32x32.png" height="16"> prowlarr:</u></b></summary>
>  
>  - If you prefer Prowlarr over Jackett, you can integrate prowlarr into plex_debrid by navigating to '/Settings/Scraper/Sources/Edit/Add source/prowlarr'. Prowlarr has stricted rate limits than jackett for some indexers (e.g. 1337x), which could cause plex_debrid to timeout the request to prowlarr and therefore find less releases than jackett.
>  - You can now choose to use a specific debrid service for a specific torrent tracker by navigating to "/Settings/Debrid Services/Tracker specific Debrid Services". This comes in handy if you are using a private tracker that forces you to use a debrid service that will seed your torrents (e.g. debridlink,put.io).
>
></details>
>
><details>
>  <summary><b><u><img src="https://orionoid.com/web/images/logo/logo256.png" height="16"> orionoid:</u></b></summary>
>  
>  - You can integrate the orionoid scrapers into plex_debrid by navigating to '/Settings/Scraper/Sources/Edit/Add source/orionoid'.
>  - By default, only the top 5 links are fetched per scraping attempt and the links are sorted by "popularity", not the premium-only "best" attribute. This is done to be "free" account friendly, you can change these parameters in the orionoid source settings '/Settings/Scraper/Sources/Edit/Edit sources/orionoid'.
>  - You can find a full list of all possible parameters and their respective values at "https://panel.orionoid.com/" in the "Developers" menu, section "API Docs" under "Stream API".
>
></details>
 
### :arrow_down_small: Debrid Services:

*The services that plex_debrid can use to download torrents. You can add any combination of services.* 

><details>
>  <summary><b><u>Debrid services:</u></b></summary>
>  
>  - You can add more than one debrid service and change the order in which they should be checked for cached releases by navigating to '/Settings/Debrid Services/Edit'.
>
></details>
>
 
### <img src="https://seeklogo.com/images/1/4k-logo-0B1F5255A1-seeklogo.com.png" height="16"> Defining versions to download:

><details>
>  <summary><b><u>Defining versions to download:</u></b></summary>
>  
>  - You can define what release qualities plex_debrid should download by defining a "version". You can add an unlimited amount of versions by navigating to '/Settings/Scraper Settings/versions'. By default, plex_debrid only comes with 1 version definiton ([1080p SDR])
>  - versions consist of an unlimited amount of completely customizable "rules" and "triggers". 
>  - "Rules" define the quality requirements of your versions. The rules can be either formulated as a requirement or as a preference. The first rule has the highest priority, the last one the lowest. To give some examples, here are the rules that make up the default [1080p SDR] version:
>      
>        1) cache status  requirement :   cached
>        2) resolution    requirement :       <=  1080
>        3) resolution    preference  :  highest
>        4) title         requirement :  exclude  (\.DV\.|3D|\.H?D?.?CAM\.)
>        5) title         requirement :  exclude  (\.HDR\.)
>        6) title         preference  :  include  (EXTENDED|REMASTERED)
>        7) size          preference  :   lowest
>        8) seeders       preference  :  highest
>        9) size          requirement :       >=  0.1
>      
>  - "Triggers" define when plex_debrid should look for a version. You can add triggers that limit a version to a specific media type, or to specific movies/shows. You can define how many times plex_debrid should attempt to download a version and how many attempts should be made with other versions, before a version is attempted to be downloaded. Here are some of the possible triggers, given in an example of a 720p version that should only be looked for, if the media items in question are "shows" that have been released "before 2010", are not "Family Guy" or "Last week tonight", and no other version has been found for "5 attempts":
>      
>        A) media type    requirement :   shows
>        B) retries       requirement :       >=  5
>        C) retries       requirement :       <=  48
>        D) title         requirement :  exclude  (family.guy|last.week.tonight)
>        E) year          requirement :       <=  2010
>      
>
></details>
 
## Limitations:

><details>
>  <summary><b><u>Plex Limitations:</u></b></summary>
>  
>  - If plex is chosen as the library collection service, trakt and overseerr content needs to be matched to the plex media type. In order to accurate match content from Overseerr and Trakt to Plex, its neccessary to have at least one movie and one show inside a library thats visible by plex_debrid. Thats because in order to accurately match content, a search by imdb/tmdb/tvdb ID is necessary - which currently only works by requesting a "Fix Match" call to an existing library item. Until Plex allows a universal search by ID, this is the best I can do.
>  - plex_debrid cannot destinguish between a truly empty library and a library that couldnt be reached because its offline (or not reachable for any other reason). In order to avoid unwanted behaviour, the script simply stops running whenever an empty library is encountered. You will need to manually add at least one media item to the libraries visible by plex_debrid, before the download automation can run savely.
>  - The plex discover api only provides release dates, not precise release times. Its recommended to connect the script to trakt.tv, which enables plex_debrid to find more accurate release dates and even find out if movies can be downloaded before their actual release date.
>
></details>

## Buy me a beer/coffee? :)

I've written this automation because it's a hell of a lot of fun and because I've wanted a setup like this for a while. The continuation of this project does **not**, in any way, depend on monetary contributions. If you do want to buy me a beer/coffee, feel free to use my real-debrid [affiliate link](http://real-debrid.com/?id=5708990) or send a virtual beverage via [PayPal](https://www.paypal.com/paypalme/oidulibbe) :)
