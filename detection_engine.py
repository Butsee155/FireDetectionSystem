import cv2
import numpy as np
import os
from datetime import datetime
from db_config import get_connection

SNAPSHOT_DIR = "snapshots"
os.makedirs(SNAPSHOT_DIR, exist_ok=True)


def get_alert_settings():
    try:
        conn   = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT TOP 1 * FROM AlertSettings")
        row = cursor.fetchone()
        conn.close()
        if row:
            return {
                "email_enabled":  bool(row[1]),
                "email_from":     row[2] or "",
                "email_password": row[3] or "",
                "email_to":       row[4] or "",
                "sound_enabled":  bool(row[5]),
                "confidence":     float(row[6]) if row[6] else 0.45,
            }
    except Exception as e:
        print(f"[ERROR] Settings: {e}")
    return {"email_enabled": False, "sound_enabled": True, "confidence": 0.45}


def log_detection(detection_type, confidence, snapshot_path=""):
    try:
        conn   = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO DetectionLogs
            (DetectionType, Confidence, SnapshotPath, AlertSent)
            VALUES (?, ?, ?, 1)
        """, (detection_type, confidence, snapshot_path))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"[ERROR] Log: {e}")


def save_snapshot(frame, detection_type):
    ts       = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{SNAPSHOT_DIR}/{detection_type}_{ts}.jpg"
    cv2.imwrite(filename, frame)
    return filename


def detect_fire_by_color(frame):
    """
    Detects fire using HSV color analysis.
    Returns list of (x, y, w, h, confidence) for each fire region.
    """
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Orange-red fire range
    lower1 = np.array([0,  120, 120])
    upper1 = np.array([25, 255, 255])

    # Yellow-orange range
    lower2 = np.array([25, 100, 150])
    upper2 = np.array([40, 255, 255])

    mask1 = cv2.inRange(hsv, lower1, upper1)
    mask2 = cv2.inRange(hsv, lower2, upper2)
    mask  = cv2.bitwise_or(mask1, mask2)

    # Clean up noise
    kernel = np.ones((5, 5), np.uint8)
    mask   = cv2.morphologyEx(mask, cv2.MORPH_OPEN,  kernel)
    mask   = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

    contours, _ = cv2.findContours(
        mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    detections = []
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area > 1200:
            x, y, w, h = cv2.boundingRect(cnt)
            # Confidence based on area size
            conf = min(area / 8000.0, 0.99)
            detections.append((x, y, w, h, conf))

    return detections


def process_frame(frame, min_confidence=0.45):
    """
    Run fire+smoke detection on frame.
    Returns (annotated_frame, detections)
    detections = list of (type, confidence)
    """
    display    = frame.copy()
    detections = []

    # ── Color-based fire detection ────────────────────────────────────────────
    fire_regions = detect_fire_by_color(frame)
    for (x, y, w, h, conf) in fire_regions:
        if conf >= min_confidence:
            detections.append(("FIRE", conf))
            # Draw fire box
            cv2.rectangle(display, (x, y), (x+w, y+h), (0, 60, 255), 2)
            cv2.rectangle(display, (x, y-28), (x+w, y), (0, 60, 255), -1)
            cv2.putText(display, f"FIRE  {conf:.0%}",
                        (x+5, y-8), cv2.FONT_HERSHEY_SIMPLEX,
                        0.6, (255, 255, 255), 2)

    # ── Smoke detection via frame blur analysis ───────────────────────────────
    gray     = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blur     = cv2.GaussianBlur(gray, (21, 21), 0)
    diff     = cv2.absdiff(gray, blur)
    _, thresh = cv2.threshold(diff, 25, 255, cv2.THRESH_BINARY)
    smoke_px  = cv2.countNonZero(thresh)
    h_f, w_f  = frame.shape[:2]
    smoke_ratio = smoke_px / (h_f * w_f)

    if smoke_ratio > 0.18:
        smoke_conf = min(smoke_ratio * 3.5, 0.95)
        if smoke_conf >= min_confidence:
            detections.append(("SMOKE", smoke_conf))
            cv2.rectangle(display, (5, 5), (w_f-5, h_f-5), (120, 120, 120), 2)
            cv2.putText(display, f"SMOKE  {smoke_conf:.0%}",
                        (15, 35), cv2.FONT_HERSHEY_SIMPLEX,
                        0.7, (200, 200, 200), 2)

    return display, detections