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
RES_F = pg.display.list_modes()[0]
RES_W = (1200, 600)
FPS = 60
FRAME = 1. / FPS

MUSIC_VOLUME = 0
SOUND_VOLUME = 0
EVENT_ENDMUSIC = pg.USEREVENT

KEYS_MOVE = (
    ((pg.K_LEFT,), (pg.K_UP,), (pg.K_RIGHT,), (pg.K_DOWN,)),
    ((pg.K_a,), (pg.K_w, pg.K_COMMA), (pg.K_d, pg.K_e), (pg.K_s, pg.K_o))
)
KEYS_MINIMISE = (pg.K_F10,)
KEYS_FULLSCREEN = (pg.K_F11, (pg.K_RETURN, pg.KMOD_ALT, True),
                   (pg.K_KP_ENTER, pg.KMOD_ALT, True))

BORDER = 20
LINE_ELAST = .7
CAR_MASS = 50
CAR_ELAST = .7
AIR_RESISTANCE = 2
CAR_ACCEL = 5000