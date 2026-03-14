"""
ScoutAI — Shared angle calculation utility
"""

import numpy as np


def calculate_angle(a, b, c):
    """
    Calculate the angle at point b formed by points a-b-c.
    Uses arctan2 for robust angle computation.
    
    Args:
        a, b, c: Each is a list/tuple [x, y] or [x, y, z].
    
    Returns:
        Angle in degrees (0–180).
    """
    a = np.array(a[:2], dtype=np.float64)
    b = np.array(b[:2], dtype=np.float64)
    c = np.array(c[:2], dtype=np.float64)

    radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
    angle = np.abs(radians * 180.0 / np.pi)

    if angle > 180:
        angle = 360 - angle

    return angle


def compute_angle_3pt(a, b, c):
    """
    Alternative angle calculation using dot product (0–180°).
    Used in metrics_engine for form scoring.
    """
    ba = np.array(a[:2]) - np.array(b[:2])
    bc = np.array(c[:2]) - np.array(b[:2])
    cosine = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc) + 1e-6)
    return float(np.degrees(np.arccos(np.clip(cosine, -1.0, 1.0))))
