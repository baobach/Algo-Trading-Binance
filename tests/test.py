import pandas as pd
import numpy as np
import pytest
import sys
import os

# Add the project directory to the Python path
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(project_dir, '..'))

# Now import the TickBar class
from tickcomp import TickBar


# Sample DataFrame fixture
@pytest.fixture
def sample_dataframe():
    data = {
        'timestamp': pd.date_range(start='2022-01-01', periods=100, freq='T'),
        'close': np.random.rand(100),
        'v': np.random.randint(100, 1000, size=100),
        'dv': np.random.uniform(10, 100, size=100)
    }
    df = pd.DataFrame(data)
    df.set_index('timestamp', inplace=True)
    return df

# Test price_tick method
def test_price_tick(sample_dataframe):
    tick_bar = TickBar(sample_dataframe)
    target_price = 5
    resampled_price = tick_bar.price_tick(target_price)
    assert isinstance(resampled_price, pd.DataFrame)

# Test volume_tick method
def test_volume_tick(sample_dataframe):
    tick_bar = TickBar(sample_dataframe)
    target_volume = 500
    resampled_volume = tick_bar.volume_tick(target_volume)
    assert isinstance(resampled_volume, pd.DataFrame)

# Test dollar_tick method
def test_dollar_tick(sample_dataframe):
    tick_bar = TickBar(sample_dataframe)
    target_dollar = 50
    resampled_dollar = tick_bar.dollar_tick(target_dollar)
    assert isinstance(resampled_dollar, pd.DataFrame)

