# -*- coding: utf-8 -*-
"""
Created on Mon Jul  6 10:53:48 2020

@author: Tom McLean
"""

import numpy as np
import simpy
import random
import pandas as pd
import plotly.express as px
from plotly.offline import download_plotlyjs, init_notebook_mode,  plot
import plotly.io as pio
pio.renderers.default='svg'
import plotly.graph_objects as go
import matplotlib.pyplot as plt
from plotly.figure_factory import create_gantt
from itertools import permutations


class simulation_manager(object):
    """

    """

    def __init__(self, nCTVs, nSOVs, nHelis):
        """
        Initialise a simulation.

        Inputs:
            nCTVs   -   Number of CTVs
            nSOVs   -   Number of SOVs
            nHelis  -   Number of helicopters
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
        Initialise the schedule manager and create the vessels in the
        simulation

        Inputs:
            nCTVs   -   The number of CTVs
            nSOVs   -   The number of SOVs
            nHelis  -   The number of helicopters
        """
        self.nCTVs = nCTVs
        self.nSOVs = nSOVs
        self.nHelis = nHelis
        self.nVehicles = nCTVs + nSOVs + nHelis
        self.CTVs = [CTV(i) for i in range(nCTVs)]
        self.SOVs = [SOV(i) for i in range(nSOVs)]
        self.Helis = [Heli(i) for i in range(nHelis)]
        vessels = [self.CTVs, self.SOVs, self.Helis]

        # Create a dataframe which holds the locations of all of the vessels
        self.vessels_df = pd.DataFrame([], columns=["Vessel", "Type", "ID", "Schedule"])
        
        # Add the data about the vessles to the dataframe which holds all the
        # vessels
        for i in range(len(vessels)): # For each vessel type
            for j in range(len(vessels[i])): # For each vessel of that type
                # Add the vessels details
                new_row = {'Vessel': vessels[i][j],
                           'Type': vessels[i][j].type,
                           'ID': vessels[i][j].ID,
                           'Schedule': [pd.DataFrame([["Waiting at Harbour",
                                                       "0",
                                                       "24",
                                                       "Waiting",
                                                       "Port"]],
                                                     columns=["Task",
                                                              "Start",
                                                              "Finish",
                                                              "Resource",
                                                              "Position"])]}
                self.vessels_df = self.vessels_df.append(new_row, ignore_index=True)

# =============================================================================
#       FOR TESTING ONLY, INPUT SOME EXMAPLE FAILURES AND SCHEDULE MAINTENANCE
#       TO SEE THE OUTPUT SCHEDULE.
# =============================================================================
        self.failures = pd.read_csv('failures.csv')
        self.schedule_maintenance()

    def schedule_maintenance(self):
        """
        When there is a new failure, or it is the start of a new working day,
        the maintenance has to be scheduled.
        """
        unrepaied_failures = self.failures[self.failures["Status"] != "repaired"]
        unrepaired_corrective_failures = unrepaied_failures[unrepaied_failures["Type"] == "corrective"]

        vessels_at_sea = self.find_vessels_at_sea(10)

    def find_vessels_at_sea(self, time):
        print(time)


class CTV(object):
    """
    """

    def __init__(self, ID):
        """
        """
        self.max_crew = 12
        self.ID = ID
        self.type = "CTV"

    def start_time(self):
        return 6

    def finish_time(self):
        return 20

    def say_hello(self):
        print("Hello")


class SOV(object):
    """
    """

    def __init__(self, ID):
        """
        """
        self.max_crew = 21
        self.ID = ID
        self.type = "SOV"
    
    def start_time(self):
        return 3
    
    def finish_time(self):
        return 21


class Heli(object):
    """
    """

    def __init__(self, ID):
        """
        """
        self.max_crew = 3
        self.ID = ID
        self.type = "Heli"


simulation = simulation_manager(10, 10, 2)
