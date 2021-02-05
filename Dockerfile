
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

FROM python:3.7.3 as base-python-talib
ENV PYTHONUNBUFFERED 1

COPY --from=python-builder ["/usr/lib/libta*", "/usr/lib/"]
COPY --from=python-builder ["/usr/lib/python3.6/site-packages/numpy", "/usr/local/lib/python3.6/site-packages/numpy"]

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

RUN apt-get -y install libc-dev

RUN pip3 install convertdate>=2.1.2 lunarcalendar holidays ipython==7.5.0
RUN pip3 install --upgrade plotly
RUN pip3 uninstall pystan -y
RUN pip3 install pystan==2.18

FROM pkjmesra/fastquant:0.1.3.23 as fastquant-builder
FROM wajdikh/fbprophet:latest as fbprophet-builder

WORKDIR /nseta-docker
COPY requirements.txt /nseta-docker
RUN pip3 install -r requirements.txt

FROM scratch

COPY --from=base-python-talib ["/", "/"]
COPY --from=python-builder ["/usr/lib/python3.6/site-packages/talib", "/usr/local/lib/python3.6/site-packages/talib"]
COPY --from=fastquant-builder ["/fastquant", "/usr/local/lib/python3.6/site-packages/fastquant"]
COPY --from=fbprophet-builder ["/fbprophet", "/usr/local/lib/python3.6/site-packages/fbprophet"]
RUN pip3 install --upgrade plotly

# Build
COPY . /nseta-docker
RUN pip3 install -e .

RUN python3 -c "import nseta; print(nseta.__version__);"
CMD ["python3"]
RUN python3 -c 'from fastquant import backtest;'
RUN python3 -c 'import numpy, talib; close = numpy.random.random(100); output = talib.SMA(close); print(output)'
RUN python3 -c "from fbprophet import Prophet;m = Prophet();"
RUN from nseta.scanner.volumeScanner import volumeScanner;s=volumeScanner(5,['HDFC']); s.scan();
WORKDIR /home
