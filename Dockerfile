FROM python:3.6.0
ENV PYTHONUNBUFFERED 1

RUN apt-get update \
    && apt-get -y install build-essential libssl-dev \
    && apt-get clean \
    && pip install --upgrade pip

RUN pip3 install Cython numpy

# Prepare environment
RUN mkdir /nseta-docker
WORKDIR /nseta-docker

# Install TA-lib
# COPY docker_build_helpers/* /tmp/
# RUN cd /tmp && /tmp/install_ta-lib.sh && rm -r /tmp/*ta-lib*
ENV LD_LIBRARY_PATH=/usr/local/lib:$LD_LIBRARY_PATH

# Install dependencies
RUN pip3 install fastquant git+git://github.com/enzoampil/fastquant.git@5f17e7087e1efb534e2db88775dba268d31de4be
RUN pip3 install timeout-decorator
COPY requirements.txt /nseta-docker
RUN pip3 install -r requirements.txt

# Build
COPY . /nseta-docker
RUN pip3 install -e .

WORKDIR /home