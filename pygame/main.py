import enum
import json
import os
import sys
from typing import Self
import pygame
from pygame.locals import *
from util import *

FPS = 60

LEVEL_PATH = "./pygame/levels/"
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
	
	class Level:
		def __init__(self, name, music, difficulty, colour, level):
			self.name = name
			self.music = music
			self.difficulty = difficulty
			self.colour = colour
			self.level = level

		@staticmethod
		def parse_level(levelData: str) -> Self | None:
			level_data = None
			try:
				# Ensure data is valid
				level_data = json.loads(levelData)
				assert "name" in level_data
				assert "music" in level_data
				assert "difficulty" in level_data
				assert "colour" in level_data
				assert "level" in level_data
			except (ValueError, AssertionError):
				return None
			
			return Game.Level(
					level_data["name"],
					level_data["music"],
					level_data["difficulty"],
					level_data["colour"],
					level_data["level"],
			)
			

	def __init__(self):
		self.running = True
		self.state = Game.State.MAIN_MENU
		self.size = self.width, self.height  = 1280, 800

		pygame.init()
		self.display_surf = pygame.display.set_mode(self.size)
		self.fontObj = pygame.font.Font(pygame.font.get_default_font(), 100)

		self.shown_level_index = 0

		self.levels = self.get_levels()
	
	def get_levels(self) -> list[Level]:
		if not os.path.exists(LEVEL_PATH):
			print(f"Level path not found! Currently: \"{LEVEL_PATH}\". Change the path or make the folder")
			
		level_files = os.listdir(LEVEL_PATH)

		levels = []
		for level_file in level_files:
			with open(os.path.join(LEVEL_PATH, level_file)) as file:
				level = Game.Level.parse_level(file.read())
				if level == None:
					continue
				levels.append(level)
		
		return levels

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
				if (buttons_pressed["left"]):
					self.shown_level_index = self.shown_level_index - 1 if self.shown_level_index > 0 else len(self.levels) - 1
				elif (buttons_pressed["right"]):
					self.shown_level_index = self.shown_level_index + 1 if self.shown_level_index + 1 < len(self.levels) else 0
				
				
				level = self.levels[self.shown_level_index] if self.shown_level_index < len(self.levels) else None
				self.display_surf.fill(level.colour)
				textSurfaceObj = self.fontObj.render(f"{level.name if level is not None else f"None {self.shown_level_index}"}", True, (255, 255, 255))
				textRectObj = textSurfaceObj.get_rect()
				textRectObj.center = (640, 300)

				textBgRect = pygame.Rect(0, 0, 1000, 400)
				textBgRect.center = textRectObj.center
				pygame.draw.rect(self.display_surf, (0, 0, 0), textBgRect, border_radius=20)

				self.display_surf.blit(textSurfaceObj, textRectObj)

				pygame.draw.circle(self.display_surf, (255, 255, 0), (40, 40), 20)
				pygame.draw.circle(self.display_surf, (0, 255, 0), (40, 40), 15)
				if (buttons_pressed["mouse"]
						and pos_in_circle((40, 40), 20, pygame.mouse.get_pos())):
					self.state = Game.State.MAIN_MENU

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