FROM node:6.12

RUN npm install -g \
    protractor \
    typescript

ADD run_tests.sh /app/
ADD urls.ts /app/

WORKDIR /app

CMD ["./run_tests.sh"]
