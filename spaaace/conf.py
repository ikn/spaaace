import os

import pygame as pg

DATA_DIR = ''
IMG_DIR = DATA_DIR + 'img' + os.sep
SOUND_DIR = DATA_DIR + 'sound' + os.sep
MUSIC_DIR = DATA_DIR + 'music' + os.sep
LEVEL_DIR = DATA_DIR + 'lvl' + os.sep
FONT_DIR = DATA_DIR + 'font' + os.sep

WINDOW_ICON = IMG_DIR + 'icon.png'
WINDOW_TITLE = 'Spaaace'
MOUSE_VISIBLE = False
RESIZABLE = True
FULLSCREEN = False
FLAGS = pg.DOUBLEBUF
SCALE = .75
SIZE = (1400, 700)
RES_W = (int(round(SIZE[0] * SCALE)), int(round(SIZE[1] * SCALE)))
MIN_RES_W = (320, 160)
RES_F = pg.display.list_modes()[0]
FPS = 60
FRAME = 1. / FPS
STEP = .005
FPS_STAT_TIME = 5

MUSIC_VOLUME = 30
PAUSED_MUSIC_VOLUME = 10
SOUND_VOLUME = 70
EVENT_ENDMUSIC = pg.USEREVENT
CRASH_VOLUME = .0000025
SOUNDS = {'crash': 2, 'explode': 7, 'powerup': 5, 'powerdown': 5}
SOUND_VOLUMES = {'powerup': .5, 'powerdown': .5} # defaults to 1
BASE_SIMUL_SNDS = 3 # for same base ID
EXTRA_SIMUL_SNDS = 5

KEYS_MOVE = (
    (pg.K_LEFT, pg.K_UP, pg.K_RIGHT, pg.K_DOWN),
    (pg.K_a, (pg.K_w, pg.K_COMMA), (pg.K_d, pg.K_e), (pg.K_s, pg.K_o)),
    (pg.K_KP4, pg.K_KP8, pg.K_KP6, pg.K_KP5),
    ((pg.K_j, pg.K_h), (pg.K_i, pg.K_c), (pg.K_l, pg.K_n), (pg.K_k, pg.K_t))
)
KEYS_MINIMISE = (pg.K_F10,)
KEYS_FULLSCREEN = (pg.K_F11, (pg.K_RETURN, pg.KMOD_ALT, True),
                   (pg.K_KP_ENTER, pg.KMOD_ALT, True))
KEYS_NEXT = ((pg.K_RETURN, 0, True), pg.K_SPACE, (pg.K_KP_ENTER, 0, True))
KEYS_BACK = (pg.K_ESCAPE, pg.K_BACKSPACE)
JOY_START_MOVE = .6
JOY_STOP_MOVE = .4
JOY_CONTROLS = {
    'Microsoft X-Box 360 pad': {
        'move': (0, 1),
        'next': (0,),
        'back': (1, 6, 7)
    }
}
for s in ('XBOX 360 For Windows (Controller)', 'Controller (XBOX 360 For Windows)'):
    JOY_CONTROLS[s] = JOY_CONTROLS['Microsoft X-Box 360 pad']
FB_JOY_CONTROLS = {'move': (0, 1), 'next': (0,), 'back': (1, 6, 7)}
MENU_REPEAT_DELAY = .4
MENU_REPEAT_RATE = .15

EXPLOSION_FORCE = 10000
CAR_EXPLOSION_FORCE = 2000
OBJ_EXPLOSION_FORCE = .7 # per unit mass
DEATH_PARTICLES = 2500
OBJ_PARTICLES = OBJ_EXPLOSION_FORCE
POWERUP_PARTICLES = 100
CRASH_PARTICLES = .0001
BOMB_PARTICLES = 5000
PARTICLE_SPEED = 10
PARTICLE_SPEED_IF_ACCEL = 40
PARTICLE_ACCEL = -1
PARTICLE_LIFE = 2 * FPS
PARTICLE_SIZE = 10

BORDER = 18
FREEZE_TIME = PARTICLE_LIFE
WON_TIME = 5 * FPS
AIR_RESISTANCE = 3
ANGULAR_AIR_RESISTANCE = .1
INITIAL_VEL = -1000
TARGET_SCORE = 10
BG_SPEED = 1 # ratio of FG speed
SPAWN_RATE = .0004
POWERUP_SPAWN_RATE = .00003
POWERUP_GROUP_RATE = .05
POWERUP_GROUP_SPAWN_RATE_MULTIPLIER = 20
POWERUP_GROUP_SIZE = 10
LEVEL_ACCEL = .5

CAR_MASS = 50.
CAR_ELAST = 1.7
OBJ_ELAST = .3
CAR_FRICTION = .5
OBJ_FRICTION = .5
CAR_ACCEL = 10000
CAR_ANGLE_RESTORATION = .8 # amount to multiply angle by each frame moved
CAR_FORCE_OFFSET = (-5, 0)
OBJ_DENSITY = .0004
OBJ_VEL = 100
OBJ_ANG_VEL = 10
OBJ_SHAPES = {
    'car': ((35, 0), (15, 35), (-10, 40), (-15, 0), (-10, -40), (15, -35)),
    'rock0': ((-81, -101), (62, -105), (112, -42), (109, 58), (63, 114), (-56, 94), (-115, -5), (-110, -60)),
    'rock1': ((-5, -61), (71, -4), (55, 35), (-18, 59), (-60, 15), (-56, -31)),
    'rock2': ((10, -22), (22, -8), (15, 24), (-21, 21), (-22, -7))
}
weightings = {'rock0': 1, 'rock1': 1, 'rock2': 1}
OBJS, OBJ_WEIGHTINGS = zip(*(weightings.iteritems()))
POWERUP_MASS = 20
POWERUP_SIZE = 20
weightings = {'invincible': 1, 'heavy': 1, 'fast': .5, 'health': 1, 'bomb': .15}
POWERUPS, POWERUP_WEIGHTINGS = zip(*(weightings.iteritems()))
POWERUP_TIME = {'invincible': 10 * FPS, 'heavy': 5 * FPS, 'fast': 10 * FPS}
HEAVY_MULTIPLIER = 10
FAST_MULTIPLIER = 1.5
HEALTH_INCREASE = .5
BOMB_FORCE = 100000

CAR_HEALTH_ON = True
CAR_HEALTH_BASE = 1000000
CAR_HEALTH_MULTIPLIER = 1.
CAR_DAMAGE_STEPS = (.75, .5, .25)

GRAPHICS = 1
UNFILTERED_ROTATE_THRESHOLD = .8
HALF_FPS_THRESHOLD = .5
THIRD_FPS_THRESHOLD = 0
NO_IMAGE_THRESHOLD = .2

BG = (0, 0, 0)
BORDER_COLOUR = (255, 255, 170)
FONT = 'Chunk.otf'
UI_FONT_COLOUR = (200, 200, 150)
UI_FONT_COLOUR_SEL = (140, 0, 0)
UI_FONT_SIZE = 80
UI_FONT_SHADOW = (50, 50, 40)
UI_FONT_SHADOW_SEL = (76, 0, 0)
UI_FONT_SHADOW_OFFSET = (UI_FONT_SIZE * .05,) * 2
UI_FONT_SPACING = .2 * UI_FONT_SIZE
SCORES_FONT_SIZE = 70
SCORES_FONT_SHADOW_OFFSET = (SCORES_FONT_SIZE * .05,) * 2
SCORES_EDGE_PADDING = (55, 45)
SCORES_PADDING = 50
CAR_COLOURS = ((76, 0, 0), (0, 68, 76), (59, 76, 0), (76, 0, 75))
CAR_COLOURS_DARK = ((64, 0, 0), (0, 57, 64), (50, 64, 0), (64, 0, 63))
CAR_COLOURS_MID_DARK = ((89, 0, 0), (0, 80, 90), (70, 90, 0), (90, 0, 89))
CAR_COLOURS_MID_LIGHT = ((114, 0, 0), (0, 102, 114), (89, 114, 0), (114, 0, 113))
CAR_COLOURS_LIGHT = ((140, 0, 0), (0, 125, 140), (109, 140, 0), (140, 0, 138))
ALL_CAR_COLOURS = zip(CAR_COLOURS_LIGHT, CAR_COLOURS_MID_LIGHT, CAR_COLOURS_MID_DARK, CAR_COLOURS_DARK)
OBJ_COLOUR = (59, 47, 23)
OBJ_COLOUR_LIGHT = (117, 92, 47)
POWERUP_COLOURS = {'invincible': (50, 50, 255), 'heavy': (80, 0, 0), 'fast': (0, 60, 0), 'health': (150, 150, 150), 'bomb': (130, 85, 0)}
POWERUP_COLOURS_LIGHT = {'invincible': (100, 100, 255), 'heavy': (160, 0, 0), 'fast': (0, 100, 0), 'health': (255, 255, 255), 'bomb': (200, 130, 0)}
POWERUP_BORDER_WIDTH = 3
POWERUP_BORDER_OFFSET = {'invincible': 1, 'heavy': 9, 'fast': 5}
MAX_ROTATE_THRESHOLD = .1
ROTATE_THRESHOLD = .015
ROTATE_THRESHOLD_POWER = 1.5
