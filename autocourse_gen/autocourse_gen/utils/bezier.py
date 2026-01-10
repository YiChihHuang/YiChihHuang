"""
Bezier Curve Utilities
======================

Provides Bezier curve calculations for smooth mouse movement animation.
Simulates natural human-like cursor movement.
"""

import math
from typing import List, Tuple
from dataclasses import dataclass

import numpy as np
from scipy.special import comb


@dataclass
class Point:
    """2D point with x, y coordinates."""
    x: float
    y: float

    def __add__(self, other: "Point") -> "Point":
        return Point(self.x + other.x, self.y + other.y)

    def __sub__(self, other: "Point") -> "Point":
        return Point(self.x - other.x, self.y - other.y)

    def __mul__(self, scalar: float) -> "Point":
        return Point(self.x * scalar, self.y * scalar)

    def __rmul__(self, scalar: float) -> "Point":
        return self * scalar

    def to_tuple(self) -> Tuple[float, float]:
        return (self.x, self.y)

    def distance_to(self, other: "Point") -> float:
        return math.sqrt((self.x - other.x) ** 2 + (self.y - other.y) ** 2)


class BezierCurve:
    """
    Bezier curve calculator for smooth path generation.

    Supports any degree Bezier curve (quadratic, cubic, etc.)
    """

    def __init__(self, control_points: List[Point]):
        """
        Initialize with control points.

        Args:
            control_points: List of control points defining the curve
        """
        self.control_points = control_points
        self.n = len(control_points) - 1  # Degree of the curve

    def point_at(self, t: float) -> Point:
        """
        Calculate point on curve at parameter t.

        Args:
            t: Parameter value (0.0 to 1.0)

        Returns:
            Point on the curve
        """
        if not 0 <= t <= 1:
            t = max(0, min(1, t))

        x = 0.0
        y = 0.0

        for i, point in enumerate(self.control_points):
            # Bernstein polynomial coefficient
            coeff = comb(self.n, i, exact=True) * (t ** i) * ((1 - t) ** (self.n - i))
            x += coeff * point.x
            y += coeff * point.y

        return Point(x, y)

    def generate_path(self, num_points: int = 60) -> List[Point]:
        """
        Generate a path of points along the curve.

        Args:
            num_points: Number of points to generate

        Returns:
            List of points along the curve
        """
        return [
            self.point_at(t / (num_points - 1))
            for t in range(num_points)
        ]


def generate_smooth_path(
    start: Tuple[float, float],
    end: Tuple[float, float],
    num_points: int = 60,
    curvature: float = 0.3,
    randomness: float = 0.1,
) -> List[Tuple[float, float]]:
    """
    Generate a smooth, human-like path between two points.

    Uses cubic Bezier curves with randomized control points
    to simulate natural mouse movement.

    Args:
        start: Starting point (x, y)
        end: Ending point (x, y)
        num_points: Number of points in the path
        curvature: How curved the path should be (0-1)
        randomness: Random variation in control points (0-1)

    Returns:
        List of (x, y) tuples representing the path
    """
    start_point = Point(start[0], start[1])
    end_point = Point(end[0], end[1])

    # Calculate distance and midpoint
    distance = start_point.distance_to(end_point)
    mid_x = (start[0] + end[0]) / 2
    mid_y = (start[1] + end[1]) / 2

    # Generate control points with some randomness
    # This creates a more natural, human-like movement
    np.random.seed(None)  # Use random seed

    # Control point offsets based on curvature
    offset_magnitude = distance * curvature

    # Perpendicular direction for curve
    dx = end[0] - start[0]
    dy = end[1] - start[1]

    # Perpendicular vector (normalized)
    if distance > 0:
        perp_x = -dy / distance
        perp_y = dx / distance
    else:
        perp_x, perp_y = 0, 1

    # Random offsets
    rand1 = (np.random.random() - 0.5) * 2 * randomness
    rand2 = (np.random.random() - 0.5) * 2 * randomness

    # Control points for cubic Bezier
    # First control point: 1/3 of the way, with perpendicular offset
    cp1 = Point(
        start[0] + dx / 3 + perp_x * offset_magnitude * (1 + rand1),
        start[1] + dy / 3 + perp_y * offset_magnitude * (1 + rand1),
    )

    # Second control point: 2/3 of the way, with opposite perpendicular offset
    cp2 = Point(
        start[0] + 2 * dx / 3 + perp_x * offset_magnitude * (-0.5 + rand2),
        start[1] + 2 * dy / 3 + perp_y * offset_magnitude * (-0.5 + rand2),
    )

    # Create cubic Bezier curve
    curve = BezierCurve([start_point, cp1, cp2, end_point])

    # Generate path with easing
    path = []
    for i in range(num_points):
        # Apply ease-in-out for more natural movement
        t = i / (num_points - 1)
        eased_t = ease_in_out_cubic(t)
        point = curve.point_at(eased_t)
        path.append(point.to_tuple())

    return path


def ease_in_out_cubic(t: float) -> float:
    """
    Cubic ease-in-out function.

    Creates smooth acceleration and deceleration.

    Args:
        t: Input value (0-1)

    Returns:
        Eased value (0-1)
    """
    if t < 0.5:
        return 4 * t * t * t
    else:
        return 1 - pow(-2 * t + 2, 3) / 2


def ease_out_quad(t: float) -> float:
    """Quadratic ease-out (deceleration)."""
    return 1 - (1 - t) * (1 - t)


def ease_in_quad(t: float) -> float:
    """Quadratic ease-in (acceleration)."""
    return t * t


def generate_multi_segment_path(
    waypoints: List[Tuple[float, float]],
    points_per_segment: int = 30,
    curvature: float = 0.2,
) -> List[Tuple[float, float]]:
    """
    Generate a smooth path through multiple waypoints.

    Args:
        waypoints: List of (x, y) waypoints to pass through
        points_per_segment: Number of points per segment
        curvature: Curvature of each segment

    Returns:
        Complete path as list of (x, y) tuples
    """
    if len(waypoints) < 2:
        return [waypoints[0]] if waypoints else []

    full_path = []

    for i in range(len(waypoints) - 1):
        segment = generate_smooth_path(
            waypoints[i],
            waypoints[i + 1],
            num_points=points_per_segment,
            curvature=curvature,
            randomness=0.05,
        )

        # Avoid duplicating the last point of previous segment
        if i > 0 and full_path:
            segment = segment[1:]

        full_path.extend(segment)

    return full_path


def interpolate_timestamps(
    path: List[Tuple[float, float]],
    total_duration: float,
) -> List[Tuple[float, float, float]]:
    """
    Add timestamps to each point in the path.

    Args:
        path: List of (x, y) points
        total_duration: Total duration in seconds

    Returns:
        List of (x, y, timestamp) tuples
    """
    if not path:
        return []

    num_points = len(path)
    timestamped_path = []

    for i, (x, y) in enumerate(path):
        t = (i / (num_points - 1)) * total_duration if num_points > 1 else 0
        timestamped_path.append((x, y, t))

    return timestamped_path
