FROM python:3.8-slim-buster

ARG USER=scrapy-user
ARG SCRAPY_USER_HOME=/usr/local/mops-crawler
ENV SCRAPY_HOME=${SCRAPY_USER_HOME}
ENV SCRAPY_INFO_DIR=/var/scrapyd

# Define en_US.
ENV LANGUAGE en_US.UTF-8
ENV LANG en_US.UTF-8
ENV LC_ALL en_US.UTF-8
ENV LC_CTYPE en_US.UTF-8
ENV LC_MESSAGES en_US.UTF-8

COPY . ${SCRAPY_HOME}
COPY scrapyd.conf /etc/scrapyd/scrapyd.conf

RUN set -ex\
    && buildDeps=' \
        freetds-dev \
        libkrb5-dev \
        libsasl2-dev \
        libssl-dev \
        libffi-dev \
        libpq-dev \
        git \
    ' \
    && apt-get update -yqq \
    && apt-get upgrade -yqq \
    && apt-get install -yqq --no-install-recommends \
        $buildDeps \
        freetds-bin \
        build-essential \
        default-libmysqlclient-dev \
        apt-utils \
        curl \
        rsync \
        netcat \
        locales \
    && sed -i 's/^# en_US.UTF-8 UTF-8$/en_US.UTF-8 UTF-8/g' /etc/locale.gen \
    && locale-gen \
    && update-locale LANG=en_US.UTF-8 LC_ALL=en_US.UTF-8 \
    && useradd -ms /bin/bash -d ${SCRAPY_USER_HOME} ${USER} \
    && pip install --upgrade pip\
    && pip install -r ${SCRAPY_HOME}/requirements.txt\
    && apt-get purge --auto-remove -yqq $buildDeps \
    && apt-get autoremove -yqq --purge \
    && apt-get clean \
    && rm -rf \
        /var/lib/apt/lists/* \
        /tmp/* \
        /var/tmp/* \
        /usr/share/man \
        /usr/share/doc \
        /usr/share/doc-base\
    && mkdir -p ${SCRAPY_INFO_DIR}\
    && chown -R ${USER}: ${SCRAPY_INFO_DIR}

RUN chown -R ${USER}: ${SCRAPY_HOME}
WORKDIR ${SCRAPY_HOME}
EXPOSE 6800
USER ${USER}

CMD ["bash"]