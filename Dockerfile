FROM        docker:dind

# Stakkr + dependencies installation
RUN         apk add --no-cache \
                alpine-sdk cargo curl git libffi-dev openssl-dev \
                python3 py3-pip py3-requests py3-wheel python3-dev rust && \
            # Install / upgrade pip
            python3 -m pip install --upgrade pip && \
            # Add dev tools
            # Install stakkr
            python3 -m pip install --pre stakkr && \
            # Clean
            apk del \
                alpine-sdk cargo curl libffi-dev openssl-dev \
                python3-dev py3-pip py3-wheel rust && \
            rm -rf /var/cache/apk/* /var/log/*

# Create user / group
RUN         addgroup stakkr && \
            adduser -s /bin/ash -D -S -G stakkr stakkr && \
            addgroup stakkr root

EXPOSE      80 443

# At the end as it changes everytime ;)
ARG         BUILD_DATE
ARG         DOCKER_TAG
ARG         VCS_REF
LABEL       maintainer="Emmanuel Dyan <emmanueldyan@gmail.com>" \
            org.label-schema.build-date=${BUILD_DATE} \
            org.label-schema.name=${DOCKER_TAG} \
            org.label-schema.description="Stakkr image with docker installed" \
            org.label-schema.url="https://hub.docker.com/r/stakkr/stakkr" \
            org.label-schema.vcs-url="https://github.com/stakkr-org/stakkr" \
            org.label-schema.vcs-ref=${VCS_REF} \
            org.label-schema.schema-version="1.0" \
            org.label-schema.vendor="edyan" \
            org.label-schema.docker.cmd="docker run -d --rm ${DOCKER_TAG}"
