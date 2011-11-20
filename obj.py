from math import pi
from random import random

import pygame as pg
import pymunk as pm

import conf

class ObjBase:
    def __init__ (self, level, ID, b, pos, v, pts, img_ID = None):
        self.level = level
        self.ID = ID
        b.position = pos
        b.velocity = v
        if img_ID is None:
            img_ID = ID
        try:
            self.img = level.game.img(ID, img_ID + '.png')
            w, h = self.img.get_size()
            self.centre = self.img.get_rect().center
            self.offset = o = [-w / 2, -h / 2]
        except pg.error:
            self.img = None
        self._last_angle = None

    def update (self):
        pass

    def draw (self, screen):
        if self.img is None:
            pg.draw.polygon(screen, (0, 0, 0), self.shape.get_points())
        else:
            angle = self.body.angle
            last = self._last_angle
            p = list(self.body.position)
            g = conf.GRAPHICS
            max_t = conf.MAX_ROTATE_THRESHOLD
            if g == 0:
                threshold = max_t
            else:
                threshold = min(conf.ROTATE_THRESHOLD / g ** conf.ROTATE_THRESHOLD_POWER, max_t)
            if last is not None and abs(last - angle) < threshold:
                # retrieve
                img, o = self._last_angle_data
            else:
                # rotate image
                o = list(self.offset)
                img = pg.transform.rotozoom(self.img, -180 * angle / pi, 1.)
                rect = img.get_rect()
                # rotated about image centre: realign to match up
                new_c = rect.center
                o[0] += self.centre[0] - new_c[0]
                o[1] += self.centre[1] - new_c[1]
                # store
                self._last_angle = angle
                self._last_angle_data = (img, o)
            p[0] += o[0]
            p[1] += o[1]
            screen.blit(img, p)

class Obj (ObjBase):
    def __init__ (self, level, ID, x, y, vx):
        pts = conf.OBJ_SHAPES[ID]
        width, height = [max(i[j] for i in pts) - min(i[j] for i in pts) for j in (0, 1)]
        self.mass = conf.OBJ_DENSITY * (width * height) ** 1.5
        self.moment = pm.moment_for_poly(self.mass, pts)
        b = self.body = pm.Body(self.mass, self.moment)
        # randomise angle/vel
        b.angle = random() * 2 * pi
        b.angular_velocity = (random() - .5) * conf.OBJ_ANG_VEL
        s = self.shape = pm.Poly(b, pts)
        # make sure we don't start OoB (need new points after rotation)
        new_pts = s.get_points()
        x -= min(i[0] for i in new_pts) + 1
        ObjBase.__init__(self, level, ID, b, (x, y), (vx, 0), pts)
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
        s = self.shape = pm.Poly(b, pts)
        pos = (level.game.res[0] / 2, y)
        ObjBase.__init__(self, level, ID, b, pos, (0, 0), pts, 'car' + str(ID))
        s.elasticity = conf.CAR_ELAST
        s.friction = conf.CAR_FRICTION
        level.space.add(b, s)

    def move (self, k, x, mode, d):
        axis = d % 2
        sign = 1 if d > 1 else -1
        f = [0, 0]
        f[axis] = sign * conf.CAR_ACCEL
        self.body.apply_impulse(f, conf.CAR_FORCE_OFFSET)

    def die (self):
        self.level.game.play_snd('explode')
        self.level.spawn_particles(self.body.position,
            (conf.CAR_COLOURS[self.ID], conf.GRAPHICS * conf.DEATH_PARTICLES),
            (conf.CAR_COLOURS_LIGHT[self.ID], conf.GRAPHICS * conf.DEATH_PARTICLES)
        )
        self.level.space.remove(self.body, self.shape)

    def update (self):
        # death condition
        if not self.level.death_bb.contains_vect(self.body.position):
            self.die()
            return True
        # move towards facing the right a bit
        self.body.angle = conf.CAR_ANGLE_RESTORATION * self.body.angle
        ObjBase.update(self)
        # damp angular velocity
        v = self.body.angular_velocity
        f = -conf.ANGULAR_AIR_RESISTANCE * v
        if abs(f) > abs(v):
            f = -v
        v += f
        self.body.angular_velocity = v
        # damp movement
        v = self.body.velocity
        f = []
        for vi in v:
            fi = -conf.AIR_RESISTANCE * vi
            max_fi = self.mass * vi
            if abs(fi) > abs(max_fi):
                fi = -max_fi
            f.append(fi)
        self.body.apply_impulse(f, conf.CAR_FORCE_OFFSET)
        return False