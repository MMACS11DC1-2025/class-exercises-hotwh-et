import math
import pygame

def pos_in_circle(circle_centre: tuple[int, int], circle_radius: int, pos: tuple[int, int]):
	x, y = pos
	circle_x, circle_y = circle_centre

	x_squared = (x - circle_x) ** 2
	y_squared = (y - circle_y) ** 2

	if math.sqrt(x_squared + y_squared) < circle_radius:
		return True
	return False

def clamp(num: float, min: float, max: float):
	return min if num < min else max if num > max else num

def scale(num: float, min_old: float, max_old: float, min_new: float, max_new: float):
	return min_new + ((num - min_old) / (max_old - min_old)) * (max_new - min_new)

# Copied from "plastic_astronomer" and modified
def draw_arrow(
        surface: pygame.Surface,
        start: tuple[int, int],
        end: tuple[int, int],
        color: pygame.Color,
        body_width: int = 2,
        head_width: int = 4,
        head_height: int = 2,
    ):
    """Draw an arrow between start and end with the arrow head at the end.

    Args:
        surface (pygame.Surface): The surface to draw on
        start (pygame.Vector2): Start position
        end (pygame.Vector2): End position
        color (pygame.Color): Color of the arrow
        body_width (int, optional): Defaults to 2.
        head_width (int, optional): Defaults to 4.
        head_height (float, optional): Defaults to 2.
    """
    start_vector = pygame.Vector2(start)
    end_vector = pygame.Vector2(end)
    arrow = start_vector - end_vector
    angle = arrow.angle_to(pygame.Vector2(0, -1))
    body_length = arrow.length() - head_height

    # Create the triangle head around the origin
    head_verts = [
        pygame.Vector2(0, head_height / 2),  # Center
        pygame.Vector2(head_width / 2, -head_height / 2),  # Bottomright
        pygame.Vector2(-head_width / 2, -head_height / 2),  # Bottomleft
    ]
    # Rotate and translate the head into place
    translation = pygame.Vector2(0, arrow.length() - (head_height / 2)).rotate(-angle)
    for i in range(len(head_verts)):
        head_verts[i].rotate_ip(-angle)
        head_verts[i] += translation
        head_verts[i] += start_vector

    pygame.draw.polygon(surface, color, head_verts)

    # Stop weird shapes when the arrow is shorter than arrow head
    if arrow.length() >= head_height:
        # Calculate the body rect, rotate and translate into place
        body_verts = [
            pygame.Vector2(-body_width / 2, body_length / 2),  # Topleft
            pygame.Vector2(body_width / 2, body_length / 2),  # Topright
            pygame.Vector2(body_width / 2, -body_length / 2),  # Bottomright
            pygame.Vector2(-body_width / 2, -body_length / 2),  # Bottomleft
        ]
        translation = pygame.Vector2(0, body_length / 2).rotate(-angle)
        for i in range(len(body_verts)):
            body_verts[i].rotate_ip(-angle)
            body_verts[i] += translation
            body_verts[i] += start_vector

        pygame.draw.polygon(surface, color, body_verts)