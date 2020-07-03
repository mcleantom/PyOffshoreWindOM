# -*- coding: utf-8 -*-
"""
Created on Fri Jul  3 11:34:37 2020

@author: Rastko
"""

import numpy as np
import simpy
import random
import pandas as pd
import plotly.express as px
from plotly.offline import download_plotlyjs, init_notebook_mode,  plot
import plotly.io as pio

SIM_TIME=24*7

class simulation(object):
    """
    """
    def __init__(self, env):
        """
        """
        self.env = env
        self.rm = resource_manager(env)

class resource_manager(object):
    """
    """
    def __init__(self, env):
        """
        """
        self.env = env
        self.new_day_clock = env.process(self.new_day_trigger())

    def new_day_trigger(self):
            while True:
                yield env.timeout(24)
                self.schedule_maintenance()

    def schedule_maintenance(self):
        print("New day at " + str(env.now))


env = simpy.rt.RealtimeEnvironment(factor=0.1)
sim = simulation(env)
env.run(until=SIM_TIME)
        