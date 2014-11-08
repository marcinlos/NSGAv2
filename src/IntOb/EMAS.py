
from .utils import dominates
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

    def must_die(self):
        return self.energy < self.env.death_threshold

    def step(self):
        """ One full step of agent's lifecycle """
        if self.must_die():
            self.die()
            self.env.died(self)
        else:
            self.act()

    def winner(self, other):
        if dominates(other.val, self.val):
            return other
        elif dominates(self.val, other.val):
            return self
        else:
            return None

    # Methods determining behaviour of agent (strategy, actions)


    def act(self):
        """ Invoked once during every step of lifecycle. Here, agent is free to
        undertake whatever action he feels appropriate.
        """
        pass

    def meet_offer(self, other):
        """ Invoked when some other agent wishes to meet with this one.

        other - agent that makes the offer

        Returns:
            True - offer accepted, False - rejected
        """
        pass

    def reproduction_offer(self, mate):
        """ Invoked when some other agent wishes to reproduce.

        other - agent that makes the offer

        Returns:
            True - offer accepted, False - rejected
        """
        pass

    def reproduce(self):
        pass

    def travel(self):
        pass

    def fight(self, enemy):
        best = winner(self, enemy)
        if self is best:
            pass
        elif enemy is best:
            pass

    def die(self):
        """ Invoked when the agent has died, i.e. when his life energy has
        fallen below the death threshold.
        """
        pass


class Island(object):

    def __init__(self, energy):
        self.neighbours = []
        self.inhabitants = set()
        self.energy = energy

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

    def find_encounters(self):
        # return sample(self.island.inhabitants, 1)
        return self.island.inhabitants

    def find_mates(self):
        pass

    def neighbour_islands(self):
        return self.island.neighbours


    def travel(self, agent, destination):
        e = self.travel_threshold
        agent.energy -= e
        self.island.energy += e
        self.island.remove_agent(agent)
        destination.add_agent(agent)

    def died(self, agent):
        pass

    @property
    def travel_threshold(self):
        return self.params['travel_threshold']

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
        'travel_threshold': 0.7,
        'reproduction_threshold': 0.7,
        'death_threshold': 0.2,
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

