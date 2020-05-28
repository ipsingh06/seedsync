#!/bin/bash

# exit on first error
set -e

echo "Running entrypoint"

echo "Installing SeedSync"
./expect_seedsync.exp

echo "Continuing docker CMD"
echo "$@"
exec $@
