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

### Ubuntu

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

5. Setup key-based SSH access. See the First Time Setup section below for a simple tutorial.


### Docker

1. Run the docker image with the following command:

   ```bash
   docker run -p 8800:8800 -v <downloads directory>:/downloads ipsingh06/seedsync
   ```
   where &lt;downloads directory&gt; refers to the location on host machine where downloaded files will be placed.

2. Access application GUI by going to [http://localhost:8800](http://localhost:8800) in your browser.

3. Setup key-based SSH access.

   1. Generate a SSH private/public key pair. See the First Time Setup section below for a simple tutorial.

   2. Run this command in a new terminal while the docker container is running:
      ```bash
      docker container ls

      CONTAINER ID        IMAGE                COMMAND                  CREATED             STATUS              PORTS                    NAMES
      28c87db489e1        ipsingh06/seedsync   "/bin/sh -c '/app/..."   12 seconds ago      Up 11 seconds       0.0.0.0:8800->8800/tcp   pedantic_raman
      ```
      Note down the container id for the image named ipsingh06/seedsync.
      It this example the container id is 28c87db489e1

   3. Copy the private key 'id_rsa' that you generated earlier into the container:
      ```bash
      docker cp id_rsa 28c87db489e1:/root/.ssh/
      ```

   4. Set the correct permissions on the private key
      ```bash
      docker exec 28c87db489e1 chmod 600 /root/.ssh/id_rsa
      ```

   5. Verify that the container can SSH into remote server without password.
      ```bash
      docker exec -it 28c87db489e1 ssh <username>@<address>
      ```
      where &lt;username&gt; and &lt;address&gt; are the username and address of the remote server.

4. Follow the rest of the First Time Setup section below to connect to the remote server.


### Windows

SeedSync supports Windows via the Docker container.

1. Install Docker on Windows.

   1. [Docker for Windows](https://www.docker.com/docker-windows) if you have Windows 10 Pro or above

   2. [Docker Toolbox](https://docs.docker.com/toolbox/toolbox_install_windows/) if you have Windows 10 Home or below

2. Make sure you can successfully run the [Hello World](https://docs.docker.com/get-started/#test-docker-installation) app in Docker.

3. Open the Docker terminal and run the SeedSync image with the following command:

   ```bash
   docker run -p 8800:8800 -v <downloads directory>:/downloads ipsingh06/seedsync
   ```
   where &lt;downloads directory&gt; refers to the location on host machine where downloaded files will be placed.
   Note: the Windows host machine path is specified as /c/Users/...

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
   

5. Setup key-based SSH access.

   1. Generate a SSH private/public key pair. See the First Time Setup section below for a simple tutorial.
      You can do this in a Docker terminal.

   2. Run this command in a new Docker terminal while the SeedSync container is running:
      ```bash
      docker container ls

      CONTAINER ID        IMAGE                COMMAND                  CREATED             STATUS              PORTS                    NAMES
      28c87db489e1        ipsingh06/seedsync   "/bin/sh -c '/app/..."   12 seconds ago      Up 11 seconds       0.0.0.0:8800->8800/tcp   pedantic_raman
      ```
      Note down the container id for the image named ipsingh06/seedsync.
      It this example the container id is 28c87db489e1

   3. Copy the private key 'id_rsa' that you generated earlier into the container:
      ```bash
      docker cp id_rsa 28c87db489e1:/root/.ssh/
      ```

   4. Set the correct permissions on the private key
      ```bash
      docker exec 28c87db489e1 chmod 600 /root/.ssh/id_rsa
      ```

   5. Verify that the container can SSH into remote server without password.
      ```bash
      docker exec -it 28c87db489e1 ssh <username>@<address>
      ```
      where &lt;username&gt; and &lt;address&gt; are the username and address of the remote server.

6. Follow the rest of the First Time Setup section below to connect to the remote server.
    


## Usage

SeedSync's web-based GUI can be accessed at [http://localhost:8800](http://localhost:8800).

You may also access it from another device by replacing 'localhost' with the IP address or hostname of the machine where it is installed.

### First Time Setup

You need to configure SeedSync to connect to the remote server.
SeedSync requires that you have Key-Based SSH login access to the remote server.
**For security reasons, password-based access is not supported.**
You can setup Key-Based SSH access by following this [simple tutorial](https://www.tecmint.com/ssh-passwordless-login-using-ssh-keygen-in-5-easy-steps/).

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

Make sure you have key-based SSH login setup and working properly.



## License

SeedSync is distributed under Apache License Version 2.0.
See [License.txt](https://github.com/ipsingh06/seedsync/blob/master/LICENSE.txt) for more information.