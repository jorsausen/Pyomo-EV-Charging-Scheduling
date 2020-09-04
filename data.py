# -*- coding: utf-8 -*-
"""
Created on Tue Jul 28 11:35:01 2020

@author: Jordan Sausen

Data

"""
import pandas as pd

df_1 = pd.read_csv('time_tff_data.csv', sep=';', usecols=['time', 'tff'], index_col='time', header=0)
df_2 = pd.read_csv('ev_data.csv', sep=';', index_col='ev', header=0)

data_EV = {
    #'time':     {None: df_1['time'].to_dict()},             # Set of time (5 min resolution for 24h = 288 points)
    #'ev':       {None: df_2['ev'].to_dict()},               # Set of EVs (5 Evs for simplification purposes)
    'Bcap':     {'ev': df_2['Bcap'].to_dict()},             # Battery capacity of each EV (kWh)
    'Pmax':     {'ev': df_2['Pmax'].to_dict()},             # Maximum charging power (kW)
    'SoCi':     {'ev': df_2['SoCi'].to_dict()},             # Initial State of Charge (%)
    'SoCf':     {'ev': df_2['SoCf'].to_dict()},             # Final State of Charge (%)
    'arr':      {'ev': df_2['arr'].to_dict()},              # Arrival time of each EV (5 min resolution)
    'dep':      {'ev': df_2['dep'].to_dict()},              # Departure time of each EV (5 min resolution)
    'ef':       {None: 0.95},                               # Charging efficiency (%)
    'Ts':       {None: 0.0833}                              # Time sample (h)
    }
    
data_Tariff = {
    #'time':     {None: df_1['time'].to_dict()},             # Set of time (5 min resolution for 24h)
    'tff':      {'time': df_1['tff'].to_dict()}               # Set of tariff prices
    }                       
    
data_PL = {
    #'time':     {None: df_1['time'].to_dict()},             # Set of time (5 min resolution for 24h)
    #'ev':       {None: df_2['ev'].to_dict()},               # Set of EVs
    'Pmax':     {'ev': df_2['Pmax'].to_dict()},             # Maximum charging power of each EV (kW)
    'Pmax_grid':{None: 11.10},                              # Maximum grid power (7,4 + 3,7 kW = 2 EVs per time) - to simulate limitation of distribution transformer
    }

data = {None: dict( EV      = data_EV,
                    PL      = data_PL,
                    tariff  = data_Tariff)}

df_2