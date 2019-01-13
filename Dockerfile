FROM        docker:dind
MAINTAINER  Emmanuel Dyan <emmanueldyan@gmail.com>

RUN         apk add --no-cache curl git python3 w3m && \
            rm -rf /var/cache/apk/* /var/log/*

RUN         python3 -m pip install --pre --upgrade stakkr
RUN         addgroup stakkr
RUN         adduser -s /bin/ash -D -S -G stakkr stakkr
RUN         addgroup stakkr root

EXPOSE      80 443
