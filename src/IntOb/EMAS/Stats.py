
from ..hypervolume import hypervolume
from collections import defaultdict


class Data(object):

    def __init__(self):
        self.energy = []
        self.free_energy = []
        self.avg_energy = []
        self.population = []
        self.reproduction_capable = []
        self.travel_capable = []
        self.reproductions = []
        self.deaths = []
        self.encounters = []
        self.decided_encounters = []
        self.departures = []


class Stats(object):
    def __init__(self, emas, volume):
        self.emas = emas
        self.volume = volume

        self.time = []
        self.data = defaultdict(Data)
        self.total = Data()

        self.hvr = []
        self.refpoint = tuple(r[1] for r in emas.ranges)

    @property
    def islands(self):
        return self.data.keys()

    @property
    def island_data(self):
        return self.data.iteritems()

    def __getattr__(self, attr):
        return getattr(self.total, attr)

    def __getitem__(self, island):
        return self.data[island]

    def update(self, step):
        last = self.time[-1] if self.time else -1
        self.time.append(step)
        dt = float(step - last)

        energy = 0
        free_energy = 0
        population = 0
        reproduction_capable = 0
        travel_capable = 0
        reproductions = 0
        deaths = 0
        encounters = 0
        decided_encounters = 0
        departures = 0

        vals = []

        reproduction_threshold = self.emas.params['reproduction_threshold']
        travel_threshold = self.emas.params['travel_threshold']

        for island in self.emas.world:
            env = self.emas.envs[island]

            self[island].free_energy.append(island.energy)
            self[island].reproductions.append(env.reproductions)
            self[island].deaths.append(env.deaths)
            self[island].encounters.append(env.encounters)
            self[island].decided_encounters.append(env.decided_encounters)
            self[island].departures.append(env.departures)

            free_energy += island.energy
            reproductions += env.reproductions / dt
            deaths += env.deaths / dt
            encounters += env.encounters / dt
            decided_encounters += env.decided_encounters / dt
            departures += env.departures / dt

            island_size = len(island.inhabitants)
            self[island].population.append(island_size)
            population += island_size

            island_energy = 0
            island_reproduction_capable = 0
            island_travel_capable = 0

            for agent in island.inhabitants:
                island_energy += agent.energy
                if agent.energy >= reproduction_threshold:
                    island_reproduction_capable += 1
                if agent.energy >= travel_threshold:
                    island_travel_capable += 1
                vals.append(agent.val)

            energy += island_energy
            reproduction_capable += island_reproduction_capable
            travel_capable += island_travel_capable

            self[island].energy.append(island_energy)
            avg_island_energy = island_energy / island_size if island_size > 0 else 0
            self[island].avg_energy.append(avg_island_energy)
            self[island].reproduction_capable.append(island_reproduction_capable)
            self[island].travel_capable.append(island_travel_capable)

            env.reset_stats()

        self.total.energy.append(energy)
        self.total.avg_energy.append(energy / population)
        self.total.free_energy.append(free_energy)
        self.total.population.append(population)
        self.total.reproduction_capable.append(reproduction_capable)
        self.total.travel_capable.append(travel_capable)
        self.total.reproductions.append(reproductions)
        self.total.deaths.append(deaths)
        self.total.encounters.append(encounters)
        self.total.decided_encounters.append(decided_encounters)
        self.total.departures.append(departures)

        vol = hypervolume(self.refpoint, vals)
        hvr = vol / self.volume
        self.hvr.append(hvr)


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

