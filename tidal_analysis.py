#Copyright 2025 by Fay Hardwidge. CC-SA
#!/usr/bin/env python3
# pylint: disable=redefined-outer-name
# pylint: disable=line-too-long
"""
This script performs a comprehensive analysis of tidal gauge data from multiple text files.

It reads and combines tidal observations, cleans the data by handling missing values
and non-numeric entries, and then performs several key analyses:
1.  Calculates the sea-level rise using linear regression.
2.  Identifies and reports the longest contiguous period of valid sea-level data.
3.  Includes functions for extracting and normalizing data for specific years or time sections.

"""

# import the modules you need here
import argparse
import os
import datetime #pylint: disable=unused-import
import pytz #pylint: disable=unused-import
import uptide
import pandas as pd
import numpy as np
from scipy import stats

def read_tidal_data(filename):
    """
    Reads tidal data from a specified text file, cleans it, and sets a Datetime index.
    """
    df = pd.read_csv(filename,
                     skiprows=11,
                     sep=r'\s+',
                     names=['Cycle', 'Date', 'Time', 'ASLVBG02', 'Residuals'],
                     header=None)
    df['CombinedDT'] = df['Date'].astype(str) + df['Time'].astype(str)
    df['Datetime'] = pd.to_datetime(df['CombinedDT'],
                                    format='%Y/%m/%d%H:%M:%S',
                                    errors='coerce') #new Datetime column with concated Date and Time data (CombinedDT)
    df.set_index('Datetime', inplace=True)
    df.drop(columns=['CombinedDT'], inplace=True, errors='ignore')
    df.rename(columns={'ASLVBG02': 'Sea Level'}, inplace=True)
    df['Sea Level'] = df['Sea Level'].astype(str)
    df['Sea Level'] = df['Sea Level'].replace(r'.*[MNTN].*', np.nan, regex=True)
    df['Sea Level'] = pd.to_numeric(df['Sea Level'], errors='coerce')
    if not os.path.exists(filename):
        raise FileNotFoundError("This file does not exist")
    return df #layout from gemini

def extract_single_year_remove_mean(year, data):
    """
    Extracts 'Sea Level' data for a specific year and removes the mean sea level for that year.
    """
    year_string_start = str(year)
    year_string_end = str(year)
    year1947 = data.loc[year_string_start:year_string_end, ['Sea Level']].copy()
    mmm = np.mean(year1947['Sea Level']) #calculates arithmetic mean of 'Sea Level' values extracted for specified year
    year1947['Sea Level'] -= mmm
    return year1947

def extract_section_remove_mean(start, end, data):
    """
    Extracts 'Sea Level' data for a specified date range and removes the mean sea level for that period.
    """
    start = pd.to_datetime(start, format='%Y%m%d')
    end = pd.to_datetime(end, format='%Y%m%d') + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)
    data = data.loc[start:end].copy() #slices Dateframe (.loc) to collect continuous segment of data, based on calculated start/end
    data['Sea Level'] = pd.to_numeric(data['Sea Level'], errors='coerce')
    sea_level_mean = data['Sea Level'].mean() #calculates average 'Sea Level' for extracted time segment
    data['Sea Level'] = data['Sea Level'] - sea_level_mean
    return data #from gemini

def join_data(data1, data2):
    """
    Joins two DataFrames by concatenating them and sorting the resulting index.
    """
    return pd.concat([data2, data1]).sort_index() #from gemini (condensed version)

def sea_level_rise(data):
    """
    Calculates the rate of sea-level rise and its p-value using linear regression.
    """
    df_clean = data.dropna(subset=['Sea Level']) #dropna removes rows in 'Sea Level' that contain missing value
    x = df_clean.index.astype('int64')//10**9 #.astype('int64') coverts datetime objects to numerical representation (typically nanoseconds)
    y = df_clean['Sea Level'].values
    slope, _, _, p_value, _ = stats.linregress(x,y)
    slope = slope * 3600 * 24 #changed to average sea level rise per day instead of per second
    return slope, p_value

def tidal_analysis(data, constituents, start_datetime):
    """
    Performs tidal harmonic analysis on sea level data using the Uptide library
    """
    data = data.dropna(subset=['Sea Level']).copy()
    tide_obj = uptide.Tides(constituents) #creates tide_obj to hold astronomical frequencies/phases for these tidal components
    tide_obj.set_initial_time(start_datetime)
    seconds_since = (data.index.astype('int64').to_numpy() / 1e9) - start_datetime.timestamp() #1e9 divides nanoseconds to convert to seconds
    elevation_data = data['Sea Level'].to_numpy() #up to here from gemini
    amp, pha = uptide.harmonic_analysis(tide_obj, elevation_data, seconds_since)
    return amp, pha

def get_longest_contiguous_data(data):
    """
    Finds the longest contiguous period of valid 'Sea Level' data in a DataFrame.
    """
    df_clean = data.dropna(subset=['Sea Level'])
    if df_clean.empty:
        return pd.Timedelta(0), None, None
    expected_interval = pd.Timedelta(minutes=15)
    break_threshold = expected_interval + pd.Timedelta(seconds=1)
    breaks_boolean_series = (df_clean.index.to_series().diff() > break_threshold).fillna(True)
    start_indices = np.where(breaks_boolean_series)[0]
    longest_period = pd.Timedelta(0)
    longest_start = None
    longest_end = None
    for i, current_block_start_pos in enumerate(start_indices):
        current_block_start_pos = start_indices[i]
        current_block_end_pos = (start_indices[i+1] - 1
                                 if i + 1 < len(start_indices)
                                 else len(df_clean) - 1)
        if current_block_end_pos >= current_block_start_pos:
            current_block_start = df_clean.index[current_block_start_pos]
            current_block_end = df_clean.index[current_block_end_pos]
            duration = current_block_end - current_block_start
            if duration > longest_period:
                longest_period = duration
                longest_start = current_block_start
                longest_end = current_block_end #from gemini
    return longest_period, longest_start, longest_end

if __name__ == '__main__':

    parser = argparse.ArgumentParser(
                     prog="UK Tidal analysis",
                     description="Calculate tidal constiuents and RSL from tide gauge data",
                     epilog="Copyright 2024, Jon Hill"
                     )

    parser.add_argument("directory",
                    help="the directory containing txt files with data")
    parser.add_argument('-v', '--verbose',
                    action='store_true',
                    default=False,
                    help="Print progress")

    args = parser.parse_args()
    dirname = args.directory
    verbose = args.verbose
    data = pd.DataFrame()
    for filename in os.listdir(dirname):
        if filename.endswith(".txt"):
            filepath = os.path.join(dirname, filename)
            df = read_tidal_data(filepath)
            data = join_data(data, df)
            if verbose:
                print(f"Successfully read and joined data from {filename}")
    if not data.empty:
        slope, p_value = sea_level_rise(data)
        print(f"Sea-level rise: {slope} meters per day (p-value: {p_value})")
        first_valid_idx = data.dropna(subset=['Sea Level']).index[0]
        constituents = ['M2', 'S2']
        start_datetime = pytz.timezone("utc").localize(first_valid_idx.to_pydatetime())
        amp, pha = tidal_analysis(data, constituents, start_datetime)
        print(f"{constituents}: Amplitude = {amp}, Phase = {pha}")
        longest_period, longest_start, longest_end = get_longest_contiguous_data(data)
        print(f"Longest contiguous period of data: {longest_period}")
        if longest_start and longest_end:
            print(f"Start of longest contiguous period: {longest_start}")
            print(f"End of longest contiguous period: {longest_end}")
    print("\nSample of processed tidal data (first 5 rows):")
    print(data.head()) #from gemini
