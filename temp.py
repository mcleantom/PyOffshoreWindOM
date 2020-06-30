import numpy as np
import simpy
import random
import pandas as pd
from plotly.offline import download_plotlyjs, init_notebook_mode,  plot
import plotly.io as pio

pio.renderers.default='svg'

RANDOM_SEED = 42
WEEKS = 52*3
SIM_TIME = WEEKS*7*24
NUM_TURBINES = 100
REPAIR_TIME = 1*24
TIME_TO_FAILURE = 7

def time_to_failure():
    return np.random.choice([0.1, 0.1, 0.1], p=[0.5, 0.3, 0.2])

def repair_time():
    return np.random.choice([2000, 2400, 5000], p=[0.5, 0.3, 0.2])

class turbine(object):
    """
    A turbine produces electrictiy when not broken, and stops when there is a
    failure
    """
    
    def __init__(self, env, name):
        self.env = env
        self.name = name
#        print("Created Turbine " + str(name))
        self.power = 0
        self.num_failures = 0
        self.failure = "none"
        self.process = env.process(self.working())
#        env.process(self.break_machine())
        
    def working(self):
        while True:
            try:
                start = self.env.now
                next_failure = self.break_machine()
                yield self.env.timeout(time_to_failure())
                self.num_failures += 1
                yield self.env.timeout(repair_time())
                finish = self.env.now
                self.power += finish-start

            except simpy.Interrupt:
                pass
#                self.broken = True
#                yield self.env.timeout(repair_time())
    
    def break_machine(self):
        failure = np.random.choice([["minor"], ])
                    
print('Wind Site')
#random.seed(RANDOM_SEED)
env = simpy.Environment()
turbines = [turbine(env, 'Turbine %d' % i) for i in range(NUM_TURBINES)]
env.run(until=SIM_TIME)

turbine_data = pd.DataFrame([])
turbine_data["Avaliability"] = [(turbines[i].power/SIM_TIME)*100 for i in range(NUM_TURBINES)]
turbine_data["Failures"] = [turbines[i].num_failures for i in range(NUM_TURBINES)]
fig1 = px.histogram(turbine_data, x="Avaliability")
fig1.show()
fig2 = px.histogram(turbine_data, x="Failures")
fig2.show()