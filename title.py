from random import random, randrange

import evthandler as eh

import conf
from level import Level

class Title (Level):
    def __init__ (self, game, event_handler):
        r = int(conf.FPS * .05)
        event_handler.add_key_handlers([
            (conf.KEYS_INCREASE, [(self.change_players, (1,))], eh.MODE_ONDOWN),
            (conf.KEYS_DECREASE, [(self.change_players, (-1,))], eh.MODE_ONDOWN),
            (conf.KEYS_INCREASE_2, [(self.change_graphics, (1,))], eh.MODE_ONPRESS_REPEAT, r, r),
            (conf.KEYS_DECREASE_2, [(self.change_graphics, (-1,))], eh.MODE_ONPRESS_REPEAT, r, r),
            (conf.KEYS_NEXT, self.start_level, eh.MODE_ONDOWN),
            (conf.KEYS_BACK, lambda *args: game.quit_backend(), eh.MODE_ONDOWN)
        ])
        Level.__init__(self, game, event_handler, 0, False)
        self.accel = 0
        self.scores = [0, 0]
        self._num_players = 2
        self.x = None

    def change_players (self, key, t, mods, d):
        n = min(max(self._num_players + d, 1), 4)
        self.scores = [0] * n
        self._num_players = n

    def change_graphics (self, key, t, mods, d):
        conf.GRAPHICS = max(conf.GRAPHICS + d * .02, 0)
        if t == 1:
            # key released
            self.game.play_snd('explode')
            ID = randrange(4)
            w, h = conf.RES
            self.particles = []
            self.spawn_particles((random() * w, random() * h),
                (conf.CAR_COLOURS[ID], conf.GRAPHICS * conf.DEATH_PARTICLES),
                (conf.CAR_COLOURS_LIGHT[ID], conf.GRAPHICS * conf.DEATH_PARTICLES)
            )

    def start_level (self, key, t, mods):
        self.game.start_backend(Level, self._num_players)

    def draw (self, screen):
        rtn = Level.draw(self, screen)
        # draw text
        # setup
        size = conf.UI_FONT_SIZE
        spacing = conf.UI_FONT_SPACING
        font = (conf.FONT, size, False)
        shadow = (conf.UI_FONT_SHADOW, conf.UI_FONT_SHADOW_OFFSET)
        font_data = [font, conf.TITLE_TEXT, conf.UI_FONT_COLOUR, shadow, None, 0, False, spacing]
        # render
        sfc1, lines = self.game.img('title', font_data, text = True)
        font_data[1] = ' ' + str(conf.GRAPHICS)
        sfc2, lines = self.game.img(conf.GRAPHICS, font_data, text = True)
        # position
        y0 = int(conf.SCORES_EDGE_PADDING[1] + conf.SCORES_FONT_SIZE)
        sw, sh = sfc1.get_size()
        total_w = sw + sfc2.get_width()
        w, h = conf.RES
        h -= int(conf.BORDER) + y0
        if self.x is None:
            self.x = (w - total_w) / 2
        y = y0 + (h - sh) / 2
        # blit
        screen.blit(sfc1, (self.x, y))
        screen.blit(sfc2, (self.x + sw, y + 2 * (size + spacing)))
        return True or rtn