from math import pi
from random import random, choice

import pygame as pg
import pymunk as pm

import conf

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
        self.current_img = 0
        self.gen_imgs()

    def gen_imgs (self):
        img = self.level.game.img
        self.imgs = imgs = []
        for img_ID in self.img_IDs:
            try:
                imgs.append(img(img_ID + '.png', conf.SCALE))
            except pg.error:
                pass
        try:
            w, h = imgs[0].get_size()
        except IndexError:
            pass
        else:
            self.centre = imgs[0].get_rect().center
            self.offset = [-w / 2, -h / 2]
            self._last_angle = None
            self._img_cache = {}
            self._offset_cache = None

    def set_img (self, i):
        self.current_img = i
        self._img_cache = {}
        self._offset_cache = None

    def _draw_imgs (self, screen, *data):
        angle = self.body.angle
        last = self._last_angle
        p = pm.Vec2d(self.body.position)
        g = conf.GRAPHICS
        max_t = conf.MAX_ROTATE_THRESHOLD
        if g == 0:
            threshold = max_t
        else:
            threshold = min(conf.ROTATE_THRESHOLD / g ** conf.ROTATE_THRESHOLD_POWER, max_t)
        angle = threshold * int(round(angle / threshold))
        # get images
        imgs = []
        cache = self._img_cache
        for ID, src in data:
            # retrieve
            img = cache.get(ID, None)
            if last != angle or img is None:
                # generate rotated image
                if conf.GRAPHICS <= conf.UNFILTERED_ROTATE_THRESHOLD:
                    img = pg.transform.rotate(src, -180 * angle / pi)
                else:
                    img = pg.transform.rotozoom(src, -180 * angle / pi, 1)
                if img.get_alpha() is None and img.get_colorkey() is None:
                    img = img.convert()
                else:
                    img = img.convert_alpha()
                self._img_cache[ID] = img
            imgs.append(img)
        # retrieve offset
        o = self._offset_cache
        if last != angle or o is None:
            # compute offset
            o = pm.Vec2d(self.offset)
            rect = imgs[0].get_rect()
            new_c = rect.center
            o += self.centre
            o -= new_c
            self._offset_cache = o
        if last != angle:
            # store angle
            self._last_angle = angle
        p *= conf.SCALE
        p += o
        for img in imgs:
            screen.blit(img, p)

    def draw (self, screen):
        if conf.GRAPHICS <= conf.NO_IMAGE_THRESHOLD or not self.imgs:
            pts = [x * conf.SCALE for x in self.shape.get_points()]
            pg.draw.polygon(screen, self.colour, pts)
        else:
            if self.level.dirty:
                self.gen_imgs()
            self._draw_imgs(screen, ('main', self.imgs[self.current_img]))

class Obj (ObjBase):
    def __init__ (self, level, ID, p, vx):
        self.ID = ID
        self.colour = choice((conf.OBJ_COLOUR_LIGHT, conf.OBJ_COLOUR))
        pts = conf.OBJ_SHAPES[ID]
        width, height = [max(i[j] for i in pts) - min(i[j] for i in pts) for j in (0, 1)]
        self.mass = conf.OBJ_DENSITY * (width * height) ** 1.5
        # randomise angle/vel
        angle = random() * 2 * pi
        ang_vel = (random() - .5) * conf.OBJ_ANG_VEL
        v = (vx + (random() - .5) * conf.OBJ_VEL, (random() - .5) * conf.OBJ_VEL)
        ObjBase.__init__(self, level, ID, p, angle, v, ang_vel, pts,
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
        self.colours = conf.ALL_CAR_COLOURS[self.ID]
        pts = conf.OBJ_SHAPES['car']
        self.mass = conf.CAR_MASS
        y = (conf.SIZE[1] / (level.num_cars + 1)) * (ID + 1)
        pos = (conf.SIZE[0] / 2, y)
        ObjBase.__init__(self, level, 'car', pos, 0, (0, 0), 0, pts,
                         conf.CAR_ELAST, conf.CAR_FRICTION,
                         *('car{0}-{1}'.format(ID, i) for i in xrange(4)))
        self.dead = False
        self.dying = False
        self.health = self.max_health = conf.CAR_HEALTH_BASE * conf.CAR_HEALTH_MULTIPLIER
        self.powerups = {}

    def gen_imgs (self):
        ObjBase.gen_imgs(self)
        img = self.level.game.img
        self.p_imgs = imgs = {}
        for p in conf.POWERUPS:
            try:
                imgs[p] = img('car-{0}.png'.format(p), conf.SCALE)
            except pg.error:
                pass

    def spawn (self):
        y = (conf.SIZE[1] / (self.level.num_cars + 1)) * (self.ID + 1)
        self.body.position = (conf.SIZE[0] / 2, y)
        self.body.angle = 0
        self.body.velocity = (0, 0)
        self.body.angular_velocity = 0
        if self.dead:
            self.level.space.add(self.body, self.shape)
            self.dead = False
        self.dying = False
        self.health = self.max_health
        self.set_img(0)
        self.invincible = False
        self.body.mass = self.mass = conf.CAR_MASS
        self.power_multiplier = 1.
        self.force_multiplier = 1.

    def move (self, f):
        if not self.level.paused:
            f = [f_i * conf.CAR_ACCEL * self.force_multiplier * self.power_multiplier for f_i in f]
            self.body.apply_impulse(f, conf.CAR_FORCE_OFFSET)

    def _move (self, k, x, mode, d):
        axis = d % 2
        sign = 1 if d > 1 else -1
        f = [0, 0]
        f[axis] = sign
        self.move(f)

    def update_img (self):
        h = self.health
        steps = conf.CAR_DAMAGE_STEPS + (0,)
        mx = self.max_health
        i = steps.index(max(x for x in steps if h > x * mx))
        if i != self.current_img:
            self.set_img(i)

    def damage (self, amount):
        if not conf.CAR_HEALTH_ON or self.invincible:
            return
        self.health -= amount
        mx = self.max_health
        if self.health <= 0:
            self.dying = True
        else:
            self.update_img()

    def heal (self, amount):
        self.health = min(self.health + amount, self.max_health)
        self.update_img()

    def powerup (self, p):
        ID = p.ID
        self.level.game.play_snd('powerup')
        if ID in self.powerups:
            self.powerups[ID] += conf.POWERUP_TIME[ID]
        else:
            if ID not in ('health', 'bomb'):
                self.powerups[ID] = conf.POWERUP_TIME[ID]
            # add effects
            if ID == 'invincible':
                self.invincible = True
            elif ID == 'heavy':
                self.mass *= conf.HEAVY_MULTIPLIER
                self.body.mass = self.mass
                self.force_multiplier = conf.HEAVY_MULTIPLIER
            elif ID == 'fast':
                self.power_multiplier = conf.FAST_MULTIPLIER
            elif ID == 'health':
                self.heal(conf.HEALTH_INCREASE * self.max_health)
            elif ID == 'bomb':
                self.level.game.play_snd('explode', 1.5)
                self.level.explosion_force((conf.BOMB_FORCE, p.body.position), exclude = (self, p))

    def end_powerup (self, p):
        self.level.game.play_snd('powerdown')
        del self.powerups[p]
        if p == 'invincible':
            self.invincible = False
        elif p == 'heavy':
            self.body.mass = self.mass = conf.CAR_MASS
            self.force_multiplier = 1
        elif p == 'fast':
            self.power_multiplier = 1

    def die (self):
        l = self.level
        l.game.play_snd('explode')
        p = self.body.position
        force = conf.CAR_EXPLOSION_FORCE
        amount = conf.GRAPHICS * conf.DEATH_PARTICLES * conf.SCALE
        l.explosion_force((force, p), exclude = (self,))
        l.spawn_particles(p * conf.SCALE,
            (conf.CAR_COLOURS[self.ID], amount),
            (conf.CAR_COLOURS_LIGHT[self.ID], amount)
        )
        l.space.remove(self.body, self.shape)
        self.powerups = {}
        self.dead = True

    def update (self):
        # death condition
        if not self.level.death_bb.contains_vect(self.body.position) or self.dying:
            self.die()
            return True
        # powerups
        ps = self.powerups
        rm = []
        for p in self.powerups:
            ps[p] -= 1
            if ps[p] <= 0:
                rm.append(p)
        for p in rm:
            self.end_powerup(p)
        # move towards facing the right a bit
        self.body.angle = conf.CAR_ANGLE_RESTORATION * self.body.angle
        # damp angular velocity
        v = self.body.angular_velocity
        f = -conf.ANGULAR_AIR_RESISTANCE * self.force_multiplier * v
        if abs(f) > abs(v):
            f = -v
        v += f
        self.body.angular_velocity = v
        # damp movement
        v = self.body.velocity
        f = []
        for vi in v:
            fi = -conf.AIR_RESISTANCE * self.force_multiplier * vi
            max_fi = self.mass * vi
            if abs(fi) > abs(max_fi):
                fi = -max_fi
            f.append(fi)
        self.body.apply_impulse(f, conf.CAR_FORCE_OFFSET)
        return False

    def draw (self, screen):
        ps = self.powerups
        if conf.GRAPHICS <= conf.NO_IMAGE_THRESHOLD or not self.imgs:
            pts = [x * conf.SCALE for x in self.shape.get_points()]
            pg.draw.polygon(screen, self.colours[self.current_img], pts)
            # powerups
            if ps:
                w = max(int(round(conf.SCALE * conf.POWERUP_BORDER_WIDTH)), 1)
                pos = self.body.position * conf.SCALE
                for p in ps:
                    # grow polygon
                    grow = 1 + (conf.POWERUP_BORDER_OFFSET[p] + float(w) / 2) / 30
                    new_pts = [(x - pos) * grow + pos for x in pts]
                    pg.draw.polygon(screen, conf.POWERUP_COLOURS_LIGHT[p], new_pts, w)
        else:
            if self.level.dirty:
                self.gen_imgs()
            self._draw_imgs(screen, ('main', self.imgs[self.current_img]),
                            *((p, img) for p, img in self.p_imgs.iteritems() if p in ps))

class Powerup:
    def __init__ (self, level, ID, p, vx):
        self.level = level
        self.ID = ID
        self.mass = conf.POWERUP_MASS
        self.moment = pm.moment_for_circle(self.mass, 0, conf.POWERUP_SIZE)
        b = self.body = pm.Body(self.mass, self.moment)
        b.position = p
        b.velocity = (vx + (random() - .5) * conf.OBJ_VEL, (random() - .5) * conf.OBJ_VEL)
        s = self.shape = pm.Circle(b, conf.POWERUP_SIZE)
        s.elasticity = conf.OBJ_ELAST
        s.friction = conf.OBJ_FRICTION
        level.space.add(b, s)
        self.dying = False
        self.gen_img()

    def gen_img (self):
        try:
            self.img = self.level.game.img('powerup-{0}.png'.format(self.ID), conf.SCALE)
            w, h = self.img.get_size()
            self.offset = pm.Vec2d((-w / 2, -h / 2))
        except pg.error:
            self.img = None

    def die (self):
        p = self.body.position
        ptcls = conf.BOMB_PARTICLES if self.ID == 'bomb' else conf.POWERUP_PARTICLES
        amount = conf.GRAPHICS * ptcls * conf.SCALE
        self.level.spawn_particles(p * conf.SCALE,
            (conf.POWERUP_COLOURS[self.ID], amount),
            (conf.POWERUP_COLOURS_LIGHT[self.ID], amount)
        )
        self.dying = True

    def update (self):
        if not self.shape.cache_bb().intersects(self.level.powerup_bb) or self.dying:
            self.level.space.remove(self.body, self.shape)
            return True
        else:
            return False

    def draw (self, screen):
        p = [int(round(x * conf.SCALE)) for x in self.body.position]
        if conf.GRAPHICS <= conf.NO_IMAGE_THRESHOLD or self.img is None:
            r = int(round(conf.POWERUP_SIZE * conf.SCALE))
            pg.draw.circle(screen, conf.POWERUP_COLOURS_LIGHT[self.ID], p, r)
        else:
            if self.level.dirty:
                self.gen_img()
            screen.blit(self.img, p + self.offset)