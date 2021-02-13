FROM pkjmesra/fastquant_talib_debian_gnu_linux:latest as base-image
ENV PYTHONUNBUFFERED 1

FROM scratch

COPY --from=base-image ["/", "/"]

RUN curl -L -O https://files.pythonhosted.org/packages/1a/b5/9c3fefa8a7b839729df57deedf0a69815841dfb88f0df911f34d998230b7/fbprophet-0.7.1.tar.gz \
	&& tar -xzf fbprophet-0.7.1.tar.gz \
	&& rm -rf fbprophet-0.7.1.tar.gz

RUN apt-get -y install libc-dev
RUN apt-get update && apt-get -y install build-essential

RUN pip3 install -r fbprophet-0.7.1/requirements.txt
RUN pip3 install ipython==7.5.0

RUN cd fbprophet-0.7.1 \
	&& rm -rf fbprophet/stan_model \
	&& wget https://github.com/stan-dev/cmdstan/releases/download/v2.22.1/cmdstan-2.22.1.tar.gz -O /tmp/cmdstan.tar.gz > /dev/null \
	&& tar -xvf /tmp/cmdstan.tar.gz -C /tmp > /dev/null \
	&& make -C /tmp/cmdstan-2.22.1/ build > /dev/null \
	&& CMDSTAN=/tmp/cmdstan-2.22.1 STAN_BACKEND=CMDSTANPY python3 setup.py install \
	&& cd /

RUN cp -r fbprophet-0.7.1/build/lib/fbprophet/stan_model fbprophet-0.7.1/fbprophet/stan_model 

WORKDIR /
RUN cp -r fbprophet-0.7.1/fbprophet /usr/local/lib/python3.7/site-packages/fbprophet \
	&& rm -rf fbprophet*

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
