# SeedSync

## Dependencies
sudo apt-get install lftp

## Install
Place artifacts in /var/lib/seedsync/

Place config/systemd/seedsync.service in /lib/systemd/system

Enable service start at boot:
sudo systemctl enable seedsync.service

Place ssh private key in /root/.ssh

## Run

Start: sudo systemctl stop seedsync

Stop: sudo systemctl stop seedsync

Status: sudo systemctl status seedsync

Log file is at /var/log/seedsync/