# -*- coding: utf-8 -*-
"""EarthCamAssignment

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1eJGEAJEd85WKVQ0ZSm12JYlqj1TWFk-L

# Importing necessary librariesNew Section
"""

# Importing necessary libraries
import warnings
import ast
import itertools
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import statsmodels.api as sm

# Ignoring warnings
warnings.filterwarnings("ignore")

# Setting plot style
plt.style.use('fivethirtyeight')

# Reading data from CSV and parsing datetime columns
data = pd.read_csv('Earthcamweather_Data.csv', parse_dates=['datetime', 'ObservedAt_DateTime'])

"""# EDA"""

data.head(2)

data.tail(2)

# Checking data size
data.shape

# Checking data types
data.dtypes

# Checking all available stations
data['Station'].unique()

data.iloc[0]['Record']#['Celsius']

# Checking datetime type
data.iloc[0]['ObservedAt_DateTime']

# Checking all available datetimes
sorted([date][:10] for date in data['ObservedAt_DateTime'].unique())

# Extracting date part from datetime
data['observed_date'] = data.ObservedAt_DateTime.dt.date

# Extracting Celsius temperature
data['temp_c'] = data['Temperature'].apply(lambda x: int(ast.literal_eval(x)['Celsius']))

# Defining time bins
bins = [0, 6, 12, 18, 24]
labels = ['Night', 'Morning', 'Afternoon', 'Evening']

# Adding time bin to the dataframe
data['Time_bin'] = pd.cut(data.ObservedAt_DateTime.dt.hour, bins, labels=labels, right=False)

# Grouping data by date and time bin and calculating mean temperature
temp_data = data.groupby(['observed_date', 'Time_bin'])['temp_c'].mean().reset_index()

# Loop through time bins and perform forecasting and diagnostics
for time_bin in labels:
    # Filtering data for the specific time bin
    time_bin_data = temp_data[temp_data['Time_bin'] == time_bin].copy()
    time_bin_data.drop(columns="Time_bin", axis=1, inplace=True)

# Filling missing temperature values with mean
time_bin_data['temp_c'].fillna(time_bin_data['temp_c'].mean(), inplace=True)

# Setting date as index
time_bin_data.set_index('observed_date', inplace=True)

# Fitting SARIMA model
 mod = sm.tsa.statespace.SARIMAX(time_bin_data,
                                    order=(1, 1, 1),
                                    seasonal_order=(1, 1, 0, 12),
                                    enforce_stationarity=False,
                                    enforce_invertibility=False)
results = mod.fit()

# Printing model summary
print(results.summary().tables[1])

# Plotting diagnostics
results.plot_diagnostics(figsize=(16, 8))
plt.show()

# Forecasting
forecast_dates = pd.date_range(start=time_bin_data.index[-1], periods=30, freq='D')
forecast = results.get_forecast(steps=30)
predicted_values = forecast.predicted_mean

# Plotting forecast
plt.figure(figsize=(15, 6))
plt.plot(time_bin_data.index, time_bin_data['temp_c'], label='Observed')
plt.plot(forecast_dates, predicted_values, label='Forecast', color='r')
plt.title(f'Temperature Forecast for {time_bin}')
plt.legend()
plt.show()