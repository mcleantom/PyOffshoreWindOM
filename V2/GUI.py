# -*- coding: utf-8 -*-
"""
Created on Fri Dec  4 09:39:26 2020

@author: Rastko
"""

import tkinter as tk
from tkinter import filedialog
import pandas as pd
import MII
import ANSYS_tools
import matplotlib.pyplot as plt
from matplotlib import cm
from mpl_toolkits import mplot3d
import numpy as np
import matplotlib.animation as animation
import pandas as pd
import STL_loader
import os.path

root = tk.Tk()
root.withdraw()


def input_float(prompt=""):
    loop = True
    while loop:
        input_str = input(prompt)
        try:
            x = float(input_str)
        except ValueError:
            print("The input was not a float")
        else:
            loop = False
    return x


def input_int(prompt=""):
    loop = True
    while loop:
        input_str = input(prompt)
        try:
            x = int(input_str)
        except ValueError:
            print("The input was not a float")
        else:
            loop = False
    return x


def select_item_in_list(select_list, prompt=""):
    loop = True
    select_list = [x.upper() for x in select_list]
    print("Select:")
    print(select_list)
    while loop:
        input_str = input(prompt).upper()
        if input_str in select_list:
            loop = False
        else:
            print("Value is not in list, try again")
    return input_str


def select_run(turbine_type):
    """
    """
    d = ".\\Data\\platform_data\\"+turbine["Turbine type"]
    folders = list(filter(lambda x: os.path.isdir(os.path.join(d, x)),
                          os.listdir(d)))
    HZ = select_item_in_list(folders, "What is the wave height?")

    d += "\\"+HZ
    folders = list(filter(lambda x: os.path.isdir(os.path.join(d, x)),
                          os.listdir(d)))
    TZ = select_item_in_list(folders, "What is the wave period?")

    d += "\\"+TZ
    folders = list(filter(lambda x: os.path.isdir(os.path.join(d, x)),
                          os.listdir(d)))
    direction = select_item_in_list(folders, "What is the wave direction?")
    
    d += "\\"+direction
    run = HZ+"_"+TZ+"_"+direction+"_"
    CG_file = d+"\\"+run+"CG.csv"
    ROT_file = d+"\\"+run+"ROT.csv"
    print(CG_file)
    print(ROT_file)
    CG = pd.read_csv(CG_file, skiprows=5,encoding = "ISO-8859-1")
    ROT = pd.read_csv(ROT_file, skiprows=5, encoding = "ISO-8859-1")
    df = pd.DataFrame(CG["*Time (s)"], columns=["Time (s)"])
    df["Time"] = CG["*Time (s)"]
    df["X"] = CG["Line A (m)"]
    df["Y"] = CG["Line B (m)"]
    df["Z"] = CG["Line C (m)"]
    df["Rot x"] = ROT.iloc[:,1]
    df["Rot y"] = ROT.iloc[:,2]
    df["Rot z"] = ROT.iloc[:,3]
    return df, HZ, TZ, direction, d, run

# =============================================================================
# READING MOTION DATA
# =============================================================================

TURBINES = pd.read_excel("Turbines.xlsx")
TURBINE_TYPE = select_item_in_list(list(TURBINES["Turbine type"]),
                                   prompt="What is the turbine type?")
turbine = TURBINES[TURBINES["Turbine type"].str.upper() == TURBINE_TYPE].iloc[0]
ACC_POS = turbine[["X", "Y", "Z"]]
print("-- TURBINE --")
print(turbine)

tasks = pd.read_excel("tasks.xlsx")
tasks = tasks[tasks["Turbine type"].str.upper() == TURBINE_TYPE]
print("-- TASKS --")
print(tasks)

points = tasks[["X", "Y", "Z"]]

df, Hz, Tz, direction, folder, run = select_run(turbine["Turbine type"])
tasks["Turbine"] = [turbine["Turbine type"]]*len(tasks)
tasks["Hz"] = [Hz]*len(tasks)
tasks["Tz"] = [Tz]*len(tasks)
tasks["Wave direction"] = [direction]*len(tasks)

SHIP_ROT_Z = input_float("What is the rotation of the ship axis relative to the ANSYS axis?")
SHIP_ROT = [0,0,SHIP_ROT_Z]

PERSON_ROT_Z = input_float("What is the rotation of the person on the boat?")
tasks["Person rotation"] = [PERSON_ROT_Z]*len(tasks)

# =============================================================================
# CALCULATING MSI
# =============================================================================

print("CALCULATIONS FOR MSI")

MSI_accelerometer = ANSYS_tools.ansys_accelerometer(df,
                                                    position=ACC_POS,
                                                    ship_rot=SHIP_ROT,
                                                    person_rot=PERSON_ROT_Z)

XX, YY, ZZ = MII.points(MSI_accelerometer.motion_data["Position"],
                        points["X"],
                        points["Y"],
                        points["Z"])

XX, YY, ZZ = MSI_accelerometer.coordinates_in_person_rf(XX, YY, ZZ)

Ax, Ay, Az, A = MII.translate_accelerations(XX,
                                            YY,
                                            ZZ,
                                            MSI_accelerometer)

MSI = MII.calc_MSI(Az, XX, MSI_accelerometer, tasks["Exposure time"])

Ax_rms, Ay_rms, Az_rms, A_rms = [MII.calc_RMS(x) for x in [Ax, Ay, Az, A]]
Ax_max, Ay_max, Az_max, A_max = [np.max(x, axis=3) for x in [Ax, Ay, Az, A]]
Ax_min, Ay_min, Az_min, A_min = [np.min(x, axis=3) for x in [Ax, Ay, Az, A]]

tasks["MSI"] = MSI.flatten()
tasks["Ax_rms"] = Ax_rms.flatten()
tasks["Ay_rms"] = Ay_rms.flatten()
tasks["Az_rms"] = Az_rms.flatten()
tasks["A_rms"] = A_rms.flatten()

tasks["Ax_max"] = Ax_max.flatten()
tasks["Ay_max"] = Ay_max.flatten()
tasks["Az_max"] = Az_max.flatten()
tasks["A_max"] = A_max.flatten()

tasks["Ax_min"] = Ax_min.flatten()
tasks["Ay_min"] = Ay_min.flatten()
tasks["Az_min"] = Az_min.flatten()
tasks["A_min"] = A_min.flatten()

# =============================================================================
# CALCULATING MII
# =============================================================================

print("CALCULATIONS FOR MII")

side_mii_rate = MII.calc_MII_rate(Ay,
                                  Az,
                                  XX,
                                  MSI_accelerometer,
                                  tasks["Sideways tip coeff"].to_numpy(),
                                  h=tasks["h"].to_numpy())

side_E_task = MII.calc_E_task(side_mii_rate,
                              tasks["Recovery time"].to_numpy())

tasks["Sideways MII Rate"] = side_mii_rate
tasks["Sideways MII Task Eff."] = side_E_task

fore_mii_rate = MII.calc_MII_rate(Ax,
                                  Az,
                                  XX,
                                  MSI_accelerometer,
                                  tasks["Foreward tip coeff"].to_numpy(),
                                  h=tasks["h"].to_numpy())

fore_E_task = MII.calc_E_task(fore_mii_rate,
                              tasks["Recovery time"].to_numpy())

tasks["Foreward MII Rate"] = side_mii_rate
tasks["Foreward MII Task Eff."] = side_E_task

combined_rate = side_mii_rate + fore_mii_rate
combined_E_task = MII.calc_E_task(combined_rate,
                                  tasks["Recovery time"].to_numpy())

tasks["Combined MII rate"] = combined_rate
tasks["Combined MII Task Eff."] = combined_E_task

# =============================================================================
# SAVING RESULTS
# =============================================================================

#d = ".\\Data\\platform_data\\"+turbine["Turbine type"]+"\\results.xlsx"
#results = pd.read_excel(d)
#results = results.append(tasks)
#results.to_excel(d, index=False)
#tasks.to_excel(folder+"\\"+run+"results.xlsx")
