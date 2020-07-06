# -*- coding: utf-8 -*-
"""
Created on Mon Jul  6 10:53:48 2020

@author: Rastko
"""

import numpy as np
import simpy
import random
import pandas as pd
import plotly.express as px
from plotly.offline import download_plotlyjs, init_notebook_mode,  plot
import plotly.io as pio
pio.renderers.default='browser'
import plotly.graph_objects as go
import matplotlib.pyplot as plt
from plotly.figure_factory import create_gantt
from itertools import permutations


class simulation_manager(object):
    """

    """

    def __init__(self, nCTVs, nSOVs, nHelis):
        """

        """
        self.nCTVs = nCTVs
        self.nSOVs = nSOVs
        self.nHelis = nHelis

        self.schedule_manager = schedule_manager(nCTVs, nSOVs, nHelis)


class schedule_manager(object):
    """
    """

    def __init__(self, nCTVs, nSOVs, nHelis):
        """
        """
        self.nCTVs = nCTVs
        self.nSOVs = nSOVs
        self.nHelis = nHelis
        self.nVehicles = nCTVs + nSOVs + nHelis
        self.CTVs = [[CTV()] for i in range(nCTVs)]
        self.SOVs = [[SOV()] for i in range(nSOVs)]
        self.Helis = [[Heli()] for i in range(nHelis)]
        self.failures = pd.read_csv('failures.csv')
        self.schedule_maintenance()

    def schedule_maintenance(self):
        """
        """
        df = self.failures[self.failures["Status"] != "repaired"]
        corrective = df[df["Type"] == "corrective"]
        print(df)
        print(corrective)
        print(self.calc_new_route(corrective, self.CTVs[0]))
    
    def calc_new_route(self, failures, vessel):
        """
        Calculates the cost of a route given a vessel with no existing plan
        """
        print(list((permutations(failures.index))))
    

class CTV(object):
    """
    """

    def __init__(self):
        """
        """
        self.max_crew = 12

    def start_time(self):
        return 6

    def finish_time(self):
        return 20


class SOV(object):
    """
    """

    def __init__(self):
        """
        """
        self.max_crew = 21
    
    def start_time(self):
        return 3
    
    def finish_time(self):
        return 21


class Heli(object):
    """
    """

    def __init__(self):
        """
        """
        self.max_crew = 3


simulation = simulation_manager(10, 10, 2)
