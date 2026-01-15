from abc import ABC, abstractmethod
import enum
import json
import os
import sys
import time
from typing import Self
import pygame
from pygame.locals import *
from util import *

DEBUG = False
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

	class Player:
		# All speeds are applied per second
		JUMP_SPEED = 0.34
		GRAVITY_SPEED = -(JUMP_SPEED * 4.2)
		ROTATION_SPEED = -400

		appearance = pygame.Surface((25, 25), SRCALPHA)
		pygame.draw.rect(appearance, (0, 128, 0), (0, 0, 25, 25))
		pygame.draw.rect(appearance, (255, 255, 255), (0, 0, 25, 25), 1)
		appearance = pygame.transform.scale(appearance, (GRID_PIXEL_SIZE, GRID_PIXEL_SIZE))

		def __init__(self, game: "Game", level_objects: list[list["Game.Level.Object"]]=[[]]):
			self.screen_pos = [4, 0]
			self.level_pos = 0
			self.speed = 0
			self.vector_time = 0
			self.rotation = 0
			self.last_frame_time = time.time()

			self.game = game
			self.level_objects = level_objects

		def update(self):
			current_time = time.time()
			frame_time = current_time - self.last_frame_time
			self.last_frame_time = current_time

			self.level_pos = self.game.level_x / GRID_PIXEL_SIZE + self.screen_pos[0]

			vector = self.calculate_vector(self.speed, frame_time)
			if vector < 0 and self.on_ground((self.level_pos, self.screen_pos[1] + vector)):
				self.screen_pos[1] = self.ground_pos()
				self.rotation = 0
				self.speed = 0
			else:
				self.speed = vector
				self.screen_pos[1] += vector
			
			if not self.on_ground():
				self.rotation += self.ROTATION_SPEED * frame_time
			
			hitbox_rect = pygame.Rect(self.level_pos * GRID_PIXEL_SIZE, self.game.height - ((self.screen_pos[1] + 1) * GRID_PIXEL_SIZE), GRID_PIXEL_SIZE, GRID_PIXEL_SIZE)
			if DEBUG:
				pygame.draw.rect(self.game.active_level_surface, (0, 0, 255), hitbox_rect, 1)
			for row in self.level_objects:
				for object in row:
					if object is None:
						continue
					grounded, ground_offset = object.grounds_player(hitbox_rect)
					if object.kills_player(hitbox_rect):
						print("KILLED")
						self.game.reset_level()
						return False
					elif grounded:
						print(f"GROUNDED by {ground_offset / GRID_PIXEL_SIZE}")
						self.screen_pos[1] += ground_offset / GRID_PIXEL_SIZE
						hitbox_rect = pygame.Rect(self.level_pos * GRID_PIXEL_SIZE, self.game.height - ((self.screen_pos[1] + 1)* GRID_PIXEL_SIZE), GRID_PIXEL_SIZE, GRID_PIXEL_SIZE)
			return True

		def calculate_vector(self, speed, time_diff):
			if self.on_ground() and speed == 0:
				return 0
			vector = speed + (self.GRAVITY_SPEED * time_diff)
			
			return vector

		def jump(self):
			if self.on_ground():
				self.apply_speed(self.JUMP_SPEED)

		def apply_speed(self, speed):
			self.speed = speed
			self.vector_time = time.time()
		
		def on_ground(self, pos=None):
			if pos is None:
				pos = (self.level_pos, self.screen_pos[1])
			if pos[1] <= 0:
				return True

			hitbox_rect = pygame.Rect(pos[0] * GRID_PIXEL_SIZE, self.game.height - ((pos[1] + 1) * GRID_PIXEL_SIZE), GRID_PIXEL_SIZE, GRID_PIXEL_SIZE)
			for row in self.level_objects:
				for object in row:
					if object is None:
						continue
					if object.grounds_player(hitbox_rect)[0]:
						# print(f"On ground at {hitbox_rect=} from {object.absolute_hitbox_rect}")
						return True

			return False

		# TODO: Implement this
		def ground_pos(self, pos=None):
			if pos is None:
				pos = self.screen_pos
			return 0

	class Level:
		class Object(ABC):
			code: str
			kills: bool
			appearance: pygame.Surface
			# Relative rectangle where (10, 10) is the bottom right
			hitbox_rect: pygame.Rect

			def __init__(self, pos: tuple[int, int]):
				scalar = GRID_PIXEL_SIZE / 10
				scaled_hitbox_rect = self.hitbox_rect.scale_by(scalar)
				scaled_hitbox_rect.left = self.hitbox_rect.left * scalar
				scaled_hitbox_rect.top = self.hitbox_rect.top * scalar
				absolute_pos = (pos[0] + scaled_hitbox_rect.left, pos[1] + scaled_hitbox_rect.top)
				self.absolute_hitbox_rect = pygame.Rect(absolute_pos, scaled_hitbox_rect.size)
			
			def kills_player(self, player_rect: pygame.Rect):
				return self.kills and player_rect.colliderect(self.absolute_hitbox_rect)

			def grounds_player(self, player_rect: pygame.Rect):
				return player_rect.colliderect(self.absolute_hitbox_rect), player_rect.bottom - self.absolute_hitbox_rect.top
		
		class Spike(Object):
			code = "S1"
			kills = True
			hitbox_rect = pygame.Rect(4, 3, 2, 4)
			appearance = pygame.Surface((50, 50), SRCALPHA)

			pygame.draw.polygon(appearance, (0, 0, 0), [(25, 0), (0, 50), (50, 50)])
			pygame.draw.polygon(appearance, (255, 255, 255), [(24, 0), (0, 49), (48, 49)], 2)
		
		class ShortSpike(Object):
			code = "s1"
			kills = True
			hitbox_rect = pygame.Rect(4, 7, 2, 2)
			appearance = pygame.Surface((50, 50), SRCALPHA)

			pygame.draw.polygon(appearance, (0, 0, 0), [(25, 25), (0, 50), (50, 50)])
			pygame.draw.polygon(appearance, (255, 255, 255), [(24, 25), (0, 49), (48, 49)], 2)
		
		class Block(Object):
			code = "B1"
			kills = False
			hitbox_rect = pygame.Rect(0, 0, 10, 10)
			appearance = pygame.Surface((20, 20))

			pygame.draw.rect(appearance, (0, 0, 0), (0, 0, 20, 20))
			pygame.draw.rect(appearance, (255, 255, 255), (0, 0, 20, 20), 1)

		objects: list[Object] = [
			Spike,
			ShortSpike,
			Block
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
							# level_objects[y][x] = object_option((x * GRID_PIXEL_SIZE, (len(level_strings) - y - 1) * GRID_PIXEL_SIZE))
							level_objects[y][x] = object_option((x * GRID_PIXEL_SIZE, y * GRID_PIXEL_SIZE))
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

		self.player = None
		self.active_level = None
		self.active_level_surface: pygame.Surface = None
		self.last_render_time = None
		self.level_x = 0
	
	def get_levels(self) -> list[Level]:
		if not os.path.exists(LEVEL_PATH):
			print(f"Level path not found! Currently: \"{LEVEL_PATH}\". Change the path or make the folder")
			
		level_files = os.listdir(LEVEL_PATH)

		levels = []
		for level_file in level_files:
			if not level_file.endswith(".level"):
				continue
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
			"jump": False,
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
				buttons_pressed["jump"] = (
					event.key == K_w
					or event.key == K_SPACE
					or event.key == K_UP
				)

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
				elif buttons_pressed["jump"]:
					self.open_level(self.shown_level_index)

				if buttons_pressed["escape"]:
					self.state = Game.State.MAIN_MENU
			case Game.State.PLAYING_LEVEL:
				target_rect = self.active_level_surface.get_rect()
				target_rect.bottom = self.height

				SPEED = 10 * GRID_PIXEL_SIZE
				current_time = time.time()
				time_diff = current_time - self.last_render_time
				x_diff = -SPEED * time_diff
				self.level_x = self.level_x - x_diff
				target_rect.left = -self.level_x
				self.last_render_time = current_time

				screen = pygame.Surface(self.size)
				screen.blit(self.active_level_surface, target_rect)

				if self.jump_input():
					self.player.jump()
				if not self.player.update():
					return

				player_rect = pygame.Rect(self.player.screen_pos[0] * GRID_PIXEL_SIZE, self.height - (self.player.screen_pos[1] + 1) * GRID_PIXEL_SIZE, GRID_PIXEL_SIZE, GRID_PIXEL_SIZE)
				rotated_player = pygame.transform.rotate(self.player.appearance, self.player.rotation)
				screen.blit(rotated_player, player_rect)

				self.display_surf.blit(screen, (0, 0, GRID_PIXEL_SIZE, GRID_PIXEL_SIZE))

				if buttons_pressed["escape"]:
					self.close_level()

		pygame.display.update()
	
	def open_level_menu(self):
		self.state = Game.State.LEVEL_MENU
		self.shown_level_index = 0

	def open_level(self, index: int):
		self.state = Game.State.PLAYING_LEVEL
		self.active_level = self.levels[index]
		self.player = Game.Player(self, self.active_level.level)
		self.active_level_surface = self.render_level(self.active_level)
		self.last_render_time = time.time()
		self.level_x = 0

	def close_level(self):
		self.state = Game.State.LEVEL_MENU
		self.player = None
		self.active_level = None
		self.active_level_surface = None
		self.last_render_time = None
	
	def reset_level(self):
		self.player = Game.Player(self, self.active_level.level)
		self.level_x = 0
		self.last_render_time = time.time()
	
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
				
				object_appearance = pygame.transform.scale(object.appearance, (GRID_PIXEL_SIZE, GRID_PIXEL_SIZE))
				object_rect = pygame.Rect(x * GRID_PIXEL_SIZE, y * GRID_PIXEL_SIZE, GRID_PIXEL_SIZE, GRID_PIXEL_SIZE)
				level_surface.blit(object_appearance, object_rect)
				if DEBUG:
					hitbox_rect = object.absolute_hitbox_rect
					pygame.draw.rect(level_surface, (255, 0, 0), hitbox_rect, 1)
				# pygame.draw.rect(level_surface, (0, 0, 0), object_rect)
		
		return level_surface

	# Used when player can hold to repeatedly jump
	def jump_input(self):
		return (pygame.key.get_pressed()[K_w] or
		pygame.key.get_pressed()[K_SPACE] or
		pygame.key.get_pressed()[K_UP])
	
if __name__ == "__main__" :
	fpsClock = pygame.time.Clock()
	game = Game()
	count = 0
	while game.running:
		game.loop()
		fpsClock.tick(FPS)