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
Initial log joint probability = -6.20343
    Iter      log prob        ||dx||      ||grad||       alpha      alpha0  # evals  Notes 
      99       930.108     0.0162936       321.927           1           1      117   
    Iter      log prob        ||dx||      ||grad||       alpha      alpha0  # evals  Notes 
     199       959.793     0.0202279       367.334          10           1      235   
    Iter      log prob        ||dx||      ||grad||       alpha      alpha0  # evals  Notes 
     201       959.932   0.000323678       119.582    8.93e-07       0.001      274  LS failed, Hessian reset 
     299       966.946    0.00436297       112.347      0.8895      0.8895      391   
    Iter      log prob        ||dx||      ||grad||       alpha      alpha0  # evals  Notes 
     313       969.159   0.000423916       207.361   9.919e-07       0.001      450  LS failed, Hessian reset 
     399       974.294   0.000208377        85.133      0.5089      0.5089      552   
    Iter      log prob        ||dx||      ||grad||       alpha      alpha0  # evals  Notes 
     487       980.981   0.000350673         190.2   2.604e-06       0.001      700  LS failed, Hessian reset 
     499       981.522   0.000224398       86.8409      0.8047      0.8047      713   
    Iter      log prob        ||dx||      ||grad||       alpha      alpha0  # evals  Notes 
     595       982.077    0.00011557       96.0631   1.437e-06       0.001      871  LS failed, Hessian reset 
     599       982.082   4.96415e-05       69.7541      0.5502           1      876   
    Iter      log prob        ||dx||      ||grad||       alpha      alpha0  # evals  Notes 
     643       982.086   5.63279e-06       71.6814   6.367e-08       0.001      975  LS failed, Hessian reset 
     663       982.086   7.38231e-09       89.4916     0.07783     0.07783     1004   
Optimization terminated normally: 
  Convergence detected: absolute parameter change was below tolerance
Starting Portfolio Value: 100000.00
===Global level arguments===
init_cash : 100000
buy_prop : 1
sell_prop : 1
commission : 0.0075
===Strategy level arguments===
Upper limit:  1.5
Lower limit:  -1.5
2019-01-02, BUY CREATE, 552.15
2019-01-02, Cash: 100000.0
2019-01-02, Price: 552.15
2019-01-02, Buy prop size: 179
2019-01-02, Afforded size: 179
2019-01-02, Final size: 179
2019-01-03, BUY EXECUTED, Price: 552.15, Cost: 98834.85, Comm: 741.26, Size: 179.00
2019-01-11, SELL CREATE, 443.20
2019-01-14, SELL EXECUTED, Price: 443.20, Cost: 98834.85, Comm: 595.00, Size: -179.00
2019-01-14, OPERATION PROFIT, GROSS: -19502.05, NET: -20838.31
2019-02-06, BUY CREATE, 440.40
2019-02-06, Cash: 79161.692625
2019-02-06, Price: 440.4
2019-02-06, Buy prop size: 178
2019-02-06, Afforded size: 178
2019-02-06, Final size: 178
2019-02-07, BUY EXECUTED, Price: 440.40, Cost: 78391.20, Comm: 587.93, Size: 178.00
2019-03-01, SELL CREATE, 486.50
2019-03-05, SELL EXECUTED, Price: 486.50, Cost: 78391.20, Comm: 649.48, Size: -178.00
2019-03-05, OPERATION PROFIT, GROSS: 8205.80, NET: 6968.39
2019-04-05, BUY CREATE, 548.15
2019-04-05, Cash: 86130.08112500001
2019-04-05, Price: 548.15
2019-04-05, Buy prop size: 155
2019-04-05, Afforded size: 155
2019-04-05, Final size: 155
2019-04-08, BUY EXECUTED, Price: 548.15, Cost: 84963.25, Comm: 637.22, Size: 155.00
2019-07-12, SELL CREATE, 549.40
2019-07-15, SELL EXECUTED, Price: 549.40, Cost: 84963.25, Comm: 638.68, Size: -155.00
2019-07-15, OPERATION PROFIT, GROSS: 193.75, NET: -1082.15
2019-10-01, BUY CREATE, 470.35
2019-10-01, Cash: 85047.92925
2019-10-01, Price: 470.35
2019-10-01, Buy prop size: 179
2019-10-01, Afforded size: 179
2019-10-01, Final size: 179
2019-10-03, BUY EXECUTED, Price: 470.35, Cost: 84192.65, Comm: 631.44, Size: 179.00
2019-10-25, SELL CREATE, 592.15
2019-10-27, SELL EXECUTED, Price: 592.15, Cost: 84192.65, Comm: 794.96, Size: -179.00
2019-10-27, OPERATION PROFIT, GROSS: 21802.20, NET: 20375.79
2020-01-31, BUY CREATE, 450.35
2020-01-31, Cash: 105423.723
2020-01-31, Price: 450.35
2020-01-31, Buy prop size: 232
2020-01-31, Afforded size: 232
2020-01-31, Final size: 232
2020-02-01, BUY EXECUTED, Price: 450.35, Cost: 104481.20, Comm: 783.61, Size: 232.00
2020-02-01, SELL CREATE, 438.00
2020-02-03, SELL EXECUTED, Price: 438.00, Cost: 104481.20, Comm: 762.12, Size: -232.00
2020-02-03, OPERATION PROFIT, GROSS: -2865.20, NET: -4410.93
2020-04-01, BUY CREATE, 194.90
2020-04-01, Cash: 101012.794
2020-04-01, Price: 194.9
2020-04-01, Buy prop size: 513
2020-04-01, Afforded size: 513
2020-04-01, Final size: 513
2020-04-03, BUY EXECUTED, Price: 194.90, Cost: 99983.70, Comm: 749.88, Size: 513.00
2020-04-03, SELL CREATE, 167.25
2020-04-07, SELL EXECUTED, Price: 167.25, Cost: 99983.70, Comm: 643.49, Size: -513.00
2020-04-07, OPERATION PROFIT, GROSS: -14184.45, NET: -15577.82
2020-04-08, BUY CREATE, 193.75
2020-04-08, Cash: 85434.971875
2020-04-08, Price: 193.75
2020-04-08, Buy prop size: 437
2020-04-08, Afforded size: 437
2020-04-08, Final size: 437
2020-04-09, BUY EXECUTED, Price: 193.75, Cost: 84668.75, Comm: 635.02, Size: 437.00
2020-05-08, SELL CREATE, 239.85
2020-05-11, SELL EXECUTED, Price: 239.85, Cost: 84668.75, Comm: 786.11, Size: -437.00
2020-05-11, OPERATION PROFIT, GROSS: 20145.70, NET: 18724.58
2020-05-13, BUY CREATE, 252.20
2020-05-13, Cash: 104159.547875
2020-05-13, Price: 252.2
2020-05-13, Buy prop size: 409
2020-05-13, Afforded size: 409
2020-05-13, Final size: 409
2020-05-14, BUY EXECUTED, Price: 252.20, Cost: 103149.80, Comm: 773.62, Size: 409.00
2020-05-20, BUY CREATE, 222.10
2020-05-20, Cash: 236.12437500001556
2020-05-20, Price: 222.1
2020-05-20, Buy prop size: 1
2020-05-20, Afforded size: 1
2020-05-20, Final size: 1
2020-05-21, BUY EXECUTED, Price: 222.10, Cost: 222.10, Comm: 1.67, Size: 1.00
2020-07-10, SELL CREATE, 370.10
2020-07-13, SELL EXECUTED, Price: 370.10, Cost: 103371.90, Comm: 1138.06, Size: -410.00
2020-07-13, OPERATION PROFIT, GROSS: 48369.10, NET: 46455.75
2020-08-26, BUY CREATE, 298.05
2020-08-26, Cash: 150615.30112500003
2020-08-26, Price: 298.05
2020-08-26, Buy prop size: 501
2020-08-26, Afforded size: 501
2020-08-26, Final size: 501
2020-08-27, BUY EXECUTED, Price: 298.05, Cost: 149323.05, Comm: 1119.92, Size: 501.00
Final Portfolio Value: 137220.87825000004
Final PnL: 37220.88
==================================================
Number of strat runs: 1
Number of strats per run: 1
Strat names: ['custom']
**************************************************
--------------------------------------------------
{'init_cash': 100000, 'buy_prop': 1, 'sell_prop': 1, 'commission': 0.0075, 'execution_type': 'close', 'channel': None, 'symbol': None, 'upper_limit': 1.5, 'lower_limit': -1.5, 'custom_column': 'custom'}
OrderedDict([('rtot', 0.3164216915602497), ('ravg', 0.0007307660313169739), ('rnorm', 0.2021997935449528), ('rnorm100', 20.21997935449528)])
OrderedDict([('sharperatio', 1.3576522240477626)])
Time used (seconds): 0.1845560073852539
Optimal parameters: {'init_cash': 100000, 'buy_prop': 1, 'sell_prop': 1, 'commission': 0.0075, 'execution_type': 'close', 'channel': None, 'symbol': None, 'upper_limit': 1.5, 'lower_limit': -1.5, 'custom_column': 'custom'}
Optimal metrics: {'rtot': 0.3164216915602497, 'ravg': 0.0007307660313169739, 'rnorm': 0.2021997935449528, 'rnorm100': 20.21997935449528, 'sharperatio': 1.3576522240477626, 'pnl': 37220.88, 'final_value': 137220.87825000004}
   init_cash   final_value       pnl
0     100000  137220.87825  37220.88
```
![](./docs/assets/forecast-closing.png)
![](./docs/assets/forecast.png)

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
              Updated      Symbol     Close       LTP
 30-DEC-2020 16:00:00         ABB  1,203.05  1,205.30
 30-DEC-2020 16:00:00         ACC  1,616.75  1,651.00
 30-DEC-2020 16:00:00    ADANIENT    489.20    480.00
 30-DEC-2020 16:00:00  APOLLOTYRE    180.75    180.05
 30-DEC-2020 16:00:00      ASHOKA     90.85     90.05
 30-DEC-2020 16:00:00    ASHOKLEY     95.00     94.80
 30-DEC-2020 16:00:00   AMBUJACEM    244.40    252.50
 30-DEC-2020 16:00:00      ARVIND     45.60     46.85
 30-DEC-2020 16:00:00  ASIANPAINT  2,696.80  2,735.30
 30-DEC-2020 16:00:00        ATUL  6,389.55  6,500.00
 30-DEC-2020 16:00:00  AUROPHARMA    905.05    907.85
 30-DEC-2020 16:00:00    AXISBANK    630.20    623.60
 30-DEC-2020 16:00:00  BAJFINANCE  5,200.50  5,335.00
 30-DEC-2020 16:00:00  BANDHANBNK    413.20    406.50
 30-DEC-2020 16:00:00   BANKINDIA     49.40     49.15
 30-DEC-2020 16:00:00  BANKBARODA     62.35     62.05
 30-DEC-2020 16:00:00   BATAINDIA  1,584.40  1,581.70
 30-DEC-2020 16:00:00         BEL    114.75    114.70
 30-DEC-2020 16:00:00        BEML    993.90    964.10
 30-DEC-2020 16:00:00  BERGEPAINT    744.05    753.10
 30-DEC-2020 16:00:00  BHARATFORG    523.45    516.30
 30-DEC-2020 16:00:00        BHEL     35.40     35.30
 30-DEC-2020 16:00:00   BOMDYEING     74.85     76.85
 30-DEC-2020 16:00:00        BPCL    381.50    382.00
 30-DEC-2020 16:00:00   BRITANNIA  3,593.30  3,588.65
 30-DEC-2020 16:00:00    CADILAHC    479.35    479.80
 30-DEC-2020 16:00:00  CASTROLIND    121.95    123.55
 30-DEC-2020 16:00:00  CENTURYTEX    396.25    394.50
 30-DEC-2020 16:00:00  CHAMBLFERT    235.90    231.80
 30-DEC-2020 16:00:00       CIPLA    827.95    823.40
 30-DEC-2020 16:00:00    CROMPTON    369.15    370.15
 30-DEC-2020 16:00:00  CUMMINSIND    569.00    572.00
 30-DEC-2020 16:00:00       DABUR    528.95    538.60
 30-DEC-2020 16:00:00     DCBBANK    117.90    120.10
 30-DEC-2020 16:00:00         DLF    231.45    235.30
 30-DEC-2020 16:00:00     DRREDDY  5,165.60  5,165.00
 30-DEC-2020 16:00:00   EICHERMOT  2,460.55  2,521.00
 30-DEC-2020 16:00:00     ESCORTS  1,268.90  1,261.25
 30-DEC-2020 16:00:00    EVEREADY    204.95    208.70
 30-DEC-2020 16:00:00    EXIDEIND    191.35    192.50
 30-DEC-2020 16:00:00         FCL     66.05     63.75
 30-DEC-2020 16:00:00  FEDERALBNK     67.40     67.00
 30-DEC-2020 16:00:00      FORTIS    156.30    154.90
 30-DEC-2020 16:00:00         FSL    104.00     98.80
 30-DEC-2020 16:00:00        GAIL    123.75    122.90
 30-DEC-2020 16:00:00       GLAND  2,348.60  2,351.00
 30-DEC-2020 16:00:00    GLENMARK    497.90    496.50
 30-DEC-2020 16:00:00    GMRINFRA     26.40     27.30
 30-DEC-2020 16:00:00    GODREJCP    741.15    750.00
 30-DEC-2020 16:00:00   GODREJIND    431.10    423.90
 30-DEC-2020 16:00:00  GODREJPROP  1,405.05  1,390.20
 30-DEC-2020 16:00:00    GOODYEAR    969.80    958.20
 30-DEC-2020 16:00:00         HAL    836.30    830.00
 30-DEC-2020 16:00:00     HCLTECH    935.90    941.15
 30-DEC-2020 16:00:00        HDFC  2,518.95  2,521.70
 30-DEC-2020 16:00:00    HDFCBANK  1,427.20  1,432.05
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
