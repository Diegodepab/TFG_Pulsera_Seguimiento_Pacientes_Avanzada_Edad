FROM node:20.10.0 as build-deps
LABEL maintainer = "Diego De Pablo"

RUN mkdir /code
COPY frontend/platform/package.json /code
COPY frontend/platform/package-lock.json /platform
COPY frontend/platform/.npmrc /code

RUN cd /code \
    && npm install

COPY frontend/platform/. /code

RUN cd /code \
    && npm run build \
    && chown -R node.node /code

USER node

WORKDIR /code
CMD [ "npm", "run", "dev" ]
