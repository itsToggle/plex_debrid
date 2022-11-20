# plex_debrid (android)
Please note that this readme only includes some setup assistance for an android. Check the main branch for a more detailed readme regarding the actual plex_debrid usage!

## Setup:

### 1) Mount your debrid services:

*For this download automation to work, you need to mount at least one debrid service as a virtual drive. I highly recommend using RealDebrid, as this service will recieve updates and new features from plex_debrid first.*

android version has only been tested with realdebrid. 

<details>
  <summary><b><u>Mounting RealDebrid (non-root, doesnt work with plex)</u></b></summary>
  
  *Its recommended to remove all but a few pages of finished torrents before mounting realdebrid for the first time. You can add as many torrents as you want after that.*
  
    1) Create an rclone config file:
  
    Create the file manually:
    - Open your favorite text editor and paste the following lines:
  
    [realdebrid]
    type = realdebrid
    api_key = your-api-key-here

    - replace 'your-api-key-here' with your api key, save the file as 'rclone.conf' and copy it to your android device.
  
    or install my rclone fork on a PC:
  
    - configure rclone by running the command 'rclone config' (could be './rclone config' depending on your os)
    - create a new remote by typing 'n'
    - give your remote a name (e.g. 'your-remote')
    - choose '47) realdebrid' as your remote type
    - follow the rest of the prompted instructions, choose 'no advaced configuration'
    - Head over to `C:\Users\BigSchlong\.config\rclone` and copy the `rclone.conf` file to your android device.
  
    2. Open the app and click on 'import config' - choose the rclone config file
    3. You can now see files from your debrid service!

</details>

<details>
  <summary><b><u>Mounting RealDebrid (root, works with plex)</u></b></summary>
  
  *Its recommended to remove all but a few pages of finished torrents before mounting realdebrid for the first time. You can add as many torrents as you want after that.*
  
  This setup can be done entirely on your android device:
  
  You can either run the official rclone software and mount realdebrid through their webdav implementation (recommended), or you can run realdebrid through my fork.
  
  official version (Magisk Module):
  https://github.com/Magisk-Modules-Repo/com.piyushgarg.rclone
  or
  https://github.com/AvinashReddy3108/rclone-mount-magisk
   
  my fork:
  1. Install Termux from F-Droid
  2. run command 'pkg update'
  3. run command 'termux-setup-storage', allow the permission
  4. run command 'pkg install wget'
  5. run command 'wget https://github.com/itsToggle/rclone_RD/releases/download/v1.58.1-rd.1.4/rclone-android'
  6. run command 'chmod +x rclone-android'
  7. run command './rclone-android config'
  8. create a new remote by typing 'n'
  9. give your remote a name (e.g. 'your-remote')
  10. choose '47) realdebrid' as your remote type
  11. follow the rest of the prompted instructions, choose 'no advaced configuration'
  12. You've successfully created a realdebrid remote!
  13. I dont have a rooted device, so I dont know what 'sudo' or 'su' commands will be necessary here, but this is as far as I can come without root:
  14. when running the command './rclone-android mount your-remote: x:' you will probaply encounter an error saying that fuselib2 is missing. Follow the prompted instructions by running both the commands that the error tells you to run.
  15. From here you need to consult official rclone sources (e.g. googeling)
</details>

### 2) Setup Plex:
This step will only work if you have a rooted device and followed the rooted mounting procedure above.

1. Create a plex 'movie' library of the mounted virtual drive or add the virtual drive to an existing 'movie' library.
2. Create a plex 'shows' library of the mounted virtual drive or add the virtual drive to an existing 'shows' library.
3. *Recommendation: disable 'video preview thumbnails', ~disable 'intro detection'~, disable the scheduled task 'perfom extensive media analysis' to reduce the download traffic*
4. You and your home users can now stream cached torrents from RealDebrid!

### 3) Setup plex_debrid:
1. Install Termux from F-Droid
2. run command 'pkg update'
3. run command 'pkg install python'
4. run command 'pkg install git'
5. run command 'termux-setup-storage', allow the permission
6. run command 'git clone https://github.com/itsToggle/plex_debrid'
7. run command 'python plex_debrid/main.py'
8. The script will guide you through the initial setup.
9. You're done!
10. You will most likely need to edit your plex server address, if the server is not running on your android device. the script will tell you if it can't reach the server.
11. Choose option '1' to run the download automation. Choose option '2' to explore or edit the Settings or open the "settings.json" file the script creates after the first run.
12. Read the rest of the README!

