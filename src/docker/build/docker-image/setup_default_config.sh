#!/bin/bash

# exit on first error
set -e

CONFIG_DIR="/config"
SETTINGS_FILE="${CONFIG_DIR}/settings.cfg"
SCRIPT_PATH="/app/python/seedsync.py"

replace_setting() {
    NAME=$1
    OLD_VALUE=$2
    NEW_VALUE=$3

    echo "Replacing ${NAME} from ${OLD_VALUE} to ${NEW_VALUE}"
    sed -i "s/${NAME} = ${OLD_VALUE}/${NAME} = ${NEW_VALUE}/" ${SETTINGS_FILE} && \
        grep -q "${NAME} = ${NEW_VALUE}" ${SETTINGS_FILE}
}

# Generate default config
python ${SCRIPT_PATH} \
    -c ${CONFIG_DIR} \
    --html / \
    --scanfs / \
    --exit > /dev/null 2>&1 > /dev/null || true

cat ${SETTINGS_FILE}


# Replace default values
replace_setting 'local_path' '<replace me>' '\/downloads\/'

echo
echo
echo "Done configuring seedsync"
cat ${SETTINGS_FILE}
