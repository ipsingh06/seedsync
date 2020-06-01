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
- Auto-Queue + Auto-Extract - automatically download and extract files as soon as they appear on your seedbox
- Only fetch the files you want with Auto-Queue pattern matching
- Fully open source!


Supported OS:
* Linux (debian package, docker image)
* Windows (docker image)
* MacOS (docker image)

Tested on:
* Ubuntu 14.04 and above
* Windows 10 Home



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

Installation options are:
* [Ubuntu Deb Package](#install-ubuntu) (easiest method)
* [Docker Image on Linux](#install-docker)
* [Docker Image on Windows](#install-windows)

### <a name="install-ubuntu"></a> Ubuntu Deb Package

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

5. Go to the Settings page and fill out the required information.
   **While password-based login is supported, key-based authentication is highly recommended!**
   See the [Key-Based Authentication Setup](#key-auth) section for details.


### <a name="install-docker"></a> Docker Image on Linux

1. Run the docker image with the following command:
   ```bash
   docker run \
       -p 8800:8800 \
       -v <downloads directory>:/downloads \
       -v <config directory>:/config \
       ipsingh06/seedsync
   ```
   where
    - `<downloads directory>` refers to the location on host machine where downloaded files will be placed
    - `<config directory>` refers to the location on host machine where config files will be placed
    - both these directories must already exist

   By default the docker image is run under the default user (uid=1000).
   To run as a different user, include the option `--user <uid>:<gid>`.

2. Access application GUI by going to [http://localhost:8800](http://localhost:8800) in your browser.

3. Go to the Settings page and fill out the required information.
   Under the Local Directory setting, enter `/downloads`.

4. **While password-based login is supported, key-based authentication is highly recommended!**
   See the [Key-Based Authentication Setup](#key-auth) section for details.


### <a name="install-windows"></a> Docker Image on Windows

SeedSync supports Windows via the Docker container.

1. Install Docker on Windows.

   1. [Docker for Windows](https://www.docker.com/docker-windows) if you have Windows 10 Pro or above

   2. [Docker Toolbox](https://docs.docker.com/toolbox/toolbox_install_windows/) if you have Windows 10 Home or below

2. Make sure you can successfully run the [Hello World](https://docs.docker.com/get-started/#test-docker-installation) app in Docker.

3. Open the Docker terminal and run the SeedSync image with the following command:
   ```bash
   docker run \
       -p 8800:8800 \
       -v <downloads directory>:/downloads \
       -v <config directory>:/config \
       ipsingh06/seedsync
   ```
   where
    - `<downloads directory>` refers to the location on host machine where downloaded files will be placed
    - `<config directory>` refers to the location on host machine where config files will be placed
    - both these directories must already exist

   Note: the Windows host machine path is specified as `/c/Users/...`

4. Access application GUI to verify SeedSync is running.
   Docker on Windows may not forward port to the local host. We need to find the IP address of the container.
   
   1. Open a new Docker terminal and run the command:
      ```bash
      docker-machine ip
      192.168.100.17
      ```

   2. Open &lt;ip address&gt;:8800 in your browser.
      In this example that would be [http://192.168.100.17:8800](http://192.168.100.17:8800)

   3. Verify that SeedSync dashboard loads.

5. Go to the Settings page and fill out the required information.
   Under the Local Directory setting, enter `/downloads`.

6. **While password-based login is supported, key-based authentication is highly recommended!**
   See the [Key-Based Authentication Setup](#key-auth) section for details.


## Usage

SeedSync's web-based GUI can be accessed at [http://localhost:8800](http://localhost:8800).

You may also access it from another device by replacing 'localhost' with the IP address or hostname of the machine where it is installed.

### <a name="key-auth"></a> Password-less/Key-based Authentication Setup

Password-based access to your remote server is highly unsecure.
It is strongly recommended that you setup key-based authentication.

1. You will need to generate a public-private key pair.
   Here is a [simple tutorial](https://www.tecmint.com/ssh-passwordless-login-using-ssh-keygen-in-5-easy-steps/)
   that walks you through this process.

   Note: make sure the access is setup for the user under which SeedSync is running.

   Note2: if you're using docker, also see the
   [Using SSH Keys with Docker](#keys-inside-docker) section.


2. Before continuing, verify the password-less access by SSH'ing into your remote server in a terminal:

   ```bash
   ssh <remote user>@<remote server>
   ```
   You should be able to log in to the remote server without being prompted for a password


3. Update the settings
   1. Access the web GUI and choose the Settings page from the menu.
   2. Replace your password in the "Server Password" field with anything else (it can't be empty).
   3. Select "Use password-less key-based authentication".
   4. Restart SeedSync

#### <a name="keys-inside-docker"></a> Using SSH Keys with Docker

1. Generate a SSH private/public key pair if you haven't already.
   Here is a [simple tutorial](https://www.tecmint.com/ssh-passwordless-login-using-ssh-keygen-in-5-easy-steps/)
   that walks you through this process.

2. Include the following option with your docker command:
   ```bash
   -v <path to .ssh directory>:/home/seedsync/.ssh
    ```
   Most commonly this should be:
   ```bash
   -v ~/.ssh:/home/seedsync/.ssh
   ```

Note: If you are running the docker guest with a non-standard user using the `--user` option, then you must make sure that your `.ssh` directory is also readable by that user.

### Dashboard

The Dashboard page shows all the files and directories on the remote server and the local machine.
Here you can manually queue files to be transferred, extract archives and delete files.

### AutoQueue

AutoQueue queues all newly discovered files on the remote server.
You can also restrict AutoQueue to pattern-based matches (see this option in the Settings page).
When pattern restriction is enabled, the AutoQueue page is where you can add or remove patterns.
Any files or directories on the remote server that match a pattern will be automatically queued for transfer.



## Report an Issue

Please report any issues on the [issues](../../issues) page.
Please post the logs as well. The logs are available at:
* Deb install: `<user home directory>/.seedsync/log/seedsync.log`
* Docker: Run `docker logs <container id>`



## FAQ

#### How do I restart SeedSync?

SeedSync can be restarted from the web GUI. If that fails, you can restart the service from command-line:

```bash
sudo service seedsync restart
```

#### SeedSync can't seem to connect to my remote server?

Make sure your remote server address was entered correctly.
If using password-based login, make sure the password is correct.
Check the logs for details about the exact failure.

#### How can I save my settings across updates when using the Docker image?

To maintain state across updates, you can store the settings in the host machine.
Add the following option when starting the container.
```bash
-v <directory on host>:/config
```
where `<directory on host>` refers to the location on host machine where you wish to store the application
state.


## Contribute

Contributions to SeedSync are welcome!
Please take a look at the [Developer Readme](doc/DeveloperReadme.md) for instructions
on environment setup and the build process.


## License

SeedSync is distributed under Apache License Version 2.0.
See [License.txt](https://github.com/ipsingh06/seedsync/blob/master/LICENSE.txt) for more information.