import evthandler as eh

import conf
from level import Level

class Title (Level):
    def __init__ (self, game, event_handler):
        event_handler.add_key_handlers([
            (conf.KEYS_INCREASE, [(self.change_players, (1,))], eh.MODE_ONDOWN),
            (conf.KEYS_DECREASE, [(self.change_players, (-1,))], eh.MODE_ONDOWN),
            (conf.KEYS_NEXT, self.start_level, eh.MODE_ONDOWN),
            (conf.KEYS_BACK, lambda *args: game.quit_backend(), eh.MODE_ONDOWN)
        ])
        Level.__init__(self, game, event_handler, 0)
        self._num_players = 2
        self.scores = [0, 0]

    def change_players (self, key, t, mods, d):
        n = self._num_players + d
        n = min(max(n, 1), 4)
        self.scores = [0] * n
        self._num_players = n

    def start_level (self, key, t, mods):
        self.game.start_backend(Level, self._num_players)

    def draw (self, screen):
        rtn = Level.draw(self, screen)
        # draw text
        font = (conf.FONT, conf.TITLE_FONT_SIZE, False)
        shadow = (conf.TITLE_FONT_SHADOW, conf.FONT_SHADOW_OFFSET)
        font_data = (font, conf.TITLE_TEXT, conf.TITLE_FONT_COLOUR, shadow)
        sfc, lines = self.game.img('title', font_data, text = True)
        sw, sh = sfc.get_size()
        w, h = self.game.res
        screen.blit(sfc, ((w - sw) / 2, (h - sh) / 2))
        return True or rtn