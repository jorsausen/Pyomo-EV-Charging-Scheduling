# -*- coding: utf-8 -*-
"""
Created on Tue Jul 28 10:46:49 2020

@author: Jordan Sausen

PARKING LOT:
Charging scheduling of 5 Electric Vehicles for 24h time horizon. 5 min
resolution totals 288 points in a day.

This modelling is based in two indexed sets: 'time' and 'ev'
'time' = (0,288) -> Time horizon
'ev' = (0,5) -> 5 Electric Vehicles to test the scheduling algorithm
"""

from pyomo.environ import *

m = AbstractModel()
m.time    = Set(initialize=(0, 288))

m.Pc_grid = Var(m.time, within=PositiveReals)

from EVs import EV
m.EV = EV()                 # EV Class

from Tariff import tariff
m.tariff = tariff()         # Tariff Class 

@m.Constraint(m.time)
def transformer(m, t):
    return (Pc_grid[t] <= Pmax_grid for t in m.time)

@m.Constraint(m.time)
def power_balance(m, t):
    return sum((m.EV.C[n,t]*m.EV.Pmax[n] for n in m.EV.ev) == Pc_grid[t] for t in m.time)

def obj_rule (m, n, t):
    return sum(m.EV.C[n,t]*m.EV.Pmax[n]*m.EV.yC[n,t]*m.EV.roC[n,t]*m.tariff.tC[t] for n in m.EV.ev for t in m.time)
m.obj = Objective(rule=obj_rule, sense=maximize)

inst = m.create_instance(data.py)

opt = SolverFactory("clc")                 # See what solver to use
res = opt.solve(inst, load_solutions=True)