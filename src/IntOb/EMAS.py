
from itertools import ifilter
from .utils import dominates, randVector
from .genetics import Specimen, mutation, crossover
from random import choice, shuffle


names = [
    'Adam', 'Bartek', 'Ania', 'Pawel', 'Kasia', 'Andrzej', 'Alicja',
    'Michal', 'Zbigniew', 'Mateusz', 'Marcin', 'Filip', 'Felicja',
    'Tomek', 'Piotr', 'Paulina', 'Dariusz'
]



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

    def attack(self, enemy):
        self.combat(enemy)
        enemy.attacked(self)

    def attacked(self, enemy):
        self.combat(enemy)

    def combat(self, enemy):
        best = self.env.winner(self, enemy)
        if self is best:
            gain = self.env.fight_transfer
            self.energy += gain
            enemy.energy -= gain
        elif enemy is best:
            loss = self.env.fight_transfer
            self.energy -= loss
            enemy.energy += loss

    def __str__(self):
        return '{}#{}'.format(self.name, hash(self))

    # Methods determining behaviour of agent (strategy, actions)

    def act(self):
        """ Invoked once during every step of lifecycle. Here, agent is free to
        undertake whatever action he feels appropriate.
        """
        if self.can_reproduce() and self.reproduce():
            return
        if self.can_travel() and self.travel():
            return
        self.fight()


    def meet_offer(self, other):
        """ Invoked when some other agent wishes to meet with this one.

        other - agent that makes the offer

        Returns:
            True - offer accepted, False - rejected
        """
        return True

    def reproduction_offer(self, mate):
        """ Invoked when some other agent wishes to reproduce.

        mate - agent that makes the offer

        Returns:
            True - offer accepted, False - rejected
        """
        return True

    def reproduce(self):
        mates = self.env.find_mates(self)
        shuffle(mates)

        for mate in mates:
            if mate.reproduction_offer(self):
                self.env.reproduce(self, mate)
                return True
        else:
            return False

    def travel(self):
        costs = self.env.neighbour_islands()
        islands = list(costs.keys())
        shuffle(islands)

        for island in islands:
            cost = costs[island]
            if self.energy >= self.env.travel_threshold + cost:
                self.env.travel(self, island)
                return True
        else:
            return False

    def fight(self):
        enemies = self.env.find_encounters(self)
        if enemies:
            max_attempts = 10
            for _ in xrange(max_attempts):
                enemy = choice(enemies)
                if enemy.meet_offer(self):
                    self.attack(enemy)
                    return True
            else:
                print 'Noone wants to fight ({} rejected challenges)'\
                    .format(max_attempts)
        else:
            return False


    def die(self):
        """ Invoked when the agent has died, i.e. when his life energy has
        fallen below the death threshold.
        """
        pass


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

        e = self.emas.params['init_energy']
        p1.energy -= e
        p2.energy -= e

        a1 = Agent(c1.x, v1, e, self)
        a2 = Agent(c2.x, v2, e, self)
        a1.name = choice(names)
        a2.name = choice(names)

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
        agent.energy -= e
        self.island.energy += e
        self.island.remove_agent(agent)
        destination.add_agent(agent)
        agent.env = self.emas.envs[destination]

    def died(self, agent):
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
        'reproduction_threshold': 0.7,
        'death_threshold': 0.1,
        'mutation_probability': 0.05,
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
                agent.name = choice(names)

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

