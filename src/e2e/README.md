###To run e2e tests in dev mode:

1. Start the docker dev image
```
export PATH_TO_INSTALL_DEB=<path to deb file>
docker-compose -f src/docker/compose/e2e-base.yml -f src/docker/compose/e2e-ubu1604.dev.yml -p seedsync_test_dev up
```

2. Compile and run the tests

```
cd src/e2e/
rm -rf tmp && tsc && protractor tmp/conf.js
```
