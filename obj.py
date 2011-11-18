from math import pi

import pygame as pg
import pymunk as pm

import conf

class ObjBase:
    def __init__ (self, level, ID, b, pos, v, pts = None, img_ID = None):
        self.level = level
        self.ID = ID
        b.position = pos
        b.velocity = v
        if img_ID is None:
            img_ID = ID
        try:
            self.img = level.game.img(ID, img_ID + '.png')
            self.centre = self.img.get_rect().center
            self.offset = [min(x[i] for x in pts) for i in (0, 1)]
        except pg.error:
            self.img = None

    def update (self):
        # damp angular velocity
        v = self.body.angular_velocity
        f = -conf.ANGULAR_AIR_RESISTANCE * v
        if abs(f) > abs(v):
            f = -v
        v += f
        self.body.angular_velocity = v

    def draw (self, screen):
        if self.img is None:
            pg.draw.polygon(screen, (0, 0, 0), self.shape.get_points())
        else:
            o = self.offset
            p = list(self.body.position)
            p[0] += o[0]
            p[1] += o[1]
            # rotate image
            angle = self.body.angle
            img = pg.transform.rotozoom(self.img, -180 * angle / pi, 1.)
            rect = img.get_rect()
            # rotated about image centre: realign to match up
            new_c = rect.center
            p[0] += self.centre[0] - new_c[0]
            p[1] += self.centre[1] - new_c[1]
            screen.blit(img, p)

class Obj (ObjBase):
    def __init__ (self, level, ID, m, x, y, vx, w, h):
        self.mass = m
        self.moment = pm.moment_for_box(m, w, h)
        b = self.body = pm.Body(self.mass, self.moment)
        s = self.shape = pm.Poly.create_box(b, (w, h))
        ObjBase.__init__(self, level, ID, b, (x, y), (vx, 0))
        s.elasticity = conf.OBJ_ELAST
        s.friction = conf.OBJ_FRICTION
        level.space.add(b, s)

    def update (self):
        ObjBase.update(self)
        if not self.shape.cache_bb().intersects(self.level.outer_bb):
            self.level.space.remove(self.body, self.shape)
            return True
        else:
            return False

class Car (ObjBase):
    def __init__ (self, level, ID, y):
        pts = conf.OBJ_SHAPES['car']
        self.mass = conf.CAR_MASS
        self.moment = pm.moment_for_poly(conf.CAR_MASS, pts)
        b = self.body = pm.Body(self.mass, self.moment)
        b.position = (200, y)
        b.velocity = (0, 0)
        s = self.shape = pm.Poly(b, pts)
        ObjBase.__init__(self, level, ID, b, (200, y), (0, 0), pts, 'car' + str(ID))
        # TODO: every frame we move set angle towards facing right by an amount proportional to angular distance away
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
        ObjBase.update(self)
        if not self.level.death_bb.contains(self.shape.cache_bb()):
            self.die()
            return True
        v = self.body.velocity
        f = []
        for vi in v:
            fi = -conf.AIR_RESISTANCE * vi
            max_fi = self.mass * vi
            if abs(fi) > abs(max_fi):
                fi = -max_fi
            f.append(fi)
        self.body.apply_impulse(f)
        return False