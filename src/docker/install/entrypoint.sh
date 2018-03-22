#!/bin/bash

# exit on first error
set -e

echo "Running entrypoint"

echo "Installing SeedSync"
./expect_seedsync.exp

echo "Setting up SeedSync (as user)"
su -c ./setup_seedsync.sh user

echo "Continuing entrypoint"
echo "$@"
exec $@
