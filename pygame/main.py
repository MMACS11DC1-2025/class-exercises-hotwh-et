import enum
import sys
import pygame
from pygame.locals import *
from util import *

FPS = 60

COLOURS = {
	"black": (0, 0, 0),
	"white": (255, 255, 255),
	"red": (255, 0, 0),
	"blue": (0, 255, 0),
	"green": (0, 0, 255)
}

class Game:
	class State(enum.Enum):
		MAIN_MENU = enum.auto(),
		LEVEL_MENU = enum.auto()

	def __init__(self):
		self.running = True
		self.state = Game.State.MAIN_MENU
		self.size = self.width, self.height  = 1280, 800

		pygame.init()
		self.display_surf = pygame.display.set_mode(self.size)
		self.fontObj = pygame.font.Font(pygame.font.get_default_font(), 100)

		self.shown_level_index = 0

	def loop(self):
		buttons_pressed = {
			"mouse": False,
			"left": False,
			"right": False,
		}

		for event in pygame.event.get():
			if event.type == QUIT:
				self.running = False
				pygame.quit()
				sys.exit()
				return

			buttons_pressed["mouse"] = event.type == MOUSEBUTTONDOWN
			if event.type == KEYDOWN:
				buttons_pressed["left"] = event.key == K_LEFT
				buttons_pressed["right"] = event.key == K_RIGHT

		self.display_surf.fill((0, 0, 0))
		match self.state:
			case Game.State.MAIN_MENU:
				pygame.draw.circle(self.display_surf, (255, 255, 0), (640, 400), 100)
				if (buttons_pressed["mouse"]
						and pos_in_circle((640, 400), 100, pygame.mouse.get_pos())):
					self.open_level_menu()

			case Game.State.LEVEL_MENU:
				pygame.draw.circle(self.display_surf, (0, 255, 0), (40, 40), 20)
				if (buttons_pressed["mouse"]
						and pos_in_circle((40, 40), 20, pygame.mouse.get_pos())):
					self.state = Game.State.MAIN_MENU

				if (buttons_pressed["left"]):
					self.shown_level_index = self.shown_level_index - 1
					self.shown_level_index = 0 if self.shown_level_index < 0 else self.shown_level_index
				elif (buttons_pressed["right"]):
					self.shown_level_index += 1
				
				textSurfaceObj = self.fontObj.render(f"{self.shown_level_index}", True, (255, 255, 255))
				textRectObj = textSurfaceObj.get_rect()
				textRectObj.center = (640, 400)

				self.display_surf.blit(textSurfaceObj, textRectObj)

		pygame.display.update()

	def open_level_menu(self):
		self.state = Game.State.LEVEL_MENU
		self.shown_level_index = 0

if __name__ == "__main__" :
	fpsClock = pygame.time.Clock()
	game = Game()
	count = 0
	while game.running:
		game.loop()
		fpsClock.tick(FPS)