#!/bin/bash

while :
do
  SERVER_UP=$(
      curl -s myapp:8800/server/status | \
        python ./parse_seedsync_status.py
  )
  if [[ "${SERVER_UP}" == 'True' ]]; then
    break
  fi
  echo "E2E Test is waiting for Seedsync server to come up..."
  sleep 1
done

echo "E2E Test detected that Seedsync server is UP"
node_modules/protractor/bin/protractor tmp/conf.js
