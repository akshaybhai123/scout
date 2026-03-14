"""
ScoutAI — Metrics Computation Engine
Computes speed, jump height, form score, agility, and consistency from
pose sequences and player trajectories.
"""

import numpy as np
from angle_utils import compute_angle_3pt


# ---------------------------------------------------------------------------
# Speed
# ---------------------------------------------------------------------------

def compute_speed(trajectory_points, fps=30, pixels_per_meter=50):
    """
    Estimate speed from a list of (x, y) center points.
    
    Returns:
        dict with avg_speed and max_speed in km/h.
    """
    if len(trajectory_points) < 2:
        return {"avg_speed": 0.0, "max_speed": 0.0}

    speeds = []
    for i in range(1, len(trajectory_points)):
        dx = trajectory_points[i][0] - trajectory_points[i - 1][0]
        dy = trajectory_points[i][1] - trajectory_points[i - 1][1]
        dist_px = np.sqrt(dx ** 2 + dy ** 2)
        dist_m = dist_px / pixels_per_meter
        speed_mps = dist_m * fps
        speeds.append(speed_mps * 3.6)  # m/s → km/h

    return {
        "avg_speed": float(np.mean(speeds)),
        "max_speed": float(max(speeds)),
    }


# ---------------------------------------------------------------------------
# Jump Height
# ---------------------------------------------------------------------------

def compute_jump_height(pose_sequence):
    """
    Estimate jump height from vertical displacement of the hip landmark.
    MediaPipe left hip = index 23.
    """
    if not pose_sequence:
        return 0.0

    hip_idx = 23
    hip_y = [frame[hip_idx][1] for frame in pose_sequence if len(frame) > hip_idx]
    if not hip_y:
        return 0.0

    baseline = np.percentile(hip_y, 10)  # standing reference
    peak = min(hip_y)  # highest point (lowest y in screen coords)
    jump_height_normalized = baseline - peak
    return float(jump_height_normalized * 100)


# ---------------------------------------------------------------------------
# Form Score
# ---------------------------------------------------------------------------

def compute_form_score(pose_sequence, sport="general"):
    """
    Rule-based form scoring using knee angle analysis.
    Ideal knee bend angle differs by sport; 90° is a baseline.
    """
    if not pose_sequence:
        return 50.0

    scores = []
    for frame in pose_sequence:
        if len(frame) < 28:
            continue
        # Landmarks: 23 (hip), 25 (knee), 27 (ankle)
        hip = frame[23][:2]
        knee = frame[25][:2]
        ankle = frame[27][:2]

        angle = compute_angle_3pt(hip, knee, ankle)
        score = min(100, max(0, 100 - abs(angle - 90)))
        scores.append(score)

    return float(np.mean(scores)) if scores else 50.0


# ---------------------------------------------------------------------------
# Agility
# ---------------------------------------------------------------------------

def compute_agility(trajectory_points):
    """
    Estimate agility from direction changes in the trajectory.
    More frequent direction changes = higher agility score.
    """
    if len(trajectory_points) < 3:
        return 50.0

    direction_changes = 0
    for i in range(2, len(trajectory_points)):
        dx1 = trajectory_points[i - 1][0] - trajectory_points[i - 2][0]
        dy1 = trajectory_points[i - 1][1] - trajectory_points[i - 2][1]
        dx2 = trajectory_points[i][0] - trajectory_points[i - 1][0]
        dy2 = trajectory_points[i][1] - trajectory_points[i - 1][1]

        cross = dx1 * dy2 - dy1 * dx2
        if abs(cross) > 5:  # threshold to filter noise
            direction_changes += 1

    # Normalize to 0-100 scale
    agility = min(100, (direction_changes / len(trajectory_points)) * 500)
    return float(agility)


# ---------------------------------------------------------------------------
# Consistency
# ---------------------------------------------------------------------------

def compute_consistency(pose_sequence):
    """
    Measure consistency of form across frames.
    Lower variance in form score = higher consistency.
    """
    if len(pose_sequence) < 5:
        return 50.0

    scores = []
    for frame in pose_sequence:
        if len(frame) < 28:
            continue
        hip = frame[23][:2]
        knee = frame[25][:2]
        ankle = frame[27][:2]
        angle = compute_angle_3pt(hip, knee, ankle)
        scores.append(angle)

    if not scores:
        return 50.0

    variance = np.var(scores)
    # Lower variance = better consistency, map to 0-100
    consistency = max(0, 100 - variance * 2)
    return float(min(100, consistency))


# ---------------------------------------------------------------------------
# Aggregator
# ---------------------------------------------------------------------------

def compute_all_metrics(pose_data, trajectories, fps=30):
    """
    Compute all athletic metrics from pose data and tracking trajectories.
    """
    # Get center-of-bbox trajectory for the most prominent person (track_id != -1)
    person_trajectories = {
        k: v for k, v in trajectories.items()
        if k != -1 and any(d["cls"] == 0 for d in v)
    }

    # Pick the longest trajectory
    center_points = []
    if person_trajectories:
        longest_id = max(person_trajectories, key=lambda k: len(person_trajectories[k]))
        for det in person_trajectories[longest_id]:
            if det["cls"] == 0:
                x1, y1, x2, y2 = det["bbox"]
                cx = (x1 + x2) / 2
                cy = (y1 + y2) / 2
                center_points.append((cx, cy))

    speed_metrics = compute_speed(center_points, fps=fps)
    jump_height = compute_jump_height(pose_data)
    form_score = compute_form_score(pose_data)
    agility = compute_agility(center_points)
    consistency = compute_consistency(pose_data)

    return {
        "avg_speed": round(speed_metrics["avg_speed"], 2),
        "max_speed": round(speed_metrics["max_speed"], 2),
        "jump_height": round(jump_height, 2),
        "form_score": round(form_score, 2),
        "agility": round(agility, 2),
        "consistency": round(consistency, 2),
    }
