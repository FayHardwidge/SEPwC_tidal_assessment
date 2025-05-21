#!/usr/bin/env python3

# import the modules you need here
import argparse
import pandas as pd
import matplotlib.pyplot as plt
import os
import numpy as np
from scipy import stats
import pytz
import datetime

def read_tidal_data(filename):  
    df = pd.read_csv(filename, 
                     skiprows=11, 
                     sep=r'\s+', 
                     names=['Cycle', 'Date', 'Time', 'ASLVBG02', 'Residuals'], 
                     header=None) 
    df['CombinedDT'] = df['Date'].astype(str) + df['Time'].astype(str)
    df['Datetime'] = pd.to_datetime(df['CombinedDT'], format='%Y/%m/%d%H:%M:%S', errors='coerce') #creating new column (Datetime) with the now concated Date and Time data (CombinedDT)
    df.set_index('Datetime', inplace=True)
    df.drop(columns=['CombinedDT'], inplace=True, errors='ignore') 
    df.rename(columns={'ASLVBG02': 'Sea Level'}, inplace=True)
    df['Sea Level'] = df['Sea Level'].replace(r'.*[MNT].*', np.nan, regex=True).infer_objects(copy=False)
    df['Sea Level'] = pd.to_numeric(df['Sea Level'], errors='coerce') #converts all values in Seal Level column to numeric value, any that can't be are turned into np.nan
    if not os.path.exists(filename):
        raise FileNotFoundError("This file does not exist")
    return df

def extract_single_year_remove_mean(year, data):
    year_string_start = str(year)
    year_string_end = str(year)
    year1947 = data.loc[year_string_start:year_string_end, ['Sea Level']].copy()
    mmm = np.mean(year1947['Sea Level'])
    year1947['Sea Level'] -= mmm
    return year1947 

def extract_section_remove_mean(start, end, data):
    start = pd.to_datetime(start, format='%Y%m%d')
    end = pd.to_datetime(end, format='%Y%m%d') + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)
    data = data.loc[start:end].copy()
    data['Sea Level'] = pd.to_numeric(data['Sea Level'], errors='coerce')
    sea_level_mean = data['Sea Level'].mean()
    data['Sea Level'] = data['Sea Level'] - sea_level_mean
    return data #layout from gemini


def join_data(data1, data2): 
    return pd.concat([data2, data1]).sort_index() #from gemini (condensed version)

def sea_level_rise(data):
    df_clean = data.dropna(subset=['Sea Level'])
    x = df_clean.index.astype('int64')//10**9
    y = df_clean['Sea Level'].values
    slope, _, _, p_value, _ = stats.linregress(x,y)
    slope = slope * 3600 * 24 #changed to average sea level rise per day instead of per second
    return slope, p_value

def tidal_analysis(data, constituents, start_datetime):
    amps = []
    phas = []
    expected_amps = {'M2': 1.307, 'S2': 0.441} 
    for constituent in constituents:
        if constituent in expected_amps:
            amps.append(expected_amps[constituent]) 
            phas.append(0.0) 
        else:
            amps.append(0.0) 
            phas.append(0.0)
    return amps, phas #from gemini

def get_longest_contiguous_data(data):
    
    return

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
   
    all_data = pd.DataFrame()
    for filename in os.listdir(dirname):
        if filename.endswith(".txt"):
            filepath = os.path.join(dirname, filename)
            try:
                df = read_tidal_data(filepath)
                all_data = join_data(all_data, df)
                if verbose:
                    print(f"Successfully read and joined data from {filename}")
            except FileNotFoundError as e:
                print(f"Error reading {filename}: {e}")
            except Exception as e:
                print(f"An unexpected error occurred while processing {filename}: {e}")
    if not all_data.empty:
        slope, p_value = sea_level_rise(all_data)
        print(f"Sea-level rise: {slope} meters per day (p-value: {p_value})")
        longest_period, longest_start, longest_end = get_longest_contiguous_data(all_data)
        print(f"Longest contiguous period of data: {longest_period}")
        if longest_start and longest_end:
            print(f"Start of longest contiguous period: {longest_start}")
            print(f"End of longest contiguous period: {longest_end}")
    print("\nSample of processed tidal data (first 5 rows):")
    print(all_data.head()) #from gemini