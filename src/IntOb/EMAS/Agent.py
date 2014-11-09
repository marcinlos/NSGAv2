
from random import choice, shuffle


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

    def transfer_energy(self, other, amount):
        self.energy -= amount
        other.energy += amount

    def dissipate_energy(self, amount):
        self.energy -= amount
        self.env.accept_energy(amount)

    def attack(self, enemy):
        self.combat(enemy)
        enemy.attacked(self)

    def attacked(self, enemy):
        self.combat(enemy)

    def combat(self, enemy):
        best = self.env.winner(self, enemy)
        if enemy is best:
            loss = min(self.env.fight_transfer, self.energy)
            self.transfer_energy(enemy, loss)

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

