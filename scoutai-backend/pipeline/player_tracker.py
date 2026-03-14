"""
ScoutAI — YOLOv8 Player & Ball Tracking
"""

import os


def track_players_and_ball(video_path):
    """
    Run YOLOv8 tracking on a video to detect persons (class 0) and
    sports balls (class 32).
    
    Returns:
        dict of track_id -> list of detections:
        {
            track_id: [
                {"frame_idx": int, "bbox": [x1,y1,x2,y2], "cls": int, "conf": float},
                ...
            ]
        }
    """
    try:
        from ultralytics import YOLO
    except ImportError:
        print("[WARNING] ultralytics not installed, returning empty trajectories")
        return {}

    # Use nano model for speed; auto-downloads on first run (~6 MB)
    model_path = "yolov8n.pt"
    model = YOLO(model_path)

    results = model.track(
        video_path,
        persist=True,
        classes=[0, 32],   # person, sports ball
        verbose=False,
    )

    trajectories = {}
    for frame_idx, r in enumerate(results):
        if r.boxes is None:
            continue
        for box in r.boxes:
            track_id = int(box.id[0]) if box.id is not None else -1
            conf = float(box.conf[0]) if box.conf is not None else 0.0
            cls = int(box.cls[0]) if box.cls is not None else -1
            bbox = box.xyxy[0].tolist() if box.xyxy is not None else [0, 0, 0, 0]

            trajectories.setdefault(track_id, []).append({
                "frame_idx": frame_idx,
                "bbox": bbox,
                "cls": cls,
                "conf": conf,
            })

    return trajectories
