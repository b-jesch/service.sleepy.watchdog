Idle Timer management that performs actions after an amount of inactivity time of user within a specified time frame (or always or inactive) for Kodi. Optional switch off the TV with CEC on all actions (must supported on both devices).

You can also quickly set an idle timer by calling the addon directly. Choose from a list the desired idle time. The timer starts then immediately but will reset to the idle time when a user activity is detected.

Actions are:
* Stop playing media, optional switch to home menu and power off TV via CEC
* Quit Kodi
* Shutdown, hibernate, suspend or reboot
* Change user profile
* Logoff user
<br><br>  
* Run a specified addon, plugin or Python script using
<br><br>
  * Addon:    ```script.myaddon,param=do_this```
  * Plugin:   ```plugin://plugin.video/?param=do_this```
  * Script:   ```/home/user/script.py```

Note that scripts must have set the executable flag and must be python scripts. It is recommended to use the full script path. No parameters are allowed for pure scripts. Plugins must provide the plugin name with URL scheme. 
A direct call of the addon via programme menu starts a countdown timer that executes the action set in the setup, after user inactivity selected in the menu has expired.
    