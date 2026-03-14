"""
ScoutAI — OCR Processing (Jersey Numbers & Scoreboards)
"""

import cv2


def extract_jersey_number(frame, bbox):
    """
    Extract jersey number from a bounding box region of a frame.
    
    Args:
        frame: BGR numpy array (full frame).
        bbox: [x1, y1, x2, y2] bounding box coordinates.
    
    Returns:
        Detected number as string, or empty string if none found.
    """
    try:
        import pytesseract
    except ImportError:
        return ""

    x1, y1, x2, y2 = map(int, bbox)
    # Ensure coords are within frame bounds
    h, w = frame.shape[:2]
    x1, y1 = max(0, x1), max(0, y1)
    x2, y2 = min(w, x2), min(h, y2)

    if x2 <= x1 or y2 <= y1:
        return ""

    # Crop the upper portion of the bounding box (jersey area)
    box_h = y2 - y1
    jersey_y2 = y1 + int(box_h * 0.5)  # upper half
    roi = frame[y1:jersey_y2, x1:x2]

    if roi.size == 0:
        return ""

    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY_INV)

    config = "--psm 7 --oem 3 -c tessedit_char_whitelist=0123456789"
    try:
        number = pytesseract.image_to_string(thresh, config=config)
        return number.strip()
    except Exception:
        return ""


def extract_scoreboard(frame):
    """
    Extract text from the scoreboard area (bottom 15% of frame).
    
    Args:
        frame: BGR numpy array.
    
    Returns:
        Detected text as string.
    """
    try:
        import pytesseract
    except ImportError:
        return ""

    h, w = frame.shape[:2]
    scoreboard_roi = frame[int(h * 0.85):, :]

    if scoreboard_roi.size == 0:
        return ""

    try:
        text = pytesseract.image_to_string(scoreboard_roi)
        return text.strip()
    except Exception:
        return ""
