#!/bin/bash

# exit on first error
set -e

# Compile test code
tsc -p /e2e/ --outDir ./tmp

# Link node_module to compiled code directory
# Not sure why this is needed, breaks without it
ln -s /e2e/node_modules .

# Run the tests
protractor tmp/conf.js
