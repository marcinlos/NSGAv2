
from .genetics import Specimen


class Island(object):

    def __init__(self):
        pass

    def selectAgentForEncounter():
        pass

    def neighbourIslands():
        pass

    @property
    def travel_treshold():
        pass

    @property
    def reproduction_treshold():
        pass


class Agent(object):

    def __init__(self, x, energy, env):
        self.env = env
        self.x = x
        self.energy = energy

    def can_travel(self):
        return self.energy >= self.env.travel_treshold

    def can_reproduce(self):
        return self.energy >= self.env.reproduction_treshold

    def act():
        pass

    def reproduce():
        pass

    def travel():
        pass

    def fight():
        pass
