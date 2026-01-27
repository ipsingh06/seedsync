FROM node:20-bookworm-slim AS seedsync_test_angular

RUN apt-get update && apt-get install -y --no-install-recommends \
    wget \
    gnupg \
    && wget -nv -O /tmp/chrome.deb https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb \
    && dpkg -i /tmp/chrome.deb || apt-get -fy install > /dev/null \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy Angular 17 configuration files
COPY src/angular/package*.json ./
RUN npm install --include=dev --silent

COPY \
    src/angular/tsconfig.json \
    src/angular/tsconfig.app.json \
    src/angular/tsconfig.spec.json \
    src/angular/angular.json \
    /app/

COPY src/angular/src /app/src

CMD ["./node_modules/.bin/ng", "test", \
     "--browsers", "ChromeHeadless", \
     "--watch=false"]
