#!/usr/bin/env python3

# import the modules you need here
import argparse
import pandas as pd
import matplotlib.pyplot as plt
import datetime 
import wget
import os
import numpy as np
import uptide
import pytz
import math

def read_tidal_data(filename):  
    df = pd.read_csv(filename, 
                     skiprows=11, 
                     sep=r'\s+', 
                     names=['Cycle', 'Date', 'Time', 'Sea Level', 'Residuals'], 
                     header=None) 
    df['CombinedDT'] = df['Date'].astype(str) + df['Time'].astype(str)
    df['Datetime'] = pd.to_datetime(df['CombinedDT'], format='%Y/%m/%d%H:%M:%S', errors='coerce') #creating new column (Datetime) with the now concated Date and Time data (CombinedDT)
    df.set_index('Datetime', inplace=True)
    df.drop(columns=['CombinedDT'], inplace=True, errors='ignore') #removes the temporary CombinedDT column from DataFrame
    df['Sea Level'] = df['Sea Level'].replace(r'.*[MNT].*', np.nan, regex=True)
    df['Sea Level'] = pd.to_numeric(df['Sea Level'], errors='coerce') #converts all values in Seal Level column to numeric value, any that can't be are turned into np.nan
    if not os.path.exists(filename):
        raise FileNotFoundError(f"This file does not exist")
    return df

def extract_single_year_remove_mean(year, data):
    target_year = int(year)
    year1947 = data[data.index.year == target_year].copy() #stores rows from the data DataFrame from target_year in a new year1947 DataFrame 
    year1947['Sea Level'] = pd.to_numeric(year1947['Sea Level'], errors='coerce')
    sea_level_mean = year1947['Sea Level'].mean()
    year1947['Sea Level'] = year1947['Sea Level'] - sea_level_mean #mean-centering of the Sea Level data for the extracted year, 1947
    return year1947

def extract_section_remove_mean(start, end, data):


    return 


def join_data(data1, data2): 
    return pd.concat([data2, data1]).sort_index() #concates DataFrame (links data1 and data2 in a series) then rearranges in chronological order 

def sea_level_rise(data):

                                                     
    return 

def tidal_analysis(data, constituents, start_datetime):


    return 

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
    


