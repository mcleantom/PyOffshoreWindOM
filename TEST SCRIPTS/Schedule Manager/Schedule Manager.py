# -*- coding: utf-8 -*-
"""
Created on Mon Jul  6 10:53:48 2020

@author: Tom McLean
"""

import numpy as np
import simpy
import random
import datetime
import pandas as pd
import plotly.express as px
from plotly.offline import download_plotlyjs, init_notebook_mode,  plot
import plotly.io as pio
pio.renderers.default = 'iframe'
import plotly.graph_objects as go
import plotly.figure_factory as ff
import matplotlib.pyplot as plt
from plotly.figure_factory import create_gantt
from itertools import permutations
    
START_DATE = datetime.datetime(2020, 1, 1, 0, 0, 0, 0)

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
        self.CTVs = [CTV(i) for i in range(nCTVs)]
        self.SOVs = [SOV(i+len(self.CTVs)) for i in range(nSOVs)]
        self.Helis = [Heli(i+len(self.CTVs)+len(self.SOVs)) for i in range(nHelis)]
        vessels = [self.CTVs, self.SOVs, self.Helis]
        self.schedule_manager = schedule_manager(vessels)


class schedule_manager(object):
    """
    """

    def __init__(self, vessels):
        """
        Initialise the schedule manager and create the vessels in the
        simulation

        Inputs:
            nCTVs       -   The number of CTVs
            nSOVs       -   The number of SOVs
            nHelis      -   The number of helicopters

        Attributes:
            CTVs        -   A list of the CTVs
            SOVs        -   A list of the SOVs
            Helis       -   A list of the helicopters
            vessels_df  -   A dataframe of the fleet
            failures    -   A dataframe of the current and previous failures
        """

        # Create a dataframe which holds the locations of all of the vessels
        self.vessels_df = pd.DataFrame([], columns=["Vessel", "Type", "ID", "Position", "Onboard Crew"])
        
        # Add the data about the vessles to the dataframe which holds all the
        # vessels
        for i in range(len(vessels)): # For each vessel type
            for j in range(len(vessels[i])): # For each vessel of that type
                # Add the vessels details
                new_row = {'Vessel': vessels[i][j],
                           'Type': vessels[i][j].type,
                           'ID': vessels[i][j].ID,
                           'Position': 'Harbour',
                           'Onboard Crew': vessels[i][j].max_crew}

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


    def update_fleet_info(self):
        """
        Updates the current fleet position and onboard crew
        """
        self.vessels_df["Position"] = [x.schedule.current_position for x in self.vessels_df["Vessel"]]

    def find_vessels_at_sea(self):
        """
        Returns a dataframe of  vessels which are currently not in the harbour
        """
        self.update_fleet_info()
        return self.vessels_df[self.vessels_df["Position"] != "Harbour"]

    def fleet_task_at_time(self, time):
        """
        Creates a dataframe of the fleets tasks in the schedule at a given time

        Inputs:
            time    -   Time to find the given tasks

        Outputs:
            df      -   A dataframe of vessels and the task information
        """
        df = pd.DataFrame(columns = ["Vessel",
                                     "ID",
                                     "Task",
                                     "Start",
                                     "Finish",
                                     "Crew on board",
                                     "Resource",
                                     "Position"])
        # For each vessel
        for i, vessel in enumerate(self.vessels_df["Vessel"]):
            # Get the task at the time
            vessel_schedule = vessel.schedule.get_schedule_at_time(time)
            new_row = {'Vessel': vessel,
                       'ID': vessel.ID,
                       'Task': vessel_schedule["Task"],
                       'Start': vessel_schedule["Start"],
                       'Finish': vessel_schedule["Finish"],
                       'Crew on board': vessel_schedule["Crew on board"],
                       'Resource': vessel_schedule["Resource"],
                       'Position': vessel_schedule["Position"]}
            # Add it to the dataframe
            df = df.append(new_row, ignore_index=True)
            
        return df
            
    
    def say_hello(self):
        """
        Print hello.
        """
        print("hello")
    
    def calc_travel_time(self):
        """
        Calculate the travel time between two locations
        """
        return 2


class schedule(object):
    """
    """

    def __init__(self, ID):
        """
        """
        self.ID = ID
        self.schedule_manager = schedule_manager
        self.schedule = pd.DataFrame(columns=["Task",
                                              "Start",
                                              "Finish",
                                              "Crew on board",
                                              "Resource",
                                              "Position"])
        self.current_position = "Harbour"

    def add_event(self, task, start, finish, crew_on_board, resource, position):
        """
        """
        new_row = {"Task": task,
                   "Start": start,
                   "Finish": finish,
                   "Crew on board": crew_on_board,
                   "Resource": resource,
                   "Position": position}
        self.schedule = self.schedule.append(new_row, ignore_index=True)
    
    def get_times_with_required_crew(self, required_crew):
        """
        """
        df = self.schedule[self.schedule["Crew on board"] >= required_crew]
        return df
    
    def plot_gantt_chart(self):
        """
        Plot a gantt chart of the vessels schedule
        """
        df = self.schedule
        df["Start"] = START_DATE + pd.to_timedelta(df["Start"], unit="h")
        df["Finish"] = START_DATE + pd.to_timedelta(df["Finish"],  unit="h")
        fig = ff.create_gantt(self.schedule,
                              colors = ['#333F44', '#93e4c1'],
                              index_col = 'Crew on board',
                              showgrid_x = True,
                              showgrid_y = True,
                              title = "Vessel " + str(self.ID))
        fig.show()
        return df
    
    def get_schedule_at_time(self, time):
        """
        """
        event = self.schedule[self.schedule["Finish"]>=time].iloc[0]
        return event

class CTV(object):
    """
    """

    def __init__(self, ID):
        """
        """
        self.max_crew = 12
        self.ID = ID
        self.type = "CTV"
        self.schedule = schedule(self.ID)
        self.schedule.current_position = "Field"
        self.schedule.add_event("Harbour", 0, 6, self.max_crew, "Waiting", "Harbour")
        self.schedule.add_event("Travel to turbine 1", 6, 8, self.max_crew, "Traveling", "Outbound")
        self.schedule.add_event("Waiting for repair on turbine 1", 8, 14, self.max_crew-3, "Waiting", "Turbine 1")
        self.schedule.add_event("Travel to harbour", 14, 16, self.max_crew, "Traveling", "Inbound")
        self.schedule.add_event("Harbour", 16, 24, self.max_crew, "Waiting", "Harbour")

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
        self.schedule = schedule(self.ID)
        self.schedule.current_position = "Harbour"
        self.schedule.add_event("Harbour", 0, 24, self.max_crew, "Waiting", "Harbour")

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
        self.schedule = schedule(self.ID)
        self.schedule.add_event("Harbour", 0, 24, self.max_crew, "Waiting", "Harbour")


simulation = simulation_manager(4, 3, 2)
