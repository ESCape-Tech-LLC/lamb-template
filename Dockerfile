FROM python:3.13-slim-bookworm


# tools
RUN apt-get update -y \
    && apt-get install -y --no-install-recommends \
        procps \
        net-tools \
        iputils-ping \
        dnsutils \
        traceroute \
        telnet \
        zlib1g \
        libjpeg-dev \
        libwebp-dev \
        zlib1g-dev \
        libfreetype6-dev \
        libraqm0 \
        libmagic-dev \
        libopenjp2-7-dev \
        liblcms2-dev \
        gcc \
        git \
        curl \
        vim \
        pkg-config \
        libcairo2-dev \
        argon2 \
        postgresql-server-dev-all \
        libpq-dev

# dependencies
COPY requirements.txt requirements.txt
COPY requirements-main.txt requirements-main.txt

# TODO: omit cache layer
RUN git config --global http.sslverify "false"  \
    && pip install -r requirements.txt \
    && pip cache purge


# application
WORKDIR /app
COPY . /app


# cleanup
RUN apt-get remove -y build-essential gcc python3-dev git \
    && apt-get clean autoclean \
    && apt-get autoremove --yes \
    && rm -rf /var/lib/{apt,dpkg,cache,log}/
