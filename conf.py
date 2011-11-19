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
FLAGS = pg.DOUBLEBUF
SIZE = 600
RES_W = (2 * SIZE, SIZE)
FPS = 60
FRAME = 1. / FPS

FULLSCREEN = False
RES_F = pg.display.list_modes()[0]

MUSIC_VOLUME = 70
SOUND_VOLUME = 70
EVENT_ENDMUSIC = pg.USEREVENT
SOUNDS = {'crash': 2, 'explode': 7}

KEYS_MOVE = (
    (pg.K_LEFT, pg.K_UP, pg.K_RIGHT, pg.K_DOWN),
    (pg.K_a, (pg.K_w, pg.K_COMMA), (pg.K_d, pg.K_e), (pg.K_s, pg.K_o)),
    (pg.K_KP4, pg.K_KP8, pg.K_KP6, pg.K_KP2),
    ((pg.K_j, pg.K_h), (pg.K_i, pg.K_c), (pg.K_l, pg.K_n), (pg.K_k, pg.K_t))
)
KEYS_MINIMISE = (pg.K_F10,)
KEYS_FULLSCREEN = (pg.K_F11, (pg.K_RETURN, pg.KMOD_ALT, True),
                   (pg.K_KP_ENTER, pg.KMOD_ALT, True))
KEYS_NEXT = (pg.K_RETURN, pg.K_SPACE, pg.K_KP_ENTER)
KEYS_BACK = (pg.K_ESCAPE, pg.K_BACKSPACE)
KEYS_INCREASE = (pg.K_RIGHT, pg.K_UP, pg.K_PLUS, pg.K_KP_PLUS)
KEYS_DECREASE = (pg.K_LEFT, pg.K_DOWN, pg.K_MINUS, pg.K_KP_MINUS)

BORDER = .03 * SIZE
PHYSICAL_BORDER = .025 * SIZE
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
CAR_ANGLE_RESTORATION = .8 # amount to multiply angle by each frame moved
CAR_FORCE_OFFSET = (-5, 0)
OBJ_DENSITY = .0004
OBJ_SHAPES = {
    'car': ((35, 0), (15, 35), (-10, 40), (-15, 0), (-10, -40), (15, -35)),
    'rock0': ((-81, -101), (62, -105), (112, -42), (109, 58), (63, 114), (-56, 94), (-115, -5), (-110, -60)),
    'rock1': ((-5, -61), (71, -4), (55, 35), (-18, 59), (-60, 15), (-56, -31))
}
weightings = {'rock0': 1, 'rock1': 1}
OBJS, OBJ_WEIGHTINGS = zip(*(weightings.iteritems()))

BG = (210, 160, 85)
FONT = 'Chunk.otf'
FONT_SHADOW_OFFSET = (SIZE * .005, SIZE * .005)
TITLE_TEXT = '''Enter: start
Left/right: cycle players
Escape: quit'''
TITLE_FONT_COLOUR = (30, 23, 11)
TITLE_FONT_SHADOW = (176, 139, 71)
TITLE_FONT_SIZE = int(SIZE * .15)
TITLE_FONT_SPACING = .5
SCORES_FONT_SIZE = int(SIZE * .1)
SCORES_EDGE_PADDING = (.08 * SIZE, .06 * SIZE)
SCORES_PADDING = .1 * SIZE
CAR_COLOURS = ((76, 0, 0), (0, 68, 76), (59, 76, 0), (76, 0, 75))
CAR_COLOURS_LIGHT = ((140, 0, 0), (0, 125, 140), (109, 140, 0), (140, 0, 138))
ROTATE_THRESHOLD = .05