import pandas as pd
import joblib
from tickcomp import TickBar
from sklearn.preprocessing import MinMaxScaler, RobustScaler
from sklearn.compose import ColumnTransformer
import pandas_ta as ta
import json
import os

class TradingDataProcessor:
    def __init__(self, json_file_path, model_path="models/final_model.joblib"):
        # Get the absolute paths based on the script's location
        script_dir = os.path.dirname(os.path.abspath(__file__))
        self.json_file_path = os.path.join(script_dir, json_file_path)
        self.model_path = os.path.join(script_dir, model_path)
        self.model = joblib.load(self.model_path)
        self.data = self._initialize_data()

    def _initialize_data(self):
        # Import JSON data and perform initial data wrangling
        df = self.json_import(self.json_file_path)
        df = self.data_wrangling(df)
        return df

    def json_import(self, json_file_path):
        # Load JSON data from file
        with open(json_file_path, 'r') as json_file:
            data_list = json.load(json_file)

        # Convert the list of dictionaries to a DataFrame
        df = pd.DataFrame(data_list)

        # Convert 'E' column to datetime format and rename it to 'timestamp'
        df['E'] = pd.to_datetime(df['E'], unit='ms')
        df.rename(columns={'E': 'timestamp'}, inplace=True)

        # Set 'timestamp' column as the index
        df.set_index('timestamp', inplace=True)

        # Rename other columns for better readability
        df.columns = ['event', 'symbol', 'close', 'open', 'high', 'low', 'volume', 'quoteVolume']

        # Convert object columns to numeric types
        numeric_columns = ['close', 'open', 'high', 'low', 'volume']
        df[numeric_columns] = df[numeric_columns].apply(pd.to_numeric, errors='coerce')

        # Reorder columns as per your desired output
        df = df[['open', 'high', 'low', 'close', 'volume']]

        return df

    def data_wrangling(self, df):
        # Volume column
        df['v'] = df['volume']
        # Dollar value column
        df['dv'] = df['volume']*df['close']
        # Generate tick bar
        df = TickBar(df).dollar_tick(100_000_000)
        # Create 285 teachnical indicators
        df.ta.strategy()
        # Select the important features
        df = df[['AD', 'AMATe_LR_8_21_2', 'OBV', 'AOBV_LR_2', 'BOP', 'CDL_2CROWS',
            'CDL_3BLACKCROWS', 'CDL_3INSIDE', 'CDL_3LINESTRIKE', 'CDL_3OUTSIDE',
            'CDL_3STARSINSOUTH', 'CDL_3WHITESOLDIERS', 'CDL_ABANDONEDBABY',
            'CDL_ADVANCEBLOCK', 'CDL_BELTHOLD', 'CDL_BREAKAWAY',
            'CDL_CLOSINGMARUBOZU', 'CDL_CONCEALBABYSWALL', 'CDL_COUNTERATTACK',
            'CDL_DARKCLOUDCOVER', 'CDL_DOJI_10_0.1', 'CDL_DOJISTAR',
            'CDL_DRAGONFLYDOJI', 'CDL_ENGULFING', 'CDL_EVENINGDOJISTAR',
            'CDL_EVENINGSTAR', 'CDL_GAPSIDESIDEWHITE', 'CDL_GRAVESTONEDOJI',
            'CDL_HAMMER', 'CDL_HANGINGMAN', 'CDL_HARAMI', 'CDL_HARAMICROSS',
            'CDL_HIGHWAVE', 'CDL_HIKKAKE', 'CDL_HIKKAKEMOD', 'CDL_HOMINGPIGEON',
            'CDL_IDENTICAL3CROWS', 'CDL_INNECK', 'CDL_INSIDE', 'CDL_INVERTEDHAMMER',
            'CDL_KICKING', 'CDL_KICKINGBYLENGTH', 'CDL_LADDERBOTTOM',
            'CDL_LONGLINE', 'CDL_MARUBOZU', 'CDL_MATCHINGLOW', 'CDL_MATHOLD',
            'CDL_MORNINGDOJISTAR', 'CDL_MORNINGSTAR', 'CDL_ONNECK', 'CDL_PIERCING',
            'CDL_RICKSHAWMAN', 'CDL_RISEFALL3METHODS', 'CDL_SEPARATINGLINES',
            'CDL_SHOOTINGSTAR', 'CDL_SHORTLINE', 'CDL_SPINNINGTOP',
            'CDL_STALLEDPATTERN', 'CDL_STICKSANDWICH', 'CDL_TAKURI',
            'CDL_TASUKIGAP', 'CDL_THRUSTING', 'CDL_TRISTAR', 'CDL_UNIQUE3RIVER',
            'CDL_UPSIDEGAP2CROWS', 'CDL_XSIDEGAP3METHODS', 'LDECAY_5', 'DEC_1',
            'PSARr_0.02_0.2', 'PVOL', 'PVR', 'SQZ_ON', 'SQZ_OFF', 'SQZ_NO',
            'SQZPRO_ON_WIDE', 'SQZPRO_ON_NARROW', 'STC_10_12_26_0.5',
            'STCstoch_10_12_26_0.5', 'SUPERTd_7_3.0', 'THERMOl_20_2_0.5',
            'THERMOs_20_2_0.5', 'TTM_TRND_6']]

        # Instantiate transformer
        preprocessing = ColumnTransformer([
        ('MinMax', MinMaxScaler(), ['AD', 'OBV', 'PVOL', 'LDECAY_5']),
        ('Robust', RobustScaler(), [
            'CDL_2CROWS', 'CDL_3INSIDE', 'CDL_3OUTSIDE', 'CDL_ABANDONEDBABY', 'CDL_BELTHOLD',
            'CDL_BREAKAWAY', 'CDL_CLOSINGMARUBOZU', 'CDL_COUNTERATTACK', 'CDL_DARKCLOUDCOVER',
            'CDL_DOJI_10_0.1', 'CDL_DOJISTAR', 'CDL_DRAGONFLYDOJI', 'CDL_ENGULFING',
            'CDL_EVENINGDOJISTAR', 'CDL_EVENINGSTAR', 'CDL_GAPSIDESIDEWHITE', 'CDL_GRAVESTONEDOJI',
            'CDL_HAMMER', 'CDL_HANGINGMAN', 'CDL_HARAMI', 'CDL_HARAMICROSS', 'CDL_HIGHWAVE',
            'CDL_HIKKAKE', 'CDL_HIKKAKEMOD', 'CDL_HOMINGPIGEON', 'CDL_INNECK', 'CDL_INSIDE',
            'CDL_INVERTEDHAMMER', 'CDL_KICKING', 'CDL_KICKINGBYLENGTH', 'CDL_LADDERBOTTOM',
            'CDL_LONGLINE', 'CDL_MARUBOZU', 'CDL_MATCHINGLOW', 'CDL_MORNINGDOJISTAR',
            'CDL_MORNINGSTAR', 'CDL_ONNECK', 'CDL_PIERCING', 'CDL_RICKSHAWMAN',
            'CDL_SEPARATINGLINES', 'CDL_SHOOTINGSTAR', 'CDL_SHORTLINE', 'CDL_SPINNINGTOP',
            'CDL_STALLEDPATTERN', 'CDL_STICKSANDWICH', 'CDL_TAKURI', 'CDL_TASUKIGAP',
            'CDL_THRUSTING', 'CDL_TRISTAR', 'CDL_UNIQUE3RIVER', 'CDL_UPSIDEGAP2CROWS',
            'CDL_XSIDEGAP3METHODS', 'PSARr_0.02_0.2', 'PVOL', 'SQZ_ON', 'SQZ_OFF', 'SQZ_NO',
            'SQZPRO_ON_WIDE', 'SQZPRO_ON_NARROW', 'STC_10_12_26_0.5', 'STCstoch_10_12_26_0.5',
            'THERMOl_20_2_0.5'
        ])
        ], remainder='passthrough')

        # Transform the data
        df_transformed = preprocessing.fit_transform(df)
        df = pd.DataFrame(
        df_transformed, columns=preprocessing.get_feature_names_out(),
        index=df.index)

        return df

    # def add_new_row(self, new_row):
    #     # Convert new_row to DataFrame and perform the same data wrangling
    #     new_df = self.json_import(new_row)
    #     new_df = self.data_wrangling(new_df)

    #     # Append the new row to the existing data
    #     self.data = pd.concat([self.data, new_df])

    #     # Trigger ML algorithm prediction
    #     prediction = self.predict()
    #     return prediction

    def predict(self):
        # Make predictions using the ML model
        predictions = self.model.predict(self.data)
        return predictions
