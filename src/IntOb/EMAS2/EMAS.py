
from ..utils import inverslyDominates, randVector
from ..genetics import crossover, mutation
from ..EMAS.param_sets import param_sets, default_params
from random import choice
from itertools import chain


class Agent(object):

    def __init__(self, x, val, energy, env):
        self.x = x
        self.val = val
        self.energy = energy
        self.env = env

    def accept_meet(self, other):
        return not self.dead

    def accept_reproduction(self, other):
        return self.can_reproduce

    def seek_migration(self):
        if self.env.neighbouring_islands:
            return choice(self.env.neighbouring_islands)

    def seek_meet(self):
        return self.random_peer()

    def seek_partner(self):
        return self.random_peer()

    def random_peer(self):
        peers = self.env.peers
        if len(peers) > 1:
            agent = self
            while agent == self:
                agent = choice(peers)
            return agent

    @property
    def dead(self):
        return self.energy < self.env.death_threshold

    @property
    def can_reproduce(self):
        return self.energy >= self.env.reproduction_threshold

    @property
    def can_travel(self):
        return self.energy >= self.env.travel_threshold

    def wants_to_meet(self):
        return True

    def wants_to_migrate(self):
        return True

    def wants_to_reproduce(self):
        return True

    def step(self):
        if self.dead:
            self.env.die(self)
        else:
            self.env.strategy_migration(self)
            self.env.strategy_reproduce(self)
            self.env.strategy_meet(self)


class Environment(object):

    def __init__(self, world, island):
        self.world = world
        self.island = island
        self.neighbouring_islands = tuple(island.neighbours.keys())
        self.reset_stats()

    def reset_stats(self):
        self.reproductions = 0
        self.deaths = 0
        self.encounters = 0
        self.decided_encounters = 0
        self.departures = 0

    def transfer(self, a1, a2, amount):
        amount = min(amount, a2.energy)
        a1.energy += amount
        a2.energy -= amount

    def dissipate(self, agent, amount):
        self.island.energy += amount
        agent.energy -= amount

    def move(self, agent, island):
        self.island.remove(agent)
        island.add(agent)
        agent.env = self.world.envs[island]

    def strategy_migration(self, agent):
        if agent.wants_to_migrate():
            where = agent.seek_migration()
            if where is not None:
                cost = self.cost[where]

                if agent.energy >= cost + self.travel_threshold:
                    self.dissipate(agent, cost)
                    self.move(agent, where)
                    self.departures += 1

    def strategy_meet(self, a1):
        if a1.wants_to_meet():
            a2 = a1.seek_meet()
            if a2 is not None and a2.accept_meet(a1):
                if self.dominates(a1, a2):
                    self.transfer(a1, a2, self.fight_transfer)
                    self.decided_encounters += 1
                elif self.dominates(a2, a1):
                    self.transfer(a2, a1, self.fight_transfer)
                    self.decided_encounters += 1
                self.encounters += 1

    def strategy_reproduce(self, a1):
        if a1.wants_to_reproduce:
            a2 = a1.seek_partner()
            if a2 is not None and a2.accept_reproduction(a1):
                x21, x12 = self.create_offspring(a1, a2)
                x21 = self.mutate(x21)
                x12 = self.mutate(x12)

                v21 = self.world.f(x21.x)
                v12 = self.world.f(x12.x)

                a21 = Agent(x21.x, v21, 0, self)
                a12 = Agent(x12.x, v12, 0, self)

                e = self.init_energy

                self.transfer(a21, a1, e / 2)
                self.transfer(a12, a1, e / 2)
                self.transfer(a21, a2, e / 2)
                self.transfer(a12, a2, e / 2)

                self.island.add(a21)
                self.island.add(a12)
                self.reproductions += 1

    def die(self, agent):
        self.dissipate(agent, agent.energy)
        self.island.remove(agent)
        self.deaths += 1

    def create_offspring(self, a1, a2):
        return crossover(a1, a2)

    def mutate(self, a):
        p = self.world.params['mutation_probability']
        return mutation(a, p, self.world.bounds, self.world.max_changes)

    def dominates(self, a, b):
        return inverslyDominates(b.val, a.val)

    @property
    def cost(self):
        return self.island.neighbours

    @property
    def peers(self):
        return self.island.inhabitants

    @property
    def init_energy(self):
        return self.world.params['init_energy']

    @property
    def death_threshold(self):
        return self.world.params['death_threshold']

    @property
    def travel_threshold(self):
        return self.world.params['travel_threshold']

    @property
    def reproduction_threshold(self):
        return self.world.params['reproduction_threshold']

    @property
    def fight_transfer(self):
        return self.world.params['fight_transfer']


class Island(object):

    def __init__(self):
        self.energy = 0
        self.inhabitants = []
        self.neighbours = {}

    def add(self, agent):
        self.inhabitants.append(agent)

    def remove(self, agent):
        self.inhabitants.remove(agent)


class EMAS(object):

    params = default_params

    def __init__(self, fs, bounds, ranges, **params):
        self.f = lambda x: tuple(f(x) for f in fs)
        self.bounds = bounds
        self.ranges = ranges
        self.params = dict(EMAS.params, **params)

        self.max_changes = [0.1 * (M - m) for m, M in bounds]
        self.world = []
        self.envs = {}

        self.create_world()
        self.populate_world()

    def create_world(self):
        size = self.params['world_size']
        cost = self.params['travel_cost']

        self.world = [Island() for _ in xrange(size)]

        for a in self.world:
            for b in self.world:
                if a is not b:
                    a.neighbours[b] = cost

        for island in self.world:
            self.envs[island] = Environment(self, island)

    def populate_world(self):
        N = self.params['population_size']
        energy = self.params['init_energy']

        for island in self.world:
            env = self.envs[island]
            for _ in xrange(N):
                x = randVector(self.bounds)
                val = self.f(x)
                agent = Agent(x, val, energy, env)
                island.add(agent)

    def create_new_agents(self):
        init_energy = self.params['init_energy']

        for island in self.world:
            if island.energy >= 0:
                N = int(island.energy / init_energy)

                for _ in xrange(N):
                    env = self.envs[island]
                    x = randVector(self.bounds)
                    val = self.f(x)
                    agent = Agent(x, val, init_energy, env)
                    island.add(agent)
                    island.energy -= init_energy
            else:
                print 'Negative island energy: {}'.format(island.energy)

    def agents_iter(self):
        return chain(*(island.inhabitants for island in self.world))

    def agents(self):
        return list(self.agents_iter())

    def optimize(self, steps, callback=None):
        if callback:
            callback(0, list(self.agents()))

        for step in xrange(steps):
            self.create_new_agents()

            for agent in self.agents():
                agent.step()
            if callback:
                callback(step + 1, self.agents())

        return self.agents()

