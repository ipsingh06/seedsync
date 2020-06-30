# Frequently Asked Questions (FAQ)

## General

### How do I restart SeedSync Debian Service?

SeedSync can be restarted from the web GUI. If that fails, you can restart the service from command-line:

    :::bash
    sudo service seedsync restart


### SeedSync can't seem to connect to my remote server?

Make sure your remote server address was entered correctly.
If using password-based login, make sure the password is correct.
Check the logs for details about the exact failure.


### How can I save my settings across updates when using the Docker image?

To maintain state across updates, you can store the settings in the host machine.
Add the following option when starting the container.

    :::bash
    -v <directory on host>:/config

where `<directory on host>` refers to the location on host machine where you wish to store the application
state.


## Security

### Does SeedSync collect any data?

No, SeedSync does not collect any data.