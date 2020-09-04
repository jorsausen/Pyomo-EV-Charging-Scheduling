# -*- coding: utf-8 -*-
"""
Created on Mon Jul 27 12:06:01 2020

@author: Jordan Sausen

Tariff model

"""
from pyomo.environ import *
#from data import *
#m.time    = Set(initialize=(0,288))
from pyomo.environ import SimpleBlock

class tariff(SimpleBlock):
    """ This class defines parameters and variables related to the Time of Use
    Tariff adopted for optimization.
    
    The tariff priority index calculation is done through Constraint declaration.
    """
    
    
    def __init__(self, *args, **kwds):
        
        super().__init__(*args, **kwds)

        self.time = Set()
        
        self.Tmax   = Param(self.time, doc='Maximum tariff price',  multable=True)
        self.Tmin   = Param(self.time, doc='Minimum tariff price',  multable=True)
        self.tff    = Param(self.time, doc='Set of tariff prices',  mutable=True)
        self.Tc     = Var  (self.time, doc='Tariff priority index', initialize=0)
        
#    for t in time:      # should I use a for loop or no? Since 'time' is a Set (0,288)
        def _Tc(m, t):
            if tff is not None:
                return (m.Tc[t] == (m.Tmax-m.tff[t])/(m.Tmax-m.Tmin) for t in m.time)
            return Constraint.Skip
    
        self.Tc = Constraint(self.time, rule=_Tc, doc='Tariff priority index')
