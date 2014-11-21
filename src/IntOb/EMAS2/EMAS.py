
from ..utils import inverslyDominates, randVector, distance
from ..genetics import crossover, mutation
from ..EMAS.param_sets import param_sets, default_params
from random import choice
from itertools import chain
from math import sqrt


class Agent(object):

    def __init__(self, x, val, energy, env):
        self.x = x
        self.val = val
        self.energy = energy
        self.env = env
        self.elite = False

        self.encounters = 0
        self.won = 0
        self.lost = 0
        self.close_encounters = 0
        self.sum_env_crowding = 0.0

    @property
    def prestige(self):
        return self.won

    def __avg(self, val, default=0.0):
        return val / float(self.encounters) if self.fought else default

    @property
    def fought(self):
        return self.encounters > 0

    @property
    def won_frac(self):
        return self.__avg(self.won)

    @property
    def lost_frac(self):
        return self.__avg(self.lost)

    @property
    def crowding(self):
        return self.__avg(self.close_encounters)

    @property
    def env_crowding(self):
        return self.__avg(self.sum_env_crowding)

    def accept_meet(self, other):
        return not self.dead

    def accept_reproduction(self, other):
        return self.can_reproduce

    def seek_migration(self):
        if self.elite:
            world = self.env.elite_neighbouring_islands
        else:
            world = self.env.neighbouring_islands

        if world:
            return choice(world)

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

    @property
    def can_be_elite(self):
        return self.prestige >= self.env.elite_threshold

    def wants_to_meet(self):
        return True

    def wants_to_migrate(self):
        return self.can_travel # and self.crowding > self.env_crowding

    def wants_to_reproduce(self):
        return self.can_reproduce

    def wants_to_be_elite(self):
        return True

    def step(self):
        if not self.elite:
            if self.dead:
                self.env.die(self)
            else:
                self.env.strategy_migration(self)
                self.env.strategy_reproduce(self)
                self.env.strategy_meet(self)
                self.env.strategy_become_elite(self)
        elif not self.dead:
            self.env.strategy_meet(self)


class Environment(object):

    def __init__(self, world, island):
        self.world = world
        self.island = island
        islands = tuple(island.neighbours.keys())
        self.neighbouring_islands = filter(lambda x: not x.elite, islands)
        self.elite_neighbouring_islands = filter(lambda x: x.elite, islands)
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
                a1.encounters += 1
                a2.encounters += 1

                if self.dominates(a1, a2):
                    a1.won += 1
                    a2.lost += 1
                elif self.dominates(a2, a1):
                    a1.lost += 1
                    a2.won += 1

                if distance(a1.val, a2.val) < self.world.params['epsilon']:
                    a1.close_encounters += 1
                    a2.close_encounters += 1

                a1.sum_env_crowding += a2.crowding
                a2.sum_env_crowding += a1.crowding

                if a1.elite:
                    self.meet_elite(a1, a2)
                else:
                    self.meet_ordinary(a1, a2)

                self.encounters += 1

    def meet_elite(self, a1, a2):
        if self.dominates(a1, a2):
            self.die(a2)
            self.decided_encounters += 1
        elif self.dominates(a2, a1):
            self.die(a1)
            self.decided_encounters += 1

    def meet_ordinary(self, a1, a2):
        if self.dominates(a1, a2):
            self.victory(a1, a2)
        elif self.dominates(a2, a1):
            self.victory(a2, a1)
        else:
            if a1.lost_frac < a2.lost_frac:
                self.victory(a1, a2)
            elif a1.lost_frac > a2.lost_frac:
                self.victory(a2, a1)
            else:
                if a1.crowding < a2.crowding and (a2.energy > self.fight_transfer
                        or a2.lost > 0):
                    self.victory(a1, a2)
                if a2.crowding < a1.crowding and (a1.energy > self.fight_transfer
                        or a1.lost > 0):
                    self.victory(a2, a1)

    def victory(self, winner, looser):
        self.transfer(winner, looser, self.fight_transfer)
        self.decided_encounters += 1

    def strategy_reproduce(self, a1):
        if a1.wants_to_reproduce():
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

    def strategy_become_elite(self, agent):
        if agent.can_be_elite and agent.wants_to_be_elite():
            if agent.crowding > agent.env_crowding:
                self.transcend(agent)

    def transcend(self, agent):
        agent.elite = True
        where = agent.seek_migration()

        if where is not None:
            cost = self.cost[where]

            if agent.energy >= cost + self.travel_threshold:
                self.dissipate(agent, cost)
                self.move(agent, where)
                self.departures += 1
            else:
                agent.elite = False
        else:
            agent.elite = False


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
    def elite_threshold(self):
        return self.world.params['elite_threshold']

    @property
    def fight_transfer(self):
        return self.world.params['fight_transfer']


class Island(object):

    def __init__(self, elite=False):
        self.elite = elite
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

        elite_size = self.params['elite_islands']
        self.valhalla = [Island(elite=True) for _ in xrange(elite_size)]

        for a in self.valhalla:
            for b in self.valhalla:
                if a is not b:
                    a.neighbours[b] = cost
            # passage from real world to valhalla
            for b in self.world:
                b.neighbours[a] = cost

        for island in chain(self.world, self.valhalla):
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

        for island in chain(self.world, self.valhalla):
            if island.energy >= 0:
                N = int(island.energy / init_energy)

                for _ in xrange(N):
                    where = island if not island.elite else choice(self.world)
                    env = self.envs[where]
                    x = randVector(self.bounds)
                    val = self.f(x)
                    agent = Agent(x, val, init_energy, env)
                    where.add(agent)
                    island.energy -= init_energy
            else:
                print 'Negative island energy: {}'.format(island.energy)

    def agents_iter(self):
        return chain(*(island.inhabitants for island in self.world))

    def agents(self):
        return list(self.agents_iter())

    def elite_agents_iter(self):
        return chain(*(island.inhabitants for island in self.valhalla))

    def elite_agents(self):
        return list(self.elite_agents_iter())

    def all_agents_iter(self):
        return chain(self.agents_iter(), self.elite_agents_iter())

    def all_agents(self):
        return list(self.all_agents_iter())

    def optimize(self, steps, callback=None):
        if callback:
            callback(0, list(self.agents()))

        for step in xrange(steps):
            self.create_new_agents()

            for agent in self.all_agents():
                agent.step()
            if callback:
                callback(step + 1, self.agents())

        return self.agents()

