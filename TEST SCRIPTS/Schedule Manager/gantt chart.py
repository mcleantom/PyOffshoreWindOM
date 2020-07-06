# -*- coding: utf-8 -*-
"""
Created on Mon Jul  6 12:18:43 2020

@author: Rastko
"""

import plotly.io as pio

pio.renderers.default='browser'
from plotly.figure_factory import create_gantt

df = [dict(Task="Job A", Start='2009-01-01',
           Finish='2009-02-30', Resource='Apple'),
      dict(Task="Job B", Start='2009-03-05',
           Finish='2009-04-15', Resource='Grape'),
      dict(Task="Job C", Start='2009-02-20',
           Finish='2009-05-30', Resource='Banana')]
      
fig = create_gantt(df, colors=['rgb(200, 50, 25)', (1, 0, 1), '#6c4774'],
                   index_col='Resource', reverse_colors=True,
                   show_colorbar=True)
fig.show()