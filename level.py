from math import pi, cos, sin
from random import random as r
from bisect import bisect
from time import time

import pygame
import pymunk as pm
import evthandler as eh

import conf
from obj import Car, Obj

def col_cb (space, arbiter, level):
    if arbiter.is_first_contact:
        # sound
        f = arbiter.total_impulse_with_friction
        f = (f[0] ** 2 + f[1] ** 2) ** .5
        level.game.play_snd('crash', f * conf.CRASH_VOLUME)
        # particles
        amount = f * conf.GRAPHICS * conf.CRASH_PARTICLES
        ptcls = []
        car_shapes = dict((c.shape, c.ID) for c in level.cars)
        for shape in arbiter.shapes:
            if shape in car_shapes:
                ID = car_shapes[shape]
                ptcls.append((conf.CAR_COLOURS[ID], amount))
                ptcls.append((conf.CAR_COLOURS_LIGHT[ID], amount))
            else:
                ptcls.append((conf.OBJ_COLOUR, amount))
                ptcls.append((conf.OBJ_COLOUR_LIGHT, amount))
        level.spawn_particles(arbiter.contacts[0].position, *ptcls)

class Level:
    def __init__ (self, game, event_handler, num_cars = 2, allow_pause = True):
        self.game = game
        self.event_handler = event_handler
        self.num_cars = num_cars
        self.FRAME = conf.FRAME
        w, h = conf.RES
        self.next_spawn = 1
        s = self.space = pm.Space()
        s.add_collision_handler(0, 0, None, None, col_cb, None, self)
        # variables
        self.pos = 0
        self.vel = conf.INITIAL_VEL
        self.accel = conf.LEVEL_ACCEL
        self.scores = [0] * self.num_cars
        self.start_time = time()
        # lines
        l = self.lines = []
        b = conf.BORDER
        for x0, y0, x1, y1 in ((b, b, b, h - b), (b, b, w - b, b),
                               (w - b, b, w - b, h - b),
                               (b, h - b, w - b, h - b)):
            l.append(((x0, y0), (x1, y1)))
        # stuff
        self.death_bb = pm.BB(b, b, w - b, h - b)
        self.outer_bb = pm.BB(0, 0, w, h)
        self.objs = []
        if allow_pause:
            event_handler.add_key_handlers([
                (conf.KEYS_BACK + conf.KEYS_NEXT, self.toggle_paused, eh.MODE_ONDOWN),
                (conf.KEYS_QUIT, self.quit, eh.MODE_ONDOWN)
            ])
        self.paused = False
        self.particles = []
        self.cars = []
        self.won = None
        self.reset(True)

    def reset (self, first = False):
        s = self.space
        try:
            # destroy all objects
            forces = []
            for o in self.objs:
                amount = conf.OBJ_PARTICLES * o.mass
                p = o.body.position
                forces.append((amount, p))
                amount = int(conf.GRAPHICS * amount)
                self.spawn_particles(p,
                    ((conf.OBJ_COLOUR, amount)), ((conf.OBJ_COLOUR_LIGHT, amount)))
                s.remove(o.body, o.shape)
            self.objs = []
            self.explosion_force(*forces)
        except AttributeError:
            self.objs = []
        # objs
        if first:
            self.spawn_players()
        self.frozen = not first
        self.freeze_end = False if first else time() + conf.FREEZE_TIME

    def spawn_players (self, *ps):
        if not ps:
            IDs = [c.ID for c in self.cars]
            ps = [i for i in xrange(self.num_cars) if i not in IDs]
        cs = self.cars
        keys = []
        d = conf.RES[1] / (self.num_cars + 1)
        for i in ps:
            assert not any(c.ID == i for c in cs)
            c = Car(self, i, d * (i + 1))
            cs.append(c)
            for j, k in enumerate(conf.KEYS_MOVE[i]):
                if isinstance(k, int):
                    k = (k,)
                keys.append((k, [(c.move, (j,))], eh.MODE_HELD))
        self.event_handler.add_key_handlers(keys)

    def spawn_particles (self, pos, *colours):
        # colours is a list of (colour, amount) tuples
        pos = list(pos)
        ptcls = self.particles
        max_speed = conf.PARTICLE_SPEED
        max_speed_accel = conf.PARTICLE_SPEED_IF_ACCEL
        life = conf.PARTICLE_LIFE
        max_size = conf.PARTICLE_SIZE
        for c, amount in colours:
            while amount > 0:
                size = int(r() * max_size)
                amount -= size
                angle = r() * 2 * pi
                ac = r() > .5
                speed = r() * (max_speed_accel if ac else max_speed)
                v = [speed * cos(angle), speed * sin(angle)]
                t = int(r() * life)
                ptcls.append((c, list(pos), v, ac, t, size))

    def explosion_force (self, *forces, **kw):
        exclude = kw.get('exclude', [])
        for f, p1 in forces:
            f *= conf.EXPLOSION_FORCE
            # apply to every existing object
            for o in self.cars + self.objs:
                if o in exclude:
                    continue
                p2 = o.body.position
                assert p1 != p2
                r = p2 - p1
                r_sq = r.get_length_sqrd()
                o.body.apply_impulse((f * o.mass / r_sq) * r.normalized())

    def toggle_paused (self, key, t, mods):
        if self.paused:
            # unpause
            self.start_time -= self._stored_time - time()
            del self._drawn_once
            self.paused = False
            self.frozen = False
            pygame.mixer.music.set_volume(conf.MUSIC_VOLUME * .01)
        else:
            # pause
            self._stored_time = time()
            self._drawn_once = 0
            self.paused = True
            self.frozen = True
            pygame.mixer.music.set_volume(conf.PAUSED_MUSIC_VOLUME * .01)

    def quit (self, *args):
        pygame.mixer.music.set_volume(conf.MUSIC_VOLUME * .01)
        self.game.quit_backend()

    def update (self):
        if not self.paused:
            self.space.step(conf.STEP)
            # move background
            self.pos += conf.BG_SPEED * self.vel * conf.STEP
            # update cars
            rm = []
            for c in self.cars:
                if c.update():
                    rm.append(c)
            for c in rm:
                self.cars.remove(c)
        # update particles
        ptcls = []
        a = conf.PARTICLE_ACCEL
        for c, p, v, ac, t, size in self.particles:
            p[0] += v[0]
            p[1] += v[1]
            if ac:
                v[0] += (1 if v[0] > 0 else -1) * a
                v[1] += (1 if v[1] > 0 else -1) * a
            t -= 1
            if t > 0:
                ptcls.append((c, p, v, ac, t, size))
        self.particles = ptcls
        # do nothing else if frozen
        if self.frozen:
            if self.freeze_end:
                if time() >= self.freeze_end:
                    self.freeze_end = False
                    if not self.paused:
                        self.frozen = False
                    self.spawn_players()
                    self.start_time = time()
            return
        # add objs
        self.next_spawn -= r() * conf.SPAWN_RATE * -self.vel
        if self.next_spawn < 0:
            self.next_spawn = 1
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
            lw, lh = conf.RES
            self.objs.append(Obj(self, ID, lw, r() * lh, self.vel))
        # update objs
        rm = []
        for o in self.objs:
            if o.update():
                rm.append(o)
        for o in rm:
            self.objs.remove(o)
        # increase speed
        self.vel -= self.accel
        n = len(self.cars)
        if self.won is None:
            if n < self.num_cars:
                if n < 1:
                    self.reset()
                elif n == 1:
                    winner = self.cars[0]
                    ID = winner.ID
                    self.scores[ID] += 1
                    if self.scores[ID] == conf.TARGET_SCORE:
                        self.won = ID
                        self.won_end = time() + conf.WON_TIME
                    else:
                        self.reset()
            elif self.num_cars == 1:
                self.scores = [int(time() - self.start_time)]
        elif time() >= self.won_end:
            self.quit()

    def draw (self, screen):
        if self.paused and not self.particles:
            if self._drawn_once == 1:
                return False
            else:
                self._drawn_once = 1
        # background
        try:
            img = self.game.img('bg', 'bg.png')
        except pygame.error:
            screen.fill(conf.BG)
        else:
            # tile image
            iw, ih = img.get_size()
            x = int(self.pos) % iw - iw
            w, h = conf.RES
            while x < w:
                y = 0
                while y < h:
                    screen.blit(img, (x, y))
                    y += ih
                x += iw
        # border
        imgs = [self.game.img(ID, ID + '.png') for ID in ('border0', 'border1')]
        bounds = conf.RES
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
        # particles
        for c, p, v, ac, t, size in self.particles:
            screen.fill(c, p + [size, size])
        # scores
        size = conf.SCORES_FONT_SIZE
        x, y = conf.SCORES_EDGE_PADDING
        pad = conf.SCORES_PADDING
        for i, s in enumerate(self.scores):
            s = str(s)
            h = conf.RES[1]
            font = (conf.FONT, size, False)
            c = conf.CAR_COLOURS_LIGHT[i]
            sc = conf.CAR_COLOURS[i]
            font_args = (font, s, c, (sc, conf.SCORES_FONT_SHADOW_OFFSET))
            sfc, lines = self.game.img(s + str(i), font_args, text = True)
            screen.blit(sfc, (x, y))
            x += sfc.get_width() + pad
        # text
        won = self.won
        if self.paused or won is not None:
            font = (conf.FONT, conf.UI_FONT_SIZE, False)
            shadow = [conf.UI_FONT_SHADOW, conf.UI_FONT_SHADOW_OFFSET]
            font_data = [font, conf.PAUSE_TEXT, conf.UI_FONT_COLOUR, shadow, None, 0, False, conf.UI_FONT_SPACING]
            if self.paused:
                # pause screen text
                ID = 'paused'
            else:
                # winner text
                ID = 'won' + str(won)
                font_data[1] = conf.WON_TEXT
                font_data[2] = conf.CAR_COLOURS_LIGHT[won]
                font_data[3][0] = conf.CAR_COLOURS[won]
            sfc, lines = self.game.img(ID, font_data, text = True)
            sw, sh = sfc.get_size()
            w, h = conf.RES
            screen.blit(sfc, ((w - sw) / 2, (h - sh) / 2))
        return True