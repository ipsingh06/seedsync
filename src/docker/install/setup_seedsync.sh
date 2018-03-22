#!/bin/bash

# exit on first error
set -e

CONFIG_DIR="/home/user/.seedsync"
SETTINGS_FILE="${CONFIG_DIR}/settings.cfg"

replace_setting() {
    NAME=$1
    OLD_VALUE=$2
    NEW_VALUE=$3

    echo "Replacing ${NAME} from ${OLD_VALUE} to ${NEW_VALUE}"
    sed -i "s/${NAME} = ${OLD_VALUE}/${NAME} = ${NEW_VALUE}/" ${SETTINGS_FILE} && \
        grep -q "${NAME} = ${NEW_VALUE}" ${SETTINGS_FILE}
}

# Generate default config
mkdir -p ${CONFIG_DIR}
/usr/lib/seedsync/seedsync -c ${CONFIG_DIR} --exit > /dev/null 2>&1 > /dev/null || true

# Replace default values
replace_setting 'debug' 'False' 'True'
replace_setting 'verbose' 'False' 'True'
replace_setting 'remote_address' '<replace me>' 'remote'
replace_setting 'remote_username' '<replace me>' 'remoteuser'
replace_setting 'remote_password' '<replace me>' 'nopass'
replace_setting 'remote_port' '22' '1234'
replace_setting 'remote_path' '<replace me>' '\/home\/remoteuser\/files'
replace_setting 'local_path' '<replace me>' '\/home\/user\/files'
replace_setting 'use_ssh_key' 'False' 'True'
replace_setting 'patterns_only' 'False' 'True'

echo
echo
echo "Done configuring seedsync"
cat ${SETTINGS_FILE}
