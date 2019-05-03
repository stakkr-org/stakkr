FROM        docker:dind
MAINTAINER  Emmanuel Dyan <emmanueldyan@gmail.com>

# Stakkr + dependencies installation
RUN         apk add --no-cache python3 alpine-sdk curl git openssl-dev python3-dev libffi-dev && \
            # Install / upgrade pip
            python3 -m pip install --upgrade pip && \
            # Add dev tools
            # Install stakkr
            python3 -m pip install --pre stakkr && \
            # Clean
            apk del alpine-sdk curl openssl-dev python3-dev libffi-dev && \
            rm -rf /var/cache/apk/* /var/log/*

# Create user / group
RUN         addgroup stakkr && \
            adduser -s /bin/ash -D -S -G stakkr stakkr && \
            addgroup stakkr root

EXPOSE      80 443
