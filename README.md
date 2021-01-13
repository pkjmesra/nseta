# nseta :nerd_face:

[![Build Status](https://travis-ci.com/pkjmesra/nseta.svg?branch=main)](https://travis-ci.com/pkjmesra/nseta)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/pkjmesra/nseta/blob/main/LICENSE)
[![Downloads](https://pepy.tech/badge/nseta/month)](https://pepy.tech/project/nseta/month)
[![Python](https://img.shields.io/pypi/pyversions/nseta.svg?style=plastic)](https://badge.fury.io/py/nseta)
[![PyPI](https://badge.fury.io/py/nseta.svg)](https://badge.fury.io/py/nseta)
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/14cc594e2dfe48519c699caa48136108)](https://app.codacy.com/gh/pkjmesra/nseta?utm_source=github.com&utm_medium=referral&utm_content=pkjmesra/nseta&utm_campaign=Badge_Grade)
[![Total alerts](https://img.shields.io/lgtm/alerts/g/pkjmesra/nseta.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/pkjmesra/nseta/alerts/)
[![Language grade: Python](https://img.shields.io/lgtm/grade/python/g/pkjmesra/nseta.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/pkjmesra/nseta/context:python)
[![codecov](https://codecov.io/gh/pkjmesra/nseta/branch/main/graph/badge.svg)](https://codecov.io/gh/pkjmesra/nseta)

Python Library (and console/CLI application) to 
-  Get publicly available data on [NSE India website](https://www1.nseindia.com/) <img src="/docs/assets/NSE_Logo.svg" width="118" height="28" alt="NSE India" > ie. stock live-quotes and historical data[ *EQUITY ONLY* AT THIS TIME. No support for Futures/Options/Derivatives yet.]
-  Plot various technical indicators
-  Pattern recognition and fitment using candlestick charts
-  Backtest trading strategies
-  Forecasting with standard as well as custom strategies
-  Create scanners and generate signals for various technical indicators or for BUY/SELL
-  Create and build your own trading strategy

## Disclaimer
- The recommendations that you receive when you run the scan for intraday or swing trading is only for academic research purposes.
- Though, you are free to take the recommended BUY/SELL positions, any loss you make from those are entirely at your own risk.
- The author of this library/console cannot be held responsible and is deemed free from any legal liability.

## Donate

[![Otechie](https://api.otechie.com/pkjmes/badge.svg)](https://otechie.com/pkjmes)

## Libraries Required
- (See requirements.txt file for more)

For Windows systems you can install Anaconda, this will cover many dependancies (You'll have to install requests and beautifulsoup additionally though)

## Installation
-  From code
```
python3 setup.py clean build install
```
-  Python pip
```
pip3 install nseta
```
-  Installing specific version
```
pip3 install nseta==0.6.68
```
  You can also directly install specific versions from pypi.org:
```
pip install --index-url https://pypi.org/simple/ --extra-index-url https://pypi.org/simple nseta==<Specific_Version>
```

-  Python shell
``` 
python3 -m pip install --upgrade nseta
```
-  Wheel (.whl) file from PyPi.org
  Just go ahead and download the ```.whl``` file from ```https://pypi.org/project/nseta/#files``` and install from the downloaded directory:

```
pip3 install ./nseta-0.6.68-py3-none-any.whl
```
  where 0.6.68 is the version of the library.

- Specific test versions(under development) can be installed from test.pypi.org
```
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple nseta==<Specific_Version>
```

After installation you can check what version you got installed
```
python3 -c "import nseta; print(nseta.__version__)"
```

## Usage

- Top level command options that provide you with various features
```python

#Usage Commands (You can use nsetacli or nseta - either is good.)
$ nseta
Usage: nseta [OPTIONS] COMMAND [ARGS]...

Options:
  --debug / --no-debug  --debug to turn debugging on. Default is off
  --trace / --no-trace  --trace to turn tracing on (works only with --debug). Default is off.
  --version             Shows the version of this library
  --help                Show this message and exit.

Commands:
  create-cdl-model       Create candlestick model.Plot uncovered patterns
  forecast-strategy      Forecast & measure performance of a trading model
  history                Get price history of a security for given dates
  live-quote             Get live price quote of a security
  pe-history             Get PE history of a security for given dates
  plot-ta                Plot various technical analysis indicators
  scan                   Scan live price quotes and calculate RSI for...
  test-trading-strategy  Measure the performance of your trading strategy
```
- Sample commands
```python

  Example:
  nseta create-cdl-model -S bandhanbnk -s 2019-07-30 -e 2020-11-20 --steps
  nseta forecast-strategy -S bandhanbnk -s 2019-07-30 -e 2020-11-20 --strategy rsi
  nseta history -S bandhanbnk -s 2019-07-30 -e 2020-11-20
  nseta live-quote -S bandhanbnk
  nseta pe-history -S bandhanbnk -s 2019-07-30 -e 2020-11-20
  nseta plot-ta -S bandhanbnk -s 2019-07-30 -e 2020-11-20
  nseta test-trading-strategy -S bandhanbnk -s 2019-07-30 -e 2020-11-20 --strategy rsi
  nseta scan -S HDFC,ABB -s
  nseta scan -i
  nseta scan -l
  nseta scan -s
  nseta scan -v
```
- Test your trading strategies

```python
nseta test-trading-strategy
Please provide start and end date in format yyyy-mm-dd
Usage:  [OPTIONS]

  Measure the performance of your trading strategy

Options:
  -S, --symbol TEXT               Security code
  -s, --start TEXT                Start date in yyyy-mm-dd format
  -e, --end TEXT                  End date in yyyy-mm-dd format
  --strategy [rsi|smac|macd|emac|bbands|multi|custom]
                                  rsi, smac, macd, emac, bbands, multi,
                                  custom. Choose one.
  -u, --upper TEXT                Used as upper limit, for example, for RSI.
                                  Only when strategy is "custom", we buy the
                                  security when the predicted next day return
                                  is > +{upper} %
  -l, --lower TEXT                Used as lower limit, for example, for RSI.
                                  Only when strategy is "custom", we sell the
                                  security when the predicted next day return
                                  is < -{lower} %
  --autosearch / --no-autosearch  --auto for allowing to automatically measure
                                  the performance of your trading strategy on
                                  multiple combinations of parameters.
  -i, --intraday                  Test trading strategy for the current
                                  intraday price history (Optional)
  --help                          Show this message and exit.
```

- Test your trading strategies (for example, using *RSI* as technical indicator)

```python
$ nseta test-trading-strategy -S bandhanbnk -s 2020-01-01 -e 2020-10-03 --strategy rsi --autosearch

init_cash : 100000
buy_prop : 1
sell_prop : 1
commission : 0.0075
===Strategy level arguments===
rsi_period : 14
rsi_upper : 70
rsi_lower : 15
Final Portfolio Value: 162418.36025
Final PnL: 62418.36

Time used (seconds): 0.13728976249694824
Optimal parameters: {'init_cash': 100000, 'buy_prop': 1, 'sell_prop': 1, 'commission': 0.0075, 'execution_type': 'close', 'channel': None, 'symbol': None, 'rsi_period': 14, 'rsi_upper': 70, 'rsi_lower': 15}
Optimal metrics: {'rtot': 0.4850052910757702, 'ravg': 0.00255265942671458, 'rnorm': 0.9026928562651005, 'rnorm100': 90.26928562651005, 'sharperatio': None, 'pnl': 62418.36, 'final_value': 162418.36025}
   rsi_period  rsi_upper  rsi_lower  init_cash    final_value       pnl
0          14         70         15     100000  162418.360250  62418.36
1          11         70         15     100000  154007.773625  54007.77
2           7         70         15     100000   96213.602375  -3786.40
3          14         70         30     100000   83074.073000 -16925.93
4          11         70         30     100000   78397.304875 -21602.70
```
![](./docs/assets/trading_strategy_rsi.png)

- Check historical data and export to csv file

```
$ nseta history -S bandhanbnk -s 2019-01-01 -e 2020-09-30
       Symbol Series        Date  Prev Close    Open   High     Low    Last   Close    VWAP   Volume      Turnover  Trades  Deliverable Volume  %Deliverable
0  BANDHANBNK     EQ  2019-01-01      550.15  552.50  560.0  544.10  558.00  556.70  552.21   589317  3.254256e+13   16658              175430        0.2977
1  BANDHANBNK     EQ  2019-01-02      556.70  553.00  563.7  549.60  551.40  552.15  556.91   834846  4.649319e+13   32119              250782        0.3004
2  BANDHANBNK     EQ  2019-01-03      552.15  551.00  554.0  530.00  532.05  533.80  540.61   620161  3.352631e+13   18616              282037        0.4548
3  BANDHANBNK     EQ  2019-01-04      533.80  534.25  541.7  527.05  528.05  528.90  533.42   579027  3.088645e+13   22405              186702        0.3224
4  BANDHANBNK     EQ  2019-01-07      528.90  540.00  542.0  495.55  495.55  498.05  509.49  2684675  1.367813e+14   76816             1160901        0.4324
Saved to: bandhanbnk.csv
```
- Create candlestick model
```python
nseta create-cdl-model
Usage:  [OPTIONS]

  Create candlestick model.Plot uncovered patterns

Options:
  -S, --symbol TEXT       Security code
  -s, --start TEXT        Start date in yyyy-mm-dd format
  -e, --end TEXT          End date in yyyy-mm-dd format
  -o, --file TEXT         Output file name. Default is {symbol}.csv
  --steps / --no-steps    --steps for saving intermediate steps in output file
  -f, --format [csv|pkl]  Output format, pkl - to save as Pickel and csv - to
                          save as csv
  --help                  Show this message and exit.
```
- Create candlestick models with pattern recognition
```
$ nseta create-cdl-model -S bandhanbnk -s 2019-01-01 -e 2020-09-30 --steps
                Symbol Series  Prev Close    Open   High  ...  CDLUNIQUE3RIVER  CDLUPSIDEGAP2CROWS  CDLXSIDEGAP3METHODS  candlestick_pattern  candlestick_match_count
Date                                                      ...                                                                                                        
2019-01-01  BANDHANBNK     EQ      550.15  552.50  560.0  ...                0                   0                    0           CDLHARAMI_Bull                      0.0
2019-01-02  BANDHANBNK     EQ      556.70  553.00  563.7  ...                0                   0                    0           CDLHARAMI_Bull                      0.0
2019-01-03  BANDHANBNK     EQ      552.15  551.00  554.0  ...                0                   0                    0           CDLMATCHINGLOW_Bull                      0.0
2019-01-04  BANDHANBNK     EQ      533.80  534.25  541.7  ...                0                   0                    0           CDLBELTHOLD_Bull                      0.0
2019-01-07  BANDHANBNK     EQ      528.90  540.00  542.0  ...                0                   0                    0           CDLTHRUSTING_Bear                      0.0

[5 rows x 72 columns]
Model saved to: bandhanbnk.csv
Candlestick pattern model plot saved to: bandhanbnk_candles.html
```
![](./docs/assets/cdl_model.png)

- Create various plots for analysis with technical indicators 
```
$ nseta plot-ta -S bandhanbnk -s 2019-01-01 -e 2020-09-30
```
![](./docs/assets/ti_plots.png)

- Forecast strategies
```python
nseta forecast-strategy
Usage:  [OPTIONS]

  Forecast & measure performance of a trading model

Options:
  -S, --symbol TEXT               Security code
  -s, --start TEXT                Start date in yyyy-mm-dd format
  -e, --end TEXT                  End date in yyyy-mm-dd format
  --strategy [rsi|smac|macd|emac|bbands|multi|custom]
                                  rsi, smac, macd, emac, bbands, multi,
                                  custom. Choose one.
  -u, --upper FLOAT               Only when strategy is "custom". We buy the
                                  security when the predicted next day return
                                  is > +{upper} %
  -l, --lower FLOAT               Only when strategy is "custom". We sell the
                                  security when the predicted next day return
                                  is < -{lower} %
  --help                          Show this message and exit.
```
- Create forecast strategies and verify them
```python
$ nseta forecast-strategy -S bandhanbnk -s 2019-01-01 -e 2020-09-30 --upper 1.5 --lower 1.5
   init_cash   final_value       pnl
0     100000  137220.87825  37220.88
```
![](./docs/assets/forecast-closing.png)
![](./docs/assets/forecast.png)
![](./docs/assets/forecast-predictions.png)

-  Get live quotes for a security
```python
nseta live-quote
Please provide security/index code
Usage:  [OPTIONS]

  Get live price quote of a security along with other (Optional) parameters

Options:
  -S, --symbol TEXT  Security code
  --series TEXT      Default series - EQ (Equity) (Optional)
  -g, --general      Get the general (Name, ISIN) details also (Optional)
  -o, --ohlc         Get the OHLC values also (Optional)
  -w, --wk52         Get the 52 week high/low values also (Optional)
  -v, --volume       Get the traded volume details also (Optional)
  -b, --orderbook    Get the current bid/offer details also (Optional)
  -p, --plot         Plot the "Close" values (Optional)
  -r, --background   Keep running the process in the background (Optional)
  --help             Show this message and exit.
```
-  Get live quotes with multiple options along with intraday history
```python
nseta live-quote -S bandhanbnk -gowvb
------------------------------------------
                                           
Name                |  Bandhan Bank Limited
ISIN                |          INE545U01014
Last Updated        |  29-DEC-2020 16:00:00
Prev Close          |                406.15
Last Trade Price    |                413.50
Change              |                  7.35
% Change            |                  1.81
Avg. Price          |                414.43
Upper Band          |                437.95
Lower Band          |                358.35
Open                |                408.00
High                |                419.25
Low                 |                407.45
Close               |                413.20
52 Wk High          |                526.00
52 Wk Low           |                152.20
Quantity Traded     |             82,37,480
Total Traded Volume |             82,37,480
Total Traded Value  |             34,138.59
Delivery Volume     |             17,43,202
% Delivery          |                 21.16


             Bid Price Offer Quantity Offer Price
Bid Quantity                                     
2,981           302.80            472      302.90
200             302.70          1,739      302.95
391             302.65         13,936      303.00
4,368           302.60          3,471      303.05
5,469           302.55            767      303.10
```
- Scan live quotes of securities
```python
nseta scan -S HDFC,ABB
              Updated Symbol     Close       LTP
 30-DEC-2020 16:00:00   HDFC  2,518.95  2,521.70
 30-DEC-2020 16:00:00    ABB  1,203.05  1,205.30
```
- Scan live quotes of a bunch of securities listed in a resource file(stocks.py)
```python
nseta scan -l
 All Stocks LTP and Signals:
              Updated      Symbol      Close        LTP  % Delivery  Buy - Sell TotalTradedVolume
 13-JAN-2021 15:30:02        ATUL   6,597.90   6,640.95       86.12     -7069.0          1,27,120
 13-JAN-2021 15:30:02   TEAMLEASE   2,774.05   2,822.00       74.94     -3491.0            39,713
 13-JAN-2021 15:30:02     MPHASIS   1,657.35   1,655.00       72.53     -8819.0          5,04,007
 13-JAN-2021 15:30:02   KOTAKBANK   1,903.45   1,880.00       71.40    -14945.0         55,82,559
 13-JAN-2021 15:30:02         FCL      64.50      62.10       71.16   -168378.0          5,86,217
 13-JAN-2021 15:30:02         FSL      99.05      97.65       67.68   -391015.0         23,45,958
 13-JAN-2021 15:30:02         MCX   1,686.50   1,696.00       66.67    -20385.0          1,90,965
 13-JAN-2021 15:30:02       GLAND   2,248.35   2,204.00       60.96     -8184.0          3,41,991
 13-JAN-2021 15:30:02         ABB   1,269.30   1,276.00       60.61     -3306.0          1,59,568
 13-JAN-2021 15:30:02      INDOCO     318.00     310.00       59.76     -6597.0          1,68,736
 13-JAN-2021 15:30:02    EVEREADY     207.10     204.45       59.62   -152053.0          2,70,159
 13-JAN-2021 15:30:02        HDFC   2,747.55   2,672.00       58.71    -19654.0         55,80,886
 13-JAN-2021 15:30:02    SYMPHONY   1,065.15   1,051.00       55.44     -8900.0            49,398
 13-JAN-2021 15:30:02  CASTROLIND     128.05     129.50       55.26   -388442.0         18,29,577
 13-JAN-2021 15:30:02         TCS   3,174.85   3,158.00       55.03     -8764.0         35,72,287
 13-JAN-2021 15:30:02  WOCKPHARMA     509.45     495.30       54.25    -47592.0          6,20,728
 13-JAN-2021 15:30:02   POWERGRID     203.70     205.00       54.17   -190444.0       1,33,82,757
 13-JAN-2021 15:30:02          LT   1,349.80   1,350.00       53.85   -282955.0         43,89,199
 13-JAN-2021 15:30:02        IDBI      32.15      31.40       53.66  -2591283.0       1,39,30,466
 13-JAN-2021 15:30:02  KAJARIACER     741.40     747.00       53.62    -14266.0          2,64,187
 13-JAN-2021 15:30:02    CROMPTON     403.30     397.25       53.12    -10720.0         11,89,119
 13-JAN-2021 15:30:02      RADICO     507.05     507.00       52.91    -86642.0          4,33,139
 13-JAN-2021 15:30:02  CHAMBLFERT     232.60     231.35       52.80   -105721.0          6,29,960
 13-JAN-2021 15:30:02   GODREJIND     434.55     434.00       52.45   -101223.0         17,55,353
 13-JAN-2021 15:30:02    GOODYEAR     959.15     955.95       51.76      2937.0            23,649
 13-JAN-2021 15:30:02      BIOCON     471.75     462.65       49.93   -219459.0         34,30,009
 13-JAN-2021 15:30:02      CONCOR     445.60     439.00       49.91   -185639.0         27,45,347
 13-JAN-2021 15:30:02  TORNTPHARM   2,833.50   2,767.95       48.54     -6328.0          3,70,961
 13-JAN-2021 15:30:02   REPCOHOME     270.70     265.00       48.17   -104416.0          6,37,267
 13-JAN-2021 15:30:02    HDFCBANK   1,481.00   1,473.65       48.13   -325155.0         84,65,607
 13-JAN-2021 15:30:02  ASIANPAINT   2,720.55   2,700.00       47.40     -7592.0         28,61,619
 13-JAN-2021 15:30:02      ARVIND      55.85      55.35       47.32   -335123.0         26,59,457
 13-JAN-2021 15:30:02     PRAJIND     130.10     125.55       47.28   -331887.0         16,32,592
 13-JAN-2021 15:30:02       SPARC     195.65     193.25       46.85   -256047.0          5,79,851
 13-JAN-2021 15:30:02    GODREJCP     762.20     770.50       45.95    -58223.0         1,756,953
 13-JAN-2021 15:30:02   BOMDYEING      82.25      80.10       45.72   -674830.0         25,32,984
 13-JAN-2021 15:30:02        INFY   1,371.75   1,388.65       45.01   -145870.0       1,44,41,047
 13-JAN-2021 15:30:02  TATACONSUM     624.30     619.95       44.29   -201096.0         36,59,235
 13-JAN-2021 15:30:02  BANDHANBNK     391.45     375.65       43.43   -664910.0       2,17,29,060
 13-JAN-2021 15:30:02  TORNTPOWER     337.45     330.50       43.35    -77974.0         13,58,268
 13-JAN-2021 15:30:02      FORTIS     171.80     166.90       43.32   -336844.0         50,97,715
 13-JAN-2021 15:30:02       TECHM   1,064.20   1,065.40       43.01    -54750.0         46,70,556
 13-JAN-2021 15:30:02  HINDUNILVR   2,375.90   2,371.00       42.95    -65291.0         17,02,421
 13-JAN-2021 15:30:02       TITAN   1,527.10   1,508.00       42.56      4940.0         35,26,352
 13-JAN-2021 15:30:02        MFSL     719.90     715.00       41.65      2322.0          9,73,158
 13-JAN-2021 15:30:02     HCLTECH   1,062.10   1,057.00       41.36    -85387.0         66,89,747
 13-JAN-2021 15:30:02         IGL     567.20     565.95       41.27    -41122.0         17,86,278
 13-JAN-2021 15:30:02     DCBBANK     121.80     120.55       40.73   -222881.0         12,38,863
 13-JAN-2021 15:30:02    HINDALCO     264.35     261.65       40.61   -222962.0       1,32,99,767
 13-JAN-2021 15:30:02  PIDILITIND   1,800.10   1,794.90       39.60      6666.0          5,29,910
 13-JAN-2021 15:30:02    RELIANCE   1,957.05   1,936.00       39.40   -807328.0       1,22,79,508
 13-JAN-2021 15:30:02   ICICIBANK     548.00     556.00       39.34   -966897.0       2,19,19,320
 13-JAN-2021 15:30:02     SBILIFE     925.00     928.40       39.22   -114140.0         19,96,264
 13-JAN-2021 15:30:02   BRITANNIA   3,631.65   3,622.00       39.20    -58004.0          7,98,011
 13-JAN-2021 15:30:02  CUMMINSIND     623.20     612.95       39.00    -32783.0         15,18,652
 13-JAN-2021 15:30:02  INDUSTOWER     261.35     259.00       38.89   -172048.0         4,287,757
 13-JAN-2021 15:30:02       IRCTC   1,480.45   1,461.00       38.61   -171114.0         11,80,044
 13-JAN-2021 15:30:02  CENTURYTEX     430.10     425.00       38.33   -101445.0          6,53,028
 13-JAN-2021 15:30:02      ASHOKA      95.75      94.25       37.28   -316686.0         13,75,611
 13-JAN-2021 15:30:02  MUTHOOTFIN   1,276.65   1,237.95       36.27    -68347.0         39,80,304
 13-JAN-2021 15:30:02    INDIACEM     168.50     170.20       35.09   -404328.0         37,81,430
 13-JAN-2021 15:30:02      VOLTAS     903.20     894.90       34.96      6551.0         12,45,754
 13-JAN-2021 15:30:02       DABUR     541.00     536.60       34.91   -188787.0         29,32,616
 13-JAN-2021 15:30:02         ITC     206.45     211.20       34.43  -1712366.0       6,39,04,353
 13-JAN-2021 15:30:02     HAVELLS   1,018.80   1,011.70       34.32    -25099.0         22,10,914
 13-JAN-2021 15:30:02    AXISBANK     675.70     686.05       33.52    -27742.0       1,56,45,019
 13-JAN-2021 15:30:02  GODREJPROP   1,474.00   1,430.00       33.44    -31071.0          8,52,039
 13-JAN-2021 15:30:02   AMBUJACEM     268.10     264.50       32.88   -145332.0         52,65,065
 13-JAN-2021 15:30:02        SAIL      75.90      74.10       32.70  -3393571.0       3,30,35,958
 13-JAN-2021 15:30:02        NMDC     127.45     125.40       32.04   -488350.0         84,38,234
 13-JAN-2021 15:30:02  ULTRACEMCO   5,639.00   5,645.50       31.95      4382.0          4,23,130
 13-JAN-2021 15:30:02  BHARTIARTL     565.75     576.30       31.54  -1329795.0       8,36,53,265
 13-JAN-2021 15:30:02     DRREDDY   5,353.85   5,280.00       31.30    -12741.0          6,58,940
 13-JAN-2021 15:30:02    MINDTREE   1,750.85   1,742.80       31.04    -11366.0          4,98,998
 13-JAN-2021 15:30:02         UPL     501.50     491.00       30.97   -266679.0         46,93,036
 13-JAN-2021 15:30:02         HAL     901.60     919.95       30.87   -118629.0          8,05,801
 13-JAN-2021 15:30:02    ASHOKLEY     121.60     121.50       30.49  -1659575.0       5,13,19,295
 13-JAN-2021 15:30:02  AUROPHARMA     958.25     940.55       30.42    -98793.0         29,98,155
 13-JAN-2021 15:30:02        BEML     966.25     963.95       30.27   -102130.0          4,07,744
 13-JAN-2021 15:30:02   HINDPETRO     224.90     226.80       30.07   -766753.0       1,15,49,624
 13-JAN-2021 15:30:02    CADILAHC     490.35     487.00       29.93   -353619.0         27,27,242
 13-JAN-2021 15:30:02    GLENMARK     517.25     512.90       29.75   -274058.0         19,63,497
 13-JAN-2021 15:30:02       WIPRO     457.70     459.00       29.71   -339092.0       2,91,81,001
 13-JAN-2021 15:30:02        VEDL     181.10     180.55       29.57  -1185879.0       1,67,79,793
 13-JAN-2021 15:30:02        NTPC     100.15     102.50       29.43  -1087932.0       4,92,30,289
 13-JAN-2021 15:30:02         LTI   4,285.15   4,430.00       29.04     -1554.0          3,76,219
 13-JAN-2021 15:30:02  FEDERALBNK      76.20      74.75       28.77  -2313685.0       4,17,59,426
 13-JAN-2021 15:30:02         PFC     121.45     121.05       28.24   -737947.0         55,61,616
 13-JAN-2021 15:30:02  MCDOWELL-N     644.00     639.35       28.12    -58907.0         24,38,564
 13-JAN-2021 15:30:02         ACC   1,795.10   1,788.95       28.09     -7598.0          9,22,665
 13-JAN-2021 15:30:02   NESTLEIND  17,999.10  18,015.00       27.82     -2651.0          1,09,381
 13-JAN-2021 15:30:02    EXIDEIND     204.30     201.50       27.80   -315475.0         91,66,650
 13-JAN-2021 15:30:02        GAIL     141.40     141.45       26.92  -1174576.0       2,71,65,471
 13-JAN-2021 15:30:02         BEL     134.45     133.70       26.71   -788405.0       1,28,15,348
 13-JAN-2021 15:30:02  IDFCFIRSTB      47.15      46.05       26.60  -3366528.0       5,65,33,589
 13-JAN-2021 15:30:02  HEROMOTOCO   3,248.25   3,256.00       26.49    -33410.0         14,23,881
 13-JAN-2021 15:30:02     ESCORTS   1,377.45   1,360.00       26.48   -109294.0         14,03,891
 13-JAN-2021 15:30:02      INDIGO   1,680.00   1,640.00       26.00      7530.0         13,12,936
 13-JAN-2021 15:30:02  BAJFINANCE   5,042.20   4,894.00       25.74    -72782.0         32,68,429
 13-JAN-2021 15:30:02         M&M     779.85     824.00       25.24     63029.0       1,96,05,430
 13-JAN-2021 15:30:02        BPCL     402.55     411.50       25.16   -983991.0       2,11,75,970
 13-JAN-2021 15:30:02   BANKINDIA      53.90      54.05       25.13  -2563022.0       2,25,70,545
 13-JAN-2021 15:30:02   LICHSGFIN     438.80     437.25       24.86   -203596.0       1,34,33,112
 13-JAN-2021 15:30:02  APOLLOTYRE     192.85     191.85       24.78   -314888.0         84,89,771
 13-JAN-2021 15:30:02   SUNPHARMA     609.65     602.45       24.78   -214719.0         61,85,389
 13-JAN-2021 15:30:02        ONGC     103.45     105.50       24.49  -2231590.0       4,23,83,660
 13-JAN-2021 15:30:02         PNB      36.50      36.50       23.29  -9043640.0      22,73,96,221
 13-JAN-2021 15:30:02       LUPIN   1,060.30   1,065.90       22.66   -112428.0         28,03,745
 13-JAN-2021 15:30:02  BERGEPAINT     803.15     798.00       22.52     11109.0          7,15,677
 13-JAN-2021 15:30:02        SBIN     292.50     305.95       22.45   -282891.0       7,80,34,626
 13-JAN-2021 15:30:02     SIEMENS   1,642.55   1,630.50       22.27     -2223.0          4,24,845
 13-JAN-2021 15:30:02         MGL   1,126.65   1,113.90       21.92    -43560.0          4,38,535
 13-JAN-2021 15:30:02  SRTRANSFIN   1,262.60   1,215.85       21.49   -127729.0         53,06,679
 13-JAN-2021 15:30:02       CIPLA     843.15     840.90       21.34    -16450.0         35,94,632
 13-JAN-2021 15:30:02         MRF  85,746.90  85,422.45       21.23      -906.0            57,613
 13-JAN-2021 15:30:02        BHEL      39.35      40.75       21.18  -7405715.0      15,44,12,403
 13-JAN-2021 15:30:02        MOIL     146.05     153.00       20.67   -234848.0         42,53,184
 13-JAN-2021 15:30:02      MARUTI   8,188.05   8,132.00       20.50    -25620.0          8,77,169
 13-JAN-2021 15:30:02    GMRINFRA      27.10      27.00       20.10  -2305909.0       1,61,78,790
 13-JAN-2021 15:30:02         SRF   5,929.40   6,020.00       19.26     32332.0          1,60,848
 13-JAN-2021 15:30:02     RBLBANK     257.50     254.00       18.81   -766251.0       1,75,60,356
 13-JAN-2021 15:30:02         IOC      97.95     101.05       17.81  -1193693.0       5,59,32,924
 13-JAN-2021 15:30:02   BATAINDIA   1,624.25   1,636.00       17.44    -33289.0         10,16,486
 13-JAN-2021 15:30:02    TVSMOTOR     518.75     510.60       17.44   -120370.0         29,63,845
 13-JAN-2021 15:30:02  BANKBARODA      70.75      75.35       17.29    127363.0      12,75,12,244
 13-JAN-2021 15:30:02   TATAELXSI   2,087.60   2,398.95       17.28    424055.0         53,67,299
 13-JAN-2021 15:30:02   EICHERMOT   2,881.65   2,877.00       17.03     -4381.0         18,77,984
 13-JAN-2021 15:30:02        ZEEL     226.15     228.45       16.70   -828424.0       1,34,41,022
 13-JAN-2021 15:30:02  INDUSINDBK     927.65     942.15       16.63   -396281.0         94,72,201
 13-JAN-2021 15:30:02         PEL   1,564.50   1,565.10       15.66    -94828.0         39,40,511
 13-JAN-2021 15:30:02         PVR   1,452.45   1,457.00       15.49    -78072.0         20,50,096
 13-JAN-2021 15:30:02   TATASTEEL     694.90     709.90       15.36   -385224.0       1,93,51,481
 13-JAN-2021 15:30:02    JSWSTEEL     399.55     401.80       14.88   -121780.0         68,83,661
 13-JAN-2021 15:30:02    TATACHEM     523.00     544.90       14.44   -125633.0       1,66,60,559
 13-JAN-2021 15:30:02  BHARATFORG     621.40     626.50       13.40    -91469.0       1,51,11,888
 13-JAN-2021 15:30:02  TATAMOTORS     237.80     242.85       12.47  -1893323.0      16,46,24,772
 13-JAN-2021 15:30:02         DLF     267.55     279.10       10.27   -148217.0       5,31,91,510
 13-JAN-2021 15:30:02    ADANIENT     525.40     533.00        9.95    -13314.0         49,48,295
 13-JAN-2021 15:30:02  JINDALSTEL     294.40     298.65        9.85   -271520.0       1,05,45,511
No signals to show here.
Live scanning finished.

```

## Signals and Scanners

### Scanners
- When RSI(14) > 75
- When RSI(14) < 25
- When LTP > SMA(10)
- When LTP < SMA(10)
- When LTP > EMA(9)
- When LTP < SMA(9)
- When LTP < lower BBand
- When LTP > higher BBand

- Scanning options
```python
nseta scan --help
Usage: nseta scan [OPTIONS]

  Scan live and intraday for prices and signals.

Options:
  -S, --stocks TEXT               Comma separated security codes(Optional.
                                  When skipped, all stocks configured in
                                  stocks.py will be scanned.)
  -l, --live                      Scans (every min.) the live-quote and lists
                                  those that meet the signal criteria. Works
                                  best with --background.
  -i, --intraday                  Scans (every 10 sec) the intraday price
                                  history and lists those that meet the signal
                                  criteria
  -s, --swing                     Scans (every 10 sec) the past 365 days price
                                  history and lists those that meet the signal
                                  criteria
  -t, --indicator [rsi|sma10|sma50|ema|macd|bbands|all]
                                  rsi, sma10, sma50, ema, macd, bbands, all.
                                  Choose one.
  -r, --background                Keep running the process in the background
                                  (Optional)
  --help                          Show this message and exit.
```

For example:
- Scanning intraday based on Bollinger bands
```python
nseta scan -i -t bbands
INFO - tiscanner.py(scan_intraday - 123)
This run of intraday scan took 10.7 sec

INFO - livecli.py(scan_intraday_results - 150)
Saved to: Scan_Results.csv

Saved to: Scan_Results.csv
INFO - livecli.py(scan_intraday_results - 155)

We recommend taking the following BUY/SELL positions immediately for day trading. Intraday Signals:
               Date      Symbol     BBands-U     BBands-L      LTP                   Signal
2021-01-04 14:30:04      ASHOKA    93.434693    93.170307    93.40  (SELL) [LTP ~ BBands-U]
2021-01-04 14:30:00   BANKINDIA    50.440129    50.294871    50.40  (SELL) [LTP ~ BBands-U]
2021-01-04 14:30:01        BHEL    40.154087    39.935913    40.10  (SELL) [LTP ~ BBands-U]
2021-01-04 14:30:00  JINDALSTEL   284.777021   282.052979   284.80  (SELL) [LTP > BBands-U]
2021-01-04 14:30:00        NTPC    99.039443    98.860557    99.00  (SELL) [LTP ~ BBands-U]
2021-01-04 14:30:00        SAIL    77.886024    77.103976    77.85  (SELL) [LTP ~ BBands-U]
2021-01-04 14:30:00  ULTRACEMCO  5313.098214  5301.341786  5313.15  (SELL) [LTP > BBands-U]
```
- Scanning live-quotes during trading session
```python
nseta scan -l
All Stocks LTP and Signals:
              Updated      Symbol      Close        LTP  % Delivery  Buy - Sell TotalTradedVolume
 13-JAN-2021 15:30:02        ATUL   6,597.90   6,640.95       86.12     -7069.0          1,27,120
 13-JAN-2021 15:30:02   TEAMLEASE   2,774.05   2,822.00       74.94     -3491.0            39,713
 13-JAN-2021 15:30:02     MPHASIS   1,657.35   1,655.00       72.53     -8819.0          5,04,007
 13-JAN-2021 15:30:02   KOTAKBANK   1,903.45   1,880.00       71.40    -14945.0         55,82,559
 13-JAN-2021 15:30:02         FCL      64.50      62.10       71.16   -168378.0          5,86,217
 13-JAN-2021 15:30:02         FSL      99.05      97.65       67.68   -391015.0         23,45,958
 13-JAN-2021 15:30:02         MCX   1,686.50   1,696.00       66.67    -20385.0          1,90,965
 13-JAN-2021 15:30:02       GLAND   2,248.35   2,204.00       60.96     -8184.0          3,41,991
 13-JAN-2021 15:30:02         ABB   1,269.30   1,276.00       60.61     -3306.0          1,59,568
 13-JAN-2021 15:30:02      INDOCO     318.00     310.00       59.76     -6597.0          1,68,736
 13-JAN-2021 15:30:02    EVEREADY     207.10     204.45       59.62   -152053.0          2,70,159
 13-JAN-2021 15:30:02        HDFC   2,747.55   2,672.00       58.71    -19654.0         55,80,886
 13-JAN-2021 15:30:02    SYMPHONY   1,065.15   1,051.00       55.44     -8900.0            49,398
 13-JAN-2021 15:30:02  CASTROLIND     128.05     129.50       55.26   -388442.0         18,29,577
 13-JAN-2021 15:30:02         TCS   3,174.85   3,158.00       55.03     -8764.0         35,72,287
 13-JAN-2021 15:30:02  WOCKPHARMA     509.45     495.30       54.25    -47592.0          6,20,728
 13-JAN-2021 15:30:02   POWERGRID     203.70     205.00       54.17   -190444.0       1,33,82,757
 13-JAN-2021 15:30:02          LT   1,349.80   1,350.00       53.85   -282955.0         43,89,199
 13-JAN-2021 15:30:02        IDBI      32.15      31.40       53.66  -2591283.0       1,39,30,466
 13-JAN-2021 15:30:02  KAJARIACER     741.40     747.00       53.62    -14266.0          2,64,187
 13-JAN-2021 15:30:02    CROMPTON     403.30     397.25       53.12    -10720.0         11,89,119
 13-JAN-2021 15:30:02      RADICO     507.05     507.00       52.91    -86642.0          4,33,139
 13-JAN-2021 15:30:02  CHAMBLFERT     232.60     231.35       52.80   -105721.0          6,29,960
 13-JAN-2021 15:30:02   GODREJIND     434.55     434.00       52.45   -101223.0         17,55,353
 13-JAN-2021 15:30:02    GOODYEAR     959.15     955.95       51.76      2937.0            23,649
```
- Scanning for swing trading
```python
nseta scan -s
This run of swing scan took 36.5 sec

We recommend taking the following BUY/SELL positions for swing trading. Swing Signals:
     Symbol       Date    RSI   EMA(9)  macd(12)  macdsignal(9)  macdhist(26)  BBands-U  BBands-L      LTP Signal           Remarks Confidence
   ADANIENT 2021-01-13  78.71   512.08     24.53          19.08          5.46    540.15    433.29   536.05   SELL       [RSI >= 75]       20 %
   ASHOKLEY 2021-01-13  85.71   112.24      6.14           2.63          3.51    121.06     83.93   121.65   SELL       [RSI >= 75]       30 %
     ARVIND 2021-01-13  73.24    52.04      1.92           1.41          0.51     55.43     42.52    55.45   SELL  [LTP > BBands-U]       30 %
 BANKBARODA 2021-01-13  77.69    67.68      1.13           0.50          0.63     71.74     56.65    75.25   SELL       [RSI >= 75]       30 %
 BHARATFORG 2021-01-13  75.41   591.40     14.56           1.63         12.94    627.04    485.89   628.25   SELL       [RSI >= 75]       30 %
 BHARTIARTL 2021-01-13  77.49   545.25     13.74           9.90          3.85    565.51    481.84   578.25   SELL       [RSI >= 75]       30 %
        DLF 2021-01-13  80.37   253.49     13.07          11.52          1.56    267.99    209.78   280.45   SELL       [RSI >= 75]       30 %
  EICHERMOT 2021-01-13  77.02  2733.29    106.27          29.89         76.38   2872.25   2283.86  2868.65   SELL       [RSI >= 75]       20 %
       GAIL 2021-01-13  79.57   134.22      4.72           2.47          2.25    141.37    112.35   141.25   SELL       [RSI >= 75]       20 %
   GMRINFRA 2021-01-13  53.35    27.00      0.18          -0.11          0.30     28.37     24.97    27.05    BUY    [LTP > EMA(9)]       60 %
    HAVELLS 2021-01-13  81.00   978.66     46.03          39.09          6.95   1022.68    842.39  1012.45   SELL       [RSI >= 75]       40 %
    HCLTECH 2021-01-13  77.34  1009.59     53.99          42.17         11.82   1065.45    840.21  1055.95   SELL       [RSI >= 75]       20 %
        IGL 2021-01-13  77.63   543.35     25.17          13.90         11.27    572.96    451.60   565.60   SELL       [RSI >= 75]       20 %
       INFY 2021-01-13  77.84  1324.04     60.16          52.29          7.86   1388.67   1134.20  1387.15   SELL       [RSI >= 75]       20 %
        LTI 2021-01-13  77.46  4087.24    306.71         235.82         70.89   4410.78   3122.27  4402.45   SELL       [RSI >= 75]       20 %
        M&M 2021-01-13  75.18   770.40     15.71          -2.31         18.02    802.97    669.92   828.35   SELL       [RSI >= 75]       30 %
     RADICO 2021-01-13  75.98   490.61     12.22           1.33         10.90    512.44    422.56   507.55   SELL       [RSI >= 75]       20 %
       SBIN 2021-01-13  76.97   288.21      8.71           5.65          3.06    300.68    253.14   306.80   SELL       [RSI >= 75]       30 %
        SRF 2021-01-13  76.59  5819.21    184.53         143.22         41.31   6018.07   5226.76  6008.95   SELL       [RSI >= 75]       20 %
   TATACHEM 2021-01-13  81.15   506.85      1.60          -0.88          2.49    525.12    454.61   541.95   SELL       [RSI >= 75]       30 %
  TATAELXSI 2021-01-13  85.08  2065.71    174.65         113.52         61.12   2258.77   1477.74  2371.85   SELL       [RSI >= 75]       30 %
 TATAMOTORS 2021-01-13  87.18   212.61     12.80           3.92          8.88    231.93    150.03   242.60   SELL       [RSI >= 75]       30 %
      TECHM 2021-01-13  75.67  1032.22     44.72          29.42         15.30   1081.25    882.72  1069.65   SELL       [RSI >= 75]       40 %
      WIPRO 2021-01-13  88.42   427.88     26.79          17.74          9.05    457.49    332.60   459.00   SELL       [RSI >= 75]       30 %
Swing scanning finished.

```

- Scanning based on volumes
```python
nseta scan -v
Volume Signals:
     Symbol                  Date     VWAP       LTP  TodayVsYest(%)  TodayVs7Day(%)  YestVs7Day(%)  Yest-%Deliverable  Today%Deliverable  7DayAvgVolume  TodaysVolume  TodaysBuy-SelllDiff
       MOIL  13-JAN-2021 16:00:00   147.77    153.00           960.0           937.0           -2.0              45.32              16.29      410063.43     42,53,516                  NaN
 BHARATFORG  13-JAN-2021 16:00:00   619.08    626.50           544.0           338.0          -32.0              18.90              11.85     3454696.14   1,51,15,174                  NaN
  TATAELXSI  13-JAN-2021 16:00:00  2114.73  2,398.95           530.0          1021.0           78.0              23.87              12.63      478625.57     53,67,427                  NaN
       ATUL  13-JAN-2021 16:00:00  6593.64  6,640.95           393.0           287.0          -22.0              62.71              86.12       32846.00      1,27,126                  NaN
       BHEL  13-JAN-2021 16:00:00    39.51     40.75           308.0           296.0           -3.0              20.14              18.32    39062576.86  15,45,73,968                  NaN
  TEAMLEASE  13-JAN-2021 16:00:00  2789.78  2,822.00           272.0            29.0          -65.0              38.50              74.94       30741.71        39,718                  NaN
        M&M  13-JAN-2021 16:00:00   785.66    824.00           254.0           431.0           50.0              29.54              22.67     3691342.86   1,96,10,461                  NaN
 BHARTIARTL  13-JAN-2021 16:00:00   559.81    576.30           230.0           357.0           39.0              38.74              31.54    18309113.57   8,36,68,562                  NaN
 MUTHOOTFIN  13-JAN-2021 16:00:00  1273.55  1,237.95           214.0           271.0           18.0              49.30              34.41     1074672.71     39,82,200                  NaN
    SIEMENS  13-JAN-2021 16:00:00  1651.87  1,630.50           191.0            64.0          -44.0              16.40              22.27      258853.43      4,24,905                  NaN
  GODREJIND  13-JAN-2021 16:00:00   434.44    434.00           178.0           470.0          105.0              48.07              48.75      308610.14     17,58,041                  NaN
        HAL  13-JAN-2021 16:00:00   904.84    919.95           176.0            73.0          -37.0              43.93              27.24      464817.57      8,06,377                  NaN
  HINDPETRO  13-JAN-2021 16:00:00   226.10    226.80           156.0           162.0            2.0              35.12              30.07     4418919.00   1,15,55,573                  NaN
       BPCL  13-JAN-2021 16:00:00   404.45    411.50           154.0           252.0           38.0              27.33              23.82     6025170.43   2,11,81,147                  NaN
  LICHSGFIN  13-JAN-2021 16:00:00   438.29    437.25           129.0            96.0          -14.0              29.83              24.86     6842493.43   1,34,35,773                  NaN
       NTPC  13-JAN-2021 16:00:00    99.85    102.50           103.0           153.0           24.0              42.72              26.44    19498864.00   4,92,36,964                  NaN
Volume scanning finished.

```

### Signals
- SELL : When RSI(14) > 75
- BUY : When RSI(14) < 25
- BUY : When LTP > SMA(10) and SMA(10) is upstrending
- SELL : When LTP < SMA(10) and SMA(10) is downtrending
- BUY : When LTP > EMA(9) and EMA(9) is upstrending
- SELL : When LTP < EMA(9) and EMA(9) is downtrending
- BUY : When LTP < lower BBand
- SELL : When LTP > higher BBand

### Submit patches

If you have fixed an issue or added a new feature, please fork this repository, make your changes and submit a pull request. [Here's good article on how to do this.](https://code.tutsplus.com/tutorials/how-to-collaborate-on-github--net-34267) 

## License
[MIT License](https://github.com/pkjmesra/nseta/blob/main/LICENSE)

## Inspirations (Thank you so much!)
-  [nsepy](https://github.com/swapniljariwala/nsepy)
-  [fastquant](https://github.com/enzoampil/fastquant)
-  [fbprophet](https://github.com/facebook/prophet)
-  [nsetools](https://github.com/vsjha18/nsetools)
-  [ta-lib](https://github.com/mrjbq7/ta-lib)
-  [medium](https://github.com/CanerIrfanoglu/medium)
