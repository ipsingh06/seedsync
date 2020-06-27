![](https://user-images.githubusercontent.com/12875506/85908858-c637a100-b7cb-11ea-8ab3-75c0c0ddf756.png)

SeedSync is a tool to sync the files on a remote Linux server (like your seedbox, for example).
It uses LFTP to transfer files fast!

## Features

* Built on [LFTP](http://lftp.tech/), the fastest file transfer program ever
* Web UI - track and control your transfers from anywhere
* Automatically extract your files after sync
* Auto-Queue - only sync the files you want based on pattern matching
* Delete local and remote files easily
* Fully open source!

## How it works

Install SeedSync on a local machine.
SeedSync will connect to your remote server and sync files to the local machine as
they become available.

You don't need to install anything on the remote server.
All you need are the SSH credentials for the remote server.

## Supported Platforms

SeedSync releases come in the following flavours:
* Debian package (.deb file)
* Docker image

The following OSes are supported:
* Linux (debian package and docker image)
* Windows (docker image)
* MacOS (docker image)


## Installation and Usage

Please refer to the [documentation](https://ipsingh06.github.io/seedsync/).


## Report an Issue

Please report any issues on the [issues](../../issues) page.
Please post the logs as well. The logs are available at:
* Deb install: `<user home directory>/.seedsync/log/seedsync.log`
* Docker: Run `docker logs <container id>`


## Contribute

Contributions to SeedSync are welcome!
Please take a look at the [Developer Readme](doc/DeveloperReadme.md) for instructions
on environment setup and the build process.


## License

SeedSync is distributed under Apache License Version 2.0.
See [License.txt](https://github.com/ipsingh06/seedsync/blob/master/LICENSE.txt) for more information.



![](https://user-images.githubusercontent.com/12875506/37031587-3a5df834-20f4-11e8-98a0-e42ee764f2ea.png)
