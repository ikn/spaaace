from math import pi
from random import random, choice

import pygame as pg
import pymunk as pm

import conf

class ObjBase:
    def __init__ (self, level, ID, b, pos, v, pts, *img_IDs):
        self.level = level
        self.ID = ID
        if isinstance(self.ID, int):
            self.colour = conf.CAR_COLOURS_LIGHT[self.ID]
        else:
            self.colour = choice((conf.OBJ_COLOUR_LIGHT, conf.OBJ_COLOUR))
        b.position = pos
        b.velocity = v
        if not img_IDs:
            img_IDs = (ID,)
        try:
            self.imgs = imgs = []
            for img_ID in img_IDs:
                imgs.append(level.game.img(img_ID, img_ID + '.png'))
            w, h = imgs[0].get_size()
            self.centre = imgs[0].get_rect().center
            self.offset = o = [-w / 2, -h / 2]
        except pg.error:
            self.imgs = []
        self._last_angle = None

    def draw (self, screen):
        if conf.GRAPHICS <= conf.NO_IMAGE_THRESHOLD or not self.imgs:
            pg.draw.polygon(screen, self.colour, self.shape.get_points())
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
                imgs, o = self._last_angle_data
            else:
                imgs = []
                for img in self.imgs:
                    # rotate image
                    img = pg.transform.rotozoom(img, -180 * angle / pi, 1.)
                    if img.get_alpha() is None and img.get_colorkey() is None:
                        img = img.convert()
                    else:
                        img = img.convert_alpha()
                    imgs.append(img)
                # get offset
                o = list(self.offset)
                rect = imgs[0].get_rect()
                new_c = rect.center
                o[0] += self.centre[0] - new_c[0]
                o[1] += self.centre[1] - new_c[1]
                # store
                self._last_angle = angle
                self._last_angle_data = (imgs, o)
            p[0] += o[0]
            p[1] += o[1]
            for img in imgs:
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
        pos = (conf.RES[0] / 2, y)
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
        l = self.level
        l.game.play_snd('explode')
        p = self.body.position
        force = conf.DEATH_PARTICLES
        l.explosion_force((force, p), exclude = [self])
        self.level.spawn_particles(p,
            (conf.CAR_COLOURS[self.ID], conf.GRAPHICS * force),
            (conf.CAR_COLOURS_LIGHT[self.ID], conf.GRAPHICS * force)
        )
        self.level.space.remove(self.body, self.shape)

    def update (self):
        # death condition
        if not self.level.death_bb.contains_vect(self.body.position):
            self.die()
            return True
        # move towards facing the right a bit
        self.body.angle = conf.CAR_ANGLE_RESTORATION * self.body.angle
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
