import pygame as pg
import pymunk as pm

from random import random

import conf

class Obj:
    def __init__ (self, level, m, x, y, vx, w, h):
        self.level = level
        b = self.body = pm.Body(m, pm.moment_for_box(m, w, h))
        b.position = (x, y)
        b.velocity = (vx, 0)
        s = self.shape = pm.Poly.create_box(b, (w, h))
        s.elasticity = conf.OBJ_ELAST
        s.friction = conf.OBJ_FRICTION
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
        s = self.shape = pm.Poly(b, ((25, 0), (13, 35), (8, 35), (-25, 0), (8, -35), (13, -35)))
        s.elasticity = conf.CAR_ELAST
        s.friction = conf.CAR_FRICTION
        level.space.add(b, s)

    def move (self, k, x, mode, d):
        if self.level.paused and not self.level.can_move:
            return
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