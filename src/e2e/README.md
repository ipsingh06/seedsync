###To run e2e tests in dev mode:

1. Install dependencies
```
sudo npm install -g protractor
cd src/e2e
npm install
```

2. Choose which dev image to run: deb install or docker image
    1. Deb install
       ```
       export PATH_TO_INSTALL_DEB=<path to deb file>
       export TEST_FLAGS="\
         -f src/docker/compose/e2e-base.yml \
         -f src/docker/compose/e2e-dev.yml \
         -f src/docker/compose/install-base.yml \
         -p seedsync_test_dev"
       ```

    OR

    2. Docker image install
       ```
       export TEST_VERSION=<image version>
       export TEST_FLAGS="\
         -f src/docker/compose/e2e-base.yml \
         -f src/docker/compose/e2e-dev.yml \
         -f src/docker/compose/image.yml \
         -p seedsync_test_dev"
       ```

3. Build the docker dev image
```
docker-compose $TEST_FLAGS build
```


4. Start the docker dev image
```
docker-compose $TEST_FLAGS up
```

Note: to restart the docker images:
```
docker-compose $TEST_FLAGS down
```

4. Compile and run the tests

```
cd src/e2e/
rm -rf tmp && \
    ./node_modules/typescript/bin/tsc && \
    ./node_modules/protractor/bin/protractor tmp/conf.js
```

### About
The dev end-to-end tests use the following docker images:
1. myapp: Installs and runs the seedsync deb package
2. chrome: Runs the selenium server
3. remote: Runs a remote SSH server

The automated e2e tests additionally have:
4. tests: Runs the e2e tests

Notes:
1. In dev mode, the app is visible at http://localhost:port.
However the url used in test is still http://myapp:port as
that's how the selenium server accesses it.

2. The app requires a fully configured settings.cfg.