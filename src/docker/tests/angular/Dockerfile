FROM node:12.16

RUN npm install -g \
    angular \
    @angular/cli

RUN apt-get update

# Install chrome
RUN wget -O /tmp/chrome.deb https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb && \
    dpkg -i /tmp/chrome.deb; apt-get -fy install

# ng src needs to be mounted on /src
WORKDIR /src

CMD ["ng", "test", \
     "--browsers", "ChromeHeadless", \
     "--single-run"]
