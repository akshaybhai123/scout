"""
ScoutAI — Real-Time Fitness Tracker (Webcam Bicep Curl Counter)
Uses MediaPipe Pose to count exercise reps via webcam.

Run standalone:  python pipeline/fitness_tracker.py
"""

import cv2
import mediapipe as mp
import numpy as np

mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose


def calculate_angle(a, b, c):
    """Calculate the angle at point b formed by a-b-c."""
    a = np.array(a)
    b = np.array(b)
    c = np.array(c)

    radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
    angle = np.abs(radians * 180.0 / np.pi)

    if angle > 180:
        angle = 360 - angle

    return angle


def run_fitness_tracker(camera_index=0):
    """
    Open the webcam and start counting bicep curls in real time.
    Press 'q' to quit.
    """
    cap = cv2.VideoCapture(camera_index)
    count = 0
    stage = None

    with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = pose.process(image)
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

            try:
                landmarks = results.pose_landmarks.landmark

                shoulder = [
                    landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,
                    landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y,
                ]
                elbow = [
                    landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].x,
                    landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].y,
                ]
                wrist = [
                    landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].x,
                    landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].y,
                ]

                angle = calculate_angle(shoulder, elbow, wrist)

                # State machine for rep counting
                if angle > 160:
                    stage = "down"
                if angle < 40 and stage == "down":
                    stage = "up"
                    count += 1

            except Exception:
                pass

            # --- HUD overlay ---
            # Semi-transparent background bar
            overlay = image.copy()
            cv2.rectangle(overlay, (0, 0), (300, 80), (40, 40, 40), -1)
            cv2.addWeighted(overlay, 0.7, image, 0.3, 0, image)

            cv2.putText(image, "REPS", (15, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 200, 255), 1)
            cv2.putText(image, str(count), (15, 65), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 128), 3)

            cv2.putText(image, "STAGE", (150, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 200, 255), 1)
            cv2.putText(image, stage or "-", (150, 65), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 128), 3)

            # Draw skeleton
            mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)

            cv2.imshow("ScoutAI Fitness Tracker", image)

            if cv2.waitKey(10) & 0xFF == ord("q"):
                break

    cap.release()
    cv2.destroyAllWindows()
    return count


if __name__ == "__main__":
    print("=== ScoutAI Fitness Tracker ===")
    print("Perform bicep curls in front of your webcam.")
    print("Press 'q' to quit.\n")
    total = run_fitness_tracker()
    print(f"\nSession complete! Total reps: {total}")
