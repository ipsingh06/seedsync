#!/bin/bash

./wait-for-it.sh myapp:8800 -- echo "Seedsync app is up (before configuring)"
curl -sS "http://myapp:8800/server/config/set/general/debug/true"; echo
curl -sS "http://myapp:8800/server/config/set/general/verbose/true"; echo
curl -sS "http://myapp:8800/server/config/set/lftp/remote_address/remote"; echo
curl -sS "http://myapp:8800/server/config/set/lftp/remote_username/remoteuser"; echo
curl -sS "http://myapp:8800/server/config/set/lftp/remote_password/remotepass"; echo
curl -sS "http://myapp:8800/server/config/set/lftp/remote_port/1234"; echo
curl -sS "http://myapp:8800/server/config/set/lftp/remote_path/%252Fhome%252Fremoteuser%252Ffiles"; echo
curl -sS "http://myapp:8800/server/config/set/autoqueue/patterns_only/true"; echo

curl -sS "http://myapp:8800/server/command/restart"; echo

./wait-for-it.sh myapp:8800 -- echo "Seedsync app is up (after configuring)"

echo
echo "Done configuring SeedSync app"
