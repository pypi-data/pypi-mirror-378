import pandas as pd
import numpy as np

class TargetClassifier:
    def __init__(self, df):
        self.df = df.copy()

    def trend_detection(self):
        self.df['Trend'] = self.df['Close'] > self.df['Close'].shift(1).astype(int)
        
        return self
    
    def peak_detection(self, window=1):
        col_name = f'PK_{window}'
        self.df[col_name] = 0
        for i in range(window, len(self.df) - window):
            current = self.df['Close'].iloc[i]
            left = self.df['Close'].iloc[i - window:i]
            right = self.df['Close'].iloc[i + 1 : i + window + 1]

            if current > left.max() and current > right.max():
                self.df.at[df.index[i], col_name] = 1

        return self
    
    def trough_detection(self, window=1):
        col_name = f'TRU_{window}'
        self.df[col_name] = 0

        for i in range(window, len(self.df) - window):
            current = self.df['Close'].iloc[i]
            left = self.df['Close'].iloc[i-window:i]
            right = self.df['Close'].iloc[i+1: i+window+1]

            if current < left.min() and current < right.min():
                self.df.at[df.index[i], col_name] = 1
        
        return self

    def get_df(self):
        return self.df
    

class TargetRegressor:
    def __init__(self, df):
        self.df = df.copy()

    def distance_between_two_consecutive_peak(self, window=1):
        tc = TargetClassifier(self.df)
        pk_df = tc.peak_detection(window=window).get_df()
        self.df = pk_df.copy()
        peak_col = f'PK_{window}'
        peak_indices = self.df.index[self.df[peak_col] == 1].to_list()
        col_name = f'DBP_{window}'

        for i in range(1, len(peak_indices)):
            pos1 = self.df.index.get_loc(peak_indices[i])
            pos0 = self.df.index.get_loc(peak_indices[i - 1])
            dist = pos1 - pos0
            self.df.at[peak_indices[i], col_name] = dist    
        self.df.drop(columns=[f'PK_{window}'], inplace=True)

        return self

    def distance_between_two_consecutive_trough(self, window=1):
        tc = TargetClassifier(self.df)
        tru_df = tc.trough_detection(window=window).get_df()
        self.df = tru_df.copy()
        trough_col = f'TRU_{window}'
        trough_indices = self.df.index[self.df[trough_col] == 1].to_list()
        col_name = f'DBT_{window}'

        for i in range(1, len(trough_indices)):
            pos1 = self.df.index.get_loc(trough_indices[i])
            pos0 = self.df.index.get_loc(trough_indices[i - 1])
            dist = pos1 - pos0
            self.df.at[trough_indices[i], col_name] = dist    
        self.df.drop(columns=[f'TRU_{window}'], inplace=True)

        return self
    
    def distance_between_one_peak_or_trough_to_next(self, window=1):
        tc = TargetClassifier(self.df)
        classified_df = tc.peak_detection(window=window).trough_detection(window=window).get_df()
        self.df = classified_df.copy()
        peak_col = f'PK_{window}'
        trough_col = f'TRU_{window}'
        dbpt_col = f'DBPT_{window}'

        self.df[dbpt_col] = np.nan
        turning_points = []

        for idx in self.df.index:
            if self.df.at[idx, peak_col] == 1:
                turning_points.append((idx, 'peak'))
            elif self.df.at[idx, trough_col] == 1:
                turning_points.append((idx, 'trough'))

        for i in range(1, len(turning_points)):
            prev_idx, prev_type = turning_points[i - 1]
            curr_idx, curr_type = turning_points[i]

            if prev_type != curr_type:
                pos1 = self.df.index.get_loc(curr_idx)
                pos0 = self.df.index.get_loc(prev_idx)
                dist = pos1 - pos0
                self.df.at[curr_idx, dbpt_col] = dist

        self.df.drop(columns=[peak_col, trough_col], inplace=True)

        return self

    def height_of_peak(self, window=1):
        tc = TargetClassifier(self.df)
        classified_df = tc.peak_detection(window=window).trough_detection(window=window).get_df()
        self.df = classified_df.copy()

        peak_col = f'PK_{window}'
        trough_col = f'TRU_{window}'
        height_col = f'PKHe_{window}'
        self.df[height_col] = np.nan

        peak_indices = self.df.index[self.df[peak_col] == 1].to_list()
        trough_indices = self.df.index[self.df[trough_col] == 1].to_list()

        for pk_idx in peak_indices:
            pk_pos = self.df.index.get_loc(pk_idx)
            pk_price = self.df.at[pk_idx, 'Close']

            prev_troughs = []
            for idx in trough_indices:
                if self.df.index.get_loc(idx) < pk_pos:
                    prev_troughs.append(idx)

            if prev_troughs:
                last_trough_idx = prev_troughs[-1]
                trough_price = self.df.at[last_trough_idx, 'Close']
                height = pk_price - trough_price
                self.df.at[pk_idx, height_col] = height

        self.df.drop(columns=[peak_col, trough_col], inplace=True)

        return self

    def depth_of_next_trough(self, window=1):
        tc = TargetClassifier(self.df)
        pk_df = tc.peak_detection(window=window).get_df()
        tru_df = tc.trough_detection(window=window).get_df()

        self.df = pk_df.copy()
        self.df[f'TRU_{window}'] = tru_df[f'TRU_{window}']
        
        peak_col = f'PK_{window}'
        trough_col = f'TRU_{window}'
        col_name = f'TRUDe_{window}'
        self.df[col_name] = np.nan

        peak_indices = self.df.index[self.df[peak_col] == 1].to_list()
        trough_indices = self.df.index[self.df[trough_col] == 1].to_list()

        for pk_idx in peak_indices:
            pk_pos = self.df.index.get_loc(pk_idx)

            next_troughs = []
            for idx in trough_indices:
                if self.df.index.get_loc(idx) > pk_pos:
                    next_troughs.append(idx)

            if next_troughs:
                next_trough = next_troughs[0] 
                depth = self.df.at[pk_idx, 'Close'] - self.df.at[next_trough, 'Close']
                self.df.at[pk_idx, col_name] = depth

        self.df.drop(columns=[peak_col, trough_col], inplace=True)

        return self


    def delta(self):
        self.df['Delta'] = self.df['Close'] - self.df['Close'].shift(1)
        return self

    def daily_return(self, log_return=False):
        if log_return:
            self.df['Daily_Return'] = np.log(self.df['Close'] / self.df['Close'].shift(1))
        else:
            self.df['Daily_Return'] = self.df['Close'].pct_change()
        return self

    def get_df(self):
        return self.df

### -----------------xxx---- testing----xxx-----------------------###

def asset_df(data='SPY'):
    df = pd.read_csv(f'local_data/assets/{data}.csv')
    df = df.iloc[2:]
    df = df.set_index('Price')
    cols_to_float = ['Open', 'High', 'Low', 'Close', 'Volume']
    df[cols_to_float] = df[cols_to_float].astype(float)
    return df

df = asset_df()
tr = TargetRegressor(df)
df_tr = tr.depth_of_next_trough().get_df()
