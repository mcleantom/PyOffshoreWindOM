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
        self.time_to_fail = 0
        self.failure_type = ""
        self.len_of_repair = 0
        self.broken=False
        
    def working(self, resource_manager):
        while True:
            try:
#                print(str(self.name) + " Is Fixed at " + str(env.now))
                # Create a failure
                start = self.env.now
                self.failure_type, self.time_to_fail, self.len_of_repair = self.break_machine()
                
                # Skip to when that failure occurs
                yield self.env.timeout(self.time_to_fail)
#                print(str(self.name) + " Is Broken at " + str(env.now))
                #That failure has now occured
                finish = self.env.now
                self.power += finish-start
                self.num_failures += 1
                
                broken = env.process(self.broken_machine(env, resource_manager))
                yield broken
                
            except simpy.Interrupt:
                print("Interrupted")
    
    def broken_machine(self, env, resource_manager):
        """
        """
        self.waiting = resource_manager.request_resource(self)
        yield self.waiting
        
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
        self.failure_list = pd.DataFrame([])
        
    def request_resource(self, turbine):
        """
        A wind turbine has requested a vessel to fix a failure. This will either
        allocate a vessel to the turbine or let it know to wait for a period
        before it will try to allocate a vessel again.
        """
#        print("Resource requested")
        return env.process(self.waiting_failure(env))
    
    def waiting_failure(self, env):
        CTV = CTVs[0]
        with CTV.request(priority=1) as req:
            yield req
            yield env.timeout(10000)
        

print('Wind Site')
random.seed(RANDOM_SEED)
env = simpy.Environment()
CTVs = [simpy.PreemptiveResource(env, capacity=1000)]
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