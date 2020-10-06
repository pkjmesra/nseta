# nseta :nerd_face:
Python Library to 
- get publicly available data on [NSE India website](https://www1.nseindia.com/) ie. stock live quotes, historical data, live indices.
- plot various technical indicators
- pattern recognition and fitment using candlestick charts
- backtest trading strategies
- forecasting with custom strategies

## Libraries Required
- beautifulsoup4
- requests
- numpy
- pandas
- Click
- six
- lxml
- Sphinx
- pystan
- fbprophet
- fastquant

For Windows systems you can install Anaconda, this will cover many dependancies (You'll have to install requests and beautifulsoup additionally though)

## Installation

```python setup.py clean build install```

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

```
Sample commands
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

### Submit patches

If you have fixed an issue or added a new feature, please fork this repository, make your changes and submit a pull request. [Here's good article on how to do this.](https://code.tutsplus.com/tutorials/how-to-collaborate-on-github--net-34267) 

## License
[MIT License](https://github.com/pkjmesra/nseta/blob/main/LICENSE)

## Inspirations (Thank you so much!)
- [nsepy](https://github.com/swapniljariwala/nsepy)
- [fastquant](https://github.com/enzoampil/fastquant)
- [fbprophet](https://github.com/facebook/prophet)
- [nsetools](https://github.com/vsjha18/nsetools)
- [ta-lib](https://github.com/mrjbq7/ta-lib)
- [medium](https://github.com/CanerIrfanoglu/medium)
