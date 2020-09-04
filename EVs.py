# -*- coding: utf-8 -*-
"""
Created on Thu Jul 23 15:22:03 2020

@author: Jordan Sausen

Electric Vehicle model

"""
from pyomo.environ import *
#from PL import C
#from data import *
from pyomo.environ import SimpleBlock


class EV(SimpleBlock):
    """
    This class defines variables and parameters for Electric Vehicles (EVs),
    whereas specific characteristic of each EV is defined by dictionary data 
    on data file (data.py).
    
    Battery limitations, degradation costs as well as variables calculation
    for optimization are all described by Constraints.
    """
       
    def __init__(self, *args, **kwds):
        
        super().__init__(*args, **kwds)

        self.time = Set()
        self.ev   = Set()
        
        self.Bcap   = Param(self.ev,            doc='Battery capacity',             mutable=True)
        self.Pmax   = Param(self.ev,            doc='Maximum charging power',       mutable=True)
        self.SoCi   = Param(self.ev,            doc='Initial State of Charge (SoC)',mutable=True)
        self.SoCf   = Param(self.ev,            doc='Final State of Charge (SoC)',  mutable=True)
        self.arr    = Param(self.ev,            doc='Arrival time',                 mutable=True)
        self.dep    = Param(self.ev,            doc='Departure time',               mutable=True)
        self.ef     = Param(                    doc='Charging efficiency',          mutable=True)
        self.Ts     = Param(                    doc='Time sample',                  mutable=True)
            
        self.a      = Var(self.ev, self.time,   doc='Connection status',            initialize=0, within=Binary)      
        self.SoC    = Var(self.ev, self.time,   doc='SoC at each time step',        initialize=0)           
        self.Cdeg   = Var(self.ev, self.time,   doc='Degradation cost',             initialize=0)              
        self.roC    = Var(self.ev, self.time,   doc='Charging priority index',      initialize=0)                  
        self.yC     = Var(self.ev, self.time,   doc='Degradation cost index',       initialize=0)                 
        self.C      = Var(self.ev, self.time,   doc='Charging rate',                initialize=0) # From objective function! C is my decision variable.

#--------------Cálculo do Custo de Degradação máximo----------------#        # VE "n"
        def _Cdeg_max(m, n):
            m.Cdeg_max[n] = ((-(0.05*m.Pmax[n]**2)/(0.795*m.Bcap[n]))*\
            (((1-0.98-((m.Pmax[n]/m.Bcap[n])*m.Ts))**0.795)-((1-0.98)**0.795)) for n in m.ev)

    #---------------Cálculo do Custo de Degradação mínimo---------------#
        def _Cdeg_min(m, n):
            m.Cdeg_min[n] = ((-(0.05*m.Pmax[n]**2)/(0.795*m.Bcap[n]))*\
            (((1-0-((m.Pmax[n]/m.Bcap[n])*m.Ts))**0.795)-((1-0)**0.795)) for n in m.ev)

    #---------------Cálculo do Custo de Degradação inicial--------------#
        def _Cdegi(m, n):
            m.Cdegi[n] = ((-(0.05*m.Pmax[n]**2)/(0.795*m.Bcap[n]))*\
            (((1-m.SoCi[n]-((m.Pmax[n]/m.Bcap[n])*m.Ts))**0.795)-\
                 ((1-m.SoCi[n])**0.795)) for n in m.ev)

    #----------Parâmetro binário: status de conexão do VE "n"------------#
        def alpha(m, n, t):
            if (t >= m.arr.value[n] and m.dep.value[n] >= t for n in m.ev for t in m.time):
                return (m.a[n,t] == True for n in m.ev for t in m.time)
            else:
                return (m.a[n,t] == False for n in m.ev for t in m.time)
            return Constraint.Skip

    #----------------Restrição de taxa de carregamento-------------------#
        def _C(m, n, t):
            return (m.C[n,t] <= m.a[n,t] for n in m.ev for t in m.time)

    #------------------Limite de potência VE-----------------------------#
        def _Pmax_EV (m, n, t):
            return (m.C[n,t]*m.Pmax[n] <= m.Pmax[n] for n in m.ev for t in m.time)
                # OBS m.C[n,t] is from optimization (charging rate = decision variable)

    #----------------------Cálculo do SoC do VE "n"----------------------#
        def _SoC(m, n, t):
            if (t == m.arr.value[n] for n in m.ev for t in m.time):
                return (m.SoC[n,t] == m.SoCi[n] for n in m.ev for t in m.time)
            elif m.a[n,t] is True:
                return (m.SoC[n,t] == ((m.SoC[n,t-1] + m.ef*m.Pmax[n]*m.C[n,t]\
                                        *m.Ta))/m.Bcap[n] for n in m.ev for t in m.time)
                    # OBS m.C[n,t] is from optimization
            else:
                return Constraint.Skip

    #------------------------SoC máximo----------------------------------#
        def _SoC_max (m, n, t):
            return (m.SoC[n,t] <= 1.0 for n in m.ev for t in m.time)

    #------------------------SoC mínimo----------------------------------#
        def _SoC_min (m, n, t):
            return (m.SoC[n,t] >= 0.0 for n in m.ev for t in m.time)

    #------------------SoC desejado na partida---------------------------#
        def _SoC_dep (m, n, t):
            if (m.dep.value[n] == t for n in m.ev for t in m.time):
                return (m.SoC[n,t-1] + sum(((m.ef*m.Pmax[n]*m.C[n, t-1]*m.Ts)\
                    /(m.Bcap[n])) for n in m.ev for t in m.time)) >= m.SoCf[n]
                    # OBS m.C[n,t-1] is from optimization

    #--------------Cálculo do custo de degradação do VE "n"--------------#
        def _Cdeg(m, n, t):
            if (t == m.arr.value[n] for n in m.ev for t in m.time):
                return (m.Cdeg[n,t] == m.Cdegi[n] for n in m.ev for t in m.time)
            elif (m.a[n,t] is True for n in m.ev for t in m.time):
                return m.Cdeg[n,t] == ((-(0.05*(m.Pmax[n]*m.C[n,t])**2)/(0.795\
                                         *m.Bcap[n]))*(((1-m.SoC[n,t]-((m.Pmax[n]/m.Bcap[n])\
                                   *m.Ts))**0.795)-((1-m.SoC[n])**0.795)) for n in m.ev for t in m.time)
                        # OBS m.C[n,t-1] is from optimization
            else:
                return Constraint.Skip

    #--------------------------------------------------------------------#
    #                   Índices para otimização                          #
    #--------------------------------------------------------------------#
    #------------------Cálculo do índice de preferência------------------#
        def _roC(m, n, t):
            if (m.a[n,t] is True for n in m.ev for t in m.time):
                return m.roC == ((m.Bcap[n]*(m.SoCf[n]-m.SoC[n,t]))/(m.Pmax[n]*\
                                    (m.dep[n]-t)*m.Ts) for n in m.ev for t in m.time)
            else:
                return Constraint.Skip

    #------------------Cálculo do índice de degradação------------------#
        def _yC(m, n, t):
            if (m.a[n,t] is True for n in m.ev for t in m.time):
                return m.yC[n,t] == (((m.Cdeg_max[n]-m.Cdeg[n,t])\
                               /(m.Cdeg_max[n]-m.Cdeg_min[n])) for n in m.ev for t in m.time)
            else:
                return Constraint.Skip


        self.Cdeg_min = Constraint(self.ev,             rule=_Cdeg_min, doc='Minimum degradation cost')
        self.Cdeg_max = Constraint(self.ev,             rule=_Cdeg_max, doc='Maximum degradation cost')
        self.Cdegi    = Constraint(self.ev,             rule=_Cdegi,    doc='Initial degradation cost')
        self.a        = Constraint(self.ev, self.time,  rule=alpha,     doc='Connection status (binary)')
        self.C        = Constraint(self.ev, self.time,  rule=_C,        doc='Charging rate constraint')
        self.Pmax_EV  = Constraint(self.ev, self.time,  rule=_Pmax_EV,  doc='Maximum EV power')
        self.SoC      = Constraint(self.ev, self.time,  rule=_SoC,      doc='State of Charge (SoC)')
        self.SoC_max  = Constraint(self.ev, self.time,  rule=_SoC_max,  doc='Maximum SoC')
        self.SoC_min  = Constraint(self.ev, self.time,  rule=_SoC_min,  doc='Minimum SoC')
        self.SoC_dep  = Constraint(self.ev, self.time,  rule=_SoC_dep,  doc='Departure time SoC')
        self.Cdeg     = Constraint(self.ev, self.time,  rule=_Cdeg,     doc='Degradation cost')
        self.yC       = Constraint(self.ev, self.time,  rule=_yC,       doc='Degradation cost index')
        self.roC      = Constraint(self.ev, self.time,  rule=_roC,      doc='Charging preference index')
            

            
            
           
            
            
            
            
            

                
