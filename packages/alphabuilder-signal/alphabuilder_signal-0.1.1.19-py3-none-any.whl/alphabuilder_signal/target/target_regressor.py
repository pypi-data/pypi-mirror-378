import pandas as pd
import numpy as np
from alphabuilder_signal import Fetch
from typing import Optional, List, Union
from .target_classifier import TargetClassifier

class TargetRegressor:
    """
    TargetRegressor class for generating regression-style target variables
    such as returns, log returns, moving averages, etc.
    
    Handles both single combined DataFrame (multi-asset) and individual
    ticker-based DataFrames depending on the `combined` flag.
    """
    def __init__(
        self,
        tickers: Optional[List[str]] = None,
        start_date: str = "2010-01-01",
        end_date: Optional[str] = None,
        verbose: bool = True,
        combined: bool = False,
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
            verbose=verbose,
        )

        self.combined = combined
        self.data: Union[dict[str, pd.DataFrame], pd.DataFrame] = fetcher.get_asset_data(combined=self.combined)
        self.tc = TargetClassifier(tickers=tickers, start_date=start_date, end_date=end_date, verbose=verbose, combined=self.combined)

    def distance_between_two_consecutive_peak(self, windows: Union[int, list[int]] = 1):
        """
        Calculate the distance (in number of periods) between two consecutive local peaks.

        Args:
            windows (Union[int, list[int]], optional): 
                Window size(s) used for peak detection. Defaults to 14.

        Returns:
            TargetRegressor: Self with a new column "Peak_Distance" (or similar) added 
            to each DataFrame.
        """
        if isinstance(windows, int):
            windows = [windows]

        if self.combined:
            for w in windows:
                self.tc.data = self.data.copy()
                pk_df = self.tc.peak_detection(windows=w).get_data()

                peak_col = f"PK_{w}"
                col_name = f"DBP_{w}"
                pk_df[col_name] = np.nan

                peak_indices = pk_df.index[pk_df[peak_col] == 1].to_list()
                for i in range(1, len(peak_indices)):
                    pos1 = pk_df.index.get_loc(peak_indices[i])
                    pos0 = pk_df.index.get_loc(peak_indices[i - 1])
                    pk_df.at[peak_indices[i], col_name] = pos1 - pos0

                pk_df.drop(columns=[peak_col], inplace=True)
                self.data = pk_df
        else:
            for ticker, df in self.data.items():
                tc_single = TargetClassifier(combined=True, data=df.copy())
                tc_single.data = df.copy()
                for w in windows:
                    pk_df = tc_single.peak_detection(windows=w).get_data()
                    peak_col = f"PK_{w}"
                    col_name = f"DBP_{w}"
                    pk_df[col_name] = np.nan

                    peak_indices = pk_df.index[pk_df[peak_col] == 1].to_list()
                    for i in range(1, len(peak_indices)):
                        pos1 = pk_df.index.get_loc(peak_indices[i])
                        pos0 = pk_df.index.get_loc(peak_indices[i - 1])
                        pk_df.at[peak_indices[i], col_name] = pos1 - pos0

                    pk_df.drop(columns=[peak_col], inplace=True)
                self.data[ticker] = pk_df
        return self

    def distance_between_two_consecutive_trough(self, windows: Union[int, list[int]] = 1):
        """
        Calculate the distance (in number of periods) between two consecutive local troughs.

        Args:
            windows (Union[int, list[int]], optional): 
                Window size(s) used for trough detection. Defaults to 14.

        Returns:
            TargetRegressor: Self with a new column "Trough_Distance" (or similar) added 
            to each DataFrame.
        """
        if isinstance(windows, int):
            windows = [windows]

        if self.combined:
            for w in windows:
                self.tc.data = self.data.copy()
                tru_df = self.tc.trough_detection(windows=w).get_data()

                trough_col = f"TRU_{w}"
                col_name = f"DBT_{w}"
                tru_df[col_name] = np.nan

                trough_indices = tru_df.index[tru_df[trough_col] == 1].to_list()
                for i in range(1, len(trough_indices)):
                    pos1 = tru_df.index.get_loc(trough_indices[i])
                    pos0 = tru_df.index.get_loc(trough_indices[i - 1])
                    tru_df.at[trough_indices[i], col_name] = pos1 - pos0

                tru_df.drop(columns=[trough_col], inplace=True)
                self.data = tru_df
        else:
            for ticker, df in self.data.items():
                tc_single = TargetClassifier(combined=True, data=df.copy())
                tc_single.data = df.copy()
                for w in windows:
                    tru_df = tc_single.trough_detection(windows=w).get_data()
                    trough_col = f"TRU_{w}"
                    col_name = f"DBT_{w}"
                    tru_df[col_name] = np.nan

                    trough_indices = tru_df.index[tru_df[trough_col] == 1].to_list()
                    for i in range(1, len(trough_indices)):
                        pos1 = tru_df.index.get_loc(trough_indices[i])
                        pos0 = tru_df.index.get_loc(trough_indices[i - 1])
                        tru_df.at[trough_indices[i], col_name] = pos1 - pos0

                    tru_df.drop(columns=[trough_col], inplace=True)
                self.data[ticker] = tru_df
        return self

    def distance_between_one_peak_or_trough_to_next(self, windows: Union[int, list[int]] = 1):
        """
        Calculate the distance (in number of periods) from one local peak to the next trough,
        or from one local trough to the next peak.

        Args:
            windows (Union[int, list[int]], optional): 
                Window size(s) used for detecting peaks and troughs. Defaults to 14.

        Returns:
            TargetRegressor: Self with a new column "Peak_Trough_Distance" (or similar) 
            added to each DataFrame.
        """
        if isinstance(windows, int):
            windows = [windows]

        if self.combined:
            for w in windows:
                self.tc.data = self.data.copy()
                classified_df = (self.tc.peak_detection(windows=w)
                                 .trough_detection(windows=w).get_data())

                peak_col, trough_col = f"PK_{w}", f"TRU_{w}"
                dbpt_col = f"DBPT_{w}"
                classified_df[dbpt_col] = np.nan

                turning_points = []
                for idx in classified_df.index:
                    if classified_df.at[idx, peak_col] == 1:
                        turning_points.append((idx, "peak"))
                    elif classified_df.at[idx, trough_col] == 1:
                        turning_points.append((idx, "trough"))

                for i in range(1, len(turning_points)):
                    prev_idx, prev_type = turning_points[i - 1]
                    curr_idx, curr_type = turning_points[i]
                    if prev_type != curr_type:
                        pos1 = classified_df.index.get_loc(curr_idx)
                        pos0 = classified_df.index.get_loc(prev_idx)
                        classified_df.at[curr_idx, dbpt_col] = pos1 - pos0

                classified_df.drop(columns=[peak_col, trough_col], inplace=True)
                self.data = classified_df
        else:
            for ticker, df in self.data.items():
                tc_single = TargetClassifier(combined=True, data=df.copy())
                tc_single.data = df.copy()
                for w in windows:
                    classified_df = (tc_single.peak_detection(windows=w)
                                    .trough_detection(windows=w)
                                    .get_data())

                    peak_col, trough_col = f"PK_{w}", f"TRU_{w}"
                    dbpt_col = f"DBPT_{w}"
                    classified_df[dbpt_col] = np.nan

                    turning_points = []
                    for idx in classified_df.index:
                        if classified_df.at[idx, peak_col] == 1:
                            turning_points.append((idx, "peak"))
                        elif classified_df.at[idx, trough_col] == 1:
                            turning_points.append((idx, "trough"))

                    for i in range(1, len(turning_points)):
                        prev_idx, prev_type = turning_points[i - 1]
                        curr_idx, curr_type = turning_points[i]
                        if prev_type != curr_type:
                            pos1 = classified_df.index.get_loc(curr_idx)
                            pos0 = classified_df.index.get_loc(prev_idx)
                            classified_df.at[curr_idx, dbpt_col] = pos1 - pos0

                    classified_df.drop(columns=[peak_col, trough_col], inplace=True)
                self.data[ticker] = classified_df
        return self

    def delta(self):
        """
        Compute the first difference of the closing price.

        Notes:
            - Delta is defined as: Delta_t = Close_t - Close_{t-1}.
            - Useful for momentum analysis or as input to further indicators.

        Returns:
            TargetRegressor: Self with a new column "Delta" added to each DataFrame.
        """
        if self.combined:
            self.data["Delta"] = self.data["Close"].diff()
        else:
            for ticker, df in self.data.items():
                df["Delta"] = df["Close"].diff()
                self.data[ticker] = df
        return self

    def daily_return(self, log_return: bool = False):
        """
        Compute daily returns from closing prices.

        Args:
            log_return (bool, optional): 
                If True, compute logarithmic returns:
                    log(Close_t / Close_{t-1}).
                If False, compute simple returns:
                    (Close_t - Close_{t-1}) / Close_{t-1}.
                Defaults to False.

        Returns:
            TargetRegressor: Self with a new column "Daily_Return" added to each DataFrame.
        """
        if self.combined:
            if log_return:
                self.data["Daily_Log_Return"] = np.log(self.data["Close"] / self.data["Close"].shift(1))
            else:
                self.data["Daily_Return"] = self.data["Close"].pct_change()
        else:
            for ticker, df in self.data.items():
                if log_return:
                    df["Daily_Log_Return"] = np.log(df["Close"] / df["Close"].shift(1))
                else:
                    df["Daily_Return"] = df["Close"].pct_change()
                self.data[ticker] = df
        return self

    def get_data(self) -> Union[dict[str, pd.DataFrame], pd.DataFrame]:
        return self.data

#----------xxx---------------

