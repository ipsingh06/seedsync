# SeedSync

SeedSync is a GUI-configurable, LFTP-based file transfer and management program.
With a LFTP backend, it can fetch files from a remote server (like your seedbox) at maximum throughput.
Fully GUI-configurable means not having to muck around with scripts.
SeedSync also allows you to extract archives and delete files on both the local machine and the remote server,
 all from the GUI!

![](https://user-images.githubusercontent.com/12875506/37031587-3a5df834-20f4-11e8-98a0-e42ee764f2ea.png)

SeedSync currently supports the following features:

- LFTP-backend for high-throughput, parallel transfers
- Web-based GUI accessible from any device
- View and control progress of file transfers from GUI
- Extract/decompress archive files
- Delete local or remote files
- Only fetch the files you want with Auto-Queue pattern matching
- Fully open source!


Supported OS: Linux (sorry no Windows or Mac support at this time)

Tested on: Ubuntu 14.04 and above



## Screenshots

<table>
<tr>
    <td>
        <a href="https://user-images.githubusercontent.com/12875506/37031659-74653182-20f4-11e8-856d-c1655d7d8150.png">
        <img src="https://user-images.githubusercontent.com/12875506/37031659-74653182-20f4-11e8-856d-c1655d7d8150.png"
        alt="Dashboard on Desktop"
        style="max-width: 100px;" />
        </a>
    </td>
    <td>
        <a href="https://user-images.githubusercontent.com/12875506/37031725-b8a79f9c-20f4-11e8-8caa-de45383f72b6.png">
        <img src="https://user-images.githubusercontent.com/12875506/37031725-b8a79f9c-20f4-11e8-8caa-de45383f72b6.png"
        alt="Dashboard on Mobile"
        style="max-width: 100px;" />
        </a>
    </td>
    <td>
        <a href="https://user-images.githubusercontent.com/12875506/34560372-52b6fcfc-f0fa-11e7-9618-edf18a7665cd.png">
        <img src="https://user-images.githubusercontent.com/12875506/34560372-52b6fcfc-f0fa-11e7-9618-edf18a7665cd.png"
        alt="Change LFTP settings from GUI"
        style="max-width: 100px;" />
        </a>
    </td>
</tr>
<tr>
    <td>
        Dashboard on Desktop
    </td>
    <td>
        Dashboard on Mobile
    </td>
    <td>
        Change LFTP settings from GUI
    </td>
</tr>
</table>



## Installation

1. Download the deb package from the [latest](https://github.com/ipsingh06/seedsync/releases/latest) release

2. Install the deb package:

   ```bash
   sudo dpkg -i <deb file>
   ```

3. During the first install, you will be prompted for a user name:
   ![Install prompt for username](https://raw.githubusercontent.com/ipsingh06/seedsync/master/doc/images/install_1.png)
   This is the user under which the seedsync service will run. The transferred files will be owned by this user.
   It is recommended that you set this to your user (and NOT root).

4. After the installation is complete, verify that the application is running by going to [http://localhost:8800](http://localhost:8800) in your browser.



## Usage

SeedSync's web-based GUI can be accessed at [http://localhost:8800](http://localhost:8800).

You may also access it from another device by replacing 'localhost' with the IP address or hostname of the machine where it is installed.

### First Time Setup

You need to configure SeedSync to connect to the remove server.
SeedSync requires that you have Key-Based SSH login access to the remote server.
Password-based access is not supported for security reasons.
You can setup Key-Based SSH access by following this [simple tutorial](http://www.thegeekstuff.com/2008/11/3-steps-to-perform-ssh-login-without-password-using-ssh-keygen-ssh-copy-id).

Note: make sure the access is setup for the user under which SeedSync is running.

Before continuing, verify the password-less access by SSH'ing into your remote server in a terminal:

```bash
ssh <remote user>@<remote server>
```

You should be able to log in to the remote server without being prompted for a password



Next, access the web GUI and choose the Settings page from the menu.

Fill out the missing configuration. Then select Restart from the menu. SeedSync will restart and connect to the remote server.

![First time settings](https://raw.githubusercontent.com/ipsingh06/seedsync/master/doc/images/install_2.png)

### Dashboard

The Dashboard page shows all the files and directories on the remote server and the local machine.
Here you can manually queue files to be transferred.

### AutoQueue

AutoQueue queues all newly discovered files on the remote server.
You can also restrict AutoQueue to pattern-based matches (see this option in the Settings page).
When pattern restriction is enabled, the AutoQueue page is where you can add or remove patterns.
Any files or directories on the remote server that match a pattern will be automatically queued for transfer.




## FAQ

#### How do I restart SeedSync?

SeedSync can be restarted from the web GUI. If that fails, you can restart the service from command-line:

```bash
sudo service seedsync restart
```

#### SeedSync can't seem to connect to my remote server?

Make sure you have key-based SSH login setup and working properly.
You may need to look at the logs to determine the exact cause of failure.
The logs are available at: `<user home directory>/.seedsync/logs/`



## License

SeedSync is distributed under Apache License Version 2.0.
See [License.txt](https://github.com/ipsingh06/seedsync/blob/master/LICENSE.txt) for more information.