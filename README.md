# plex_debrid
Plex torrent streaming through Debrid Services, using the new Plex Discover feature.

**Using the new Plex Discover Feature, your Plex Home users can add movies/shows to their watchlist and they become available to stream in seconds.**

## In Action:

![Alt Text](https://github.com/itsToggle/plex_debrid/blob/main/cool.gif)

## Description:

*For this download automation to work, you need to mount your debrid service as a virtual drive. After creating a plex library of this virtual drive, you can stream torrents that are cached on your debrid service without the need to download them first.* 

The plex watchlist of specified users is constantly checked for newly added movies/shows and newly released episodes of watchlisted shows.
Once new content is found, torrent indexers are scraped for the best, cached release on selected debrid services. The torrent is then added to a suitable debrid service and a library refresh is performed to make the newly added content available. 

**For any debrid-cached content (movies, one-season tv shows or even multi-season tv shows) the entire process from watchlisting content to watching it takes about 10-20 seconds.**

This is a pre-alpha release. shits not ready! Feel free to check it out though, I will continously improve the speed, reliability and user-friendlyness.

## Setup:

**1) Mount your debrid services**

Realdebrid:

1. Install my rclone fork: https://github.com/itsToggle/rclone_RD
2. configure rclone by running the command 'rclone config' (could be './rclone config' depending on your os)
3. create a new remote by typing 'n'
4. give your remote a name (e.g. 'your-remote')
5. choose '47) realdebrid' as your remote type
6. follow the rest of the prompted instructions, choose 'no advaced configuration'
7. You can mount your newly created remote by running the command 'rclone cmount your-remote: X: --dir-cache-time=10s --vfs-cache-mode=full' (replace 'your-remote' with your remote name, replace X with a drive letter of your choice e.g 'X','Y','Z',...)
8. You've successfuly created a virtual drive of your debrid service!

Premiumize:

1. Install either the official rclone software or my fork: https://github.com/itsToggle/rclone_RD
2. configure rclone by running the command 'rclone config' (could be './rclone config' depending on your os)
3. create a new remote by typing 'n'
4. give your remote a name (e.g. 'your-remote')
5. choose '46) premiumize' as your remote type
6. follow the rest of the prompted instructions, choose 'no advaced configuration'
7. You can mount your newly created remote by running the command 'rclone cmount your-remote: X: --dir-cache-time=10s --vfs-cache-mode=full' (replace 'your-remote' with your remote name, replace X with a drive letter of your choice e.g 'X','Y','Z',...)
8. You've successfuly created a virtual drive of your debrid service!

**2) Setup Plex**

2. Create a plex 'movie' library of the mounted virtual drive or add the mounted virtual drive to an existing 'movie' library.
3. Create a plex 'shows' library of the mounted virtual drive or add the mounted virtual drive to an existing 'shows' library.
4. *Recommendation: disable 'video preview thumbnails', disable 'intro detection', disable the scheduled task 'perfom extensive media analysis' to reduce the download traffic
5. You and your home users can now stream cached torrents from RealDebrid!

**3) Setup plex_debrid**
1. Run the script! (google "how to run a python script" ;) )
2. The script will guide you through the initial setup.
3. You're done!
4. Choose option '1' to run the download automation. Choose option '2' to explore or edit the Settings or open the "settings.json" file the script creates after the first run.
5. Read the rest of the README!

## Managing your Plex Content:

- The Plex Watchlist and the Discover feature are only available for accounts that are linked to an email address - so no managed accounts.
- You've already added one user in the initial setup. To allow content download by other users that youve invited to your Plex Home, create a new user by navigation to '/Settings/Content Services/Plex/Plex users/Edit/Add user'.
- You and the users you've added can now browse the Discover part of Plex and download content by adding it to the Plex Watchlist.
- Your *entire* Plex Library (including shares) is checked before downloading anything and the script will avoid duplicate downloads.
- If you want to delete something from your Plex server, make sure that you've removed it from your Watchlist first. Otherwise the script will see that its in your watchlist and not on your server and will simply download it again.
- Movies that you add to your Plex Watchlist are removed automatically once they are downloaded. Shows stay in the Watchlist, because only shows that are in the Watchlist are monitored for newly released episodes.
- The Plex Watchlist of your specified users will polled for changes every 5 seconds, which is when it will try to find newly added content. 
- The Plex Watchlist will be updated entirely every 30 minutes, which is when it will try to find newly released episodes from watchlisted series. This is only done every 30 minutes, because building the whole watchlist can take more than a minute, depending on the amount of shows you have in there.
- If you dont want to download a specific episode or season of a show, navigate to that show in the discovery feature and mark the episodes/seasons that you want to ignore as 'watched'. The watch status inside the discovery feature is not connected to the watch status inside your libraries.
- When some content could repeatedly not be downloaded, it will be marked as 'watched' in the Discovery feature of the first specified user. This will cause the scraper to ignore the content, until its marked as 'unwatched' again.
- You can explore and remove ignored content in the main menu.

## Integrating Trakt:

- You can connect the script to trakt.tv to get more accurate release dates and times for your content. You can also synchronize your trakt watchlist and the trakt watchlist of other users to your plex watchlist.
- To connect the script to trakt, navigate to '/Settings/Content Services/Trakt/Trakt users/Edit/Add user'. You can add an unlimited amount of users.
- To enable one-way Watchlist synchronization from Trakt to Plex for your specified users, navigate to '/Settings/Content Services/Trakt/Trakt-to-Plex synchronization'. Your Trakt Watchlist will be synchronized to Plex every 30 minutes.

## Integrating your favorite torrent indexers:

- The only legacy scrapers currently integrated are for rarbg.to and 1337x.to 
- Its recommended to install "jackett", a program that wraps a huge amount of torrent indexers (https://github.com/Jackett/Jackett). Once installed and setup, you can enable jackett by navigating to '/Settings/Scraper/Sources/Edit/Add source/jackett'. Once enabled, you can delete the legacy scrapers, since jackett can handle both 1337x and rarbg.

## Download Automation Settings:

- The only debrid service currently integrated is RealDebrid. In the future you will be able to select your favorite debrid services and change the order in which they should be checked for cached releases, aswell as the service that should download uncached releases.
- This script will automatically pick the best release that could be found. To change how the script picks the best release, check out the next section.
- If you don't want the main menu to show when you start the script and run the download automation right away, you can define this in the 'UI Settings' section of the 'Settings' menu. You can return to the main menu at any time by typing 'exit'.

## Sorting the scraped releases:

The scrapers usually provide a whole bunch of releases. Adding them all to your debrid services would clutter your library and slow things down. This is why this script automatically sorts the releases by completely customizable categories and picks the best one.

The sorting is done by providing an unlimited number of sorting 'rules'. Rules can be added, edited, delted or moved. The first rule has the highest priority, the last one the lowest.

Each rule consist of:
- a regex match group that defines what we are looking for. Check out regexr.com to try out some regex match definitions.
- an attribute definition that defines which attribute of the release we want to look in (can be the title, the source, or the size)
- an interpretation method. This can be either:
  - "number" : the first regex match group will be interpreted as an integer and releases will be ranked by this number.
  - "text" : we will give each release a rank accoring to which match group its in.
- lastly we define wheter to rank the releases in ascending or descending order.

You can test out your current sorting rules by manually scraping for releases from the main menu. The returned releases are sorted by your current rules.

Lets make some rules: 
### Example resolution sorting:
We want to download releases up to our prefered resolution of 1080p.
For this, we will choose the following setup:
- regex definition: "(1080|720|480)(?=p)" - This is one match group, that matches either "1080", "720" or "480", followed by the letter "p". This is a typical Resolution definition of releases.
- attribute definition: "title" - we want to look for this inside the release title
- interpretation method: "number" - we want to sort the releases by the highest number to the lowest number
- ascending/descending: "1" - 1 means descending. We want to sort the releases in decending order to get the highest resolution release.

### Example codec sorting:
We want to download releases that use the x265 Codec, rather then the x264 codec. 
For this, we will choose the following setup:
- regex definition: "(h.?265|x.?265)|(h.?264|x.?264)" - These are two match groups, that match typical codec descriptions in the release titles
- attribute definition: "title" - we want to look for this inside the release title
- interpretation method: "text" - by choosing this, we define that the releases should be sorted by the match group they are in.
- ascending/descending: "1" - 1 means descending. Descending in this context means, that the First matchgroup is preffered over the second matchgroup, and both are prefered over a release that doesnt match.

### Example release exclusion:
We don't want to download releases that are HDR or 3D. For this rule to ne effective, we need to make it our first rule.
For this, we will choose the following setup:
- regex definition: "(\\.HDR\\.|\\.3D\\.)"
- attribute definition: "title" - we want to look for this inside the release title
- interpretation method: "text" - by choosing this, we define that the releases should be sorted by the match group they are in.
- ascending/descending: "0" - 0 means ascending. Ascending in this context means, that releases that don't match are prefered over releases that do.

### Example size sorting:
We want to sort or releases by size - this should be implemented as one of the last rules.
For this, we will choose the following setup:
- regex definition: "(.*)" - This is one match group that simply matches everything.
- attribute definition: "size" - we want to look for this inside the release size
- interpretation method: "number" - by choosing number, we define that the release size should be interpreted as a number.
- ascending/descending: "0" - 0 means ascending. We want to select the smallest release.


## Limitations:
- The plex discover API only provides a release date, not a release time for new episodes. This makes it hard to determined when to start looking for releases and when to ignore an episode. This script will only download episodes when its been a day since the air-date or if plex shows the episode as availabe on streaming services. It is recommended to connect this script to trakt.tv, to allow for more accurate release dates and times.
- Since this is more of a proof of concept at the moment, There are only two scrapers implemented - rarbg and 1337x.
