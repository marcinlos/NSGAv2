
from .genetics import Specimen
from random import sample



class Agent(object):

    def __init__(self, x, val, energy, env):
        self.env = env
        self.x = x
        self.energy = energy
        self.val = val

    def can_travel(self):
        return self.energy >= self.env.travel_threshold

    def can_reproduce(self):
        return self.energy >= self.env.reproduction_threshold

    def act():
        pass

    def reproduce():
        pass

    def travel():
        pass

    def fight():
        pass


class Island(object):

    def __init__(self):
        self.neighbours = []
        self.inhabitants = set()

    def add_neighbour(self, island):
        self.neighbours.append(island)

    def add_agent(a):
        self.inhabitants.add(a)

    def remove_agent(a):
        self.inhabitants.remove(a)


class Env(object):

    def __init__(self, params, island):
        self.params = params
        self.island = island

    def pick_encounter(self):
        return sample(self.island.inhabitants)[0]

    def neighbour_islands(self):
        return self.island.neighbours

    @property
    def reproduction_threshold(self):
        return self.params['reproduction_threshold']

    @property
    def death_threshold(self):
        return self.params['reproduction_threshold']


class EMAS(object):
    params = {
        'world_size' : 5,
        'population_size': 10,
        'init_energy': 0.5,
    }

    def __init__(self, fs, bounds, ranges, **params):
        self.f = lambda x: tuple(f(x) for f in fs)
        self.bounds = bounds
        self.ranges = ranges
        self.params = dict(EMAS.params, **params)
        self.max_changes = [s * (M - m) for m, M in bounds]
        self.world = []

    def create_world(self):
        """ Creates fully connected island graph.
        """
        size = self.params['world_size']
        self.world = [Island() for _ in xrange(size)]

        for a in self.world:
            for b in self.world:
                if a is not b:
                    a.add_neighbour(b)

    def populate_world(self):
        """ Fills the islands with population_size randomly chosen individuals.
        """
        N = self.params['population_size']
        energy = self.params['init_energy']

        for island in self.world:
            env = Env(self.params, island)
            for _ in xrange(N):
                x = randVector(self.bounds)
                val = self.f(x)
                agent = Agent(x, val, energy, env)
                island.add_agent(agent)

    def agents(self):
        for island in self.world:
            for agent in island.inhabitants:
                yield agent

    def optimize(self, steps, callback=None):
        self.create_world()
        self.populate_world()

        for step in xrange(steps):
            for agent in self.agents():
                agent.step()

