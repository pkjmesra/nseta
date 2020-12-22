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

Python Library to 
-  get publicly available data on [NSE India website](https://www1.nseindia.com/) ie. stock live quotes, historical data, live indices.
-  plot various technical indicators
-  pattern recognition and fitment using candlestick charts
-  backtest trading strategies
-  forecasting with custom strategies

## Libraries Required
-  beautifulsoup4
-  requests
-  numpy
-  pandas
-  Click
-  six
-  lxml
-  Sphinx
-  pystan
-  fbprophet
-  fastquant
- (See requirements.txt file for more)

For Windows systems you can install Anaconda, this will cover many dependancies (You'll have to install requests and beautifulsoup additionally though)

## Installation

```python3 setup.py clean build install```
or
```pip3 install nseta```

If you experience problems installing from pypi, you can also try the following:
``` python3 -m pip install --upgrade nseta ```

or just go ahead and download the ```.whl``` file from ```https://pypi.org/project/nseta/#files``` and install from the downloaded directory:

```pip3 install ./nseta-0.6-py3-none-any.whl``` where 0.6 is the version of the library.

You can also directly install specific versions from pypi.org:
```pip install --index-url https://pypi.org/simple/ --extra-index-url https://pypi.org/simple nseta==<Specific_Version>
```

Specific test versions can be installed from test.pypi.org
```pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple nseta==<Specific_Version>
```

After installation you can check what version you got installed
```python3 -c "import nseta; print(nseta.__version__)"```

## Usage


Get the price history of stocks and NSE indices directly in pandas dataframe-
```python

#Usage Commands
$ nsetacli
Usage: nsetacli [OPTIONS] COMMAND [ARGS]...

Options:
  --debug / --no-debug  --debug to turn debugging on. Default is off
  --help                Show this message and exit.

Commands:
  create-cdl-model       Create candlestick model.Plot uncovered patterns
  forecast-strategy      Forecast & measure performance of a trading model
  history                Get price history of a security for given dates
  live-quote             Get live price quote of a security
  pe-history             Get PE history of a security for given dates
  plot-ta                Plot various technical analysis indicators
  test-trading-strategy  Measure the performance of your trading strategy

  Example:
  nseta --debug create-cdl-model -S bandhanbnk -s 2019-07-30 -e 2020-11-20 --steps
  nseta --debug forecast-strategy -S bandhanbnk -s 2019-07-30 -e 2020-11-20 --strategy rsi
  nseta --debug history -S bandhanbnk -s 2019-07-30 -e 2020-11-20
  nseta --debug live-quote -S bandhanbnk
  nseta --debug pe-history -S bandhanbnk -s 2019-07-30 -e 2020-11-20
  nseta --debug plot-ta -S bandhanbnk -s 2019-07-30 -e 2020-11-20
  nseta --debug test-trading-strategy -S bandhanbnk -s 2019-07-30 -e 2020-11-20 --strategy rsi

```
Sample commands

- Test your trading strategies (for example, using *RSI* as technical indicator)
```
$ nsetacli test-trading-strategy -S bandhanbnk -s 2020-01-01 -e 2020-10-03 --strategy rsi --autosearch

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
$ nsetacli history -S bandhanbnk -s 2019-01-01 -e 2020-09-30
       Symbol Series        Date  Prev Close    Open   High     Low    Last   Close    VWAP   Volume      Turnover  Trades  Deliverable Volume  %Deliverable
0  BANDHANBNK     EQ  2019-01-01      550.15  552.50  560.0  544.10  558.00  556.70  552.21   589317  3.254256e+13   16658              175430        0.2977
1  BANDHANBNK     EQ  2019-01-02      556.70  553.00  563.7  549.60  551.40  552.15  556.91   834846  4.649319e+13   32119              250782        0.3004
2  BANDHANBNK     EQ  2019-01-03      552.15  551.00  554.0  530.00  532.05  533.80  540.61   620161  3.352631e+13   18616              282037        0.4548
3  BANDHANBNK     EQ  2019-01-04      533.80  534.25  541.7  527.05  528.05  528.90  533.42   579027  3.088645e+13   22405              186702        0.3224
4  BANDHANBNK     EQ  2019-01-07      528.90  540.00  542.0  495.55  495.55  498.05  509.49  2684675  1.367813e+14   76816             1160901        0.4324
Saved to: bandhanbnk.csv
```

- Create candlestick models with pattern recognition
```
$ nsetacli create-cdl-model -S bandhanbnk -s 2019-01-01 -e 2020-09-30 --steps
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
$ nsetacli plot-ta -S bandhanbnk -s 2019-01-01 -e 2020-09-30
```
![](./docs/assets/ti_plots.png)

- Create forecast strategies and verify them
```
$ nsetacli forecast-strategy -S bandhanbnk -s 2019-01-01 -e 2020-09-30 --upper 1.5 --lower 1.5
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
```
$ nsetacli live-quote -S bandhanbnk
As of 06-OCT-2020 10:16:17

                     Last Trade Price Price Change    Open    High     Low Close Prev Close 52 wk High 52 wk Low
Name                                                                                                            
Bandhan Bank Limited           302.90         3.61  295.00  304.50  294.55  0.00     292.35     650.00    152.20


                Total Traded Volume Total Traded Value
Quantity Traded                                       
29,70,467                 42,65,994          12,771.53


             Bid Price Offer Quantity Offer Price
Bid Quantity                                     
2,981           302.80            472      302.90
200             302.70          1,739      302.95
391             302.65         13,936      303.00
4,368           302.60          3,471      303.05
5,469           302.55            767      303.10
```

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
