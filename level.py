from random import random as r
from bisect import bisect
from time import time

import pygame
import pymunk as pm
import evthandler as eh

import conf
from obj import Car, Obj

def col_cb (space, arbiter, game):
    if arbiter.is_first_contact:
        f = arbiter.total_impulse_with_friction
        f = (f[0] ** 2 + f[1] ** 2) ** .5
        game.play_snd('crash', f / 400000)

class Level:
    def __init__ (self, game, event_handler, num_cars = 2):
        self.game = game
        self.event_handler = event_handler
        self.num_cars = num_cars
        self.FRAME = conf.FRAME
        w, h = self.game.res
        self.last_spawn = 0
        s = self.space = pm.Space()
        s.add_collision_handler(0, 0, None, None, col_cb, None, game)
        # variables
        self.vel = -4000
        self.spawn_r = 1
        self.scores = [0] * self.num_cars
        # lines
        l = self.lines = []
        b = conf.BORDER
        for x0, y0, x1, y1 in ((b, b, b, h - b), (b, b, w - b, b),
                               (w - b, b, w - b, h - b),
                               (b, h - b, w - b, h - b)):
            l.append(((x0, y0), (x1, y1)))
        # stuff
        b = conf.PHYSICAL_BORDER
        self.death_bb = pm.BB(b, b, w - b, h - b)
        self.outer_bb = pm.BB(0, 0, w, h)
        self.objs = []
        self.reset(True)

    def reset (self, first = False):
        s = self.space
        w, h = self.game.res
        try:
            for o in self.cars + self.objs:
                s.remove(o.body, o.shape)
        except AttributeError:
            pass
        # objs
        cs = self.cars = []
        self.objs = []
        keys = []
        d = h / (self.num_cars + 1)
        for i in xrange(self.num_cars):
            c = Car(self, i, d * (i + 1))
            cs.append(c)
            for j, k in enumerate(conf.KEYS_MOVE[i]):
                if isinstance(k, int):
                    k = (k,)
                keys.append((k, [(c.move, (j,))], eh.MODE_HELD))
        self.event_handler.add_key_handlers(keys)
        self.paused = True
        self.init_pause_end = time() + conf.INITIAL_PAUSE
        self.can_move = first

    def update (self):
        do = True
        if self.paused:
            if self.init_pause_end:
                if time() >= self.init_pause_end:
                    self.init_pause_end = False
                    self.paused = False
                    self.can_move = False
            do = False
        if do or self.can_move:
            # update cars
            rm = []
            for c in self.cars:
                if c.update():
                    rm.append(c)
            for c in rm:
                self.cars.remove(c)
        if do:
            # add objs
            if r() * self.spawn_r * self.last_spawn * self.FRAME > .5:
                self.last_spawn = 0
                # choose obj type
                l = conf.OBJ_WEIGHTINGS
                cumulative = []
                last = 0
                for x in l:
                    last += x
                    cumulative.append(last)
                index = min(bisect(cumulative, cumulative[-1] * r()), len(l) - 1)
                ID = conf.OBJS[index]
                # create
                lw, lh = self.game.res
                self.objs.append(Obj(self, ID, lw, r() * lh, self.vel))
            else:
                self.last_spawn += 1
            # update objs
            rm = []
            for o in self.objs:
                if o.update():
                    rm.append(o)
            for o in rm:
                self.objs.remove(o)
        if do or self.can_move:
            self.space.step(.005)
            n = len(self.cars)
            if n < self.num_cars:
                if n < 1:
                    self.reset()
                elif n == 1 and not conf.TESTING:
                    if self._scores:
                        self.scores[self.cars[0].ID] += 1
                    self.reset()

    def draw (self, screen):
        # background
        screen.fill((0, 0, 0))
        # border
        imgs = [self.game.img(ID, ID + '.png') for ID in ('border0', 'border1')]
        bounds = self.game.res
        for a, b in self.lines:
            i = int(a[0] == b[0])
            img = imgs[i]
            size = list(img.get_size())
            pos = list(a)
            pos[i] = 0
            pos[not i] -= size[not i] / 2
            end = bounds[i]
            while pos[i] < end:
                screen.blit(img, pos, [0, 0] + size)
                pos[i] += size[i]
        # objs
        for c in self.cars + self.objs:
            c.draw(screen)
        # scores
        size = conf.SCORES_FONT_SIZE
        x, y = conf.SCORES_EDGE_PADDING
        pad = conf.SCORES_PADDING
        for i, s in enumerate(self.scores):
            s = str(s)
            h = self.game.res[1]
            font = (conf.FONT, size, False)
            c = conf.CAR_COLOURS_LIGHT[i]
            sc = conf.CAR_COLOURS[i]
            font_args = (font, s, c, (sc, conf.FONT_SHADOW_OFFSET))
            sfc, lines = self.game.img(s + str(i), font_args, text = True)
            screen.blit(sfc, (x, y))
            x += sfc.get_width() + pad
        return True