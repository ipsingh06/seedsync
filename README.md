# pyLFTPdaemon
Config path is ~/.pyLFTPdaemon
Service uses Upstart. Place pyLFTPdaemon.conf in /etc/init/pyLFTPdaemon.conf 
Place ssh private key in /root/.ssh


# pylftpd

## Install
Place artifacts in /var/lib/pylftp/

Place pylftpd.conf in /lib/systemd/system

Place ssh private key in /root/.ssh

## Run

Start: sudo systemctl stop pylftp

Stop: sudo systemctl stop pylftp

Status: sudo systemctl status pylftp

Log file is at /var/log/pylftpd/