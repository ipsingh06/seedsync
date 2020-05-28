### To run e2e tests in dev mode:

1. Install dependencies

   ```bash
   cd src/e2e
   npm install
   ```
   
2. Choose which dev image to run: deb install or docker image

3. Compile and run the tests

    ```bash
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
1. In dev mode, the app is visible at [http://localhost:8800](http://localhost:8800)
However the url used in test is still [http://myapp:8800](http://myapp:8800) as
that's how the selenium server accesses it.

2. The app requires a fully configured settings.cfg.
   This is done automatically in during the start of the docker image that runs the app.

