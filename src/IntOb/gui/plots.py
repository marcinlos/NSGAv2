
import matplotlib.pyplot as plt
from ..utils import maximal, inverslyDominates
from matplotlib.ticker import FuncFormatter


class Plot(object):

    def __init__(self, fig, plot, steps, data, alg):
        self.alg = alg
        self.steps = steps
        self.data = data
        self.fig = fig
        self.plot = plot
        self.set_metadata()

    def set_metadata(self):
        pass

    def update(self):
        self.redraw()
        self.set_metadata()

    def set_step_axis(self):
        if self.steps >= 8000:
            fmt = lambda x, pos: '{}K'.format(int(x / 1000))
            self.plot.xaxis.set_major_formatter(FuncFormatter(fmt))

    @property
    def step_axis(self):
        return [0, self.steps]


class EnergyPlot(Plot):
    def __init__(self, *args, **kwargs):
        super(EnergyPlot, self).__init__(*args, **kwargs)

    def set_metadata(self):
        self.plot.set_title('Total energy')
        self.plot.set_xlim(self.step_axis)
        self.plot.set_ylim(self.energy_axis)
        self.set_step_axis()

    def redraw(self):
        xs = self.data.time

        self.plot.hold(False)
        self.plot.plot(xs, self.data.energy, 'r-', label='agents')
        self.plot.hold(True)
        self.plot.plot(xs, self.data.free_energy, 'g-', label='env')
        self.plot.plot(xs, self.data.elite_energy, 'b-', label='elite')
        self.plot.legend(fontsize=10)

    @property
    def energy_axis(self):
        return [0, self.data.max_energy * 1.2]


class EnergyDistributionPlot(Plot):

    colors = [plt.cm.jet(x / 9.0) for x in xrange(10)]

    def __init__(self, *args, **kwargs):
        super(EnergyDistributionPlot, self).__init__(*args, **kwargs)

    def set_metadata(self):
        self.plot.set_title('Energy distribution')
        self.plot.set_xlim(self.step_axis)
        self.plot.set_ylim([0, 1])
        self.set_step_axis()

    def redraw(self):
        xs = self.data.time
        self.plot.hold(False)

        data = zip(*self.data.energy_dist)

        n = self.data.bin_count
        data = [[] for _ in xrange(n)]

        for i in xrange(len(self.data.energy_dist)):
            pop = self.data.population[i]
            for j in xrange(n):
                data[j].append(self.data.energy_dist[i][j] / float(pop))

        self.plot.stackplot(xs, *data, colors=self.colors)


class EnergyPerIslandPlot(Plot):
    def __init__(self, *args, **kwargs):
        super(EnergyPerIslandPlot, self).__init__(*args, **kwargs)

    def set_metadata(self):
        self.plot.set_title('Energy per island')
        self.plot.set_xlim(self.step_axis)
        self.plot.set_ylim(self.energy_axis)
        self.set_step_axis()

    def redraw(self):
        xs = self.data.time

        self.plot.hold(False)
        for island, data in self.data.island_data:
            self.plot.plot(xs, data.energy, '-')
            self.plot.hold(True)

    @property
    def energy_axis(self):
        n = self.alg.params['world_size']
        return [0, self.data.max_energy / n * 1.2]


class PopulationPlot(Plot):
    def __init__(self, *args, **kwargs):
        super(PopulationPlot, self).__init__(*args, **kwargs)

    def set_metadata(self):
        self.plot.set_title('Total population size')
        self.plot.set_xlim(self.step_axis)
        self.set_step_axis()

    def redraw(self):
        xs = self.data.time

        self.plot.hold(False)
        self.plot.plot(xs, self.data.population, 'b-', label='all')
        self.plot.hold(True)
        self.plot.plot(xs, self.data.elite, 'm-', label='elite')
        self.plot.plot(xs, self.data.reproduction_capable, 'g-', label='repr')
        self.plot.plot(xs, self.data.travel_capable, 'c-', label='travel')
        self.plot.legend(fontsize=10)

    @property
    def population_axis(self):
        return [0, self.data.max_energy * 1.2]


class BaseSolutionPlot(Plot):
    def __init__(self, *args, **kwargs):
        super(BaseSolutionPlot, self).__init__(*args, **kwargs)

    def plot_front(self):
        for xs, ys in self.alg.problem.front:
            self.plot.plot(xs, ys, 'g-')
            self.plot.hold(True)


class SolutionPlot(BaseSolutionPlot):
    def __init__(self, *args, **kwargs):
        super(SolutionPlot, self).__init__(*args, **kwargs)

    def set_metadata(self):
        self.plot.set_title('Solutions')
        self.plot.set_xlim([0, 1])
        self.plot.set_ylim(bottom=0)

    def redraw(self):
        self.plot.hold(False)
        self.plot_front()

        for island in self.alg.world:
            sx = []
            sy = []
            for agent in island.inhabitants:
                x, y = agent.val
                sx.append(x)
                sy.append(y)
            self.plot.plot(sx, sy, 'o', ms=5)


class EliteSolutionPlot(BaseSolutionPlot):
    def __init__(self, *args, **kwargs):
        super(EliteSolutionPlot, self).__init__(*args, **kwargs)

    def set_metadata(self):
        self.plot.set_title('Elite agents')
        self.plot.set_xlim([0, 1])
        self.plot.set_ylim(bottom=0)

    def redraw(self):
        self.plot.hold(False)
        self.plot_front()

        for island in self.alg.valhalla:
            sx = []
            sy = []
            for agent in island.inhabitants:
                x, y = agent.val
                sx.append(x)
                sy.append(y)
            self.plot.plot(sx, sy, 'o', ms=5)
            self.plot.hold(True)


class SolutionDensityPlot(BaseSolutionPlot):
    def __init__(self, *args, **kwargs):
        super(SolutionDensityPlot, self).__init__(*args, **kwargs)

    def set_metadata(self):
        self.plot.set_title('Density')
        self.plot.set_xlim([0, 1])
        self.plot.set_ylim(bottom=0)

    def redraw(self):
        self.plot.hold(False)
        self.plot_front()

        sx = []
        sy = []
        val = []
        for agent in self.alg.agents():
            x, y = agent.val
            sx.append(x)
            sy.append(y)
            val.append(agent.crowding)

        self.plot.scatter(sx, sy, c=val, cmap=plt.cm.jet, vmin=0, vmax=1)


class SolutionEnergyPlot(BaseSolutionPlot):
    def __init__(self, *args, **kwargs):
        super(SolutionEnergyPlot, self).__init__(*args, **kwargs)

    def set_metadata(self):
        self.plot.set_title('Energy')
        self.plot.set_xlim([0, 1])
        self.plot.set_ylim(bottom=0)

    def redraw(self):
        self.plot.hold(False)
        self.plot_front()

        sx = []
        sy = []
        val = []
        for agent in self.alg.agents():
            x, y = agent.val
            sx.append(x)
            sy.append(y)
            val.append(agent.energy)

        self.plot.scatter(sx, sy, c=val, cmap=plt.cm.jet, vmin=0, vmax=1)


class SolutionPrestigePlot(BaseSolutionPlot):
    def __init__(self, *args, **kwargs):
        super(SolutionPrestigePlot, self).__init__(*args, **kwargs)

    def set_metadata(self):
        self.plot.set_title('Prestige')
        self.plot.set_xlim([0, 1])
        self.plot.set_ylim(bottom=0)

    def redraw(self):
        self.plot.hold(False)
        self.plot_front()

        sx = []
        sy = []
        val = []
        for agent in self.alg.agents():
            x, y = agent.val
            sx.append(x)
            sy.append(y)
            val.append(agent.prestige)

        M = self.alg.params['elite_threshold']
        self.plot.scatter(sx, sy, c=val, cmap=plt.cm.jet, vmin=0, vmax=M)


class FrontPlot(BaseSolutionPlot):
    def __init__(self, *args, **kwargs):
        super(FrontPlot, self).__init__(*args, **kwargs)

    def set_metadata(self):
        self.plot.set_title('Front')
        self.plot.set_xlim([0, 1])
        self.plot.set_ylim(bottom=0)

    def redraw(self):
        self.plot.hold(False)
        self.plot_front()

        agents = self.alg.all_agents()
        less = lambda a, b: inverslyDominates(a.val, b.val)
        front = maximal(agents, less)

        sx = []
        sy = []
        for agent in front:
            x, y = agent.val
            sx.append(x)
            sy.append(y)

        self.plot.plot(sx, sy, 'o', ms=5)


class HVRPlot(Plot):
    def __init__(self, *args, **kwargs):
        super(HVRPlot, self).__init__(*args, **kwargs)

    def set_metadata(self):
        self.plot.set_title('HVR')
        self.plot.set_xlim(self.step_axis)
        self.plot.set_ylim(top=1)
        self.plot.grid(True)
        self.set_step_axis()

    def redraw(self):
        xs = self.data.time
        self.plot.hold(False)
        self.plot.plot(xs, self.data.hvr, 'r-')

        t, max_hvr = max(zip(xs, self.data.hvr), key=lambda (_,val): val)
        text = '{:.2%}'.format(max_hvr)
        _, _, ym, _ = self.plot.axis()
        self.plot.annotate(
            s=text,
            xy=(t, max_hvr),
            xytext=(t, ym + 0.1 * (1 - ym)),
            textcoords='data',
            ha='center',
            fontsize=10,
            arrowprops=dict(
                arrowstyle='->',
                shrinkB=15,
            )
        )


class TimePlot(Plot):
    def __init__(self, *args, **kwargs):
        super(TimePlot, self).__init__(*args, **kwargs)

    def set_metadata(self):
        self.plot.set_title('Step time [ms]')
        self.plot.set_xlim(self.step_axis)
        self.set_step_axis()

    def redraw(self):
        xs = self.data.time
        self.plot.hold(False)
        self.plot.plot(xs, self.data.step_time, 'r-')


class ReproductionPlot(Plot):
    def __init__(self, *args, **kwargs):
        super(ReproductionPlot, self).__init__(*args, **kwargs)

    def set_metadata(self):
        self.plot.set_title('Reproductions')
        self.plot.set_xlim(self.step_axis)
        self.set_step_axis()

    def redraw(self):
        xs = self.data.time
        self.plot.hold(False)
        self.plot.plot(xs, self.data.reproductions, 'g-')


class DeathsPlot(Plot):
    def __init__(self, *args, **kwargs):
        super(DeathsPlot, self).__init__(*args, **kwargs)

    def set_metadata(self):
        self.plot.set_title('Deaths')
        self.plot.set_xlim(self.step_axis)
        self.set_step_axis()

    def redraw(self):
        xs = self.data.time
        self.plot.hold(False)
        self.plot.plot(xs, self.data.deaths, 'r-')


class LifeCyclePlot(Plot):
    def __init__(self, *args, **kwargs):
        super(LifeCyclePlot, self).__init__(*args, **kwargs)

    def set_metadata(self):
        self.plot.set_title('Life & death')
        self.plot.set_xlim(self.step_axis)
        self.set_step_axis()

    def redraw(self):
        xs = self.data.time
        self.plot.hold(False)
        self.plot.plot(xs, self.data.deaths, 'r-', label='deaths')
        self.plot.hold(True)
        births = [2*n for n in self.data.reproductions]
        self.plot.plot(xs, births, 'g-', label='births')
        self.plot.legend(fontsize=10)


class RNIPlot(Plot):
    def __init__(self, *args, **kwargs):
        super(RNIPlot, self).__init__(*args, **kwargs)

    def set_metadata(self):
        self.plot.set_title('Rate of Natural Increase')
        self.plot.set_xlim(self.step_axis)
        self.set_step_axis()

    def redraw(self):
        xs = self.data.time
        self.plot.hold(False)

        data = [
            (2*r - d) / s
            for r, d, s in
            zip(self.data.reproductions, self.data.deaths, self.data.population)
        ]

        self.plot.bar(xs, data, color='r', edgecolor='none')
        self.plot.hold(True)
        zero = [0 for _ in self.data.time]
        self.plot.plot(xs, zero, 'k-')


class TravelPlot(Plot):
    def __init__(self, *args, **kwargs):
        super(TravelPlot, self).__init__(*args, **kwargs)

    def set_metadata(self):
        self.plot.set_title('Travel')
        self.plot.set_xlim(self.step_axis)
        self.set_step_axis()

    def redraw(self):
        xs = self.data.time
        self.plot.hold(False)
        self.plot.plot(xs, self.data.departures, 'b-')


class EncounterPlot(Plot):
    def __init__(self, *args, **kwargs):
        super(EncounterPlot, self).__init__(*args, **kwargs)

    def set_metadata(self):
        self.plot.set_title('Encounters')
        self.plot.set_xlim(self.step_axis)
        self.set_step_axis()

    def redraw(self):
        xs = self.data.time
        self.plot.hold(False)
        self.plot.plot(xs, self.data.encounters, 'b-', label='all')
        self.plot.hold(True)
        self.plot.plot(xs, self.data.decided_encounters, 'r-', label='win')
        self.plot.legend(fontsize=10)


class AgentEnergyPlot(Plot):
    def __init__(self, *args, **kwargs):
        super(AgentEnergyPlot, self).__init__(*args, **kwargs)
        self.travel_threshold = self.alg.params['travel_threshold']
        self.reproduction_threshold = self.alg.params['reproduction_threshold']
        self.death_threshold = self.alg.params['death_threshold']

    def set_metadata(self):
        self.plot.set_title('Avg agent energy')
        self.plot.set_xlim(self.step_axis)
        self.plot.set_ylim(bottom=0)
        self.set_step_axis()

    def make_series(self, value):
        return [value for _ in self.data.time]

    def redraw(self):
        xs = self.data.time
        travel_series = self.make_series(self.travel_threshold)
        reproduction_series = self.make_series(self.reproduction_threshold)
        death_series = self.make_series(self.death_threshold)

        self.plot.hold(False)
        self.plot.plot(xs, travel_series, 'c-', label='travel')
        self.plot.hold(True)

        self.plot.plot(xs, reproduction_series, 'g-', label='repr')
        self.plot.plot(xs, death_series, 'r-', label='death')
        self.plot.plot(xs, self.data.avg_energy, 'b-', label='avg')

        self.plot.legend(fontsize=10)

