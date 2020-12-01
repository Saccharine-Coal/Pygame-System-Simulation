import pygame as pg

from os import sys

import interactive_objects as io
import galaxy_system as gs


# GENERAL SETTINGS
WIDTH, HEIGHT = 1280, 720
FPS = 60

# FONT
TEXT = 'HELLO WORLD!'
TEXTCOLOR = (0, 0, 0)
TEXTBACKGROUND = (255, 255, 255)
FONTTYPE = 'freesansbold.ttf'
FONTSIZE = 24


class Game:
    def __init__(self):
        pg.init()
        self.screen = pg.display.set_mode((WIDTH, HEIGHT))
        self.clock = pg.time.Clock()
        pg.key.set_repeat(500, 100)
        self.font = pg.font.Font(FONTTYPE, FONTSIZE)

    # MAIN LOOP ---------------------------------------

    def new(self):
        self.init()

    def run(self):
        """Runs pygame."""
        while True:
            self.dt = self.clock.tick(FPS) / 1000
            self.events()
            self.update()
            self.draw()

    # MUTABLE LOOPS ------------------------------------

    def events(self):
        """Catch all events here."""
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    pg.quit()
                    sys.exit()
                if event.key == pg.K_w:
                    print('K_w')
                if event.key == pg.K_s:
                    print('K_s')
                if event.key == pg.K_d:
                    print('K_d')
                if event.key == pg.K_a:
                    print('K_a')
            if event.type == pg.MOUSEBUTTONDOWN:
                if event.button == 1:
                    # Left Click
                    print('Left Click')
                if event.button == 3:
                    # Right Click
                    print('Right Click')
                if event.button == 4:
                    # Scroll Wheel Up
                    print('Scroll Wheel Up')
                if event.button == 5:
                    # Scroll Wheel Down
                    print('Scroll Wheel Down')

    def init(self):
        # Initialize
        self.text_surface = self.font.render(TEXT, True, TEXTCOLOR, TEXTBACKGROUND)
        self.system = gs.System('PS_2020.11.30_14.52.15 - Copy', self.screen)

    def update(self):
        # Update
        pg.display.set_caption("{:.2f}".format(self.clock.get_fps()))

    def draw(self):
        # Draw
        self.screen.fill(pg.color.Color("Light Blue"))
        self.screen.blit(self.text_surface, self.screen.get_rect().center)
        self.system.draw()
        pg.display.flip()


# Create game object.
g = Game()
g.new()
g.run()