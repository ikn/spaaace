from random import random, randrange

from ext import evthandler as eh
import pygame

import conf
from level import Level

ir = lambda x: int(round(x))
def irs (x):
    if isinstance(x, (float, int)):
        return ir(x * conf.SCALE)
    else:
        return tuple(ir(i) * conf.SCALE for i in x)

class Title (Level):
    def __init__ (self, game, event_handler, num_cars = 2):
        d = int(conf.FPS * .5)
        r = int(conf.FPS * .2)
        event_handler.add_key_handlers([
            (conf.KEYS_INCREASE, [(self.change_players, (1,))], eh.MODE_ONDOWN),
            (conf.KEYS_DECREASE, [(self.change_players, (-1,))], eh.MODE_ONDOWN),
            (conf.KEYS_INCREASE_2, [(self.change_graphics, (1,))], eh.MODE_ONPRESS_REPEAT, d, r),
            (conf.KEYS_DECREASE_2, [(self.change_graphics, (-1,))], eh.MODE_ONPRESS_REPEAT, d, r),
            (conf.KEYS_NEXT, self.start_level, eh.MODE_ONDOWN),
            (conf.KEYS_BACK, lambda *args: game.quit_backend(), eh.MODE_ONDOWN)
        ])
        Level.__init__(self, game, event_handler, 0, False)
        self.accel = 0
        self.scores = [0] * num_cars
        self._num_players = num_cars
        self.init_opts(conf.TITLE_OPTIONS)

    def change_players (self, key, t, mods, d):
        n = min(max(self._num_players + d, 1), 4)
        self.scores = [0] * n
        self._num_players = n

    def change_graphics (self, key, t, mods, d):
        if t == 1:
            # key released
            self.game.play_snd('explode')
            ID = randrange(4)
            w, h = conf.RES
            self.particles = []
            amount = conf.GRAPHICS * conf.DEATH_PARTICLES * conf.SCALE
            self.spawn_particles((random() * w, random() * h),
                (conf.CAR_COLOURS[ID], amount),
                (conf.CAR_COLOURS_LIGHT[ID], amount)
            )
        else:
            old_g = conf.GRAPHICS
            conf.GRAPHICS = new_g = round(max(conf.GRAPHICS + d * .1, 0), 1)
            # delete cached images if our draw methods change
            for t in (conf.UNFILTERED_ROTATE_THRESHOLD, conf.NO_IMAGE_THRESHOLD):
                if old_g > t and new_g <= t:
                    g = self.game
                    g.files = {}
                    g.imgs = dict((k, v) for k, v in g.imgs.iteritems() if not isinstance(v, pygame.Surface))

    def start_level (self, key, t, mods):
        self.game.quit_backend(no_quit = True)
        self.game.start_backend(Level, self._num_players)

    def draw (self, screen):
        rtn = Level.draw(self, screen)
        # draw options
        y0 = int(irs(conf.SCORES_EDGE_PADDING[1]) + irs(conf.SCORES_FONT_SIZE))
        w, h = conf.RES
        self.draw_options(screen, (0, y0, w, h - y0), players = self.num_cars,
                          graphics = conf.GRAPHICS)
        return True or rtn