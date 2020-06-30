import numpy as np
import simpy
import random
import pandas as pd
import plotly.express as px
from plotly.offline import download_plotlyjs, init_notebook_mode,  plot
import plotly.io as pio

pio.renderers.default='svg'

RANDOM_SEED = 42
YEARS = 25
WEEKS = 52
SIM_TIME = YEARS*WEEKS*7*24
NUM_TURBINES = 1000
REPAIR_TIME = 1*24
TIME_TO_FAILURE = 1*7*24
FAILURES = pd.DataFrame([["Manual reset", 1272, 3, 0],
                         ["Minor repair", 2120, 7.5, 0],
                         ["Major repair", 21200, 22, 0],
                         ["Major replacement", 57818.2, 34, 0]])

class turbine(object):
    """
    A turbine produces electrictiy when not broken, and stops when there is a
    failure
    """
    
    def __init__(self, env, name, resource_manager):
        self.env = env
        self.name = name
        self.power = 0
        self.num_failures = 0
        self.failure = "none"
        self.process = env.process(self.working(resource_manager))
        
    def working(self, resource_manager):
        while True:
            try:
                start = self.env.now
                
                # Create a failure
                failure_type, time_to_fail, len_of_repair = self.break_machine()
                
                # Stop when that failure occurs
                yield self.env.timeout(time_to_fail)
                finish = self.env.now
                
                # Calculate the length of time that the turbine was on for
                # before it broke, and add to the total.
                self.power += finish-start
                
                # Keep a tally of the number of failures that the wind turbine
                # has had
                self.num_failures += 1
                
                # Request a resource from the fleet of vessels
                CTV = resource_manager.request_resource(self)
                
                with CTV.request(priority=1) as req:
                    yield req
                    yield self.env.timeout(len_of_repair)

            except simpy.Interrupt:
                print("Interrupted")

#                pass
#                self.broken = True
#                yield self.env.timeout(repair_time())
    
    def break_machine(self):
        failure_choice = np.random.choice(len(FAILURES))
        FAILURES.loc[failure_choice, 3] += 1
        return FAILURES[0][failure_choice], FAILURES[1][failure_choice], FAILURES[2][failure_choice]
    
                    
class resource_manager(object):
    """
    Manages the fleet of vessels
    """
    
    def __init__(self, env, name, CTVs):
        """
        """
        self.CTVs = CTVs
        
    def request_resource(self, turbine):
        """
        A wind turbine has requested a vessel to fix a failure. This will either
        allocate a vessel to the turbine or let it know to wait for a period
        before it will try to allocate a vessel again.
        """
        return self.CTVs[0]
        

print('Wind Site')
#random.seed(RANDOM_SEED)
env = simpy.Environment()
CTVs = [simpy.PreemptiveResource(env, capacity=1)]
resource_manager = resource_manager(env, "rm1", CTVs)
turbines = [turbine(env, 'Turbine %d' % i, resource_manager) for i in range(NUM_TURBINES)]
env.run(until=SIM_TIME)

turbine_data = pd.DataFrame([])
turbine_data["Uptime"] = [(turbines[i].power/SIM_TIME)*100 for i in range(NUM_TURBINES)]
turbine_data["Failures"] = [turbines[i].num_failures for i in range(NUM_TURBINES)]
fig1 = px.histogram(turbine_data, x="Uptime", nbins=100)
fig1.show()
fig2 = px.histogram(turbine_data, x="Failures", nbins=50)
fig2.show()