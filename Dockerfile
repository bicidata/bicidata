FROM python:latest as environment-python

# Configure Debian and define locales:
ENV DEBIAN_FRONTEND='noninteractive' DEBCONF_NONINTERACTIVE_SEEN='true'
RUN apt-get -qq update && \
    apt-get -qq install -y apt-utils && \
#    dpkg-reconfigure apt-utils libapt-inst1.5 && \
    rm -rf /var/lib/apt/lists/*
RUN ln -fs /usr/share/zoneinfo/Europe/Madrid /etc/localtime && \
    dpkg-reconfigure --frontend noninteractive tzdata && \
    apt-get -qq update && \
    apt-get -qq install --reinstall -y locales && \
    sed -i -e 's/# en_US.UTF-8 UTF-8/en_US.UTF-8 UTF-8/' /etc/locale.gen && \
    locale-gen en_US.UTF-8 && \
    dpkg-reconfigure locales && \
    /usr/sbin/update-locale LANG=en_US.UTF-8 && \
    rm -rf /var/lib/apt/lists/*
ENV LANG='en_US.UTF-8' LANGUAGE='en_US:en' LC_ALL='en_US.UTF-8'

FROM environment-python

RUN mkdir -p /opt/bicidata
WORKDIR /opt/bicidata

COPY . .

RUN pip install -r requirements.txt

ENTRYPOINT python -m bicidata.apps.server
