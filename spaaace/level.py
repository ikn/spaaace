from math import pi, cos, sin
from random import random as r, randint, triangular
from bisect import bisect
from time import time

import pygame
import pymunk as pm
from ext import evthandler as eh

import conf
from obj import Car, Obj, Powerup
import title

ir = lambda x: int(round(x))
def irs (x):
    if isinstance(x, (float, int)):
        return ir(x * conf.SCALE)
    else:
        return tuple(ir(i) * conf.SCALE for i in x)

def begin_col_cb (space, arbiter, level):
    # determine colliding objects' types
    powerup_shapes = level.powerup_shapes
    shapes = arbiter.shapes[:2]
    # if one is a powerup, layers + groups means the other will be a car
    powerups = [shape in powerup_shapes for shape in shapes]
    if any(powerups):
        i = powerups.index(True)
        p = powerup_shapes[shapes[i]]
        try:
            level.car_shapes[shapes[not i]].powerup(p)
        except KeyError:
            return True
        p.die()
        return False
    else:
        return True

def post_col_cb (space, arbiter, level):
    if arbiter.is_first_contact:
        # sound
        f = arbiter.total_impulse_with_friction
        f = (f[0] ** 2 + f[1] ** 2) ** .5
        level.game.play_snd('crash', f * conf.CRASH_VOLUME)
        # particles
        shapes = arbiter.shapes
        powerup_shapes = level.powerup_shapes
        car_shapes = level.car_shapes
        all_cars = all(shape in car_shapes for shape in shapes)
        colours = []
        for shape in shapes:
            if shape in car_shapes:
                c = car_shapes[shape]
                ID = c.ID
                # damage
                if not all_cars:
                    c.damage(f)
                colours += [conf.CAR_COLOURS[ID], conf.CAR_COLOURS_LIGHT[ID]]
            elif shape in powerup_shapes:
                ID = powerup_shapes[shape].ID
                colours += [conf.POWERUP_COLOURS[ID], conf.POWERUP_COLOURS_LIGHT[ID]]
            else:
                colours += [conf.OBJ_COLOUR, conf.OBJ_COLOUR_LIGHT]
        amount = f * conf.GRAPHICS * conf.CRASH_PARTICLES * conf.SCALE
        level.spawn_particles(arbiter.contacts[0].position * conf.SCALE,
                              *((colour, amount) for colour in colours))

class Level:
    def __init__ (self, game, event_handler, num_cars = 2, allow_pause = True):
        self.game = game
        event_handler.add_event_handlers({
            pygame.JOYAXISMOTION: self._joy_motion,
            pygame.JOYBUTTONDOWN: self.select
        })
        event_handler.add_key_handlers([
            (conf.KEYS_NEXT, self.select, eh.MODE_ONDOWN),
        ] + [
            (
                (conf.KEYS_MOVE[0][i],),
                [(lambda k, t, m, i: self.menu_move(i), (i,))],
                eh.MODE_ONDOWN_REPEAT,
                ir(conf.FPS * conf.MENU_REPEAT_DELAY),
                ir(conf.FPS * conf.MENU_REPEAT_RATE)
            ) for i in xrange(4)
        ])
        self.event_handler = event_handler
        self.num_cars = num_cars
        self.FRAME = conf.FRAME
        pw, ph = conf.SIZE
        w, h = conf.RES
        s = self.space = pm.Space()
        s.collision_bias = 0
        s.add_collision_handler(0, 0, begin_col_cb, None, post_col_cb, None, self)
        # variables
        self.pos = 0
        self.vel = conf.INITIAL_VEL
        self.next_spawn = ir(conf.FPS * triangular() / (-self.vel * conf.SPAWN_RATE))
        n = self.num_cars if self.num_cars > 0 else 2
        self.next_p_spawn = ir(conf.FPS * triangular() / (-self.vel * conf.POWERUP_SPAWN_RATE * n))
        self.powerup_group = 0
        self.accel = conf.LEVEL_ACCEL
        self.scores = [0] * self.num_cars
        self.frames = 0
        # lines
        b = conf.BORDER
        r = conf.POWERUP_SIZE
        self.death_bb = pm.BB(b, b, pw - b, ph - b)
        self.outer_bb = pm.BB(0, 0, pw, ph)
        self.powerup_bb = pm.BB(-r, -r, pw + r, ph + r)
        # stuff
        self.powerups = []
        self.powerup_shapes = {}
        self.objs = []
        if allow_pause:
            event_handler.add_event_handlers({
                pygame.JOYBUTTONDOWN: self.toggle_paused,
            })
            event_handler.add_key_handlers([
                (conf.KEYS_BACK, self.toggle_paused, eh.MODE_ONDOWN)
            ])
        self.paused = False
        self.particles = []
        num_joys = pygame.joystick.get_count()
        self.num_joys = min(num_joys, self.num_cars)
        self.joys = []
        controls = conf.JOY_CONTROLS
        for i in xrange(min(num_joys, max(self.num_cars, 1))):
            j = pygame.joystick.Joystick(i)
            j.init()
            name = j.get_name()
            print 'found controller: \'{0}\''.format(name)
            self.joys.append(controls.get(name, conf.FB_JOY_CONTROLS))
        self.won = None
        self.dirty = True
        self.options = None
        self.pause_options = (
            ('Paused', 0),
            ('Continue', 1, self.unpause),
            ('Quit', 1, self.quit)
        )
        self._menu_moved = [0, 0]
        self.won_options = (('Winner', 0),)
        self.reset(True)

    def reset (self, first = False):
        s = self.space
        # destroy all objects
        forces = []
        for o in self.objs:
            force = conf.OBJ_EXPLOSION_FORCE * o.mass
            p = o.body.position
            forces.append((force, p))
            amount = irs(conf.GRAPHICS * conf.OBJ_PARTICLES * o.mass)
            self.spawn_particles(p * conf.SCALE, (conf.OBJ_COLOUR, amount),
                                    (conf.OBJ_COLOUR_LIGHT, amount))
            s.remove(o.body, o.shape)
        self.objs = []
        self.explosion_force(*forces)
        # objs
        if first:
            self.create_players()
            self.spawn_players()
        self.frozen = not first
        self.freeze_end = 0 if first else conf.FREEZE_TIME

    def create_players (self):
        cs = self.all_cars = []
        self.joy_vals = [[0, 0] for i in xrange(self.num_joys)]
        keys = []
        used_joys = 0
        used_keys = 0
        for i in xrange(self.num_cars):
            c = Car(self, i)
            cs.append(c)
            # try to use controller
            if used_joys < self.num_joys:
                used_joys += 1
            else:
                for j, k in enumerate(conf.KEYS_MOVE[used_keys]):
                    if isinstance(k, int):
                        k = (k,)
                    keys.append((k, [(c._move, (j,))], eh.MODE_HELD))
                used_keys += 1
        self.event_handler.add_key_handlers(keys)
        self.cars = []
        self.car_shapes = {}

    def spawn_players (self, *ps):
        if not ps:
            IDs = [c.ID for c in self.cars]
            ps = [i for i in xrange(self.num_cars) if i not in IDs]
        cs = self.cars
        ss = self.car_shapes
        for i in ps:
            assert not any(c.ID == i for c in cs)
            c = self.all_cars[i]
            c.spawn()
            cs.append(c)
            ss[c.shape] = c

    def spawn_particles (self, pos, *colours):
        # colours is a list of (colour, amount) tuples
        pos = list(pos)
        ptcls = self.particles
        max_speed = conf.PARTICLE_SPEED * conf.SCALE
        max_speed_accel = conf.PARTICLE_SPEED_IF_ACCEL * conf.SCALE
        life = conf.PARTICLE_LIFE
        max_size = irs(conf.PARTICLE_SIZE)
        for c, amount in colours:
            while amount > 0:
                size = randint(1, max_size)
                amount -= size
                angle = r() * 2 * pi
                ac = randint(0, 1)
                speed = r() * (max_speed_accel if ac else max_speed)
                v = [speed * cos(angle), speed * sin(angle)]
                t = randint(0, life)
                ptcls.append((c, list(pos), v, ac, t, size))

    def explosion_force (self, *forces, **kw):
        exclude = kw.get('exclude', [])
        for f, p1 in forces:
            f *= conf.EXPLOSION_FORCE
            # apply to every existing object
            for o in self.cars + self.objs + self.powerups:
                if o in exclude:
                    continue
                p2 = o.body.position
                r = p2 - p1
                r_sq = max(r.get_length_sqrd(), 10 ** -10)
                o.body.apply_impulse((f * o.mass / r_sq) * r.normalized())

    def menu_move (self, d = None, axis = None, sign = None):
        if self.options is None or self.current_opt is None:
            return
        if axis is None:
            axis = d % 2
            sign = 1 if d > 1 else -1
        if axis == 0:
            # spin
            o = self.options[self.current_opt]
            o_type = o[1]
            if o_type not in (2, 3):
                # not a spin option
                return
            if o_type == 2:
                v, mn, mx, step = o[2:6]
                v += sign * step
                if mx is not None:
                    v = min(v, mx)
                if mn is not None:
                    v = max(v, mn)
            else:
                v, vs = o[2:4]
                v += sign
                v %= len(vs)
            o[2] = v
            # call callback
            i = 7 if o_type == 2 else 4
            o[i](v, *o[i + 1:])
        else:
            # move selection
            sels = self.selectable_opts
            i = sels.index(self.current_opt)
            i += sign
            i %= len(sels)
            self.current_opt = sels[i]
        if self.paused:
            self._drawn_once = False

    def select (self, evt = None, *args):
        if isinstance(evt, pygame.event.EventType):
            if not (evt.type == pygame.JOYBUTTONDOWN and \
                    evt.button in self.joys[evt.joy]['next']):
                return
        if self.options is None or self.current_opt is None:
            return
        o = self.options[self.current_opt]
        if o[1] == 1:
            o[2](*o[3:])
        # else not a button

    def _joy_motion (self, evt = None):
        i = evt.joy
        try:
            axis = self.joys[i]['move'].index(evt.axis)
        except ValueError:
            pass
        else:
            v = evt.value
            if i == 0:
                m = self._menu_moved
                if m[axis]:
                    if abs(v) < conf.JOY_STOP_MOVE:
                        m[axis] = 0
                elif abs(v) > conf.JOY_START_MOVE:
                    m[axis] = 1
                    self.menu_move(None, axis, 1 if v > 0 else -1)
            if i < self.num_joys:
                self.joy_vals[i][axis] = v

    def init_opts (self, options):
        self.options = [list(o) for o in options]
        selectable = [i for i, o in enumerate(options) if o[1] != 0]
        self.current_opt = selectable[0] if selectable else None
        self.selectable_opts = selectable

    def uninit_opts (self):
        self.options = None
        del self.current_opt

    def pause (self, evt = None, *args):
        if not self.paused and self.won is None:
            self.init_opts(self.pause_options)
            self._drawn_once = False
            self.paused = True
            self.frozen = True
            pygame.mixer.music.set_volume(conf.PAUSED_MUSIC_VOLUME * .01)

    def unpause (self, *args):
        if self.paused:
            del self._drawn_once
            self.uninit_opts()
            self.paused = False
            self.frozen = False
            pygame.mixer.music.set_volume(conf.MUSIC_VOLUME * .01)

    def toggle_paused (self, evt = None, *args):
        if isinstance(evt, pygame.event.EventType):
            if not (evt.type == pygame.JOYBUTTONDOWN and \
                    evt.button in self.joys[evt.joy]['back']):
                return
        if self.paused:
            self.unpause()
        else:
            self.pause()

    def quit (self, *args):
        if not self.paused and self.won is None:
            return
        # increase music volume again
        pygame.mixer.music.set_volume(conf.MUSIC_VOLUME * .01)
        self.game.quit_backend(no_quit = True)
        self.game.start_backend(title.Title, self.num_cars)

    def update (self):
        if not self.paused:
            # move cars
            for i, f in enumerate(self.joy_vals):
                c = self.all_cars[i]
                if c in self.cars:
                    c.move(f)
            # step physics
            self.space.step(conf.STEP)
            # move background
            self.pos += conf.BG_SPEED * self.vel * conf.STEP * conf.SCALE
            # update cars and powerups
            for objs, shapes in ((self.cars, self.car_shapes), (self.powerups, self.powerup_shapes)):
                rm = []
                for o in objs:
                    if o.update():
                        rm.append(o)
                for o in rm:
                    objs.remove(o)
                    del shapes[o.shape]
            # add powerups
            self.next_p_spawn -= 1
            if self.next_p_spawn <= 0:
                n = self.num_cars if self.num_cars > 0 else 2
                t = ir(conf.FPS * triangular() / (-self.vel * conf.POWERUP_SPAWN_RATE * n))
                if not self.powerup_group:
                    if r() < conf.POWERUP_GROUP_RATE:
                        self.powerup_group = randint(1, conf.POWERUP_GROUP_SIZE - 1)
                if self.powerup_group:
                    self.powerup_group -= 1
                    t /= conf.POWERUP_GROUP_SPAWN_RATE_MULTIPLIER
                self.next_p_spawn = t
                # choose obj type
                l = list(conf.POWERUP_WEIGHTINGS)
                if not conf.CAR_HEALTH_ON:
                    l[conf.POWERUPS.index('invincible')] = 0
                cumulative = []
                last = 0
                for x in l:
                    last += x
                    cumulative.append(last)
                index = min(bisect(cumulative, cumulative[-1] * r()), len(l) - 1)
                ID = conf.POWERUPS[index]
                # create
                lw, lh = conf.SIZE
                p = Powerup(self, ID, (lw, r() * lh), self.vel)
                self.powerups.append(p)
                self.powerup_shapes[p.shape] = p
        # update particles
        ptcls = []
        a = conf.PARTICLE_ACCEL * conf.SCALE
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
                self.freeze_end -= 1
                if self.freeze_end == 0:
                    if not self.paused:
                        self.frozen = False
                    self.spawn_players()
                    self.frames = 0
            return
        self.frames += 1
        # add objs
        self.next_spawn -= 1
        if self.next_spawn <= 0:
            self.next_spawn = ir(conf.FPS * triangular() / (-self.vel * conf.SPAWN_RATE))
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
            lw, lh = conf.SIZE
            self.objs.append(Obj(self, ID, (lw, r() * lh), self.vel))
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
                        self.init_opts(self.won_options)
                        self.won_end = conf.WON_TIME
                    else:
                        self.reset()
            elif self.num_cars == 1:
                self.scores = [int(self.frames * conf.FRAME)]
        else:
            self.won_end -= 1
            if self.won_end == 0:
                self.quit()

    def draw_options (self, screen, rect, colours = (None, None, None, None),
                      **spin_vals):
        # setup
        default_cs = (conf.UI_FONT_COLOUR, conf.UI_FONT_COLOUR_SEL,
                      conf.UI_FONT_SHADOW, conf.UI_FONT_SHADOW_SEL)
        colours = [d if c is None else c for c, d in zip(colours, default_cs)]
        c, c_s, sc, sc_s = colours
        size = irs(conf.UI_FONT_SIZE)
        spacing = irs(conf.UI_FONT_SPACING)
        font = (conf.FONT, size, False)
        shadow_offset = irs(conf.UI_FONT_SHADOW_OFFSET)
        shadow = [None, shadow_offset]
        font_data = [font, None, None, shadow]
        sfcs = []
        # generate text
        w = 0
        for i, o in enumerate(self.options):
            # get option type and extract data
            text, o_type = o[:2]
            opt = True
            spin = False
            if o_type == 0:
                opt = False
            elif o_type == 2:
                spin = True
                v, mn, mx, step, fmt = o[2:7]
            elif o_type == 3:
                spin = True
                v, vs = o[2:4]
            # set values for this option
            sel = self.current_opt == i
            font_data[1] = text
            font_data[2] = c_s if sel else c
            shadow[0] = sc_s if sel else sc
            # render
            sfc, lines = self.game.img(font_data)
            if o_type in (2, 3):
                # render current value
                font_data[1] = fmt.format(v) if o_type == 2 else vs[v]
                sfc2, lines = self.game.img(font_data)
                w = max(w, sfc.get_width(), sfc2.get_width())
                sfc = (sfc, sfc2)
            else:
                w = max(w, sfc.get_width())
            sfcs.append(sfc)
        # calculate positions
        h = size * len(sfcs) + spacing * (len(sfcs) - 1)
        p = [rect[0] + (rect[2] - w) / 2, rect[1] + (rect[3] - h) / 2]
        dy = spacing
        # blit
        for sfc in sfcs:
            if isinstance(sfc, tuple):
                screen.blit(sfc[0], p)
                screen.blit(sfc[1], (p[0] + sfc[0].get_width(), p[1]))
            else:
                screen.blit(sfc, p)
            p[1] += size + dy

    def draw (self, screen):
        if self.paused and not self.particles:
            if self.dirty:
                self._drawn_once = False
            elif self._drawn_once == True:
                return False
            else:
                self._drawn_once = True
        w, h = conf.RES
        lines = []
        b = irs(conf.BORDER)
        for x0, y0, x1, y1 in ((b, 0, b, h), (0, b, w, b), (w - b, 0, w - b, h),
                               (0, h - b, w, h - b)):
            lines.append(((x0, y0), (x1, y1)))
        if conf.GRAPHICS <= conf.NO_IMAGE_THRESHOLD:
            # background
            screen.fill(conf.BG)
            # border
            for a, b in lines:
                pygame.draw.line(screen, conf.BORDER_COLOUR, a, b, 5)
        else:
            # background
            img = self.game.img('bg.jpg', conf.SCALE)
            # tile image
            iw, ih = img.get_size()
            x = int(self.pos) % iw - iw
            while x < w:
                y = 0
                while y < h:
                    screen.blit(img, (x, y))
                    y += ih
                x += iw
            # border
            imgs = [self.game.img(ID + '.png', conf.SCALE) for ID in ('border0', 'border1')]
            for a, b in lines:
                i = int(a[0] == b[0])
                img = imgs[i]
                size = list(img.get_size())
                pos = list(a)
                pos[not i] -= size[not i] / 2
                end = conf.RES[i]
                while pos[i] < b[i]:
                    screen.blit(img, pos, [0, 0] + size)
                    pos[i] += size[i]
        # objs
        for o in self.cars + self.objs + self.powerups:
            o.draw(screen)
        # particles
        for c, p, v, ac, t, size in self.particles:
            screen.fill(c, p + [size, size])
        # scores
        size = irs(conf.SCORES_FONT_SIZE)
        x, y = irs(conf.SCORES_EDGE_PADDING)
        pad = irs(conf.SCORES_PADDING)
        for i, s in enumerate(self.scores):
            s = str(s)
            font = (conf.FONT, size, False)
            c = conf.CAR_COLOURS_LIGHT[i]
            sc = conf.CAR_COLOURS[i]
            font_args = (font, s, c, (sc, irs(conf.SCORES_FONT_SHADOW_OFFSET)))
            sfc, lines = self.game.img(font_args)
            screen.blit(sfc, (x, y))
            x += sfc.get_width() + pad
        # text
        won = self.won
        if self.paused or won is not None:
            rect = (0, 0) + tuple(conf.RES)
            if self.paused:
                # pause text
                self.draw_options(screen, rect)
            else:
                # winner text
                colours = (conf.CAR_COLOURS_LIGHT[won], None,
                           conf.CAR_COLOURS[won], None)
                self.draw_options(screen, rect, colours)
        if self.dirty:
            self.dirty = False
        return True