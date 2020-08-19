<p align="center">
    <img src="https://user-images.githubusercontent.com/12875506/85908858-c637a100-b7cb-11ea-8ab3-75c0c0ddf756.png" alt="SeedSync" />
</p>


<p align="center">
  <a href="https://travis-ci.com/ipsingh06/seedsync">
    <img src="https://img.shields.io/travis/com/ipsingh06/seedsync" alt="Build">
  </a>
  <a href="https://github.com/ipsingh06/seedsync">
    <img src="https://img.shields.io/github/stars/ipsingh06/seedsync" alt="Stars">
  </a>
  <a href="https://hub.docker.com/r/ipsingh06/seedsync">
    <img src="https://img.shields.io/docker/pulls/ipsingh06/seedsync" alt="Downloads">
  </a>
  <a href="https://hub.docker.com/r/ipsingh06/seedsync">
    <img src="https://img.shields.io/docker/v/ipsingh06/seedsync?color=blue" alt="Version">
  </a>
  <a href="https://hub.docker.com/r/ipsingh06/seedsync">
    <img src="https://img.shields.io/docker/image-size/ipsingh06/seedsync/latest?style=flat" alt="Size">
  </a>
  <a href="https://github.com/ipsingh06/seedsync/blob/master/LICENSE.txt">
    <img src="https://img.shields.io/github/license/ipsingh06/seedsync" alt="License">
  </a>
</p>

SeedSync is a tool to sync the files on a remote Linux server (like your seedbox, for example).
It uses LFTP to transfer files fast!

## Features

* Built on top of [LFTP](http://lftp.tech/), the fastest file transfer program ever
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

* Linux
* Raspberry Pi (v2, v3 and v4)
* Windows (via Docker)
* MacOS (via Docker)


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
