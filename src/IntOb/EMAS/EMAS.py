
from random import choice
from itertools import ifilter
from ..utils import dominates, randVector
from ..genetics import Specimen, mutation, crossover
from .Agent import Agent

names = [
    'Adam', 'Bartek', 'Ania', 'Pawel', 'Kasia', 'Andrzej', 'Alicja',
    'Michal', 'Zbigniew', 'Mateusz', 'Marcin', 'Filip', 'Felicja',
    'Tomek', 'Piotr', 'Paulina', 'Dariusz'
]


def pick_name():
    return choice(names)


class Island(object):

    def __init__(self, energy):
        self.neighbours = {}
        self.inhabitants = set()
        self.energy = energy

    def add_neighbour(self, island, cost):
        self.neighbours[island] = cost

    def add_agent(self, a):
        self.inhabitants.add(a)

    def remove_agent(self, a):
        self.inhabitants.remove(a)


class Env(object):

    def __init__(self, island, emas):
        self.island = island
        self.emas = emas

    def find_encounters(self, agent):
        enemies = list(self.island.inhabitants)
        enemies.remove(agent)
        return enemies

    def find_mates(self, agent):
        mates = []
        for a in self.island.inhabitants:
            if a is not agent and a.can_reproduce():
                mates.append(a)
        return mates

    def neighbour_islands(self):
        return self.island.neighbours

    def accept_energy(self, energy):
        self.island.energy += energy

    def reproduce(self, p1, p2):
        c1, c2 = crossover(p1, p2)

        c1 = self.mutate(c1)
        c2 = self.mutate(c2)

        v1 = self.emas.f(c1.x)
        v2 = self.emas.f(c2.x)

        a1 = Agent(c1.x, v1, 0, self)
        a2 = Agent(c2.x, v2, 0, self)

        e = self.emas.params['init_energy']
        p1.transfer_energy(a1, e)
        p2.transfer_energy(a2, e)

        a1.name = pick_name()
        a2.name = pick_name()

        self.island.add_agent(a1)
        self.island.add_agent(a2)

    def mutate(self, a):
        p = self.emas.params['mutation_probability']
        return mutation(a, p, self.emas.bounds, self.emas.max_changes)

    def winner(self, a, b):
        if dominates(b.val, a.val):
            return b
        elif dominates(a.val, b.val):
            return a
        else:
            return None

    def travel(self, agent, destination):
        e = self.island.neighbours[destination]
        agent.dissipate_energy(e)
        self.island.remove_agent(agent)
        destination.add_agent(agent)
        agent.env = self.emas.envs[destination]

    def died(self, agent):
        agent.dissipate_energy(agent.energy)
        self.island.remove_agent(agent)

    @property
    def fight_transfer(self):
        return self.emas.params['fight_transfer']

    @property
    def travel_threshold(self):
        return self.emas.params['travel_threshold']

    @property
    def reproduction_threshold(self):
        return self.emas.params['reproduction_threshold']

    @property
    def death_threshold(self):
        return self.emas.params['death_threshold']


class EMAS(object):
    params = {
        'world_size' : 4,
        'population_size': 100,
        'init_energy': 0.5,
        'fight_transfer': 0.2,
        'travel_threshold': 0.7,
        'travel_cost': 0.2,
        'reproduction_threshold': 0.8,
        'death_threshold': 0.1,
        'mutation_probability': 0.2,
    }

    def __init__(self, fs, bounds, ranges, **params):
        self.f = lambda x: tuple(f(x) for f in fs)
        self.bounds = bounds
        self.ranges = ranges
        self.params = dict(EMAS.params, **params)
        s = 0.1
        self.max_changes = [s * (M - m) for m, M in bounds]
        self.world = []
        self.envs = {}

    def create_world(self):
        """ Creates fully connected island graph.
        """
        size = self.params['world_size']
        cost = self.params['travel_cost']

        self.world = [Island(0) for _ in xrange(size)]

        for a in self.world:
            for b in self.world:
                if a is not b:
                    a.add_neighbour(b, cost)

    def populate_world(self):
        """ Fills the islands with population_size randomly chosen individuals.
        """
        N = self.params['population_size']
        energy = self.params['init_energy']

        for island in self.world:
            env = Env(island, self)
            self.envs[island] = env
            for _ in xrange(N):
                x = randVector(self.bounds)
                val = self.f(x)
                agent = Agent(x, val, energy, env)
                island.add_agent(agent)
                agent.name = pick_name()

    def agents(self):
        agents = []
        for island in self.world:
            for agent in island.inhabitants:
                agents.append(agent)
        return agents

    def optimize(self, steps, callback=None):
        self.create_world()
        self.populate_world()

        for step in xrange(steps):
            for agent in self.agents():
                agent.step()
            if callback:
                callback(step, self.agents())

        return self.agents()

