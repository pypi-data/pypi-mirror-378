import pandas as pd
import numpy as np
from alphabuilder_signal import Fetch
from typing import Optional, List, Union, Tuple

class TargetClassifier:
    def __init__(
        self,
        tickers: Optional[List[str]] = None, 
        start_date: str = "2010-01-01",        
        end_date: Optional[str] = None,
        verbose: bool = True,
        combined: bool = False,
        data: Union[dict[str, pd.DataFrame], pd.DataFrame] = None
    ):
        """
        Parameters
        ----------
        tickers : list[str], optional
            List of ticker symbols to fetch. If None, must provide `data`.
        start_date : str, default="2010-01-01"
            Starting date for fetching historical data (YYYY-MM-DD).
        end_date : str, optional
            Ending date for fetching historical data (YYYY-MM-DD).
        verbose : bool, default=True
            If True, prints progress and debug info while fetching data.
        combined : bool, default=False
            If True, returns a single DataFrame with multiindex.
            If False, returns a dictionary of DataFrames by ticker.
        data : dict[str, pd.DataFrame] or pd.DataFrame, optional
            If provided, use this data instead of fetching from tickers.
        """
        self.combined = combined

        if data is not None:
            self.data = data
        else:
            if not tickers:
                raise ValueError("No tickers provided. Please provide tickers or `data`.")
            fetcher = Fetch(
                tickers=tickers, 
                start_date=start_date, 
                end_date=end_date, 
                verbose=verbose
            )
            self.data: Union[dict[str, pd.DataFrame], pd.DataFrame] = fetcher.get_asset_data(combined=self.combined)

        
    def trend_detection(self):
        """
        Detect trend direction based on whether today's Close > yesterday's Close.
        """
        if self.combined:
            self.data["Trend"] = (self.data["Close"] > self.data["Close"].shift(1)).astype(int)
        else:
            for ticker, df in self.data.items():
                df["Trend"] = (df["Close"] > df["Close"].shift(1)).astype(int)
                self.data[ticker] = df
        return self
    
    def peak_detection(self, windows: Union[int, list[int]] = 1):
        """
        Detect local peaks within a given window for single or multiple assets.
        
        Parameters
        ----------
        windows : int or list[int], default=1
            Window size(s) to look for local peaks.
        
        Returns
        -------
        self : TargetClassifier
            Adds PK_<window> columns indicating peaks (1) or not (0).
        """
        if isinstance(windows, int):
            windows = [windows]
        
        if self.combined:
            df = self.data.copy()
            for w in windows:
                col_name = f"PK_{w}"
                df[col_name] = 0
                for i in range(w, len(df) - w):
                    current = df["Close"].iloc[i]
                    left = df["Close"].iloc[i - w:i]
                    right = df["Close"].iloc[i + 1:i + w + 1]

                    if current > left.max() and current > right.max():
                        df.loc[df.index[i], col_name] = 1
            self.data = df
        else:
            for ticker, df in self.data.items():
                df = df.copy()
                for w in windows:
                    col_name = f"PK_{w}"
                    df[col_name] = 0
                    for i in range(w, len(df) - w):
                        current = df["Close"].iloc[i]
                        left = df["Close"].iloc[i - w:i]
                        right = df["Close"].iloc[i + 1:i + w + 1]

                        if current > left.max() and current > right.max():
                            df.loc[df.index[i], col_name] = 1
                self.data[ticker] = df
        return self


    def trough_detection(self, windows: Union[int, list[int]] = 1):
        """
        Detect local troughs within a given window for single or multiple assets.
        
        Parameters
        ----------
        windows : int or list[int], default=1
            Window size(s) to look for local troughs.
        
        Returns
        -------
        self : TargetClassifier
            Adds TRU_<window> columns indicating troughs (1) or not (0).
        """
        if isinstance(windows, int):
            windows = [windows]
        
        if self.combined:
            df = self.data.copy()
            for w in windows:
                col_name = f"TRU_{w}"
                df[col_name] = 0
                for i in range(w, len(df) - w):
                    current = df["Close"].iloc[i]
                    left = df["Close"].iloc[i - w:i]
                    right = df["Close"].iloc[i + 1:i + w + 1]

                    if current < left.min() and current < right.min():
                        df.loc[df.index[i], col_name] = 1
            self.data = df
        else:
            for ticker, df in self.data.items():
                df = df.copy()
                for w in windows:
                    col_name = f"TRU_{w}"
                    df[col_name] = 0
                    for i in range(w, len(df) - w):
                        current = df["Close"].iloc[i]
                        left = df["Close"].iloc[i - w:i]
                        right = df["Close"].iloc[i + 1:i + w + 1]

                        if current < left.min() and current < right.min():
                            df.loc[df.index[i], col_name] = 1
                self.data[ticker] = df
        return self

    
    def get_data(self) -> Union[dict[str, pd.DataFrame], pd.DataFrame]:
        return self.data
    
#----------xxx---------------