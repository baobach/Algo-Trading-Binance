"""
This module is for resample the data with desirable tick type.
Curretnly implement:
- Volume
- Dollar value Bar
"""

# Data tools
import pandas as pd
import numpy as np

class TickBar:
    def __init__(self, data):
        """
        Initialize TickBar object.

        Args:
            data (pd.DataFrame): Input DataFrame.
        """
        if not isinstance(data, pd.DataFrame):
            raise ValueError("Input data must be a DataFrame.")
        
        self.data = data

    def price_tick(self, target_price):
        """
        Resample data based on price bars.

        Args:
            target_price (int): Threashold for the price.

        Returns:
            pd.DataFrame: Resampled DataFrame.
        """
        if not isinstance(target_price, int) or target_price <= 0:
            raise ValueError("target_price must be a positive integer.")

        t = self.data['close']
        ts = 0
        idx = []

        for i, price in enumerate(t):
            ts += 1
            if ts >= target_price:
                idx.append(i)
                ts = 0

        # Use iloc to select rows based on index
        resampled_data = self.data.iloc[idx].drop_duplicates()

        return resampled_data
    
    def volume_tick(self, target_volume):
        """
        Resample data based on volume bars.

        Args:
            target_volume (int): Threshold value for volume.

        Returns:
            pd.DataFrame: Resampled DataFrame.
        """
        if not isinstance(target_volume, int) or target_volume <= 0:
            raise ValueError("target_volume must be a positive integer.")

        t = self.data['v']
        ts = 0
        idx = []

        for i, x in enumerate(t):
            ts += x
            if ts >= target_volume:
                idx.append(i)
                ts = 0

        # Use iloc to select rows based on index
        resampled_data = self.data.iloc[idx].drop_duplicates()

        return resampled_data
    
    def dollar_tick(self, target_dollar):
        """
        Resample data based on dollar bars.

        Args:
            target_dollar (int): Threshold value for dollars.

        Returns:
            pd.DataFrame: Resampled DataFrame.
        """
        if not isinstance(target_dollar, int) or target_dollar <= 0:
            raise ValueError("target_dollar must be a positive integer.")

        t = self.data['dv']
        ts = 0
        idx = []

        for i, x in enumerate(t):
            ts += x
            if ts >= target_dollar:
                idx.append(i)
                ts = 0

        # Use iloc to select rows based on index
        resampled_data = self.data.iloc[idx].drop_duplicates()

        return resampled_data











