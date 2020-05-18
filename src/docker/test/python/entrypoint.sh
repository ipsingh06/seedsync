#!/bin/bash

# exit on first error
set -e

echo "Running sshd"
/usr/sbin/sshd -D &

echo "Continuing entrypoint"
echo "$@"
exec $@
