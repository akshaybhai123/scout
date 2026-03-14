"""
ScoutAI — Drawing utilities for annotated video frames
"""

import cv2
import numpy as np

# MediaPipe Pose connections (pairs of landmark indices)
POSE_CONNECTIONS = [
    (0, 1), (1, 2), (2, 3), (3, 7), (0, 4), (4, 5), (5, 6), (6, 8),
    (9, 10), (11, 12), (11, 13), (13, 15), (12, 14), (14, 16),
    (11, 23), (12, 24), (23, 24), (23, 25), (24, 26), (25, 27),
    (26, 28), (27, 29), (28, 30), (29, 31), (30, 32),
    (15, 17), (15, 19), (15, 21), (16, 18), (16, 20), (16, 22),
]


def draw_skeleton(frame, landmarks, color=(0, 255, 128), thickness=2, radius=4):
    """
    Draw a pose skeleton overlay on a frame.
    
    Args:
        frame: BGR numpy array.
        landmarks: List of 33 (x, y, z, visibility) tuples (normalized 0–1).
        color: BGR color for skeleton lines.
        thickness: Line thickness.
        radius: Landmark point radius.
    
    Returns:
        Frame with skeleton drawn on it.
    """
    h, w = frame.shape[:2]
    points = []

    for lm in landmarks:
        px = int(lm[0] * w)
        py = int(lm[1] * h)
        points.append((px, py))
        visibility = lm[3] if len(lm) > 3 else 1.0
        if visibility > 0.5:
            cv2.circle(frame, (px, py), radius, color, -1)

    for start, end in POSE_CONNECTIONS:
        if start < len(points) and end < len(points):
            vis_s = landmarks[start][3] if len(landmarks[start]) > 3 else 1.0
            vis_e = landmarks[end][3] if len(landmarks[end]) > 3 else 1.0
            if vis_s > 0.5 and vis_e > 0.5:
                cv2.line(frame, points[start], points[end], color, thickness)

    return frame


def draw_bboxes(frame, boxes, labels=None, color=(255, 100, 0), thickness=2):
    """
    Draw bounding boxes on a frame.
    
    Args:
        frame: BGR numpy array.
        boxes: List of [x1, y1, x2, y2] bounding boxes.
        labels: Optional list of label strings.
        color: BGR color for boxes.
        thickness: Line thickness.
    
    Returns:
        Frame with boxes drawn.
    """
    for i, bbox in enumerate(boxes):
        x1, y1, x2, y2 = map(int, bbox)
        cv2.rectangle(frame, (x1, y1), (x2, y2), color, thickness)
        if labels and i < len(labels):
            cv2.putText(
                frame, labels[i], (x1, y1 - 8),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2,
            )

    return frame


def generate_annotated_clip(video_path, pose_data, trajectories, output_path=None):
    """
    Generate an annotated video with skeleton overlays and bounding boxes.
    
    Args:
        video_path: Path to original video.
        pose_data: List of frame pose landmarks.
        trajectories: Dict from player_tracker (track_id -> detection list).
        output_path: Where to save the annotated video. Defaults to *_annotated.mp4.
    
    Returns:
        Path to the annotated video file.
    """
    import os

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        return None

    fps = cap.get(cv2.CAP_PROP_FPS) or 30
    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    if output_path is None:
        base, ext = os.path.splitext(video_path)
        output_path = f"{base}_annotated.mp4"

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(output_path, fourcc, fps, (w, h))

    # Build frame-indexed bbox lookup
    frame_bboxes = {}
    for track_id, detections in trajectories.items():
        for det in detections:
            fidx = det["frame_idx"]
            frame_bboxes.setdefault(fidx, []).append({
                "bbox": det["bbox"],
                "label": f"ID:{track_id}",
            })

    frame_idx = 0
    pose_idx = 0

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # Draw skeleton if pose data available for this frame
        if pose_idx < len(pose_data):
            frame = draw_skeleton(frame, pose_data[pose_idx])
            pose_idx += 1

        # Draw bounding boxes
        if frame_idx in frame_bboxes:
            boxes = [d["bbox"] for d in frame_bboxes[frame_idx]]
            labels = [d["label"] for d in frame_bboxes[frame_idx]]
            frame = draw_bboxes(frame, boxes, labels)

        out.write(frame)
        frame_idx += 1

    cap.release()
    out.release()
    return output_path
