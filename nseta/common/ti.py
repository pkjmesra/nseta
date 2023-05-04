# -*- coding: utf-8 -*-
from nseta.common.log import default_logger
import talib as ta
import pandas as pd
import numpy as np

__all__ = ['ti']

class ti:

  def update_ti(self, df, rsi=False,mom=False,sma=False,ema=False,macd=False,
    bbands=False,obv=False,dmi=False,atr=False,natr=False,trange=False,
    volatility=False,atre=False,adx=False,pivots=False):
    if df is None or len(df) == 0:
      return df
    try:
      if rsi:
        df.loc[:,'RSI'] = self.get_rsi_df(df)
      if mom:
        df.loc[:,'MOM'] = self.get_mom_df(df)
      if sma:
        df.loc[:,['close','SMA(10)', 'SMA(50)']] = self.get_sma_df(df)
      if ema:
        df.loc[:,['close','EMA(9)']] = self.get_ema_df(df)
      if macd:
        df.loc[:,['macd(12)','macdsignal(9)', 'macdhist(26)']] = self.get_macd_df(df)
      if bbands:
        df.loc[:,['close','BBands-U','BBands-M','BBands-L']] = self.get_bbands_df(df)
      if obv:
        df.loc[:,'OBV'] = self.get_obv_df(df)
      can_have_pivots = True
      for key in ['low', 'high', 'close']:
        if key not in df.keys():
          can_have_pivots = False
          break
      if can_have_pivots:
        if pivots:
          df = self.get_ppsr_df(df)
        if dmi:
          df.loc[:,'DMI'] = self.get_dmi_df(df)
        if atr:
          df.loc[:,'ATR'] = self.get_atr_df(df)
        if natr:
          df.loc[:,'NATR'] = self.get_natr_df(df)
        if trange:
          df.loc[:,'TRANGE'] = self.get_trange_df(df)
        if volatility:
          df.loc[:,'Volatility'] = self.get_atr_ratio(df)
        if atre:
          df.loc[:,'ATRE-F'], df.loc[:,'ATRE-S'], df.loc[:,'ATRE'] = self.get_atr_extreme(df)
        if adx:
          df.loc[:,'ADX'] = self.get_adx_df(df)
    except Exception as e:
      default_logger().debug(e, exc_info=True)
    except SystemExit:
      pass
    return df

  def get_rsi_df(self, df):
    df.loc[:,'RSI'] = ta.RSI(df.loc[:,'close'],14).apply(lambda x: round(x, 2))
    return df.loc[:,'RSI']

  def get_mom_df(self, df):
    df.loc[:,'MOM'] = ta.MOM(df.loc[:,'close'],2).apply(lambda x: round(x, 2))
    return df.loc[:,'MOM']

  def get_dmi_df(self, df):
    df.loc[:,'DMI'] = ta.DX(df.loc[:,'high'],df.loc[:,'low'],df.loc[:,'close'],timeperiod=14)
    return df.loc[:,'DMI']

  def get_macd_df(self, df):
    df.loc[:,'macd(12)'], df.loc[:,'macdsignal(9)'], df.loc[:,'macdhist(26)'] = ta.MACD(df.loc[:,'close'], fastperiod=12, slowperiod=26, signalperiod=9)
    df.loc[:,'macd(12)'] = df.loc[:,'macd(12)'].apply(lambda x: round(x, 3))
    df.loc[:,'macdsignal(9)']= df.loc[:,'macdsignal(9)'].apply(lambda x: round(x, 3))
    df.loc[:,'macdhist(26)'] = df.loc[:,'macdhist(26)'].apply(lambda x: round(x, 3))
    return df.loc[:,['macd(12)','macdsignal(9)', 'macdhist(26)']]

  def get_sma_df(self, df):
    df.loc[:,'SMA(10)'] = ta.SMA(df.loc[:,'close'],10).apply(lambda x: round(x, 2))
    df.loc[:,'SMA(50)'] = ta.SMA(df.loc[:,'close'],50).apply(lambda x: round(x, 2))
    return df.loc[:,['close','SMA(10)', 'SMA(50)']]

  def get_ema_df(self, df):
    df.loc[:,'EMA(9)'] = ta.EMA(df.loc[:,'close'], timeperiod = 9).apply(lambda x: round(x, 2))
    return df.loc[:,['close','EMA(9)']]

  def get_adx_df(self, df):
    df.loc[:,'ADX'] = ta.ADX(df.loc[:,'high'],df.loc[:,'low'], df.loc[:,'close'], timeperiod=14).apply(lambda x: round(x, 2))
    return df.loc[:,'ADX']

  def get_bbands_df(self, df):
    df.loc[:,'BBands-U'], df.loc[:,'BBands-M'], df.loc[:,'BBands-L'] = ta.BBANDS(df.loc[:,'close'], timeperiod =20)
    df.loc[:,'BBands-U'] = df.loc[:,'BBands-U'].apply(lambda x: round(x, 2))
    df.loc[:,'BBands-M'] = df.loc[:,'BBands-M'].apply(lambda x: round(x, 2))
    df.loc[:,'BBands-L'] = df.loc[:,'BBands-L'].apply(lambda x: round(x, 2))
    return df[['close','BBands-U','BBands-M','BBands-L']]

  def get_obv_df(self, df):
    if ('close' not in df.keys()) or ('Volume' not in df.keys()):
      return np.nan
    df.loc[:,'OBV'] = ta.OBV(df.loc[:,'close'], df.loc[:,'Volume'])
    return df.loc[:,'OBV']

  def get_atr_df(self, df):
    df.loc[:,'ATR'] = ta.ATR(df.loc[:,'high'], df.loc[:,'low'], df.loc[:,'close'], timeperiod=14).apply(lambda x: round(x, 2))
    return df.loc[:,'ATR']

  def get_natr_df(self, df):
    df.loc[:,'NATR'] = ta.NATR(df.loc[:,'high'], df.loc[:,'low'], df.loc[:,'close'], timeperiod=14).apply(lambda x: round(x, 2))
    return df.loc[:,'NATR']

  def get_trange_df(self, df):
    df.loc[:,'TRANGE'] = ta.TRANGE(df.loc[:,'high'], df.loc[:,'low'], df.loc[:,'close']).apply(lambda x: round(x, 2))
    return df.loc[:,'TRANGE']

  def get_atr_extreme(self, df):
    """
      ATR Exterme: which is based on 《Volatility-Based Technical Analysis》
      TTI is 'Trading The Invisible'

      @return: fasts, slows
    """
    highs = df.loc[:,'high']
    lows = df.loc[:,'low']
    closes = df.loc[:,'close']
    slowPeriod=30
    fastPeriod=3
    atr = self.get_atr_df(df)

    highsMean = ta.EMA(highs, 5)
    lowsMean = ta.EMA(lows, 5)
    closesMean = ta.EMA(closes, 5)

    atrExtremes = np.where(closes > closesMean,
                 ((highs - highsMean)/closes * 100) * (atr/closes * 100),
                 ((lows - lowsMean)/closes * 100) * (atr/closes * 100)
                 )
    fasts = ta.MA(atrExtremes, fastPeriod)
    slows = ta.EMA(atrExtremes, slowPeriod)
    return fasts, slows, np.std(atrExtremes[-slowPeriod:])

  def get_atr_ratio(self, df):
    """
      ATR(14)/MA(14)
    """
    closes = df.loc[:,'close']

    atr = self.get_atr_df(df)
    ma = ta.MA(closes, timeperiod=14)

    volatility = atr/ma

    s = pd.Series(volatility, index=df.index, name='volatility').dropna()
    pd.set_option('mode.chained_assignment', None)
    return pd.DataFrame({'volatility':round(s,2)})

  def get_ppsr_df(self, df):
    PP = pd.Series((df.loc[:,'high'] + df.loc[:,'low'] + df.loc[:,'close']) / 3)
    R1 = pd.Series(2 * PP - df.loc[:,'low'])
    S1 = pd.Series(2 * PP - df.loc[:,'high'])
    R2 = pd.Series(PP + df.loc[:,'high'] - df.loc[:,'low'])
    S2 = pd.Series(PP - df.loc[:,'high'] + df.loc[:,'low'])
    R3 = pd.Series(df.loc[:,'high'] + 2 * (PP - df.loc[:,'low']))
    S3 = pd.Series(df.loc[:,'low'] - 2 * (df.loc[:,'high'] - PP))
    psr = {'PP':round(PP,2), 'R1':round(R1,2), 'S1':round(S1,2), 'R2':round(R2,2), 'S2':round(S2,2), 'R3':round(R3,2), 'S3':round(S3,2)}
    pd.set_option('mode.chained_assignment', None)
    PSR = pd.DataFrame(psr)
    keys = ['PP','R1','R2','R3','S1','S2','S3']
    for key in keys:
      df[key] = PSR[key]
    return df
