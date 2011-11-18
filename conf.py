import os

import pygame as pg

DATA_DIR = ''
IMG_DIR = DATA_DIR + 'img' + os.sep
SOUND_DIR = DATA_DIR + 'sound' + os.sep
MUSIC_DIR = DATA_DIR + 'music' + os.sep
LEVEL_DIR = DATA_DIR + 'lvl' + os.sep
FONT_DIR = DATA_DIR + 'font' + os.sep

WINDOW_ICON = None
WINDOW_TITLE = None
RESIZABLE = False
FULLSCREEN = False
FLAGS = pg.DOUBLEBUF
RES_F = pg.display.list_modes()[0]
RES_W = (1200, 600)
FPS = 60
FRAME = 1. / FPS
TESTING = True

MUSIC_VOLUME = 0
SOUND_VOLUME = 0
EVENT_ENDMUSIC = pg.USEREVENT

KEYS_MOVE = (
    (pg.K_LEFT, pg.K_UP, pg.K_RIGHT, pg.K_DOWN),
    (pg.K_a, (pg.K_w, pg.K_COMMA), (pg.K_d, pg.K_e), (pg.K_s, pg.K_o)),
    (pg.K_KP4, pg.K_KP8, pg.K_KP6, pg.K_KP2),
    ((pg.K_j, pg.K_h), (pg.K_i, pg.K_c), (pg.K_l, pg.K_n), (pg.K_k, pg.K_t))
)
KEYS_MINIMISE = (pg.K_F10,)
KEYS_FULLSCREEN = (pg.K_F11, (pg.K_RETURN, pg.KMOD_ALT, True),
                   (pg.K_KP_ENTER, pg.KMOD_ALT, True))

BORDER = 20
INITIAL_PAUSE = 1
SPAWN_T_VAR = .5 # ratio of median time
AIR_RESISTANCE = 3
ANGULAR_AIR_RESISTANCE = .1

CAR_MASS = 50
CAR_ELAST = .7
OBJ_ELAST = .7
CAR_FRICTION = .5
OBJ_FRICTION = .5
CAR_ACCEL = 10000
OBJ_DENSITY = .5
OBJ_SHAPES = {
    'car': ((25, 0), (13, 40), (8, 40), (-25, 0), (8, -40), (13, -40))
}

FONT = 'Chunk.otf'
FONT_SIZE = 50
SCORES_EDGE_PADDING = (40, 30)
SCORES_PADDING = 40