FROM python:3.6-alpine3.13

ENV PYTHONUNBUFFERED 1

RUN set -ex; \
    # install prerequisites
    apk add --no-cache \
        docker-cli \
        docker-compose \
    ;

COPY . /usr/src/kiwi_scp

RUN set -ex; \
    pip3 --no-cache-dir --use-feature=in-tree-build install /usr/src/kiwi_scp

ENTRYPOINT ["kiwi"]
