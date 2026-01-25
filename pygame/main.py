from abc import ABC
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
NOCLIP = False
FPS = 60
MENU_MUSIC_FILE = "./pygame/assets/menu.mp3"
LEVEL_PATH = "./pygame/levels/"
MUSIC_PATH = "./pygame/levels/music/"
PROGRESS_FILE = "./pygame/progress.json"
GRID_PIXEL_SIZE = 80
MAX_SURFACE_WIDTH = 65535 # Limitation of pygame, otherwise causes integer overflow

class GameState(enum.Enum):
	MAIN_MENU = enum.auto(),
	LEVEL_MENU = enum.auto(),
	PLAYING_LEVEL = enum.auto(),
	WON_LEVEL = enum.auto(),

class GameMode(enum.Enum):
	CUBE = enum.auto(),
	SHIP = enum.auto(),

class DeathCause(enum.Enum):
	GENERIC = enum.auto(),
	WALL = enum.auto(),
	CEILING = enum.auto(),

class Game:
	class Player:
		# All speeds are applied per second
		# Pygame has rotation speed CCW positive
		JUMP_SPEED = 0.34
		GRAVITY_SPEED = -(JUMP_SPEED * 4.5)
		ROTATION_SPEED = -450
		SHIP_ACCEL_SPEED = 0.03
		SHIP_GRAVITY_SPEED = -0.8
		# SHIP_ROTATION_SPEED = 200
		SHIP_ROTATION_LIMIT = (-30, 30)
		SHIP_ROTATION_LIMIT_SPEED = (-0.4, 0.4)

		CUBE_APPEARANCE = pygame.Surface((GRID_PIXEL_SIZE, GRID_PIXEL_SIZE), SRCALPHA)
		pygame.draw.rect(CUBE_APPEARANCE, (200, 200, 0), (0, 0, GRID_PIXEL_SIZE, GRID_PIXEL_SIZE))
		pygame.draw.rect(CUBE_APPEARANCE, (255, 255, 255), (0, 0, GRID_PIXEL_SIZE, GRID_PIXEL_SIZE), 1)

		SHIP_APPEARANCE = pygame.Surface((GRID_PIXEL_SIZE * 1.5, GRID_PIXEL_SIZE * 1.5), SRCALPHA)
		pygame.draw.rect(SHIP_APPEARANCE, (200, 200, 0), (GRID_PIXEL_SIZE * 0.25, GRID_PIXEL_SIZE * 0.25, GRID_PIXEL_SIZE, GRID_PIXEL_SIZE))
		pygame.draw.rect(SHIP_APPEARANCE, (255, 255, 255), (GRID_PIXEL_SIZE * 0.25, GRID_PIXEL_SIZE * 0.25, GRID_PIXEL_SIZE, GRID_PIXEL_SIZE), 1)
		pygame.draw.ellipse(SHIP_APPEARANCE, (128, 0, 128), (0, GRID_PIXEL_SIZE * 0.9, GRID_PIXEL_SIZE * 1.5, GRID_PIXEL_SIZE * 0.6))

		appearances: dict[GameMode, tuple[pygame.Surface, tuple[float, float]]] = {
			GameMode.CUBE: (CUBE_APPEARANCE, (0, 0)),
			GameMode.SHIP: (SHIP_APPEARANCE, (-GRID_PIXEL_SIZE*0.25, -GRID_PIXEL_SIZE*0.25)),
		}

		def __init__(self, game: "Game", level_objects: list[list["Game.Object"]]=[[]]):
			self.game_mode = GameMode.CUBE
			self.screen_pos = [4, 0]
			self.level_pos = 0
			self.speed = 0
			self.vector_time = 0
			self.rotation = 0
			self.last_frame_time = time.time()
			self.touching_orb = False
			self.touching_orb_speed = None

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
			
			match self.game_mode:
				case GameMode.CUBE:
					if not self.on_ground():
						self.rotation += self.ROTATION_SPEED * frame_time
				case GameMode.SHIP:
					self.rotation = scale(self.speed, self.SHIP_ROTATION_LIMIT_SPEED[0], self.SHIP_ROTATION_LIMIT_SPEED[1], self.SHIP_ROTATION_LIMIT[0], self.SHIP_ROTATION_LIMIT[1])
			
			touched_orb = False
			hitbox_rect = pygame.Rect(self.level_pos * GRID_PIXEL_SIZE, self.game.active_level_surfaces[0].get_height() - ((self.screen_pos[1] + 1) * GRID_PIXEL_SIZE), GRID_PIXEL_SIZE, GRID_PIXEL_SIZE)
			if DEBUG:
				debug_hitbox_rect = hitbox_rect.copy()
				debug_hitbox_rect.left %= MAX_SURFACE_WIDTH
				pygame.draw.rect(self.game.active_level_surfaces[int(self.level_pos * GRID_PIXEL_SIZE // MAX_SURFACE_WIDTH)], (0, 0, 255), debug_hitbox_rect, 1)
			for row in self.level_objects:
				for object in row:
					if object is None:
						continue
					if not NOCLIP:
						kills, death_cause = object.kills_player(hitbox_rect)
						if kills:
							if not (self.game_mode == GameMode.SHIP and death_cause == DeathCause.CEILING):							
								self.game.reset_level()
								return False
					if self.game_mode == GameMode.SHIP:
						ceilinged, ceiling_offset = object.ceilings_player(hitbox_rect)
						if self.screen_pos[1] >= 9:
							self.screen_pos[1] = 9
							self.speed = 0
						elif ceilinged:
							self.screen_pos[1] += ceiling_offset / GRID_PIXEL_SIZE
							self.speed = 0
							hitbox_rect = pygame.Rect(self.level_pos * GRID_PIXEL_SIZE, self.game.active_level_surfaces[0].get_height() - ((self.screen_pos[1] + 1)* GRID_PIXEL_SIZE), GRID_PIXEL_SIZE, GRID_PIXEL_SIZE)
					grounded, ground_offset = object.grounds_player(hitbox_rect)
					if grounded:
						self.screen_pos[1] += ground_offset / GRID_PIXEL_SIZE
						hitbox_rect = pygame.Rect(self.level_pos * GRID_PIXEL_SIZE, self.game.active_level_surfaces[0].get_height() - ((self.screen_pos[1] + 1)* GRID_PIXEL_SIZE), GRID_PIXEL_SIZE, GRID_PIXEL_SIZE)
					if object.colliding(hitbox_rect):
						if object.portal:
							self.switch_game_mode(object.game_mode)
						elif object.pad:
							self.pad(object.pad_speed)
						
						if object.orb:
							touched_orb = True
							self.touching_orb_speed = object.orb_speed
					if object.trigger:
						triggered, value = object.trigger_activate(hitbox_rect)

						if triggered:
							self.game.change_bg_colour(value)
			
			self.touching_orb = touched_orb
			return True

		def calculate_vector(self, speed, time_diff):
			if self.on_ground() and speed == 0:
				return 0
			match self.game_mode:
				case GameMode.CUBE:
					gravity = self.GRAVITY_SPEED
				case GameMode.SHIP:
					gravity = self.SHIP_GRAVITY_SPEED
			vector = speed + (gravity * time_diff)
			
			return vector

		def jump(self):
			speed = None
			if self.touching_orb:
				speed = self.touching_orb_speed
				self.touching_orb = False
			else:
				match self.game_mode:
					case GameMode.CUBE:
						if self.on_ground():
							speed = self.JUMP_SPEED
					case GameMode.SHIP:
						speed = self.speed + self.SHIP_ACCEL_SPEED
			
			if speed is not None:
				self.apply_speed(speed)
		
		def pad(self, pad_speed):
			if pad_speed is not None:
				self.apply_speed(pad_speed)

		def apply_speed(self, speed):
			self.speed = speed
			self.vector_time = time.time()
		
		def on_ground(self, pos=None):
			if pos is None:
				pos = (self.level_pos, self.screen_pos[1])
			if pos[1] <= 0:
				return True

			hitbox_rect = pygame.Rect(pos[0] * GRID_PIXEL_SIZE, self.game.active_level_surfaces[0].get_height() - ((pos[1] + 1) * GRID_PIXEL_SIZE), GRID_PIXEL_SIZE, GRID_PIXEL_SIZE)
			for row in self.level_objects:
				for object in row:
					if object is None:
						continue
					if object.grounds_player(hitbox_rect)[0]:
						return True

			return False

		def ground_pos(self, pos=None):
			if pos is None:
				pos = self.level_pos
			
			scan_rect = pygame.Rect(int(pos * GRID_PIXEL_SIZE), self.game.active_level_surfaces[0].get_height() - ((self.screen_pos[1] + 1) * GRID_PIXEL_SIZE), GRID_PIXEL_SIZE + 1, game.active_level_surfaces[0].get_height())
			if DEBUG:
				pygame.draw.rect(game.active_level_surfaces[0], (255, 255, 255), scan_rect, width=1)
			# Only check near objects
			start_column = int(pos) - 2
			columns = 5
			highest_ground_pos = game.active_level_surfaces[0].get_height()
			for row in self.level_objects:
				for object in row[start_column:start_column + columns]:
					if object is None:
						continue
					
					if object.ground and scan_rect.colliderect(object.absolute_hitbox_rect):
						highest_ground_pos = object.absolute_hitbox_rect.top if object.absolute_hitbox_rect.top < highest_ground_pos else highest_ground_pos
			
			return (game.active_level_surfaces[0].get_height() - highest_ground_pos) / GRID_PIXEL_SIZE

		def on_ceiling(self, pos=None):
			if pos is None:
				pos = (self.level_pos, self.screen_pos[1])
			if pos[1] >= 10:
				return True

			hitbox_rect = pygame.Rect(pos[0] * GRID_PIXEL_SIZE, self.game.active_level_surfaces[0].get_height() - ((pos[1] + 1) * GRID_PIXEL_SIZE), GRID_PIXEL_SIZE, GRID_PIXEL_SIZE)
			for row in self.level_objects:
				for object in row:
					if object is None:
						continue
					if object.ceilings_player(hitbox_rect)[0]:
						return True

			return False
		
		def switch_game_mode(self, game_mode: GameMode):
			if game_mode is None or game_mode == self.game_mode:
				return
			
			match game_mode:
				case GameMode.SHIP:
					self.speed /= 2
					self.rotation = 0
				case GameMode.CUBE:
					self.speed = 0

			self.game_mode = game_mode

	class Object(ABC):
		code: str
		kills: bool = False
		ground: bool = False
		portal: bool = False
		game_mode: GameMode | None = None
		pad: bool = False
		pad_speed: float | None = None
		orb: bool = False
		orb_speed: float | None = None
		trigger: bool = False
		trigger_activated: bool = False
		trigger_value: str = None
		appearance: pygame.Surface
		hitbox_rect: pygame.Rect

		def __init__(self, pos: tuple[int, int]):
			absolute_pos = (pos[0] + self.hitbox_rect.left, pos[1] + self.hitbox_rect.top)
			self.absolute_hitbox_rect = pygame.Rect(absolute_pos, self.hitbox_rect.size)
		
		def reset(self):
			self.trigger_activated = False
		
		def colliding(self, hitbox_rect: pygame.Rect):
			return self.absolute_hitbox_rect.colliderect(hitbox_rect)
		
		def kills_player(self, player_rect: pygame.Rect) -> tuple[bool, DeathCause]:
			if not self.kills and self.ground:
				if player_rect.colliderect(self.absolute_hitbox_rect):
					if (player_rect.top < self.absolute_hitbox_rect.bottom
						and player_rect.bottom > self.absolute_hitbox_rect.bottom
						and player_rect.top > self.absolute_hitbox_rect.centery):
						return (True, DeathCause.CEILING)
					if (player_rect.right > self.absolute_hitbox_rect.left 
						and player_rect.left < self.absolute_hitbox_rect.right
						and player_rect.bottom > self.absolute_hitbox_rect.top):
						return (True, DeathCause.WALL)
			if self.kills and player_rect.colliderect(self.absolute_hitbox_rect):
				return (True, DeathCause.GENERIC)
			return (False, None)

		def grounds_player(self, player_rect: pygame.Rect):
			if not self.ground:
				return False, 0
			moved_player_rect = player_rect.move(0, 1)
			return moved_player_rect.colliderect(self.absolute_hitbox_rect) and moved_player_rect.top < self.absolute_hitbox_rect.top, player_rect.bottom - self.absolute_hitbox_rect.top
		
		def ceilings_player(self, player_rect: pygame.Rect):
			if not self.ground:
				return False, 0
			moved_player_rect = player_rect.move(0, -1)
			return moved_player_rect.colliderect(self.absolute_hitbox_rect) and moved_player_rect.top > self.absolute_hitbox_rect.centery, player_rect.top - self.absolute_hitbox_rect.bottom
		
		def trigger_activate(self, player_rect: pygame.Rect):
			if not self.trigger or self.trigger_activated:
				return (False, "")
			activated = player_rect.centerx > self.absolute_hitbox_rect.centerx
			if activated:
				self.trigger_activated = True
				return (True, self.trigger_value)
			
			return (False, "")
	
	class Spike(Object):
		code = "S1"
		kills = True
		hitbox_rect = pygame.Rect(GRID_PIXEL_SIZE * 0.4, GRID_PIXEL_SIZE * 0.3, GRID_PIXEL_SIZE * 0.2, GRID_PIXEL_SIZE * 0.4)
		appearance = pygame.Surface((GRID_PIXEL_SIZE, GRID_PIXEL_SIZE), SRCALPHA)

		pygame.draw.polygon(appearance, (0, 0, 0), [(GRID_PIXEL_SIZE * 0.5, 0), (0, GRID_PIXEL_SIZE), (GRID_PIXEL_SIZE, GRID_PIXEL_SIZE)])
		pygame.draw.polygon(appearance, (255, 255, 255), [(GRID_PIXEL_SIZE * 0.5 - 1, 0), (0, GRID_PIXEL_SIZE - 1), (GRID_PIXEL_SIZE - 2, GRID_PIXEL_SIZE - 1)], 2)

	class SpikeFlipped(Object):
		code = "S2"
		kills = True
		hitbox_rect = pygame.Rect(GRID_PIXEL_SIZE * 0.4, GRID_PIXEL_SIZE * 0.3, GRID_PIXEL_SIZE * 0.2, GRID_PIXEL_SIZE * 0.4)
		appearance = pygame.Surface((GRID_PIXEL_SIZE, GRID_PIXEL_SIZE), SRCALPHA)

		pygame.draw.polygon(appearance, (0, 0, 0), [(GRID_PIXEL_SIZE * 0.5, GRID_PIXEL_SIZE), (GRID_PIXEL_SIZE, 0), (0, 0)])
		pygame.draw.polygon(appearance, (255, 255, 255), [(GRID_PIXEL_SIZE * 0.5 - 1, GRID_PIXEL_SIZE), (GRID_PIXEL_SIZE, 0 - 1), (0 - 2, 0 - 1)], 2)
	
	class ShortSpike(Object):
		code = "s1"
		kills = True
		hitbox_rect = pygame.Rect(GRID_PIXEL_SIZE * 0.4, GRID_PIXEL_SIZE * 0.7, GRID_PIXEL_SIZE * 0.2, GRID_PIXEL_SIZE * 0.2)
		appearance = pygame.Surface((GRID_PIXEL_SIZE, GRID_PIXEL_SIZE), SRCALPHA)

		pygame.draw.polygon(appearance, (0, 0, 0), [(GRID_PIXEL_SIZE * 0.5, GRID_PIXEL_SIZE * 0.5), (0, GRID_PIXEL_SIZE), (GRID_PIXEL_SIZE, GRID_PIXEL_SIZE)])
		pygame.draw.polygon(appearance, (255, 255, 255), [(GRID_PIXEL_SIZE * 0.5 - 1, GRID_PIXEL_SIZE * 0.5), (0, GRID_PIXEL_SIZE - 1), (GRID_PIXEL_SIZE - 2, GRID_PIXEL_SIZE - 1)], 2)

	class ShortSpikeFlipped(Object):
		code = "s2"
		kills = True
		hitbox_rect = pygame.Rect(GRID_PIXEL_SIZE * 0.4, GRID_PIXEL_SIZE * 0.1, GRID_PIXEL_SIZE * 0.2, GRID_PIXEL_SIZE * 0.2)
		appearance = pygame.Surface((GRID_PIXEL_SIZE, GRID_PIXEL_SIZE), SRCALPHA)

		pygame.draw.polygon(appearance, (0, 0, 0), [(GRID_PIXEL_SIZE * 0.5, GRID_PIXEL_SIZE * 0.5), (0, 0), (GRID_PIXEL_SIZE, 0)])
		pygame.draw.polygon(appearance, (255, 255, 255), [(GRID_PIXEL_SIZE * 0.5 - 1, GRID_PIXEL_SIZE * 0.5), (0, 0 - 1), (GRID_PIXEL_SIZE - 2, 0 - 1)], 2)
	
	class Block(Object):
		code = "B1"
		ground = True
		hitbox_rect = pygame.Rect(0, 0, GRID_PIXEL_SIZE, GRID_PIXEL_SIZE)
		appearance = pygame.Surface((GRID_PIXEL_SIZE, GRID_PIXEL_SIZE))

		pygame.draw.rect(appearance, (0, 0, 0), (0, 0, GRID_PIXEL_SIZE, GRID_PIXEL_SIZE))
		pygame.draw.rect(appearance, (255, 255, 255), (0, 0, GRID_PIXEL_SIZE, GRID_PIXEL_SIZE), 1)

	class HalfBlock(Object):
		code = "b1"
		ground = True
		hitbox_rect = pygame.Rect(0, 0, GRID_PIXEL_SIZE, GRID_PIXEL_SIZE/2)
		appearance = pygame.Surface((GRID_PIXEL_SIZE, GRID_PIXEL_SIZE/2))

		pygame.draw.rect(appearance, (0, 0, 0), (0, 0, GRID_PIXEL_SIZE, GRID_PIXEL_SIZE/2))
		pygame.draw.rect(appearance, (255, 255, 255), (0, 0, GRID_PIXEL_SIZE, GRID_PIXEL_SIZE/2), 1)
	
	class CubePortal(Object):
		code = "P0"
		portal = True
		game_mode = GameMode.CUBE
		hitbox_rect = pygame.Rect(0, 0, GRID_PIXEL_SIZE, GRID_PIXEL_SIZE * 3)
		appearance = pygame.Surface((GRID_PIXEL_SIZE, GRID_PIXEL_SIZE * 3), SRCALPHA)

		pygame.draw.ellipse(appearance, (0, 128, 0), (0, 0, GRID_PIXEL_SIZE, GRID_PIXEL_SIZE * 3))

	class ShipPortal(Object):
		code = "P1"
		portal = True
		game_mode = GameMode.SHIP
		hitbox_rect = pygame.Rect(0, 0, GRID_PIXEL_SIZE, GRID_PIXEL_SIZE * 3)
		appearance = pygame.Surface((GRID_PIXEL_SIZE, GRID_PIXEL_SIZE * 3), SRCALPHA)

		pygame.draw.ellipse(appearance, (128, 0, 128), (0, 0, GRID_PIXEL_SIZE, GRID_PIXEL_SIZE * 3))
		pygame.draw.ellipse(appearance, (255, 255, 255), (0, 0, GRID_PIXEL_SIZE, GRID_PIXEL_SIZE * 3), 1)
	
	class YellowPad(Object):
		code = "p1"
		pad = True
		pad_speed = 0.48
		hitbox_rect = pygame.Rect(0, GRID_PIXEL_SIZE * 0.9, GRID_PIXEL_SIZE, GRID_PIXEL_SIZE * 0.1)
		appearance = pygame.Surface((GRID_PIXEL_SIZE, GRID_PIXEL_SIZE), SRCALPHA)

		pygame.draw.ellipse(appearance, (255, 255, 0), (0, GRID_PIXEL_SIZE * 0.9, GRID_PIXEL_SIZE, GRID_PIXEL_SIZE * 0.2))

	class YellowOrb(Object):
		code = "o1"
		orb = True
		orb_speed = 0.34
		hitbox_rect = pygame.Rect(0, 0, GRID_PIXEL_SIZE, GRID_PIXEL_SIZE)
		appearance = pygame.Surface((GRID_PIXEL_SIZE, GRID_PIXEL_SIZE), SRCALPHA)

		pygame.draw.circle(appearance, (255, 255, 0), (GRID_PIXEL_SIZE * 0.5, GRID_PIXEL_SIZE * 0.5), GRID_PIXEL_SIZE * 0.5)
	
	class BackgroundTrigger(Object):
		code = "bg"
		trigger = True
		hitbox_rect = pygame.Rect(0, 0, 0, 0)
		appearance = pygame.Surface((0, 0))

	objects: list[Object] = [
		Spike,
		SpikeFlipped,
		ShortSpike,
		ShortSpikeFlipped,
		Block,
		HalfBlock,
		CubePortal,
		ShipPortal,
		YellowPad,
		YellowOrb,
		BackgroundTrigger
	]

	class Level:
		def __init__(self, name, music, colour, level, progress):
			self.name: str = name
			self.music: str | None = music
			self.colour: tuple[int, int, int] = tuple(colour)
			self.level: list[list[Game.Level.Object]] = level
			self.progress: int = progress

		@staticmethod
		def parse_level(levelData: str) -> Self | None:
			level_data = None
			try:
				# Ensure data is valid
				level_data = json.loads(levelData)
				assert "name" in level_data
				assert "music" in level_data
				assert "colour" in level_data
				assert "level" in level_data
			except (ValueError, AssertionError):
				raise ValueError
			
			music_file_path = os.path.join(MUSIC_PATH, level_data["music"])
			music = music_file_path if os.path.exists(music_file_path) and os.path.isfile(music_file_path) else None

			level_strings = level_data["level"]
			level_objects = []
			for y in range(len(level_strings)):
				row = level_strings[y]
				level_objects.append([None for column in range(len(row))])
				for x in range(len(row)):
					string: str = row[x]
					for object_option in Game.objects:
						if object_option.trigger:
							if string.startswith(object_option.code):
								level_objects[y][x] = object_option((x * GRID_PIXEL_SIZE, y * GRID_PIXEL_SIZE))
								level_objects[y][x].trigger_value = string[2:]
								break
						else:
							if object_option.code == string:
								level_objects[y][x] = object_option((x * GRID_PIXEL_SIZE, y * GRID_PIXEL_SIZE))
								break
						level_objects[y][x] = None
			
			return Game.Level(
					level_data["name"],
					music,
					level_data["colour"],
					level_objects,
					0
			)
		
		def __str__(self):
			return f"{self.name=};{self.music=};{self.colour=};{self.level=}"
	
	icon = pygame.Surface((32, 32), SRCALPHA)
	pygame.draw.polygon(icon, (200, 200, 0), [(10, 0), (0, 10), (10, 20), (20, 10)])
	pygame.draw.polygon(icon, (0, 0, 0), [(18, 32), (25, 18), (32, 32)])

	def __init__(self):
		self.running = True
		self.state = GameState.MAIN_MENU
		self.size = self.width, self.height = 1280, 800

		pygame.init()
		pygame.display.set_caption("Rhythm Rush")
		pygame.display.set_icon(self.icon)
		self.display_surf = pygame.display.set_mode(self.size)
		self.title_font_object = pygame.font.Font(pygame.font.get_default_font(), 150)
		self.level_font_object = pygame.font.Font(pygame.font.get_default_font(), 100)
		self.percentage_font_object = pygame.font.Font(pygame.font.get_default_font(), 30)
		self.menu_music_playing = True
		pygame.mixer.music.load(MENU_MUSIC_FILE)
		pygame.mixer.music.play(-1)

		self.shown_level_index = 0

		self.levels = self.get_levels()

		self.player = None
		self.active_level = None
		self.active_level_surfaces: list[pygame.Surface] = None
		self.bg_colour: pygame.Color = pygame.Color(0, 0, 128)
		self.last_render_time = None
		self.level_x = 0
		self.open_level_jumped = False
		self.music_loaded = False
		self.percentage = 0
	
		self.shown_won_screen = False
	
	def get_levels(self) -> list[Level]:
		if not os.path.isdir(LEVEL_PATH):
			print(f"Level path not found! Currently: \"{LEVEL_PATH}\". Change the path or make the folder")
		if not os.path.isfile(PROGRESS_FILE):
			file = open(PROGRESS_FILE, "x")
			file.write("{}")
			
		progresses: dict[str: int] = {}
		with open(PROGRESS_FILE, "r") as file:
			try:
				progresses = json.load(file)
			except ValueError:
				print(f"Invalid progress file found! Fix or delete the file at {PROGRESS_FILE}")
				sys.exit()
				return []

		level_files = os.listdir(LEVEL_PATH)

		levels = []
		for level_file in level_files:
			if not level_file.endswith(".level"):
				continue
			with open(os.path.join(LEVEL_PATH, level_file)) as file:
				try:
					level: Game.Level = Game.Level.parse_level(file.read())
					progress = progresses.get(level.name)
					if progress is not None:
						level.progress = progress
				except ValueError:
					print(f"Error parsing level data for {file.name}")
				if level is None:
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
			elif event.type == KEYUP:
				if (event.key == K_w
					or event.key == K_SPACE
					or event.key == K_UP):
					self.open_level_jumped = False

		match self.state:
			case GameState.MAIN_MENU:
				self.display_surf.fill((0, 0, 128))

				pygame.draw.polygon(self.display_surf, (200, 200, 0), [(300, 200), (475, 375), (300, 550), (125, 375)])
				pygame.draw.polygon(self.display_surf, (255, 255, 255), [(300, 200), (475, 375), (300, 550), (125, 375)], 3)
				pygame.draw.polygon(self.display_surf, (0, 0, 0), [(540, 488), (671, 750), (409, 750)])
				pygame.draw.polygon(self.display_surf, (255, 255, 255), [(540, 488), (671, 750), (409, 750)], 3)

				pygame.draw.circle(self.display_surf, (255, 255, 0), (1000, 400), 150)
				pygame.draw.circle(self.display_surf, (0, 190, 0), (1000, 400), 130)
				pygame.draw.polygon(self.display_surf, (255, 255, 0), [(1060, 400), (960, 320), (960, 480)])
				if (buttons_pressed["mouse"]
						and pos_in_circle((1000, 400), 150, pygame.mouse.get_pos())) or buttons_pressed["jump"]:
					self.open_level_menu()

				text_surface = self.title_font_object.render("Rhythm Rush", True, (255, 255, 255))
				text_rect = text_surface.get_rect()
				text_rect.center = (640, 150)
				self.display_surf.blit(text_surface, text_rect)

			case GameState.LEVEL_MENU:
				level = self.levels[self.shown_level_index] if self.shown_level_index < len(self.levels) else None
				self.display_surf.fill(level.colour)
				textSurfaceObj = self.level_font_object.render(f"{level.name if level is not None else f"None {self.shown_level_index}"}", True, (255, 255, 255))
				textRectObj = textSurfaceObj.get_rect()
				textRectObj.center = (640, 300)

				textBgRect = pygame.Rect(0, 0, 1000, 400)
				textBgRect.center = textRectObj.center
				pygame.draw.rect(self.display_surf, (0, 0, 0), textBgRect, border_radius=20)

				self.display_surf.blit(textSurfaceObj, textRectObj)

				percentage = self.levels[self.shown_level_index].progress
				textPercentageSurfaceObj = self.percentage_font_object.render(f"{percentage}%", True, (255, 255, 255))
				textPercentageRectObj = textPercentageSurfaceObj.get_rect()
				textPercentageRectObj.center = (640, 600)

				progress_total_width = 1000
				progress_width = progress_total_width * (percentage / 100)

				progress_bar_bg = pygame.Rect(0, 0, progress_total_width, 50)
				progress_bar_bg.center = (640, 600)
				pygame.draw.rect(self.display_surf, (20, 20, 20), progress_bar_bg, border_radius=20)

				progress_bar = pygame.Rect((self.width - progress_total_width) / 2, 0, progress_width, 50)
				progress_bar.centery = 600
				pygame.draw.rect(self.display_surf, (0, 150, 0), progress_bar, border_radius=20)

				progress_bar_outline = progress_bar_bg.copy()
				progress_bar_outline.width += 3
				progress_bar_outline.height += 3
				progress_bar_outline.center = progress_bar_bg.center
				pygame.draw.rect(self.display_surf, (255, 255, 255), progress_bar_outline, 3, border_radius=20)

				self.display_surf.blit(textPercentageSurfaceObj, textPercentageRectObj)

				left_arrow = pygame.draw.polygon(self.display_surf, (255, 255, 255), [(20, 400), (60, 440), (60, 360)])
				right_arrow = pygame.draw.polygon(self.display_surf, (255, 255, 255), [(1260, 400), (1220, 440), (1220, 360)])
				if (buttons_pressed["left"]):
					self.shown_level_index = self.shown_level_index - 1 if self.shown_level_index > 0 else len(self.levels) - 1
				elif (buttons_pressed["right"]):
					self.shown_level_index = self.shown_level_index + 1 if self.shown_level_index + 1 < len(self.levels) else 0

				pygame.draw.circle(self.display_surf, (255, 255, 0), (60, 60), 30)
				pygame.draw.circle(self.display_surf, (0, 190, 0), (60, 60), 25)
				pygame.draw.polygon(self.display_surf, (255, 255, 255), [(50, 60), (65, 50), (65, 70)])
				if buttons_pressed["mouse"]:
					mouse_pos = pygame.mouse.get_pos()
					if pos_in_circle((60, 60), 30, mouse_pos):
						self.state = GameState.MAIN_MENU
					elif textBgRect.collidepoint(mouse_pos):
						self.open_level(self.shown_level_index)
					elif left_arrow.collidepoint(mouse_pos):
						self.shown_level_index = self.shown_level_index - 1 if self.shown_level_index > 0 else len(self.levels) - 1
					elif right_arrow.collidepoint(mouse_pos):
						self.shown_level_index = self.shown_level_index + 1 if self.shown_level_index + 1 < len(self.levels) else 0

				elif buttons_pressed["jump"]:
					self.open_level_jumped = True
					self.open_level(self.shown_level_index)

				if buttons_pressed["escape"]:
					self.state = GameState.MAIN_MENU
			case GameState.PLAYING_LEVEL:
				SPEED = (1000 / 96.3) * GRID_PIXEL_SIZE
				current_time = time.time()
				time_diff = current_time - self.last_render_time
				x_diff = -SPEED * time_diff
				self.level_x = self.level_x - x_diff
				self.last_render_time = current_time

				screen = pygame.Surface(self.size)
				screen.fill(self.bg_colour)
				for i in range(len(self.active_level_surfaces)):
					level_surface = self.active_level_surfaces[i]

					target_rect = level_surface.get_rect()
					target_rect.bottom = self.height
					target_rect.left = -self.level_x + (i * (MAX_SURFACE_WIDTH - 10))

					screen.blit(level_surface, target_rect)

				if self.jump_input():
					self.player.jump()
				if not self.player.update():
					return

				player_appearance = self.player.appearances[self.player.game_mode]
				player_rect = pygame.Rect(self.player.screen_pos[0] * GRID_PIXEL_SIZE + player_appearance[1][0], (self.height - (self.player.screen_pos[1] + 1) * GRID_PIXEL_SIZE) + player_appearance[1][1], GRID_PIXEL_SIZE, GRID_PIXEL_SIZE)
				rotated_player = pygame.transform.rotate(player_appearance[0], self.player.rotation)
				screen.blit(rotated_player, player_rect)

				self.display_surf.blit(screen, (0, 0, self.width, self.height))

				percentage = self.get_level_percentage()
				percentage_text = f"{percentage * 100:.0f}%"
				if DEBUG:
					percentage_text = f"{percentage_text} {self.player.level_pos:.2f}"
				textSurfaceObj = self.percentage_font_object.render(percentage_text, True, (255, 255, 255))
				textRectObj = textSurfaceObj.get_rect()
				textRectObj.centerx = 640
				textRectObj.top = self.height * 0.02

				self.display_surf.blit(textSurfaceObj, textRectObj)

				self.percentage = int(percentage * 100)
				if percentage >= 1:
					self.win_level()
					return

				if buttons_pressed["escape"]:
					self.close_level()

			case GameState.WON_LEVEL:
				if self.shown_won_screen:
					if (buttons_pressed["escape"] or buttons_pressed["jump"]
						or (buttons_pressed["mouse"] and pos_in_circle((self.width * 0.5, self.height * 0.7), 100, pygame.mouse.get_pos()))):
						self.close_level()
					return
				
				pygame.draw.rect(self.display_surf, (10, 10, 10), (self.width * 0.1, self.height * 0.1, self.width * 0.8, self.height * 0.6), border_radius=20)

				textSurfaceObj = self.level_font_object.render("Completed Level!", True, (255, 255, 255))
				textRectObj = textSurfaceObj.get_rect()
				textRectObj.center = (640, 300)

				self.display_surf.blit(textSurfaceObj, textRectObj)

				pygame.draw.circle(self.display_surf, (0, 128, 0), (self.width * 0.5, self.height * 0.7), 100)

				draw_arrow(self.display_surf, (self.width * 0.5 - 60, self.height * 0.7), (self.width * 0.5 + 70, self.height * 0.7), (255, 255, 255), 30, 80, 50)

				self.shown_won_screen = True

		pygame.display.update()
	
	def open_level_menu(self):
		self.state = GameState.LEVEL_MENU
		self.shown_level_index = 0

	def open_level(self, index: int):
		self.state = GameState.PLAYING_LEVEL
		self.active_level = self.levels[index]
		self.player = Game.Player(self, self.active_level.level)
		self.active_level_surfaces = self.render_level(self.active_level)
		self.bg_colour = pygame.Color(0, 0, 128)
		self.last_render_time = time.time()
		self.level_x = 0
		self.percentage = 0
		pygame.mixer.music.unload()
		self.menu_music_playing = False
		for row in self.active_level.level:
			for object in row:
				if object is not None:
					object.reset()
		if self.active_level.music is not None:
			try:
				pygame.mixer.music.load(self.active_level.music)
			except pygame.error:
				return
			pygame.mixer.music.play()
			self.music_loaded = True

	def close_level(self):
		if self.percentage > self.active_level.progress:
			percentage = clamp(self.percentage, 0, 100)
			self.save_level_progress(self.active_level.name, percentage)
			self.active_level.progress = percentage

		self.state = GameState.LEVEL_MENU
		self.player = None
		self.active_level = None
		self.active_level_surfaces = None
		self.bg_colour = None
		self.last_render_time = None
		pygame.mixer.music.stop()
		pygame.mixer.music.unload()
		self.music_loaded = False
		pygame.mixer.music.load(MENU_MUSIC_FILE)
		pygame.mixer.music.play(-1)
		self.menu_music_playing = True
		self.percentage = 0
	
	def reset_level(self):
		if self.percentage > self.active_level.progress:
			percentage = clamp(self.percentage, 0, 100)
			self.save_level_progress(self.active_level.name, percentage)
			self.active_level.progress = percentage

		self.player = Game.Player(self, self.active_level.level)
		self.level_x = 0
		self.bg_colour = pygame.Color(0, 0, 128)
		self.last_render_time = time.time()
		for row in self.active_level.level:
			for object in row:
				if object is not None:
					object.reset()
		if self.music_loaded:
			pygame.mixer.music.play()
	
	def render_level(self, level: Level):
		objects = level.level
		max_width = len(objects[0])
		for row in objects[1:]:
			max_width = max_width if len(row) < max_width else len(row)
		
		level_surfaces = []
		remaining_width = max_width * GRID_PIXEL_SIZE
		object_range = (0, 0)
		while remaining_width > 0:
			surface_width = remaining_width if remaining_width <= MAX_SURFACE_WIDTH else MAX_SURFACE_WIDTH
			object_range = (object_range[1], int((object_range[1] + 1) + (surface_width / GRID_PIXEL_SIZE) - 1))
			remaining_width -= surface_width
			level_surface = pygame.Surface((surface_width, len(objects) * GRID_PIXEL_SIZE), SRCALPHA)

			for y in range(len(objects)):
				row = objects[y]
				for x in range(object_range[0], object_range[1]):
					object = row[x]
					if object is None:
						continue
					
					object_rect = pygame.Rect((x - object_range[0]) * GRID_PIXEL_SIZE, y * GRID_PIXEL_SIZE, object.appearance.get_size()[0], object.appearance.get_size()[1])
					level_surface.blit(object.appearance, object_rect)
					if DEBUG:
						hitbox_rect = object.absolute_hitbox_rect.copy()
						hitbox_rect.left -= object_range[0] * GRID_PIXEL_SIZE
						pygame.draw.rect(level_surface, (255, 0, 0), hitbox_rect, 1)
			
			level_surfaces.append(level_surface)
			
		return level_surfaces

	# Used when player can hold to repeatedly jump
	def jump_input(self):
		return not self.open_level_jumped and (pygame.key.get_pressed()[K_w] or
		pygame.key.get_pressed()[K_SPACE] or
		pygame.key.get_pressed()[K_UP] or
		pygame.mouse.get_pressed()[0])

	def change_bg_colour(self, colour: str):
		new_colour = self.bg_colour
		try:
			new_colour = pygame.Color(colour)
		except ValueError:
			return
		self.bg_colour = new_colour
	
	def get_level_percentage(self):
		width = 0
		for surface in self.active_level_surfaces:
			width += surface.get_width()
		return (self.player.level_pos - self.player.screen_pos[0]) / (width / GRID_PIXEL_SIZE)
	
	def win_level(self):
		self.state = GameState.WON_LEVEL
		self.shown_won_screen = False

	def save_level_progress(self, level_name: str, percentage: int):
		try:
			progresses = json.load(open(PROGRESS_FILE, "r"))
		except:
			print(f"Failed to load the progress file! Fix or delete the file at {PROGRESS_FILE}")
			return
		progresses[level_name] = percentage
		try:
			json.dump(progresses, open(PROGRESS_FILE, "w"))
		except:
			print(f"Failed to save progress to {PROGRESS_FILE}! Progress not saved!")

if __name__ == "__main__" :
	fpsClock = pygame.time.Clock()
	game = Game()
	count = 0
	while game.running:
		game.loop()
		fpsClock.tick(FPS)