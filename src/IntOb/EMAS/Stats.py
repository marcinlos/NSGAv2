
from ..hypervolume import hypervolume
from collections import defaultdict


class Stats(object):
    def __init__(self, emas, volume):
        self.emas = emas
        self.volume = volume

        self.energy = []
        self.free_energy = []
        self.island_energy = defaultdict(list)
        self.energy_per_island = defaultdict(list)
        self.population = []
        self.population_per_island = defaultdict(list)
        self.hvr = []
        self.refpoint = tuple(r[1] for r in emas.ranges)

    def update(self, step):
        total_energy = 0
        free_energy = 0
        count = 0
        island_energy = {}
        energy_per_island = {}
        population_per_island = {}

        vals = []

        for island in self.emas.world:
            island_energy[island] = island.energy
            free_energy += island.energy
            energy_per_island[island] = 0
            population_per_island[island] = 0

            for agent in island.inhabitants:
                total_energy += agent.energy
                energy_per_island[island] += agent.energy
                count += 1
                population_per_island[island] += 1
                vals.append(agent.val)

        self.energy.append((step, total_energy))
        self.population.append((step, count))
        self.free_energy.append((step, free_energy))
        self.append(step, island_energy, self.island_energy)
        self.append(step, energy_per_island, self.energy_per_island)
        self.append(step, population_per_island, self.population_per_island)

        vol = hypervolume(self.refpoint, vals)
        hvr = vol / self.volume
        self.hvr.append((step, hvr))


    def append(self, step, data, history):
        for k, v in data.iteritems():
            history[k].append((step, v))

    @property
    def init_population(self):
        world_size = self.emas.params['world_size']
        per_island = self.emas.params['population_size']
        return world_size * per_island

    @property
    def max_energy(self):
        e = self.emas.params['init_energy']
        return self.init_population * e

