import evthandler as eh

import conf
from level import Level

class Title (Level):
    def __init__ (self, game, event_handler):
        event_handler.add_key_handlers([
            (conf.KEYS_INCREASE, [(self.change_players, (1,))], eh.MODE_ONDOWN),
        ])
        Level.__init__(self, game, event_handler, 0)
        self._num_players = 0

    def change_players (self, key, t, mods, d):
        self._num_players += d
        self.scores = [0] * self._num_players
        print self.scores

    def draw (self, screen):
        rtn = Level.draw(self, screen)
        return True or rtn