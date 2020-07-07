# -*- coding: utf-8 -*-
"""
Created on Fri Jul  3 15:36:24 2020

@author: Rastko
"""

import numpy as np
from numpy.random import exponential
import simpy
import random
#from scipy.stats import expon
import pandas as pd
import plotly.express as px
from plotly.offline import download_plotlyjs, init_notebook_mode,  plot
import plotly.io as pio

pio.renderers.default='svg'
#pio.renderers.default='browser'

YEARS = 1000
WEEKS = 52
SIM_TIME = YEARS*WEEKS*7*24
FAILURES = pd.DataFrame([["Manual reset", 1272, 3],
                         ["Minor repair", 2120, 7.5],
                         ["Major repair", 21200, 22],
                         ["Major replacement", 57818.2, 34]],
                        columns=["Failure Type", "MTBF", "LenOfRepair"])

failure_timeline = pd.DataFrame()


def time_to_next_fail(mtbf):
    """
    Calculates the time to the next failure by generating a random number and
    taking the inverse of an exponential distribution to generate a time. The
    exponential distribution is good for the constant failure rate section of
    a bath-tub failure curve.

    Inputs:
        mtbf    -   The mean time between failures
    """
    exp_lambda= 1/mtbf
    return exponential(1/exp_lambda, 10000)
#    return np.log(np.random.rand())*(-1*mtbf)


def generate_failures(mtbf, sim_length):
    """
    The process will generate failures where the total length of time between
    failures is equal to the simulation length.

    Inputs:
        mtbf        -   The mean time between failures
        sim_length  -   When to generate failures until
    """
    time = np.array([])
    while sum(time) < sim_length:
        time = np.append(time, time_to_next_fail(mtbf))
    df = pd.DataFrame(time)
    df.columns = ["Time"]
    return df["Time"]


def generate_turbine_failures(failures):
    """
    For each failure in the failure table for a given wind turbine, generate
    the timetable for when the failures will occur.

    Inputs:
        failures    -   A pandas dataframe of failures
    """
    df = pd.DataFrame()
    for i, x in enumerate(failures['Failure Type']):
        df[x] = generate_failures(failures.iloc[i, 1], SIM_TIME)
        print(df[x].describe())
        fig = px.histogram(df, x=x,  histnorm='probability density')
        fig.show()
        df[x] = df[x].cumsum()

    df = pd.melt(df)
    df = df.dropna()
    df.columns = ["Type", "Time"]
    df = df.sort_values(by=['Time'])
    return df


failure_timeline = generate_turbine_failures(FAILURES)
#print(failure_timeline)