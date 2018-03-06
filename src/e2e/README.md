###To run e2e tests in dev mode:

1. Install dependencies
```
sudo npm install -g protractor
cd src/e2e
npm install
```

2. Build the docker dev image
```
docker-compose -f src/docker/compose/e2e-base.yml -f src/docker/compose/e2e-ubu1604.dev.yml -p seedsync_test_dev build
```

3. Start the docker dev image
```
export PATH_TO_INSTALL_DEB=<path to deb file>
docker-compose -f src/docker/compose/e2e-base.yml -f src/docker/compose/e2e-ubu1604.dev.yml -p seedsync_test_dev up
```

Note: to restart the docker images:
```
docker-compose -f src/docker/compose/e2e-base.yml -f src/docker/compose/e2e-ubu1604.dev.yml -p seedsync_test_dev down
```

4. Compile and run the tests

```
cd src/e2e/
rm -rf tmp && tsc && protractor tmp/conf.js
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