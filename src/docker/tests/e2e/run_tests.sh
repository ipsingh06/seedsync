#!/bin/bash

# exit on first error
set -e

# Link in all the src files we need
# Links will be created in the working directory
ln -s -t . \
    /e2e/tests \
    /e2e/node_modules \
    /e2e/conf.ts \
    /e2e/package.json \
    /e2e/tsconfig.json
# Note: don't link urls.ts, since we copied in a
#       a test-specific file

# Compile test code
/e2e/node_modules/typescript/bin/tsc --outDir ./tmp

# Run the tests
/e2e/node_modules/protractor/bin/protractor tmp/conf.js
