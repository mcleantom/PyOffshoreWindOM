# -*- coding: utf-8 -*-
"""
Created on Wed Jul  8 12:38:42 2020

@author: Rastko
"""

import pandas as pd


def add_event(task, start, finish, crew_on_board, resource, position):
        """
        """
        new_row = {"Task": task,
                   "Start": start,
                   "Finish": finish,
                   "Crew on board": crew_on_board,
                   "Resource": resource,
                   "Position": position}
        return new_row


vessels_df = pd.DataFrame([], columns=["Vessel", "Type", "ID", "Schedule"])
schedule = pd.DataFrame(columns=["Task",
                                 "Start",
                                 "Finish",
                                 "Crew on board",
                                 "Resource",
                                 "Position"])

new_row = add_event("Harbour", 0, 6, 12, "Waiting", "Harbour")
schedule = schedule.append(new_row, ignore_index=True)
new_row = add_event("Harbour", 6, 8, 9, "Waiting", "Harbour")
schedule = schedule.append(new_row, ignore_index=True)
new_row = add_event("Harbour", 8, 14, 6, "Waiting", "Harbour")
schedule = schedule.append(new_row, ignore_index=True)
new_row = add_event("Harbour", 14, 16, 3, "Waiting", "Harbour")
schedule = schedule.append(new_row, ignore_index=True)


new_row = {"Vessel": "CTV1",
           "Type": "CTV", 
           "ID": 1,
           "Schedule": schedule}
vessels_df = vessels_df.append(new_row, ignore_index=True)