import os
from time import time
from random import choice

import pygame
from pygame.time import wait
pygame.mixer.pre_init(buffer = 1024)
pygame.init()
if os.name == 'nt':
    # for Windows freeze support
    import pygame._view
import evthandler as eh

from title import Title
import conf

class Fonts (object):
    """Collection of pygame.font.Font instances."""

    def __init__ (self, *fonts):
        self.fonts = {}
        for font in fonts:
            self.add(font)

    def add (self, font, force_reload = False):
        """Load a font and add it to the collection."""
        font = tuple(font)
        if force_reload or font not in self.fonts:
            fn, size, bold = font
            self.fonts[font] = pygame.font.Font(conf.FONT_DIR + fn, int(size),
                                                bold = bold)
        return self.fonts[font]

    def text (self, font, text, colour, shadow = None, width = None, just = 0,
              minimise = False, line_spacing = 0):
        """Render text from a font.

text(font, text, colour[, shadow][, width], just = 0, minimise = False,
     line_spacing = 0) -> (surface, lines)

font: (font name, size, is_bold) tuple.
text: text to render.
colour: (R, G, B[, A]) tuple.
shadow: to draw a drop-shadow: (colour, offset) tuple, where offset is (x, y).
width: maximum width of returned surface (wrap text).  ValueError is raised if
       any words are too long to fit in this width.
just: if the text has multiple lines, justify: 0 = left, 1 = centre, 2 = right.
minimise: if width is set, treat it as a minimum instead of absolute width
          (that is, shrink the surface after, if possible).
line_spacing: space between lines, in pixels.

surface: pygame.Surface containing the rendered text.
lines: final number of lines of text.

"""
        font = tuple(font)
        self.add(font)
        font, lines = self.fonts[font], []
        if shadow is None:
            offset = (0, 0)
        else:
            shadow_colour, offset = shadow

        # split into lines
        text = text.splitlines()
        if width is None:
            width = max(font.size(line)[0] for line in text)
            lines = text
            minimise = True
        else:
            for line in text:
                if font.size(line)[0] > width:
                    # wrap
                    words = line.split(' ')
                    # check if any words won't fit
                    for word in words:
                        if font.size(word)[0] >= width:
                            e = '\'{0}\' doesn\'t fit on one line'.format(word)
                            raise ValueError(e)
                    # build line
                    build = ''
                    for word in words:
                        temp = build + ' ' if build else build
                        temp += word
                        if font.size(temp)[0] < width:
                            build = temp
                        else:
                            lines.append(build)
                            build = word
                    lines.append(build)
                else:
                    lines.append(line)
        if minimise:
            width = max(font.size(line)[0] for line in lines)

        # create surface
        h = 0
        for line in lines:
            h += font.size(line)[1] + line_spacing
        # last added gap was after the last line
        h -= line_spacing
        surface = pygame.Surface((width + offset[0], h + offset[1]))
        surface = surface.convert_alpha()
        surface.fill((0, 0, 0, 0))

        # add text
        todo = []
        if shadow is not None:
            todo.append((shadow_colour, 1))
        todo.append((colour, -1))
        num_lines = 0
        for colour, mul in todo:
            o = (max(mul * offset[0], 0), max(mul * offset[1], 0))
            h = 0
            for line in lines:
                if line:
                    num_lines += 1
                    s = font.render(line, True, colour)
                    if just == 2:
                        surface.blit(s, (width - s.get_width() + o[0],
                                         h + o[1]))
                    elif just == 1:
                        surface.blit(s, ((width - s.get_width()) / 2 + o[0],
                                         h + o[1]))
                    else:
                        surface.blit(s, (o[0], h + o[1]))
                h += font.size(line)[1] + line_spacing
        return surface, num_lines


class Game (object):
    """Handles backends.

Takes the same arguments as Game.start_backend and passes them to it.

    METHODS

start_backend
quit_backend
set_backend_attrs
img
play_snd
find_music
play_music
quit
run
restart
refresh_display
minimise

    ATTRIBUTES

running: set to False to exit the main loop (Game.run).
imgs: image cache.
files: loaded image cache (before resize).
sounds: sound effect cache.
music: filenames for known music.
fonts: a Fonts instance.
backend: the current running backend.
backends: a list of previous (nested) backends, most 'recent' last.

"""

    def __init__ (self, cls, *args):
        self.running = False
        self.imgs = {}
        self.files = {}
        self.sounds = []
        # start playing music
        pygame.mixer.music.set_volume(conf.MUSIC_VOLUME * .01)
        pygame.mixer.music.set_endevent(conf.EVENT_ENDMUSIC)
        self.find_music()
        self.play_music()
        # load display settings
        self.refresh_display()
        self.fonts = Fonts()
        # start first backend
        self.backends = []
        self.start_backend(cls, *args)

    def start_backend (self, cls, *args):
        """Start a new backend.

start_backend(cls, *args) -> backend

cls: the backend class to instantiate.
args: arguments to pass to the constructor.

backend: the new created instance of cls that is the new backend.

Backends handle pretty much everything, including drawing, and must have update
and draw methods, as follows:

update(): handle input and make any necessary calculations.
draw(screen) -> drawn: draw anything necessary to screen; drawn is True if the
                       whole display needs to be updated, something falsy if
                       nothing needs to be updated, else a list of rects to
                       update the display in.

A backend is also given a dirty attribute, which indicates whether its draw
method should redraw everything (it should set it to False when it does so),
and should define a FRAME attribute, which is the length of one frame in
seconds.

A backend is constructed via
cls(Game_instance, EventHandler_instance, *args), and should store
EventHandler_instance in its event_handler attribute.

"""
        # create event handler for this backend
        h = eh.MODE_HELD
        event_handler = eh.EventHandler({
            conf.EVENT_ENDMUSIC: self.play_music
        }, [], False, self.quit)
        # store current backend in history, if any
        try:
            self.backends.append(self.backend)
        except AttributeError:
            pass
        # create new backend
        self.backend = cls(self, event_handler, *args)
        return self.backend

    def quit_backend (self, depth = 1):
        """Quit the currently running backend.

quit_backend(depth = 1)

depth: quit this many backends.

If the running backend is the last (root) one, exit the game.

"""
        depth = int(depth)
        if depth < 1:
            return
        try:
            self.backend = self.backends.pop()
        except IndexError:
            self.quit()
        else:
            self.backend.dirty = True
        depth -= 1
        if depth:
            self.quit_backend(depth)
        else:
            # need to update new backend before drawing
            self._update_again = True

    def set_backend_attrs (self, cls, attr, val, current = True,
                           inherit = True):
        """Set an attribute of all backends with a specific class.

set_backend_attrs(cls, attr, val, current = True, inherit = True)

cls: the backend class to look for.
attr: the name of the attribute to set.
val: the value to set the attribute to.
current: include the current backend in the search.
inherit: also apply to all classes that inherit from the given class.

        """
        for backend in self.backends + ([self.backend] if current else []):
            if isinstance(backend, cls) if inherit else (backend == cls):
                setattr(backend, attr, val)

    def img (self, ID, data, size = None, text = False):
        """Load or render an image, or retrieve it from cache.

img(ID, data[, size], text = False) -> surface

ID: a string identifier unique to the expected result, ignoring size.
data: if text is True, a tuple of args to pass to Fonts.text, else a filename
      to load.
size: if given, scale the image to this size.  Can be a rect, in which case its
      dimension is used.
text: whether the image should be rendered from a font (data is list of args to
      pass to Font.text).  If True, returns (img, lines) like Font.text.

"""
        if size is not None:
            if len(size) == 4:
                # rect
                size = size[2:]
            size = tuple(size)
        key = (ID, size)
        if key in self.imgs:
            return self.imgs[key]
        # else new: load/render
        if text:
            rtn = self.fonts.text(*data)
            img = rtn[0]
        else:
            # also cache loaded images to reduce file I/O
            if data in self.files:
                img = self.files[data]
            else:
                img = pygame.image.load(conf.IMG_DIR + data)
                self.files[data] = img
        # scale
        if size is not None:
            img = pygame.transform.smoothscale(img, size)
        if not text:
            rtn = img
        # speed up blitting
        if img.get_alpha() is None:
            img = img.convert()
        else:
            img = img.convert_alpha()
        # add to cache
        self.imgs[key] = rtn
        return rtn

    def play_snd (self, ID, volume = 1):
        """Play a sound with the given ID.

Only one instance of a sound will be played each frame.

"""
        IDs = [ID + str(i) for i in xrange(conf.SOUNDS[ID])]
        ID = choice(IDs)
        # load sound
        try:
            snd = conf.SOUND_DIR + ID + '.ogg'
            snd = pygame.mixer.Sound(snd)
            if snd.get_length() < 10 ** -3:
                # no way this is valid
                return
        except KeyError:
            return # just don't play the sound if it's not registered
        snd.set_volume(conf.SOUND_VOLUME * volume * .01)
        self.sounds.append(snd)

    def _play_snds (self):
        """Play queued up sounds for this frame."""
        for snd in self.sounds:
            snd.play()
        self.sounds = []

    def find_music (self):
        """Store a list of music files."""
        d = conf.MUSIC_DIR
        try:
            files = os.listdir(d)
        except OSError:
            # no directory
            self.music = []
        else:
            self.music = [d + f for f in files if os.path.isfile(d + f)]

    def play_music (self, event = None):
        """Play next piece of music."""
        if self.music:
            f = choice(self.music)
            pygame.mixer.music.load(f)
            pygame.mixer.music.play()
        else:
            # stop currently playing music if there's no music to play
            pygame.mixer.music.stop()

    def quit (self, event = None):
        """Quit the game."""
        self.running = False

    def _update (self):
        """Run the backend's update method."""
        self.backend.event_handler.update()
        # if a new backend was created during the above call, we'll end up
        # updating twice before drawing
        if not self._update_again:
            self.backend.update()

    def _draw (self):
        """Run the backend's draw method and update the screen."""
        draw = self.backend.draw(self.screen)
        if draw is True:
            pygame.display.update()
        elif draw:
            pygame.display.update(draw)

    def run (self):
        """Main loop."""
        self.running = True
        stat_t = conf.FPS_STAT_TIME
        start_stat = t0 = time()
        n = 0
        while self.running:
            # update
            self._update_again = False
            self._update()
            if self._update_again:
                self._update_again = False
                self._update()
            # play sounds
            self._play_snds()
            # draw
            self._draw()
            # wait
            frame = self.backend.FRAME
            t1 = time()
            wait(int(1000 * (frame - t1 + t0)))
            t0 = t1
            n += 1
            if n >= stat_t / frame:
                print stat_t / (frame * (t0 - start_stat))
                n = 0
                start_stat = t0

    def restart (self, *args):
        """Restart the game."""
        global restarting
        restarting = True
        self.quit()

    def refresh_display (self, *args):
        """Update the display mode from conf, and notify the backend."""
        flags = conf.FLAGS
        if conf.FULLSCREEN:
            flags |= pygame.FULLSCREEN
            self.res = conf.RES_F
        else:
            self.res = (w, h) = conf.RES_W
        if conf.RESIZABLE:
            flags |= pygame.RESIZABLE
        self.screen = pygame.display.set_mode(self.res, flags)
        try:
            self.backend.dirty = True
        except AttributeError:
            pass
        # clear image cache (very unlikely we'll need the same sizes)
        self.imgs = {}

    def minimise (self, *args):
        """Minimise the display, pausing if possible (and necessary)."""
        pygame.display.iconify()

if __name__ == '__main__':
    if conf.WINDOW_ICON is not None:
        pygame.display.set_icon(pygame.image.load(conf.WINDOW_ICON))
    if conf.WINDOW_TITLE is not None:
        pygame.display.set_caption(conf.WINDOW_TITLE)
    pygame.mouse.set_visible(False)
    restarting = True
    while restarting:
        restarting = False
        Game(Title).run()

pygame.quit()