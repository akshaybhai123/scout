"""
ScoutAI — Video utility functions
"""

import cv2


def get_video_info(video_path):
    """
    Get basic metadata from a video file.
    
    Returns:
        dict with fps, width, height, frame_count, duration_seconds.
    """
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        return None

    fps = cap.get(cv2.CAP_PROP_FPS) or 30
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = frame_count / fps if fps > 0 else 0

    cap.release()
    return {
        "fps": fps,
        "width": width,
        "height": height,
        "frame_count": frame_count,
        "duration_seconds": round(duration, 2),
    }


def extract_frames(video_path, interval=1):
    """
    Yield frames from a video at a given interval (in seconds).
    
    Args:
        video_path: Path to the video.
        interval: Seconds between extracted frames.
    
    Yields:
        (frame_index, BGR numpy array)
    """
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        return

    fps = cap.get(cv2.CAP_PROP_FPS) or 30
    frame_skip = int(fps * interval)
    idx = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        if idx % frame_skip == 0:
            yield idx, frame
        idx += 1

    cap.release()


def resize_frame(frame, max_dim=640):
    """
    Resize a frame maintaining aspect ratio so the longest side is max_dim.
    """
    h, w = frame.shape[:2]
    if max(h, w) <= max_dim:
        return frame

    scale = max_dim / max(h, w)
    new_w = int(w * scale)
    new_h = int(h * scale)
    return cv2.resize(frame, (new_w, new_h), interpolation=cv2.INTER_AREA)
