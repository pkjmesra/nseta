
FROM alpine:3.8 as python-builder

ENV PYTHON_VERSION 3.6.9-r1
ENV PYTHON_TA_LIB_VERSION 0.4.19
ENV PYTHONUNBUFFERED 1

USER root
WORKDIR /tmp

RUN apk add --no-cache python3=${PYTHON_VERSION} \
    && apk add --no-cache --virtual .build-deps \
        alpine-sdk \
        python3-dev=${PYTHON_VERSION} \
        curl \
    && cd /tmp \
    && curl -L -O http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz \
    && tar -xzf ta-lib-0.4.0-src.tar.gz \
    && cd ta-lib/ \
    && sed -i 's/^#define TA_IS_ZERO(v).*$/#define TA_IS_ZERO(v) (((-0.000000000000000001)<v)\&\&(v<0.000000000000000001))/' src/ta_func/ta_utility.h \
    && sed -i 's/^#define TA_IS_ZERO_OR_NEG(v).*$/#define TA_IS_ZERO_OR_NEG(v) (v<0.000000000000000001)/' src/ta_func/ta_utility.h \
    && ./configure --prefix=/usr \
    && make \
    && sudo make install \
    && pip3 install setuptools numpy \
    && pip3 install ta-lib==${PYTHON_TA_LIB_VERSION} \ 
    && apk del .build-deps \
    && rm -rf /root/.cache \
              /tmp/* \
              /var/cache/apk/* \
              /var/lib/apk/lists/*

WORKDIR /root

FROM python:3.6.6-alpine as base-python-talib
ENV PYTHONUNBUFFERED 1

COPY --from=python-builder ["/usr/lib/libta*", "/usr/lib/"]
COPY --from=python-builder ["/usr/lib/python3.6/site-packages/numpy", "/usr/local/lib/python3.6/site-packages/numpy"]

FROM scratch 

COPY --from=base-python-talib ["/", "/"]
COPY --from=python-builder ["/usr/lib/python3.6/site-packages/talib", "/usr/local/lib/python3.6/site-packages/talib"]

CMD ["python3"]

RUN python3 -c 'import numpy, talib; close = numpy.random.random(100); output = talib.SMA(close); print(output)'

FROM python:3.7.3
ENV PYTHONUNBUFFERED 1

RUN apt-get update \
    && apt-get -y -q --allow-unauthenticated install build-essential libssl-dev gcc g++ python-dev python3-dev sudo \
    && apt-get clean \
    && pip install --upgrade pip \
    && apt-get install curl file --no-install-recommends -y \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /root

RUN pip3 install Cython numpy
RUN pip3 install setuptools wheel twine python-dateutil
RUN pip3 install pytz==2019.3 pystan
RUN curl -L -O https://github.com/pandas-dev/pandas/releases/download/v1.0.3/pandas-1.0.3.tar.gz \
    && tar -xzf pandas-1.0.3.tar.gz \
    && cd pandas-1.0.3/ \
    && python3 setup.py install

RUN pip3 install fastquant git+git://github.com/enzoampil/fastquant.git@5f17e7087e1efb534e2db88775dba268d31de4be

# Prepare environment
RUN mkdir /nseta-docker
WORKDIR /nseta-docker

RUN curl -L -O https://github.com/pandas-dev/pandas/releases/download/v1.0.4/pandas-1.0.4.tar.gz \
    && tar -xzf pandas-1.0.4.tar.gz \
    && cd pandas-1.0.4/ \
    && python3 setup.py install

ENV LD_LIBRARY_PATH=/usr/local/lib:$LD_LIBRARY_PATH

# Install dependencies
RUN pip3 install timeout-decorator
COPY requirements.txt /nseta-docker

# RUN apt-get update \
#     && apt-get install ruby-full locales --no-install-recommends -y \
#     && rm -rf /var/lib/apt/lists/*
# RUN localedef -i en_US -f UTF-8 en_US.UTF-8
# RUN useradd -m -s /bin/zsh linuxbrew && \
#     usermod -aG sudo linuxbrew &&  \
#     mkdir -p /home/linuxbrew/.linuxbrew && \
#     chown -R linuxbrew: /home/linuxbrew/.linuxbrew
# USER linuxbrew
# RUN /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install.sh)"
# USER root
# RUN echo 'eval $(/home/linuxbrew/.linuxbrew/bin/brew shellenv)' >> /home/linuxbrew/.zprofile
# ENV PATH="/home/linuxbrew/.linuxbrew/bin:${PATH}"
# USER root
# RUN chown -R $CONTAINER_USER: /home/linuxbrew/.linuxbrew
# RUN brew install ta-lib
# ENV TA_LIBRARY_PATH=/usr/local/homebrew/lib
# ENV TA_INCLUDE_PATH=/usr/local/homebrew/include

RUN apt-get -y install libc-dev

RUN pip3 install convertdate==2.2.0 lunarcalendar holidays ipython==7.5.0
RUN pip3 install --upgrade plotly
RUN pip3 install -r requirements.txt

# Build
COPY . /nseta-docker
RUN pip3 install -e .

RUN python3 -c "import nseta; print(nseta.__version__); nseta --help"

RUN python3 -c 'from fastquant import get_stock_data; df = get_stock_data("JFC", "2021-01-01", "2021-01-01"); print(df.head(1))'

WORKDIR /home
