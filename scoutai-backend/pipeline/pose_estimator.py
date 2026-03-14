import cv2
import os

def extract_pose_sequence(video_path, max_frames=500):
    """
    Extract keypoints from video frames using YOLOv8-pose as a robust alternative to MediaPipe.
    Maps COCO keypoints to a MediaPipe-compatible indexing for the metrics engine.
    """
    try:
        from ultralytics import YOLO
    except ImportError:
        print("[ERROR] ultralytics not installed")
        return []

    # Use YOLOv8-pose nano
    model = YOLO("yolov8n-pose.pt")
    
    # Run inference on the video
    # stream=True processes one frame at a time to save memory
    results = model.predict(
        source=video_path,
        stream=True,
        conf=0.3,
        verbose=False
    )

    frames_data = []
    frame_count = 0

    for r in results:
        if frame_count >= max_frames:
            break
        
        # If multiple persons, we take the one with highest confidence (first in list usually)
        if r.keypoints is not None and len(r.keypoints.data) > 0:
            # keypoints shape: [N_persons, 17, 3] (x, y, conf)
            # COCO indices: 11 (L-hip), 13 (L-knee), 15 (L-ankle)
            kpts = r.keypoints.data[0].tolist()
            
            # Map COCO to Mediapipe placeholders (33 points)
            # Metrics engine needs 23, 25, 27
            mp_compatible = [[0.0, 0.0, 0.0, 0.0]] * 33
            
            # Mediapipe: 23 (hip), 25 (knee), 27 (ankle)
            # COCO: 11 (L-hip), 13 (L-knee), 15 (L-ankle)
            # We use left side as default reference as per previous logic
            if len(kpts) > 15:
                # Left Hip
                mp_compatible[23] = [kpts[11][0] / r.orig_shape[1], kpts[11][1] / r.orig_shape[0], 0.0, kpts[11][2]]
                # Left Knee
                mp_compatible[25] = [kpts[13][0] / r.orig_shape[1], kpts[13][1] / r.orig_shape[0], 0.0, kpts[13][2]]
                # Left Ankle
                mp_compatible[27] = [kpts[15][0] / r.orig_shape[1], kpts[15][1] / r.orig_shape[0], 0.0, kpts[15][2]]
            
            frames_data.append(mp_compatible)
        
        frame_count += 1

    return frames_data
