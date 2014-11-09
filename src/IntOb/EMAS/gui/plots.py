
class Plot(object):

    def __init__(self, plot, steps, update_every, data, emas):
        self.emas = emas
        self.steps = steps
        self.update_every = update_every
        self.data = data
        self.plot = plot
        self.set_metadata()

    def set_metadata(self):
        pass

    def set_style(self):
        pass

    @property
    def step_axis(self):
        return [0, self.steps]


class EnergyPlot(Plot):
    def __init__(self, *args, **kwargs):
        super(EnergyPlot, self).__init__(*args, **kwargs)

    def set_metadata(self):
        self.plot.set_title('Total energy in the system')
        self.plot.set_xlim(self.step_axis)
        self.plot.set_ylim(self.energy_axis)

    def redraw(self):
        self.plot.hold(False)
        self.plot.plot(self.data.energy, '-')
        self.plot.hold(True)
        self.plot.plot(self.data.free_energy, '-')
        self.set_metadata()

    @property
    def energy_axis(self):
        return [0, self.data.max_energy * 1.2]


class EnergyPerIslandPlot(Plot):
    def __init__(self, *args, **kwargs):
        super(EnergyPerIslandPlot, self).__init__(*args, **kwargs)

    def set_metadata(self):
        self.plot.set_title('Energy per island')
        self.plot.set_xlim(self.step_axis)
        self.plot.set_ylim(self.energy_axis)

    def redraw(self):
        self.plot.hold(False)
        for island, history in self.data.energy_per_island.iteritems():
            self.plot.plot(history, '-')
            self.plot.hold(True)
        self.set_metadata()

    @property
    def energy_axis(self):
        n = self.emas.params['world_size']
        return [0, self.data.max_energy / n * 1.2]


class PopulationPlot(Plot):
    def __init__(self, *args, **kwargs):
        super(PopulationPlot, self).__init__(*args, **kwargs)

    def set_metadata(self):
        self.plot.set_title('Total population size')
        self.plot.set_xlim(self.step_axis)
        self.plot.set_ylim([0, self.data.init_population * 1.2])

    def redraw(self):
        self.plot.hold(False)
        self.plot.plot(self.data.energy, '-')
        self.plot.hold(True)
        self.plot.plot(self.data.free_energy, '-')
        self.set_metadata()

    @property
    def population_axis(self):
        return [0, self.data.max_energy * 1.2]


class SolutionPlot(Plot):
    def __init__(self, *args, **kwargs):
        super(SolutionPlot, self).__init__(*args, **kwargs)

    def set_metadata(self):
        self.plot.set_title('Solutions')
        self.plot.set_xlim([0, 1])
        self.plot.set_ylim(bottom=0)

    def redraw(self):
        self.plot.hold(False)
        sx = []
        sy = []
        for island in self.emas.world:
            for agent in island.inhabitants:
                x, y = agent.val
                sx.append(x)
                sy.append(y)
        self.plot.plot(sx, sy, 'ro', ms=5)
        self.set_metadata()

class HVRPlot(Plot):
    def __init__(self, *args, **kwargs):
        super(HVRPlot, self).__init__(*args, **kwargs)

    def set_metadata(self):
        self.plot.set_title('HVR')
        self.plot.set_xlim(self.step_axis)
        self.plot.set_ylim([0, 1])

    def redraw(self):
        self.plot.hold(False)
        self.plot.plot(self.data.hvr, 'r-')
        self.set_metadata()
