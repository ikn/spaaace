import os

import pygame as pg

# TODO:
# change spawn rate to fit new size, and possible adjust size
# make allowances for runtime size changes
# change particles so that it looks the same at different scales

ir = lambda x: int(round(x))

DATA_DIR = ''
IMG_DIR = DATA_DIR + 'img' + os.sep
SOUND_DIR = DATA_DIR + 'sound' + os.sep
MUSIC_DIR = DATA_DIR + 'music' + os.sep
LEVEL_DIR = DATA_DIR + 'lvl' + os.sep
FONT_DIR = DATA_DIR + 'font' + os.sep

WINDOW_ICON = IMG_DIR + 'icon.png'
WINDOW_TITLE = '48-hour game'
RESIZABLE = False
FLAGS = pg.DOUBLEBUF
SCALE = .75
SIZE = (1600, 800)
RES_W = RES = (ir(SIZE[0] * SCALE), ir(SIZE[1] * SCALE))
FPS = 60
FRAME = 1. / FPS
STEP = .005
FPS_STAT_TIME = 5

FULLSCREEN = False
RES_F = pg.display.list_modes()[0]

MUSIC_VOLUME = 30
PAUSED_MUSIC_VOLUME = 10
SOUND_VOLUME = 70
EVENT_ENDMUSIC = pg.USEREVENT
CRASH_VOLUME = .0000025
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
KEYS_QUIT = (pg.K_q,)
KEYS_INCREASE = (pg.K_RIGHT, pg.K_PLUS, pg.K_KP_PLUS)
KEYS_DECREASE = (pg.K_LEFT, pg.K_MINUS, pg.K_KP_MINUS)
KEYS_INCREASE_2 = (pg.K_UP,)
KEYS_DECREASE_2 = (pg.K_DOWN,)

EXPLOSION_FORCE = 10000
CAR_EXPLOSION_FORCE = 2000
OBJ_EXPLOSION_FORCE = .7 # per unit mass
DEATH_PARTICLES = CAR_EXPLOSION_FORCE * SCALE
OBJ_PARTICLES = OBJ_EXPLOSION_FORCE * SCALE
CRASH_PARTICLES = .0001 * SCALE
PARTICLE_SPEED = 10 * SCALE
PARTICLE_SPEED_IF_ACCEL = 40 * SCALE
PARTICLE_ACCEL = -1 * SCALE
PARTICLE_LIFE = 2 * FPS
PARTICLE_SIZE = ir(10 * SCALE)

BORDER = 18
FREEZE_TIME = PARTICLE_LIFE
WON_TIME = 5 * FPS
AIR_RESISTANCE = 3
ANGULAR_AIR_RESISTANCE = .1
INITIAL_VEL = -1000
TARGET_SCORE = 10

BG_SPEED = 1 # ratio of FG speed
SPAWN_RATE = .0003
LEVEL_ACCEL = .5
CAR_MASS = 50
CAR_ELAST = 1.7
OBJ_ELAST = .3
CAR_FRICTION = .5
OBJ_FRICTION = .5
CAR_ACCEL = 10000
CAR_ANGLE_RESTORATION = .8 # amount to multiply angle by each frame moved
CAR_FORCE_OFFSET = (-5, 0)
OBJ_DENSITY = .0004
OBJ_ANG_VEL = 10
OBJ_SHAPES = {
    'car': ((35, 0), (15, 35), (-10, 40), (-15, 0), (-10, -40), (15, -35)),
    'rock0': ((-81, -101), (62, -105), (112, -42), (109, 58), (63, 114), (-56, 94), (-115, -5), (-110, -60)),
    'rock1': ((-5, -61), (71, -4), (55, 35), (-18, 59), (-60, 15), (-56, -31)),
    'rock2': ((10, -22), (22, -8), (15, 24), (-21, 21), (-22, -7))
}
weightings = {'rock0': 1, 'rock1': 1, 'rock2': 1}
OBJS, OBJ_WEIGHTINGS = zip(*(weightings.iteritems()))

GRAPHICS = 1
UNFILTERED_ROTATE_THRESHOLD = .8
HALF_FPS_THRESHOLD = .5
THIRD_FPS_THRESHOLD = 0
NO_IMAGE_THRESHOLD = .2

BG = (0, 0, 0)
BORDER_COLOUR = (255, 255, 170)
FONT = 'Chunk.otf'
UI_FONT_COLOUR = (200, 200, 150)
UI_FONT_SIZE = ir(90 * SCALE)
UI_FONT_SHADOW = (50, 50, 40)
UI_FONT_SHADOW_OFFSET = (ir(UI_FONT_SIZE * .05),) * 2
UI_FONT_SPACING = ir(.2 * UI_FONT_SIZE)
SCORES_FONT_SIZE = ir(60 * SCALE)
SCORES_FONT_SHADOW_OFFSET = (ir(SCORES_FONT_SIZE * .05),) * 2
SCORES_EDGE_PADDING = (ir(48 * SCALE), ir(36 * SCALE))
SCORES_PADDING = ir(60 * SCALE)
CAR_COLOURS = ((76, 0, 0), (0, 68, 76), (59, 76, 0), (76, 0, 75))
CAR_COLOURS_LIGHT = ((140, 0, 0), (0, 125, 140), (109, 140, 0), (140, 0, 138))
OBJ_COLOUR = (59, 47, 23)
OBJ_COLOUR_LIGHT = (117, 92, 47)
MAX_ROTATE_THRESHOLD = .1
ROTATE_THRESHOLD = .015
ROTATE_THRESHOLD_POWER = 1.5

TITLE_TEXT = '''Enter: start
Left/right: players
Up/down: graphics
Escape: quit'''
PAUSE_TEXT = '''Paused
Space: continue
Q: quit'''
WON_TEXT = 'Winner'