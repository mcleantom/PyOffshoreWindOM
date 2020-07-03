import numpy as np
import simpy
import random
import pandas as pd
import plotly.express as px
from plotly.offline import download_plotlyjs, init_notebook_mode,  plot
import plotly.io as pio
import plotly.graph_objects as go
import matplotlib.pyplot as plt

pio.renderers.default = 'svg'

RANDOM_SEED = 42
YEARS = 10
WEEKS = 52
SIM_TIME = YEARS*WEEKS*7*24
NUM_TURBINES = 100
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
        self.fixed = env.event()
        self.time_to_fail = 0
        self.failure_type = ""
        self.len_of_repair = 0
        self.broken=False

    def working(self, resource_manager):
        while True:
            try:
                # Create a failure
                start = env.now
                self.failure_type, self.time_to_fail, self.len_of_repair = self.break_machine()

                # Wait until that failure occurs
                yield self.env.timeout(self.time_to_fail)

                self.num_failures += 1

                broken = env.process(self.broken_machine(env, resource_manager))
                # Wait until the failure is fixed
                yield broken
                finish = env.now
                self.power += finish-start

            except simpy.Interrupt:
                print("Interrupted")

    def broken_machine(self, env, resource_manager):
        """
        """
        self.fixed.succeed()
        resource_manager.request_resource(self, self.failure_type, self.len_of_repair)
        yield self.fixed
        self.fixed = env.event()

    def break_machine(self):
        failure_choice = np.random.choice(len(FAILURES))
        FAILURES.loc[failure_choice, 3] += 1
        return (FAILURES[0][failure_choice],
                FAILURES[1][failure_choice],
                FAILURES[2][failure_choice])


class resource_manager(object):
    """
    Manages the fleet of vessels
    """

    def __init__(self, env, name, CTVs):
        """
        """
        self.env = env
        self.CTVs = CTVs
        self.failure_list = pd.DataFrame()
        self.failure_id = 0
            

    def request_resource(self, turbine, failure_type, len_of_repair):
        """
        A wind turbine has requested a vessel to fix a failure. This will
        either allocate a vessel to the turbine or let it know to wait for a
        period before it will try to allocate a vessel again.
        """
        self.failure_list = self.failure_list.append([[turbine.name,
                                                       failure_type,
                                                       "unrepaired",
                                                       len_of_repair,
                                                       env.now,
                                                       np.nan,
                                                       "corrective",
                                                       1,
                                                       1,
                                                       0,
                                                       self.failure_id]], ignore_index=True)

        self.waiting_failure(env, self.failure_id)
        self.failure_id += 1

    def waiting_failure(self, env, f_id):
        turbine_id = self.failure_list.iloc[f_id, 0]
        len_of_repair = self.failure_list.iloc[f_id, 3]
        CTV = CTVs[0]
        with CTV.request(priority=1) as req:
            yield req
            yield env.timeout(len_of_repair)
            turbines[turbine_id].fixed = env.event()
            finish_time = env.now
            self.failure_list.iloc[f_id, 5] = finish_time
            self.failure_list.iloc[f_id, 3] = 0


print('Wind Site')
#random.seed(RANDOM_SEED)
#np.random.seed(RANDOM_SEED)
env = simpy.Environment()
CTVs = [simpy.PreemptiveResource(env, capacity=1)]
resource_manager = resource_manager(env, "rm1", CTVs)
turbines = pd.DataFrame([turbine(env, i, resource_manager) for i in range(NUM_TURBINES)])
env.run(until=SIM_TIME)

#resource_manager.failure_list.columns = ["Turbine", "Failure", "Status", "Time to repaired", "Start", "Finish", "Type", "CTV", "SOV", "Helicopter"]
turbine_data = pd.DataFrame([])
turbine_data["Uptime"] = [(turbines.iloc[i,0].power/SIM_TIME)*100 for i in range(NUM_TURBINES)]
turbine_data["Failures"] = [turbines.iloc[i,0].num_failures for i in range(NUM_TURBINES)]
fig1 = px.histogram(turbine_data, x="Uptime", nbins=100)
fig1.show()
fig2 = px.histogram(turbine_data, x="Failures")
fig2.show()
#fig3 = px.histogram(resource_manager.failure_list, x="Time to repaired")
#fig3.show()
fig4 = go.Figure(data=go.Scatter(x=resource_manager.failure_list[4]/(24*7*52), y=resource_manager.failure_list[10]))
fig4.show()
