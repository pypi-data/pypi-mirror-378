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