
from collections import defaultdict


class Stats(object):
    def __init__(self, emas):
        self.emas = emas

        self.energy = []
        self.free_energy = []
        self.island_energy = defaultdict(list)
        self.energy_per_island = defaultdict(list)
        self.population = []
        self.population_per_island = defaultdict(list)

    def update(self, step):
        total_energy = 0
        free_energy = 0
        count = 0
        island_energy = {}
        energy_per_island = {}
        population_per_island = {}

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

        self.energy.append(total_energy)
        self.population.append(count)
        self.free_energy.append(free_energy)
        self.append(island_energy, self.island_energy)
        self.append(energy_per_island, self.energy_per_island)
        self.append(population_per_island, self.population_per_island)


    def append(self, data, history):
        for k, v in data.iteritems():
            history[k].append(v)

    @property
    def init_population(self):
        world_size = self.emas.params['world_size']
        per_island = self.emas.params['population_size']
        return world_size * per_island

    @property
    def max_energy(self):
        e = self.emas.params['init_energy']
        return self.init_population * e

