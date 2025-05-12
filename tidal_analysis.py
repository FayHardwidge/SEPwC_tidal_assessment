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
tidal_file = "data/1947ABE.txt"

def read_tidal_data(filename):
    df = pd.read_csv(tidal_file, # if tidal_file != "tidal_file.txt" else io.StringIO(file_content))
                    skiprows=11,
                    delim_whitespace=True,
                    names=['Cycle', 'Date', 'Time', 'Sea Level', 'Residuals'],
                    header=None)
    df['CombinedDT'] = df['Date'].astype(str) + df['Time'].astype(str).str.pad(4, fillchar='0')
    print(df['CombinedDT'].head()) 
    df['Datetime'] = pd.to_datetime(df['CombinedDT'], format='%Y/%m/%d%H:%M:%S', errors='coerce')
    df.set_index('Datetime', inplace=True)
    df.drop(columns=['CombinedDT'], inplace=True, errors='ignore')
    return df
    
def extract_single_year_remove_mean(year, data):
   

    return 


def extract_section_remove_mean(start, end, data):


    return 


def join_data(data1, data2):

    return 



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
    


