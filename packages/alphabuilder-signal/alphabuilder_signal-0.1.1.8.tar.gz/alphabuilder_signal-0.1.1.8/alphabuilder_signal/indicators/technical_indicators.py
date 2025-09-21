import pandas as pd
import numpy as np
from alphabuilder_signal import Fetch
from typing import Optional, List, Union, Tuple

class TechnicalIndicators:
    def __init__(
        self,
        tickers: Optional[List[str]] = None, 
        start_date: str = "2010-01-01",        
        end_date: Optional[str] = None,
        verbose: bool = True,
        combined = False
    ):
        fetcher = Fetch(
            tickers=tickers, 
            start_date=start_date, 
            end_date=end_date, 
            verbose=verbose
        )
        
        self.combined = combined
        self.data: Union[dict[str, pd.DataFrame], pd.DataFrame] = fetcher.get_asset_data(combined=self.combined)
    
    
    def relative_strength_index(self, windows: Union[int, list[int]] = 14, method: str = "wilder"):
        """
        Compute Relative Strength Index (RSI) for one or multiple windows.

        Parameters
        ----------
        windows : int or list of int
            Lookback periods for RSI calculation.
        method : str, default 'wilder'
            - 'wilder' : uses exponential smoothing (standard RSI)
            - 'simple' : uses simple rolling mean
        """
        if isinstance(windows, int):
            windows = [windows]

        if self.combined:
            delta = self.data.groupby(level=0)['Close'].transform(lambda x: x.diff())
            gain = delta.where(delta > 0, 0)
            loss = -delta.where(delta < 0, 0)

            for w in windows:
                col = f"RSI_{w}_{method}"
                if method == "wilder":
                    avg_gain = gain.groupby(level=0).transform(lambda x: x.ewm(alpha=1/w, adjust=False).mean())
                    avg_loss = loss.groupby(level=0).transform(lambda x: x.ewm(alpha=1/w, adjust=False).mean())
                elif method == "simple":
                    avg_gain = gain.groupby(level=0).transform(lambda x: x.rolling(window=w).mean())
                    avg_loss = loss.groupby(level=0).transform(lambda x: x.rolling(window=w).mean())

                rs = avg_gain / avg_loss.replace(0, np.nan)
                self.data[col] = 100 - (100 / (1 + rs))
        else:
            for ticker, df in self.data.items():
                delta = df['Close'].diff()
                gain = delta.where(delta > 0, 0)
                loss = -delta.where(delta < 0, 0)

                for w in windows:
                    col = f"RSI_{w}_{method}"
                    if method == "wilder":
                        avg_gain = gain.ewm(alpha=1/w, adjust=False).mean()
                        avg_loss = loss.ewm(alpha=1/w, adjust=False).mean()
                    elif method == "simple":
                        avg_gain = gain.rolling(window=w).mean()
                        avg_loss = loss.rolling(window=w).mean()

                    rs = avg_gain / avg_loss.replace(0, np.nan)
                    df[col] = 100 - (100 / (1 + rs))

                self.data[ticker] = df

        return self

    
    def momentum(self, windows: Union[int, list[int]] = 14):
        """
        Compute Momentum indicator for one or multiple windows.

        Parameters
        ----------
        windows : int or list of int
            Lookback periods for momentum calculation.
        """
        if isinstance(windows, int):
            windows = [windows]
            
        if self.combined:
            for w in windows:
                column_name = f"momentum_{w}"
                self.data[column_name] = (self.data.groupby(level=0)['Close']
                                          .transform(lambda x: x - x.shift(w)))
                
        else:
            for ticker, df in self.data.items():
                for w in windows:
                    df[f'Momentum_{w}'] = df['Close'] - df['Close'].shift(w)
                self.data[ticker] = df
        return self
    
    def true_range(self):
        """
        Compute True Range (TR)
        """
        if self.combined:
            high = self.data['High']
            low = self.data['Low']
            prev_close = self.data.groupby(level=0)['Close'].shift(1)

            tr = pd.concat([
                (high - low).abs(),
                (high - prev_close).abs(),
                (low - prev_close).abs()
            ], axis=1).max(axis=1)

            self.data["TR"] = tr

        else:
            for ticker, df in self.data.items():
                high = df['High']
                low = df['Low']
                prev_close = df['Close'].shift(1)

                tr = pd.concat([
                    (high - low).abs(),
                    (high - prev_close).abs(),
                    (low - prev_close).abs()
                ], axis=1).max(axis=1)

                df["TR"] = tr
                self.data[ticker] = df 

        return self
    
    def average_true_range(self, windows: Union[int, list[int]] = 14):
        """
        Compute Average True Range (ATR) for one or multiple windows.

        Parameters
        ----------
        windows : int or list of int
            Lookback periods for ATR calculation (default 14)
        """
        if isinstance(windows, int):
            windows = [windows]

        self.true_range()

        if self.combined:
            for w in windows:
                col = f'ATR_{w}'
                self.data[col] = (
                    self.data.groupby(level=0)['TR']
                    .transform(lambda x: x.ewm(alpha=1/w, adjust=False).mean())
                )
            self.data.drop(columns=['TR'], inplace=True)
        else:
            for ticker, df in self.data.items():
                for w in windows:
                    col = f'ATR_{w}'
                    df[col] = df['TR'].ewm(alpha=1/w, adjust=False).mean()
                df.drop(columns=['TR'], inplace=True)
                self.data[ticker] = df

        return self
    
    def commodity_channel_index(self, windows: Union[int, list[int]] = 14):
        """
        Compute Commodity Channel Index (CCI) for one or multiple windows.

        Parameters
        ----------
        windows : int or list of int
            Lookback periods for CCI calculation (default 14)
        """
        if isinstance(windows, int):
            windows = [windows]

        if self.combined:
            for w in windows:
                tp = (self.data['High'] + self.data['Low'] + self.data['Close']) / 3
                sma_tp = tp.groupby(level=0).transform(lambda x: x.rolling(w).mean())
                mad = tp.groupby(level=0).transform(
                    lambda x: x.rolling(w).apply(lambda y: np.mean(np.abs(y - np.mean(y))), raw=True)
                )
                self.data[f'CCI_{w}'] = (tp - sma_tp) / (0.015 * mad)

        else:
            for ticker, df in self.data.items():
                for w in windows:
                    tp = (df['High'] + df['Low'] + df['Close']) / 3
                    sma_tp = tp.rolling(w).mean()
                    mad = tp.rolling(w).apply(lambda y: np.mean(np.abs(y - np.mean(y))), raw=True)
                    df[f'CCI_{w}'] = (tp - sma_tp) / (0.015 * mad)
                self.data[ticker] = df

        return self
    
    def williams_R(self, windows: Union[int, list[int]] = 14):
        """
        Compute Williams %R for one or multiple windows.

        Parameters
        ----------
        windows : int or list of int
            Lookback periods for calculation (default 14)
        """
        if isinstance(windows, int):
            windows = [windows]

        if self.combined:
            for w in windows:
                high = self.data.groupby(level=0)['High'].transform(lambda x: x.rolling(w).max())
                low = self.data.groupby(level=0)['Low'].transform(lambda x: x.rolling(w).min())
                wr = -100 * (high - self.data['Close']) / (high - low)
                self.data[f'Williams_%R_{w}'] = wr

        else:
            for ticker, df in self.data.items():
                for w in windows:
                    high = df['High'].rolling(w).max()
                    low = df['Low'].rolling(w).min()
                    wr = -100 * (high - df['Close']) / (high - low)
                    df[f'Williams_%R_{w}'] = wr
                self.data[ticker] = df

        return self

    def percent_K(self, windows: Union[int, list[int]] = 14):
        """
        Compute %K (stochastic oscillator) for one or multiple windows.

        Parameters
        ----------
        windows : int or list of int
            Lookback periods for calculation (default 14)
        """
        if isinstance(windows, int):
            windows = [windows]

        if self.combined:
            for w in windows:
                low_min = self.data.groupby(level=0)['Low'].transform(lambda x: x.rolling(w).min())
                high_max = self.data.groupby(level=0)['High'].transform(lambda x: x.rolling(w).max())
                percent_k = 100 * (self.data['Close'] - low_min) / (high_max - low_min)
                self.data[f'%K_{w}'] = percent_k

        else:
            for ticker, df in self.data.items():
                for w in windows:
                    low_min = df['Low'].rolling(w).min()
                    high_max = df['High'].rolling(w).max()
                    percent_k = 100 * (df['Close'] - low_min) / (high_max - low_min)
                    df[f'%K_{w}'] = percent_k
                self.data[ticker] = df

        return self
    
    def percent_Dslow(self, windows: Union[int, list[int]] = 14, d_window: int = 3):
        """
        Compute %D slow (smoothed stochastic oscillator) for one or multiple windows.

        Parameters
        ----------
        windows : int or list of int
            Lookback periods for %K calculation (default 14)
        d_window : int
            Lookback period for smoothing %K into %D slow (default 3)
        """
        if isinstance(windows, int):
            windows = [windows]

        self.percent_K(windows)

        if self.combined:
            for w in windows:
                self.data[f'%Dslow_{w}_{d_window}'] = (
                    self.data.groupby(level=0)[f'%K_{w}'].transform(lambda x: x.rolling(d_window).mean())
                )
        else:
            for ticker, df in self.data.items():
                for w in windows:
                    df[f'%Dslow_{w}_{d_window}'] = df[f'%K_{w}'].rolling(d_window).mean()
                self.data[ticker] = df

        return self

    def bollinger_bands(self, windows: Union[int, list[int]] = 14, num_std: float = 2):
        """
        Compute Bollinger Bands (Upper, Middle, Lower) for one or multiple windows.

        Parameters
        ----------
        windows : int or list of int
            Lookback periods for moving average (default 14)
        num_std : float
            Number of standard deviations for upper/lower bands (default 2)
        """
        if isinstance(windows, int):
            windows = [windows]

        if self.combined:
            for w in windows:
                ma = self.data.groupby(level=0)['Close'].transform(lambda x: x.rolling(w).mean())
                std = self.data.groupby(level=0)['Close'].transform(lambda x: x.rolling(w).std())
                self.data[f'BB_Middle_{w}'] = ma
                self.data[f'BB_Upper_{w}'] = ma + num_std * std
                self.data[f'BB_Lower_{w}'] = ma - num_std * std
        else:
            for ticker, df in self.data.items():
                for w in windows:
                    ma = df['Close'].rolling(w).mean()
                    std = df['Close'].rolling(w).std()
                    df[f'BB_Middle_{w}'] = ma
                    df[f'BB_Upper_{w}'] = ma + num_std * std
                    df[f'BB_Lower_{w}'] = ma - num_std * std
                self.data[ticker] = df

        return self

    def average_directional_index(self, window: int = 14):
        """
        Compute Average Directional Index (ADX) for trend strength.

        Parameters
        ----------
        window : int
            Lookback period for smoothing (default 14)
        """
        if self.combined:
            high = self.data['High']
            low = self.data['Low']
            close = self.data['Close']
            prev_close = self.data.groupby(level=0)['Close'].shift(1)

            tr = pd.concat([
                (high - low).abs(),
                (high - prev_close).abs(),
                (low - prev_close).abs()
            ], axis=1).max(axis=1)

            plus_dm = np.where(
                (high - high.shift(1)) > (low.shift(1) - low),
                np.maximum(high - high.shift(1), 0),
                0
            )
            minus_dm = np.where(
                (low.shift(1) - low) > (high - high.shift(1)),
                np.maximum(low.shift(1) - low, 0),
                0
            )

            tr_smooth = tr.groupby(level=0).transform(lambda x: x.rolling(window).sum())
            plus_dm_smooth = pd.Series(plus_dm, index=tr.index).groupby(level=0).transform(lambda x: pd.Series(x).rolling(window).sum())
            minus_dm_smooth = pd.Series(minus_dm, index=tr.index).groupby(level=0).transform(lambda x: pd.Series(x).rolling(window).sum())

            plus_di = 100 * (plus_dm_smooth / tr_smooth)
            minus_di = 100 * (minus_dm_smooth / tr_smooth)
            dx = 100 * np.abs(plus_di - minus_di) / (plus_di + minus_di)
            adx = dx.groupby(level=0).transform(lambda x: x.rolling(window).mean())

            self.data['ADX'] = adx

        else:
            for ticker, df in self.data.items():
                high = df['High']
                low = df['Low']
                close = df['Close']
                prev_close = close.shift(1)

                tr = pd.concat([
                    (high - low).abs(),
                    (high - prev_close).abs(),
                    (low - prev_close).abs()
                ], axis=1).max(axis=1)

                plus_dm = np.where(
                    (high - high.shift(1)) > (low.shift(1) - low),
                    np.maximum(high - high.shift(1), 0),
                    0
                )
                minus_dm = np.where(
                    (low.shift(1) - low) > (high - high.shift(1)),
                    np.maximum(low.shift(1) - low, 0),
                    0
                )

                tr_smooth = tr.rolling(window).sum()
                plus_dm_smooth = pd.Series(plus_dm, index=df.index).rolling(window).sum()
                minus_dm_smooth = pd.Series(minus_dm, index=df.index).rolling(window).sum()

                plus_di = 100 * (plus_dm_smooth / tr_smooth)
                minus_di = 100 * (minus_dm_smooth / tr_smooth)
                dx = 100 * np.abs(plus_di - minus_di) / (plus_di + minus_di)
                adx = dx.rolling(window).mean()

                df['ADX'] = adx
                self.data[ticker] = df

        return self
    
    def parabolic_SAR(self, step: float = 0.02, max_af: float = 0.2):
        """
        Compute Parabolic SAR for trend detection.

        Parameters
        ----------
        step : float
            Acceleration factor step (default 0.02)
        max_af : float
            Maximum acceleration factor (default 0.2)
        """
        def _calculate_psar(df):
            high = df['High'].values
            low = df['Low'].values
            close = df['Close'].values
            length = len(df)
            psar = np.zeros(length)
            psar[0] = low[0] 
            bull = True
            af = step
            ep = high[0]

            for i in range(1, length):
                sar = psar[i-1] + af * (ep - psar[i-1])
                
                if bull:
                    sar = min(sar, low[i-1], low[i-2] if i > 1 else low[i-1])
                    if close[i] < sar:
                        bull = False
                        sar = ep
                        ep = low[i]
                        af = step
                    else:
                        if high[i] > ep:
                            ep = high[i]
                            af = min(af + step, max_af)
                else:
                    sar = max(sar, high[i-1], high[i-2] if i > 1 else high[i-1])
                    if close[i] > sar:
                        bull = True
                        sar = ep
                        ep = high[i]
                        af = step
                    else:
                        if low[i] < ep:
                            ep = low[i]
                            af = min(af + step, max_af)
                
                psar[i] = sar
            df['PSAR'] = psar
            return df
        
        if self.combined:
            self.data = self.data.groupby(level=0, group_keys=False).apply(_calculate_psar)
        else:
            for ticker, df in self.data.items():
                self.data[ticker] = _calculate_psar(df)

    def get_data(self) -> Union[dict[str, pd.DataFrame], pd.DataFrame]:
        return self.data

#----------xxx---------------
ta = TechnicalIndicators(tickers=['AAPL', 'MSFT', 'META'], start_date='2020-01-01', verbose=True, combined=False)

results = (ta.relative_strength_index(windows=[14, 7, 6])
           .relative_strength_index(windows=[7, 4], method='simple')
           .momentum(windows=[7, 8, 9, 4])
           .average_true_range(windows=[4, 7])
           .true_range()
           .commodity_channel_index(windows=[3,4])
           .average_directional_index()
           .bollinger_bands()
           .percent_Dslow()
           .percent_K()
           .williams_R()
           .commodity_channel_index()
           .get_data())

results['AAPL'].info()
results.info()
results

