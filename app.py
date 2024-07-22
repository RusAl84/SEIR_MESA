import random
from mesa import Agent, Model
from mesa.time import RandomActivation
from mesa.space import MultiGrid
from mesa.datacollection import DataCollector

class SEIRAgent(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.state = "S"  # Все агенты начинаются в состоянии S (восприимчивые)

    def step(self):
        if self.state == "S":
            self.check_infection()
        elif self.state == "E":
            self.become_infectious()
        elif self.state == "I":
            self.recover()

    def check_infection(self):
        neighbors = self.model.grid.get_neighbors(self.pos, moore=True, include_center=False)
        for neighbor in neighbors:
            if neighbor.state == "I" and random.random() < self.model.infection_prob:
                self.state = "E"
                break

    def become_infectious(self):
        if random.random() < self.model.incubation_period:
            self.state = "I"

    def recover(self):
        if random.random() < self.model.recovery_prob:
            self.state = "R"

class SEIRModel(Model):
    def __init__(self, width, height, population, infection_prob, incubation_period, recovery_prob):
        self.num_agents = population
        self.grid = MultiGrid(width, height, True)
        self.schedule = RandomActivation(self)
        self.infection_prob = infection_prob
        self.incubation_period = incubation_period
        self.recovery_prob = recovery_prob
        self.datacollector = DataCollector(
            agent_reporters={"State": "state"}
        )

        for i in range(self.num_agents):
            a = SEIRAgent(i, self)
            self.schedule.add(a)
            x = self.random.randrange(self.grid.width)
            y = self.random.randrange(self.grid.height)
            self.grid.place_agent(a, (x, y))

    def step(self):
        self.schedule.step()
        self.datacollector.collect(self)

# Параметры модели
width = 10
height = 10
population = 100
infection_prob = 0.05
incubation_period = 0.1
recovery_prob = 0.1

model = SEIRModel(width, height, population, infection_prob, incubation_period, recovery_prob)
for i in range(100):
    model.step()

# Анализ данных
import matplotlib.pyplot as plt
import pandas as pd

data = model.datacollector.get_agent_vars_dataframe()
data['Step'] = data.index.get_level_values(0)
data['State'] = data['State'].apply(lambda x: x.value)

plt.figure(figsize=(10, 6))
for state in ['S', 'E', 'I', 'R']:
    plt.plot(data[data['State'] == state]['Step'], data[data['State'] == state]['State'], label=state)
plt.xlabel('Step')
plt.ylabel('Number of Agents')
plt.legend()
plt.show()
