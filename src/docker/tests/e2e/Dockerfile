FROM node:latest

RUN npm install -g \
    protractor \
    typescript

ADD run_tests.sh /app/

WORKDIR /app

CMD ["./run_tests.sh"]
