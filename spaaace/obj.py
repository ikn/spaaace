from math import pi
from random import random, choice

import pygame as pg
import pymunk as pm

import conf

# TODO: only move cars once per frame

class ObjBase:
    def __init__ (self, level, ID, pos, angle, v, ang_vel, pts, elast,
                  friction, *img_IDs):
        self.level = level
        self.moment = pm.moment_for_poly(self.mass, pts)
        b = self.body = pm.Body(self.mass, self.moment)
        b.velocity = v
        b.angle = angle
        b.angular_velocity = ang_vel
        s = self.shape = pm.Poly(b, pts)
        if ID != 'car':
            # make sure we don't start OoB (need new points after rotation)
            new_pts = s.get_points()
            pos = (pos[0] - min(i[0] for i in new_pts) - 1, pos[1])
        b.position = pos
        s.elasticity = elast
        s.friction = friction
        level.space.add(b, s)
        self.img_IDs = img_IDs
        self.gen_imgs()

    def gen_imgs (self):
        try:
            self.imgs = imgs = []
            for img_ID in self.img_IDs:
                imgs.append(self.level.game.img(img_ID + '.png', conf.SCALE))
            w, h = imgs[0].get_size()
            self.centre = imgs[0].get_rect().center
            self.offset = o = [-w / 2, -h / 2]
        except pg.error:
            self.imgs = []
        self._last_angle = None

    def draw (self, screen):
        if conf.GRAPHICS <= conf.NO_IMAGE_THRESHOLD or not self.imgs:
            pts = [x * conf.SCALE for x in self.shape.get_points()]
            pg.draw.polygon(screen, self.colour, pts)
        else:
            if self.level.dirty:
                self.gen_imgs()
            angle = self.body.angle
            last = self._last_angle
            p = list(self.body.position)
            g = conf.GRAPHICS
            max_t = conf.MAX_ROTATE_THRESHOLD
            if g == 0:
                threshold = max_t
            else:
                threshold = min(conf.ROTATE_THRESHOLD / g ** conf.ROTATE_THRESHOLD_POWER, max_t)
            angle = threshold * int(round(angle / threshold))
            if last is not None and last == angle:
                # retrieve
                imgs, o = self._last_angle_data
            else:
                imgs = []
                for img in self.imgs:
                    # rotate image
                    if conf.GRAPHICS <= conf.UNFILTERED_ROTATE_THRESHOLD:
                        img = pg.transform.rotate(img, -180 * angle / pi)
                    else:
                        img = pg.transform.rotozoom(img, -180 * angle / pi, 1)
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
            p[0] *= conf.SCALE
            p[1] *= conf.SCALE
            p[0] += o[0]
            p[1] += o[1]
            for img in imgs:
                screen.blit(img, p)

class Obj (ObjBase):
    def __init__ (self, level, ID, x, y, vx):
        self.ID = ID
        self.colour = choice((conf.OBJ_COLOUR_LIGHT, conf.OBJ_COLOUR))
        pts = conf.OBJ_SHAPES[ID]
        width, height = [max(i[j] for i in pts) - min(i[j] for i in pts) for j in (0, 1)]
        self.mass = conf.OBJ_DENSITY * (width * height) ** 1.5
        # randomise angle/vel
        angle = random() * 2 * pi
        ang_vel = (random() - .5) * conf.OBJ_ANG_VEL
        ObjBase.__init__(self, level, ID, (x, y), angle, (vx, 0), ang_vel, pts,
                         conf.OBJ_ELAST, conf.OBJ_FRICTION, ID)

    def update (self):
        if not self.shape.cache_bb().intersects(self.level.outer_bb):
            self.level.space.remove(self.body, self.shape)
            return True
        else:
            return False

class Car (ObjBase):
    def __init__ (self, level, ID):
        self.ID = ID
        self.colour = conf.CAR_COLOURS_LIGHT[self.ID]
        pts = conf.OBJ_SHAPES['car']
        self.mass = conf.CAR_MASS
        y = (conf.SIZE[1] / (level.num_cars + 1)) * (ID + 1)
        pos = (conf.SIZE[0] / 2, y)
        ObjBase.__init__(self, level, 'car', pos, 0, (0, 0), 0, pts,
                         conf.CAR_ELAST, conf.CAR_FRICTION, 'car' + str(ID))
        self.dead = False

    def spawn (self):
        y = (conf.SIZE[1] / (self.level.num_cars + 1)) * (self.ID + 1)
        self.body.position = (conf.SIZE[0] / 2, y)
        self.body.angle = 0
        self.body.velocity = (0, 0)
        self.body.angular_velocity = 0
        if self.dead:
            self.level.space.add(self.body, self.shape)
            self.dead = False

    def move (self, f):
        f = [f_i * conf.CAR_ACCEL for f_i in f]
        self.body.apply_impulse(f, conf.CAR_FORCE_OFFSET)

    def _move (self, k, x, mode, d):
        axis = d % 2
        sign = 1 if d > 1 else -1
        f = [0, 0]
        f[axis] = sign
        self.move(f)

    def die (self):
        l = self.level
        l.game.play_snd('explode')
        p = self.body.position
        force = conf.CAR_EXPLOSION_FORCE
        amount = conf.GRAPHICS * conf.DEATH_PARTICLES * conf.SCALE
        l.explosion_force((force, p), exclude = [self])
        self.level.spawn_particles(p * conf.SCALE,
            (conf.CAR_COLOURS[self.ID], amount),
            (conf.CAR_COLOURS_LIGHT[self.ID], amount)
        )
        self.level.space.remove(self.body, self.shape)
        self.dead = True

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