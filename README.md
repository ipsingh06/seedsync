# pylftpd

## Dependencies
sudo apt-get install lftp

## Install
Place artifacts in /var/lib/pylftp/

Place config/systemd/pylftp.service in /lib/systemd/system

Enable service start at boot:
sudo systemctl enable pylftp.service

Place ssh private key in /root/.ssh

## Run

Start: sudo systemctl stop pylftp

Stop: sudo systemctl stop pylftp

Status: sudo systemctl status pylftp

Log file is at /var/log/pylftpd/