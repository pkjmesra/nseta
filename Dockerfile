FROM pkjmesra/fastquant_talib_debian_gnu_linux:latest as base-image
ENV PYTHONUNBUFFERED 1

FROM scratch

COPY --from=base-image ["/", "/"]

RUN apt-get -y install libc-dev
RUN apt-get update && apt-get -y install build-essential

RUN pip3 install ipython==7.5.0

WORKDIR /

RUN apt-get -y install unzip

RUN wget https://github.com/pkjmesra/nseta/archive/main.zip && \
  unzip main.zip && \
  rm -rf main.zip

WORKDIR nseta-main
RUN pip3 install --upgrade pip
RUN pip3 install convertdate>=2.3.0
RUN pip3 install sanic==19.12.2
RUN pip3 install multidict==4.6
RUN python3 setup.py clean build install

WORKDIR /
RUN rm -rf nseta*

RUN python3 -c 'import numpy, talib; close = numpy.random.random(100); output = talib.SMA(close); print(output)'

RUN python3 -c 'from fastquant import backtest, get_yahoo_data; data = get_yahoo_data("TSLA", "2020-11-01", "2021-01-30");backtest("smac", data, fast_period=15, slow_period=20, verbose=False, plot=False)'

RUN python3 -c "from fbprophet import Prophet;m = Prophet();"

RUN python3 -c "import nseta; print(nseta.__version__);"

RUN python3 -c "from nseta.scanner.volumeScanner import volumeScanner; from nseta.scanner.baseStockScanner import ScannerType; s=volumeScanner(ScannerType.Volume,['HDFC']); s.scan();"
