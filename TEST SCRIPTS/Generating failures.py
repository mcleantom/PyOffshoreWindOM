# -*- coding: utf-8 -*-
"""
Created on Fri Jul  3 15:36:24 2020

@author: Rastko
"""

import numpy as np
import simpy
import random
import pandas as pd

YEARS = 10
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
    return np.log(np.random.rand())*(-1*mtbf)


def generate_failures(mtbf, sim_length):
    """
    The process will generate failures where the total length of time between
    failures is equal to the simulation length.

    Inputs:
        mtbf        -   The mean time between failures
        sim_length  -   When to generate failures until
    """
    df = pd.DataFrame(columns=['Time'])
    while df["Time"].sum() < sim_length:
        new_row = {'Time': time_to_next_fail(mtbf)}
        df = df.append(new_row, ignore_index=True)
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
        df[x] = generate_failures(failures.iloc[i, 1], SIM_TIME).cumsum()

#    df = pd.melt(df)
#    df = df.dropna()
#    df.columns=["Type", "Time"]
#    df = df.sort_values(by=['Time'])
    return df


failure_timeline = generate_turbine_failures(FAILURES)
