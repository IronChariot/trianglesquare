import pygame
import sys
import math
from triangle_logic import TriangleDetector

# Initialize Pygame
pygame.init()

# Set up the display
WIDTH, HEIGHT = 800, 800
SQUARE_SIZE = 400
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Triangle Puzzle")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

# Game variables
lines = []
start_pos = None
snap_distance = 20
line_snap_distance = 10

def distance(p1, p2):
    return math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)

def closest_point_on_line(point, line_start, line_end):
    x1, y1 = line_start
    x2, y2 = line_end
    x3, y3 = point
    
    px = x2-x1
    py = y2-y1
    
    norm = px*px + py*py
    
    u = ((x3 - x1) * px + (y3 - y1) * py) / float(norm)
    
    if u > 1:
        u = 1
    elif u < 0:
        u = 0
    
    x = x1 + u * px
    y = y1 + u * py
    
    return (int(x), int(y))

def snap_point(pos):
    # Snap to points
    for line in lines + square_lines:
        if distance(pos, line[0]) <= snap_distance:
            return line[0]
        if distance(pos, line[1]) <= snap_distance:
            return line[1]
    
    # Snap to lines
    for line in lines + square_lines:
        closest = closest_point_on_line(pos, line[0], line[1])
        if distance(pos, closest) <= line_snap_distance:
            return closest
    
    return pos

def line_intersection(line1, line2):
    x1, y1 = line1[0]
    x2, y2 = line1[1]
    x3, y3 = line2[0]
    x4, y4 = line2[1]

    den = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
    if den == 0:  # Lines are parallel
        return None

    t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / den
    u = -((x1 - x2) * (y1 - y3) - (y1 - y2) * (x1 - x3)) / den

    if 0 <= t <= 1 and 0 <= u <= 1:
        x = x1 + t * (x2 - x1)
        y = y1 + t * (y2 - y1)
        return int(x), int(y)
    return None

def split_line(line, point):
    return [(line[0], point), (point, line[1])]

def add_line_with_intersections(new_line):
    all_lines = lines + square_lines
    intersections = []
    lines_to_split = []

    for i, line in enumerate(all_lines):
        intersection = line_intersection(new_line, line)
        if intersection and intersection not in [line[0], line[1]]:
            intersections.append(intersection)
            lines_to_split.append((i, line))

    # Sort intersections along the new line
    intersections.sort(key=lambda p: (p[0] - new_line[0][0])**2 + (p[1] - new_line[0][1])**2)

    # Split existing lines
    for i, line in reversed(lines_to_split):
        if i < len(square_lines):  # It's a square line
            split_segments = split_line(line, intersections[lines_to_split.index((i, line))])
            square_lines[i] = split_segments[0]
            square_lines.insert(i + 1, split_segments[1])
        else:  # It's a user-drawn line
            split_segments = split_line(line, intersections[lines_to_split.index((i, line))])
            lines[i - len(square_lines)] = split_segments[0]
            lines.insert(i - len(square_lines) + 1, split_segments[1])

    # Add new line segments
    prev_point = new_line[0]
    for point in intersections + [new_line[1]]:
        if point != prev_point:
            lines.append((prev_point, point))
        prev_point = point

    # Update triangle detector
    triangle_detector.reset()
    for line in square_lines + lines:
        triangle_detector.add_line(line[0], line[1])

# Create square lines
square_start = ((WIDTH - SQUARE_SIZE) // 2, (HEIGHT - SQUARE_SIZE) // 2)
square_end = (square_start[0] + SQUARE_SIZE, square_start[1] + SQUARE_SIZE)
square_lines = [
    (square_start, (square_end[0], square_start[1])),
    ((square_end[0], square_start[1]), square_end),
    (square_end, (square_start[0], square_end[1])),
    ((square_start[0], square_end[1]), square_start)
]

# Create TriangleDetector instance
triangle_detector = TriangleDetector()

# Add square lines to TriangleDetector
for line in square_lines:
    triangle_detector.add_line(line[0], line[1])

# Main game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            start_pos = snap_point(pygame.mouse.get_pos())
        elif event.type == pygame.MOUSEBUTTONUP:
            end_pos = snap_point(pygame.mouse.get_pos())
            if start_pos != end_pos:
                add_line_with_intersections((start_pos, end_pos))
            start_pos = None
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_z and lines:  # Undo last line
                lines.pop()
                triangle_detector.reset()
                for line in square_lines + lines:
                    triangle_detector.add_line(line[0], line[1])
            elif event.key == pygame.K_r:  # Reset all lines
                lines.clear()
                triangle_detector.reset()
                square_lines = [  # Reset square lines to original state
                    (square_start, (square_end[0], square_start[1])),
                    ((square_end[0], square_start[1]), square_end),
                    (square_end, (square_start[0], square_end[1])),
                    ((square_start[0], square_end[1]), square_start)
                ]
                for line in square_lines:
                    triangle_detector.add_line(line[0], line[1])

    screen.fill(WHITE)
    
    # Draw triangles
    triangles = triangle_detector.find_triangles()
    for triangle in triangles:
        color = GREEN if triangle_detector.is_acute(triangle) else RED
        pygame.draw.polygon(screen, color, triangle)
    
    # Draw the square
    for line in square_lines:
        pygame.draw.line(screen, BLACK, line[0], line[1], 2)
    
    # Draw existing lines
    for line in lines:
        pygame.draw.line(screen, BLACK, line[0], line[1], 2)
    
    # Draw the line being created
    if start_pos:
        end_pos = snap_point(pygame.mouse.get_pos())
        pygame.draw.line(screen, BLACK, start_pos, end_pos, 2)
    
    # Draw the blue dot
    cursor_pos = snap_point(pygame.mouse.get_pos())
    pygame.draw.circle(screen, BLUE, cursor_pos, 5)
    
    pygame.display.flip()

pygame.quit()
sys.exit()