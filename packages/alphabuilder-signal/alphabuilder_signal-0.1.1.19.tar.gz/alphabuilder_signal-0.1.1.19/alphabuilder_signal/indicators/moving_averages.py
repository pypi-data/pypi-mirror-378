import pandas as pd
import numpy as np
from alphabuilder_signal import Fetch
from typing import Optional, List, Union, Tuple

class MovingAverage:
    def __init__(
        self,
        tickers: Optional[List[str]] = None, 
        start_date: str = "2010-01-01",        
        end_date: Optional[str] = None,
        verbose: bool = True,
        combined = False
    ):
        """
        Parameters
        ----------
        tickers : list[str], optional
            List of ticker symbols to fetch. If None, defaults to an empty dataset.
        start_date : str, default="2010-01-01"
            Starting date for fetching historical data (YYYY-MM-DD).
        end_date : str, optional
            Ending date for fetching historical data (YYYY-MM-DD).
        verbose : bool, default=True
            If True, prints progress and debug info while fetching data.
        combined : bool, default=False
            If True, returns a single DataFrame with multiindex.
            If False, returns a dictionary of DataFrames by ticker.
        """
        fetcher = Fetch(
            tickers=tickers, 
            start_date=start_date, 
            end_date=end_date, 
            verbose=verbose
        )
        
        self.combined = combined
        self.data: Union[dict[str, pd.DataFrame], pd.DataFrame] = fetcher.get_asset_data(combined=self.combined)

    def simple_moving_average(self, windows: Union[int, list[int]] = 14):
        """
        Compute simple moving averages for one or multiple windows.

        Parameters
        ----------
        windows : int or list of int
        """
        if isinstance(windows, int):
            windows = [windows]
        
        if self.combined:
            for w in windows:
                column_name = f"SMA_{w}"
                self.data[column_name] = (
                    self.data.groupby(level=0)["Close"]
                    .transform(lambda x: x.rolling(window=w).mean())
                )
        else:
            for ticker, df in self.data.items():
                for w in windows:
                    column_name = f"SMA_{w}"
                    df[column_name] = df["Close"].rolling(window=w).mean()
                self.data[ticker] = df
        
        return self
    
    
    def weighted_moving_average(self, windows: Union[int, List[int]] = 14):
        """
        Compute weighted moving averages for one or multiple windows.

        Parameters
        ----------
        windows : int or list of int
        """
        if isinstance(windows, int):
            windows = [windows]
            
        if self.combined:
            for w in windows:
                column_name = f"WMA_{w}"
                weights = np.arange(1, w + 1)
                denominator = weights.sum()
                self.data[column_name] = (
                    self.data.groupby(level=0)["Close"]
                    .transform(lambda s: s.rolling(w).apply(
                        lambda x: np.dot(x, weights) / denominator, raw=True
                    ))
                )
        else:
            for ticker, df in self.data.items():
                for w in windows:
                    column_name = f"WMA_{w}"
                    weights = np.arange(1, w + 1)
                    denominator = weights.sum()
                    df[column_name] = df["Close"].rolling(w).apply(
                        lambda x: np.dot(x, weights) / denominator, raw=True
                    )
                self.data[ticker] = df
        
        return self
    
    def exponential_moving_average(self, windows: Union[int, List[int]] = 14):
        """
        Compute exponential moving averages for one or multiple windows.

        Parameters
        ----------
        windows : int or list of int
        """
        if isinstance(windows, int):
            windows = [windows]
            
        if self.combined:
            for w in windows:
                column_name = f"EMA_{w}"
                self.data[column_name] = (
                    self.data.groupby(level=0)["Close"]
                    .transform(lambda x: x.ewm(span=w, adjust=False).mean())
                )
        else:
            for ticker, df in self.data.items():
                for w in windows:
                    column_name = f"EMA_{w}"
                    df[column_name] = df["Close"].ewm(span=w, adjust=False).mean()
                self.data[ticker] = df
        
        return self

    def hull_moving_average(self, windows: Union[int, List[int]] = 14):
        """
        Compute Hull Moving Averages (HMA) for one or multiple windows.

        Parameters
        ----------
        windows : int or list of int
        """
        if isinstance(windows, int):
            windows = [windows]
        
        if self.combined:
            for w in windows:
                half_length = int(w / 2)
                sqrt_length = int(np.sqrt(w))
                
                wma_half = (
                    self.data.groupby(level=0)["Close"]
                    .transform(lambda x: x.rolling(half_length)
                            .apply(lambda y: np.dot(y, np.arange(1, half_length+1)) / np.arange(1, half_length+1).sum(), raw=True))
                )
                wma_full = (
                    self.data.groupby(level=0)["Close"]
                    .transform(lambda x: x.rolling(w)
                            .apply(lambda y: np.dot(y, np.arange(1, w+1)) / np.arange(1, w+1).sum(), raw=True))
                )
                
                diff = 2 * wma_half - wma_full

                hma = (
                    diff.groupby(level=0)
                    .transform(lambda x: x.rolling(sqrt_length)
                            .apply(lambda y: np.dot(y, np.arange(1, sqrt_length+1)) / np.arange(1, sqrt_length+1).sum(), raw=True))
                )
                
                self.data[f"HMA_{w}"] = hma
        
        else:
            for ticker, df in self.data.items():
                for w in windows:
                    half_length = int(w / 2)
                    sqrt_length = int(np.sqrt(w))
                    
                    wma_half = df["Close"].rolling(half_length).apply(
                        lambda y: np.dot(y, np.arange(1, half_length+1)) / np.arange(1, half_length+1).sum(), raw=True
                    )
                    wma_full = df["Close"].rolling(w).apply(
                        lambda y: np.dot(y, np.arange(1, w+1)) / np.arange(1, w+1).sum(), raw=True
                    )
                    diff = 2 * wma_half - wma_full
                    
                    df[f"HMA_{w}"] = diff.rolling(sqrt_length).apply(
                        lambda y: np.dot(y, np.arange(1, sqrt_length+1)) / np.arange(1, sqrt_length+1).sum(), raw=True
                    )
                    
                self.data[ticker] = df
    
        return self
    
    def macd(
        self, 
        params: Union[Tuple[int, int, int], List[Tuple[int, int, int]]] = (12, 26, 9)
    ):
        """
        Compute one or multiple MACD indicators.

        Parameters
        ----------
        params : tuple or list of tuples
            (fast, slow, signal) values. Example: (12, 26, 9) or [(12, 26, 9), (5, 35, 5)]
        """
        if isinstance(params, tuple):
            params = [params]

        if self.combined:
            for (fast, slow, signal) in params:
                if fast >= slow:
                    print(f"Skipping invalid params (fast={fast}, slow={slow}): fast must be smaller than slow.")
                    continue

                ema_fast = (
                    self.data.groupby(level=0)["Close"]
                    .transform(lambda x: x.ewm(span=fast, adjust=False).mean())
                )
                ema_slow = (
                    self.data.groupby(level=0)["Close"]
                    .transform(lambda x: x.ewm(span=slow, adjust=False).mean())
                )

                macd_col   = f"MACD_{fast}_{slow}"
                signal_col = f"MACD_Signal_{signal}_{fast}_{slow}"
                hist_col   = f"MACD_Hist_{fast}_{slow}_{signal}"

                self.data[macd_col] = ema_fast - ema_slow

                self.data[signal_col] = (
                    self.data.groupby(level=0)[macd_col]
                    .transform(lambda x: x.ewm(span=signal, adjust=False).mean())
                )
                
                self.data[hist_col] = self.data[macd_col] - self.data[signal_col]

        else:
            for ticker, df in self.data.items():
                for (fast, slow, signal) in params:
                    if fast >= slow:
                        print(f"Skipping invalid params (fast={fast}, slow={slow}) for {ticker}")
                        continue

                    ema_fast = df["Close"].ewm(span=fast, adjust=False).mean()
                    ema_slow = df["Close"].ewm(span=slow, adjust=False).mean()

                    macd_col   = f"MACD_{fast}_{slow}"
                    signal_col = f"MACD_Signal_{signal}_{fast}_{slow}"
                    hist_col   = f"MACD_Hist_{fast}_{slow}_{signal}"

                    df[macd_col] = ema_fast - ema_slow
                    df[signal_col] = df[macd_col].ewm(span=signal, adjust=False).mean()
                    df[hist_col] = df[macd_col] - df[signal_col]

                self.data[ticker] = df

        return self



    def get_data(self) -> Union[dict[str, pd.DataFrame], pd.DataFrame]:
        return self.data
    
#----------xxx---------------