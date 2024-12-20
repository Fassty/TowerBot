import random

def bbox_get_inscribed_circle(x1, y1, x2, y2, size = 0.6):
    center_x = (x1 + x2) // 2
    center_y = (y1 + y2) // 2
    dist_x = x2 - x1
    dist_y = y2 - y1
    radius = int(min(dist_x, dist_y) * size / 2)
    return center_x, center_y, radius

def random_point_inside_circle(center_x: int, center_y: int, radius: int):
    """
    Generate coordinates of random point inside a circle with given center and radius.
    Args:
        center_x (int): X-coordinate of the circle center.
        center_y (int): Y-coordinate of the circle center.
        radius (int): Radius of the circle.
    """
    while True:
        rand_x = random.randint(-radius, radius)
        rand_y = random.randint(-radius, radius)
        if rand_x**2 + rand_y**2 <= radius**2:  # Check if point is inside the circle
            break
    return center_x + rand_x, center_y + rand_y