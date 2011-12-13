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
        event_handler.add_key_handlers([
            (conf.KEYS_BACK, lambda *args: game.quit_backend(), eh.MODE_ONDOWN)
        ])
        Level.__init__(self, game, event_handler, 0, False)
        self.accel = 0
        self.scores = [0] * num_cars
        self._num_players = num_cars
        self.init_opts((
            ('Start', 1, self.start_level),
            ('Players: ', 2, self._num_players, 1, 4, 1, '{0}', self.change_players),
            ('Graphics: ', 2, conf.GRAPHICS, 0, None, .1, '{0:.1f}', self.change_graphics),
            ('Health: ', 2, conf.CAR_HEALTH_MULTIPLIER, 0, None, .1, '{0:.1f}', self.change_health),
            ('Quit', 1, self.game.quit_backend)
        ))

    def change_players (self, d):
        n = min(max(self._num_players + d, 1), 4)
        self.scores = [0] * n
        self._num_players = n

    def change_graphics (self, d):
        old_g = conf.GRAPHICS
        conf.GRAPHICS = new_g = round(max(conf.GRAPHICS + d, 0), 1)
        if old_g == new_g:
            return
        # delete cached images if our draw methods change
        for t in (conf.UNFILTERED_ROTATE_THRESHOLD, conf.NO_IMAGE_THRESHOLD):
            if old_g > t and new_g <= t:
                g = self.game
                g.files = {}
                g.imgs = dict((k, v) for k, v in g.imgs.iteritems() if not isinstance(v, pygame.Surface))
        # change number of sound channels
        max_snds = ir(conf.BASE_SIMUL_SNDS + conf.EXTRA_SIMUL_SNDS * conf.GRAPHICS) * len(conf.SOUNDS)
        pygame.mixer.set_num_channels(max_snds)
        # show explosion
        self.game.play_snd('explode')
        ID = randrange(4)
        w, h = conf.RES
        self.particles = []
        amount = conf.GRAPHICS * conf.DEATH_PARTICLES * conf.SCALE
        self.spawn_particles((random() * w, random() * h),
            (conf.CAR_COLOURS[ID], amount),
            (conf.CAR_COLOURS_LIGHT[ID], amount)
        )

    def change_health (self, d):
        conf.CAR_HEALTH_MULTIPLIER += d

    def start_level (self):
        self.game.quit_backend(no_quit = True)
        self.game.start_backend(Level, self._num_players)

    def quit (self, *args):
        # uninitialise controllers
        for i in xrange(min(self.num_joys, self.num_cars)):
            pygame.joystick.Joystick(i).quit()
        Level.quit(self)

    def draw (self, screen):
        rtn = Level.draw(self, screen)
        # draw options
        w, h = conf.RES
        self.draw_options(screen, (0, 0, w, h), players = self.num_cars,
                          graphics = conf.GRAPHICS)
        return True or rtn
