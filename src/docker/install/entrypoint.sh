#!/bin/bash

# exit on first error
set -e

echo "Running entrypoint"

echo "Installing pylftp"
./expect_pylftp.exp

echo "Continuing entrypoint"
echo "$@"
exec $@
