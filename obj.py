import pygame as pg
import pymunk as pm

from random import random

import conf

class Obj:
    def __init__ (self, level, x, y, vx):
        self.level = level
        b = self.body = pm.Body(500, pm.moment_for_box(500, 50, 50))
        b.position = (x, y)
        b.velocity = (vx, 0)
        s = self.shape = pm.Poly.create_box(b, (50, 50))
        s.elasticity = conf.CAR_ELAST
        level.space.add(b, s)

    def update (self):
        if not self.shape.cache_bb().intersects(self.level.outer_bb):
            self.level.space.remove(self.body, self.shape)
            return True
        else:
            return False

    def draw (self, screen):
        pg.draw.polygon(screen, (0, 0, 0), self.shape.get_points())

class Car:
    def __init__ (self, level, ID, y):
        self.level = level
        self.ID = ID
        b = self.body = pm.Body(conf.CAR_MASS, pm.inf) #pm.moment_for_box(conf.CAR_MASS, 40, 60))
        # TODO: have rotation, but every frame we move set inertia towards facing right by an amount proportional to angular distance away
        b.position = (200, y)
        b.velocity = (0, 0)
        s = self.shape = pm.Poly.create_box(b, (40, 60))
        s.elasticity = conf.CAR_ELAST
        level.space.add(b, s)

    def move (self, k, x, mode, d):
        axis = d % 2
        sign = 1 if d > 1 else -1
        f = [0, 0]
        f[axis] = sign * conf.CAR_ACCEL
        self.body.apply_impulse(f)

    def die (self):
        self.level.space.remove(self.body, self.shape)

    def update (self):
        if not self.level.death_bb.contains(self.shape.cache_bb()):
            self.die()
            return True
        v = self.body.velocity
        f = []
        for vi in v:
            fi = -conf.AIR_RESISTANCE * vi
            max_fi = conf.CAR_MASS * vi
            if abs(fi) > abs(max_fi):
                fi = -max_fi
            f.append(fi)
        self.body.apply_impulse(f)
        return False

    def draw (self, screen):
        pg.draw.polygon(screen, (0, 0, 0), self.shape.get_points())