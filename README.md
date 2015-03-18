Sublime Text 3 Plugin for Miva Software Developers and Testers

This Sublime Text plugin allows you to manage the server board (https://bugzilla.dev.mivamerchant.com/servers/) directly from your sublime. Developers can checkout/checkin servers.

To Checkout a server: Use ctrl+m ctrl+t, this will show a list of all available servers. Select the server you want to checkout and hit enter (ESC to cancel)

To Checkin a server: Use ctrl+m ctrl+r, this will show a list of all servers you have checked out. Select the server you want to checkin and hit enter (ESC to cancel)

To get your Bugzilla_login and Bugzilla_logincookie settings, using the developer tools of your browser, view the network tab and traverse to the server board (https://bugzilla.dev.mivamerchant.com/servers/). Look in the Request Headers -> Cookie and within the Cookie text find the Values Bugzilla_login and Bugzilla_logincookie, then copy those values into your user settings for MvManageServers.

Download the zip file, rename it to MvManageServers and copy it into one of the following directories:

Ubuntu: ~/.config/sublime-text-3/Packages/

OS X: ~/Library/Application Support/Sublime Text 3/Packages/

Windows: %APPDATA%\Sublime Text 3\Packages\