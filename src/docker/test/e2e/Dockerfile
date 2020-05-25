# Creates environment for e2e tests
FROM node:12.16 as seedsync_test_e2e_env

COPY src/e2e/package*.json /app/
WORKDIR /app
RUN npm install


# Builds and runs e2e tests
FROM seedsync_test_e2e_env as seedsync_test_e2e

COPY \
    src/e2e/conf.ts \
    src/e2e/tsconfig.json \
    /app/
COPY src/e2e/tests /app/tests
COPY \
    src/docker/test/e2e/urls.ts \
    src/docker/test/e2e/run_tests.sh \
    src/docker/test/e2e/parse_seedsync_status.py \
    /app/

WORKDIR /app

RUN node_modules/typescript/bin/tsc --outDir ./tmp

CMD ["/app/run_tests.sh"]
