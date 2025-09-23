import pandas as pd
import numpy as np
from alphabuilder_signal import Fetch
from typing import Optional, List, Union, Tuple

class LaggedFeatures:
    def __init__(
        self,
        tickers: Optional[List[str]] = None, 
        start_date: str = "2010-01-01",        
        end_date: Optional[str] = None,
        verbose: bool = True,
        combined: bool = False
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

    def return_close(self, k: Union[int, list[int]] = 1):
        """
        Compute log returns of Close price over k lags.
        """
        if isinstance(k, int):
            k = [k]
        
        if self.combined:
            for lag in k:
                if not (1 <= lag <= 4):
                    raise ValueError("k must be between 1 and 4")
                col = f"ret_close{lag}"
                self.data[col] = np.log(self.data['Close'].shift(lag - 1) / self.data['Close'].shift(lag))
        else:
            for ticker, df in self.data.items():
                for lag in k:
                    if not (1 <= lag <= 4):
                        raise ValueError("k must be between 1 and 4")
                    col = f"ret_close{lag}"
                    df[col] = np.log(df['Close'].shift(lag - 1) / df['Close'].shift(lag))
                self.data[ticker] = df
                
        return self
    
    def return_high_open(self, i: Union[int, list[int]] = 0, j: Union[int, list[int]] = 0):
        """
        Compute log return between High (shifted i) and Open (shifted j).
        """
        if isinstance(i, int):
            i = [i]
        if isinstance(j, int):
            j = [j]

        if self.combined:
            for ii in i:
                for jj in j:
                    if not (0 <= ii <= 3 and 0 <= jj <= 3):
                        raise ValueError("i and j must be between 0 and 3")
                    if jj < ii:
                        raise ValueError("j must be greater than or equal to i")
                    col = f"ret_ho_{ii}_{jj}"
                    self.data[col] = np.log(self.data['High'].shift(ii) / self.data['Open'].shift(jj))
        else:
            for ticker, df in self.data.items():
                for ii in i:
                    for jj in j:
                        if not (0 <= ii <= 3 and 0 <= jj <= 3):
                            raise ValueError("i and j must be between 0 and 3")
                        if jj < ii:
                            raise ValueError("j must be greater than or equal to i")
                        col = f"ret_ho_{ii}_{jj}"
                        df[col] = np.log(df['High'].shift(ii) / df['Open'].shift(jj))
                self.data[ticker] = df

        return self
    
    def return_low_open(self, k: Union[int, list[int]] = 0):
        """
        Compute log return between Low and Open with lag k.
        """
        if isinstance(k, int):
            k = [k]

        if self.combined:
            for lag in k:
                if not (0 <= lag <= 3):
                    raise ValueError("k must be between 0 and 3")
                col = f"ret_lo_{lag}"
                self.data[col] = np.log(self.data['Low'].shift(lag) / self.data['Open'].shift(lag))
        else:
            for ticker, df in self.data.items():
                for lag in k:
                    if not (0 <= lag <= 3):
                        raise ValueError("k must be between 0 and 3")
                    col = f"ret_lo_{lag}"
                    df[col] = np.log(df['Low'].shift(lag) / df['Open'].shift(lag))
                self.data[ticker] = df

        return self
    
    def get_data(self) -> Union[dict[str, pd.DataFrame], pd.DataFrame]:
        return self.data
    
#----------xxx---------------