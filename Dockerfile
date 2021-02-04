FROM python:3.6.0
ENV PYTHONUNBUFFERED 1

RUN apt-get update \
    && apt-get -y -q --allow-unauthenticated install build-essential libssl-dev git sudo \
    && apt-get clean \
    && pip install --upgrade pip \
    && apt-get install build-essential curl file git ruby-full locales --no-install-recommends -y \
    && rm -rf /var/lib/apt/lists/*
RUN localedef -i en_US -f UTF-8 en_US.UTF-8
RUN useradd -m -s /bin/zsh linuxbrew && \
    usermod -aG sudo linuxbrew &&  \
    mkdir -p /home/linuxbrew/.linuxbrew && \
    chown -R linuxbrew: /home/linuxbrew/.linuxbrew
USER linuxbrew
RUN /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install.sh)"

USER root
ENV PATH="/home/linuxbrew/.linuxbrew/bin:${PATH}"
USER root
RUN chown -R $CONTAINER_USER: /home/linuxbrew/.linuxbrew

RUN pip3 install Cython numpy
RUN pip3 install setuptools wheel twine
RUN brew install ta-lib
RUN pip3 install fastquant

# Prepare environment
RUN mkdir /nseta-docker
WORKDIR /nseta-docker

# Install TA-lib
# COPY docker_build_helpers/* /tmp/
# RUN cd /tmp && /tmp/install_ta-lib.sh && rm -r /tmp/*ta-lib*
ENV LD_LIBRARY_PATH=/usr/local/lib:$LD_LIBRARY_PATH

# Install dependencies
# RUN pip3 install fastquant git+git://github.com/enzoampil/fastquant.git@5f17e7087e1efb534e2db88775dba268d31de4be
RUN pip3 install timeout-decorator
COPY requirements.txt /nseta-docker
RUN pip3 install -r requirements.txt

# Build
COPY . /nseta-docker
RUN pip3 install -e .

WORKDIR /home
