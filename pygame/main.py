from abc import ABC, abstractmethod
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
GRID_PIXEL_SIZE = 80

class Game:
	class State(enum.Enum):
		MAIN_MENU = enum.auto(),
		LEVEL_MENU = enum.auto(),
		PLAYING_LEVEL = enum.auto(),
	
	class Level:
		class Object(ABC):
			code: str
			kills: bool
			# Relative rectangle where (10, 10) is the bottom right
			hitbox_rect: pygame.Rect

			def __init__(self, pos: tuple[int, int]):
				absolute_pos = (pos[0] + self.hitbox_rect.left, pos[1] + self.hitbox_rect.top)
				self.absolute_hitbox_rect = pygame.Rect(absolute_pos, self.hitbox_rect.size)
			
			def kills_player(self, player_rect: pygame.Rect):
				return self.kills and player_rect.colliderect(self.absolute_hitbox_rect)

			def grounds_player(self, player_rect: pygame.Rect):
				return player_rect.colliderect(self.absolute_hitbox_rect) and player_rect.bottom < self.hitbox_rect.top
		
		class Spike(Object):
			code = "S1"
			kills = True
			hitbox_rect = pygame.Rect(2, 2, 6, 6)

		objects: list[Object] = [
			Spike
		]

		def __init__(self, name, music, difficulty, colour, level):
			self.name: str = name
			self.music: str = music
			self.difficulty: int = difficulty
			self.colour: tuple[int, int, int] = tuple(colour)
			self.level: list[list[Game.Level.Object]] = level

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
			
			level_strings = level_data["level"]
			level_objects = []
			for y in range(len(level_strings)):
				row = level_strings[y]
				level_objects.append([None for column in range(len(row))])
				for x in range(len(row)):
					string = row[x]
					for object_option in Game.Level.objects:
						if object_option.code == string:
							level_objects[y][x] = object_option
							break
						level_objects[y][x] = None
			
			return Game.Level(
					level_data["name"],
					level_data["music"],
					level_data["difficulty"],
					level_data["colour"],
					level_objects,
			)
		
		def __str__(self):
			return f"{self.name=};{self.music=};{self.difficulty=};{self.colour=};{self.level=}"
			

	def __init__(self):
		self.running = True
		self.state = Game.State.MAIN_MENU
		self.size = self.width, self.height  = 1280, 800

		pygame.init()
		self.display_surf = pygame.display.set_mode(self.size)
		self.fontObj = pygame.font.Font(pygame.font.get_default_font(), 100)

		self.shown_level_index = 0

		self.levels = self.get_levels()

		self.active_level = None
		self.active_level_surface: pygame.Surface = None
	
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
			"escape": False,
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
				buttons_pressed["escape"] = event.key == K_ESCAPE

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
				if buttons_pressed["mouse"]:
					if pos_in_circle((40, 40), 20, pygame.mouse.get_pos()):
						self.state = Game.State.MAIN_MENU
					elif textBgRect.collidepoint(pygame.mouse.get_pos()):
						self.open_level(self.shown_level_index)
				if buttons_pressed["escape"]:
					self.state = Game.State.MAIN_MENU
			case Game.State.PLAYING_LEVEL:
				# print(self.active_level)
				targetRect = self.active_level_surface.get_rect()
				targetRect.bottom = self.height
				targetRect.left = 0
				self.display_surf.blit(self.active_level_surface, targetRect)

				if buttons_pressed["escape"]:
					self.close_level()

		pygame.display.update()
	
	def open_level_menu(self):
		self.state = Game.State.LEVEL_MENU
		self.shown_level_index = 0

	def open_level(self, index: int):
		self.state = Game.State.PLAYING_LEVEL
		self.active_level = self.levels[index]
		self.active_level_surface = self.render_level(self.active_level)

	def close_level(self):
		self.state = Game.State.LEVEL_MENU
		self.active_level = None
		self.active_level_surface = None
	
	def render_level(self, level: Level):
		objects = level.level
		max_width = len(objects[0])
		for row in objects[1:]:
			max_width = max_width if len(row) < max_width else len(row)
		level_surface = pygame.Surface((max_width * GRID_PIXEL_SIZE, len(objects) * GRID_PIXEL_SIZE))
		level_surface.fill((0, 0, 128))

		for y in range(len(objects)):
			row = objects[y]
			for x in range(len(row)):
				object = row[x]
				if object is None:
					continue
				object_rect = pygame.Rect(x * GRID_PIXEL_SIZE, y * GRID_PIXEL_SIZE, GRID_PIXEL_SIZE, GRID_PIXEL_SIZE)
				pygame.draw.rect(level_surface, (0, 0, 0), object_rect)
		
		return level_surface
	
if __name__ == "__main__" :
	fpsClock = pygame.time.Clock()
	game = Game()
	count = 0
	while game.running:
		game.loop()
		fpsClock.tick(FPS)