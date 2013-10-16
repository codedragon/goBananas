from math import sqrt


def distance(self, x, y):
    """
    (tuple, tuple) -> float
    Returns the distance between 2 points. x is a tuple with (x1, x2)
    and y is a tuple with (y1, y2)
    """
    dist = sqrt((x[2] - x[1]) ** 2 + (y[2] - y[1]) ** 2)
    return dist
