import pygame
import pymunk as pm
import evthandler as eh

import conf
from obj import Car, Obj

class Level:
    def __init__ (self, game, event_handler):
        self.game = game
        self.event_handler = event_handler
        self.FRAME = conf.FRAME
        w, h = conf.RES_W
        s = self.space = pm.Space()
        l = self.lines = []
        b = conf.BORDER
        for x0, y0, x1, y1 in ((b, b, b, h - b), (b, b, w - b, b),
                               (w - b, b, w - b, h - b),
                               (b, h - b, w - b, h - b)):
            l.append(((x0, y0), (x1, y1)))
        self.death_bb = pm.BB(b, b, w -b, h - b)
        self.outer_bb = pm.BB(0, 0, w, h)
        n = self.num_cars = 2
        cs = self.cars = []
        keys = []
        for i, y in enumerate(xrange(n)):
            c = Car(self, i, 100 + 150 * y)
            cs.append(c)
            for j, k in enumerate(conf.KEYS_MOVE[i]):
                keys.append((k, [(c.move, (j,))], eh.MODE_HELD))
        event_handler.add_key_handlers(keys)
        self.pos = 0
        self.vel = -5000
        self.objs = [Obj(self, 1000, 300, self.vel)]

    def update (self):
        rm = []
        for c in self.cars:
            if c.update():
                rm.append(c)
        for c in rm:
            self.cars.remove(c)
        rm = []
        for o in self.objs:
            if o.update():
                rm.append(o)
        for o in rm:
            self.objs.remove(o)
        self.space.step(.005)
        if len(self.cars) < 1:
            print 'no-one wins'
            self.game.restart()
        elif len(self.cars) == 1:
            print self.cars[0].ID, 'wins'
            self.game.restart()

    def draw (self, screen):
        screen.fill((255, 255, 255))
        for a, b in self.lines:
            pygame.draw.line(screen, (0, 0, 0), a, b, 5)
        for c in self.cars + self.objs:
            c.draw(screen)
        return True