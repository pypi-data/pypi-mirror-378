# gesture_blocks/core.py
import cv2
import mediapipe as mp
import serial
import time

# globals (used by simple block-style API)
_arduino = None
_cap = None

# mediapipe objects (simple, created at import)
_mp_hands = mp.solutions.hands
_hands = _mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7)
_mp_draw = mp.solutions.drawing_utils

def connect_arduino(port='COM5', baud=9600):
    """Connect to Arduino. Example: connect_arduino('COM3')"""
    global _arduino
    _arduino = serial.Serial(port, baud)
    time.sleep(2)
    print("✅ Arduino connected on", port)

def start_camera(index=0):
    """Start the default webcam. Returns the camera object."""
    global _cap
    _cap = cv2.VideoCapture(index)
    return _cap

def detect_fingers(cap=None):
    """
    Read one frame, detect fingers and show a simple window.
    Returns integer count of fingers (0..5).
    """
    global _cap, _hands, _mp_draw
    if cap is None:
        cap = _cap
    if cap is None:
        raise RuntimeError("Camera not started. Call start_camera() first.")

    success, img = cap.read()
    if not success:
        return 0

    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = _hands.process(img_rgb)
    fingers_up = 0

    if results.multi_hand_landmarks:
        for handLms in results.multi_hand_landmarks:
            _mp_draw.draw_landmarks(img, handLms, _mp_hands.HAND_CONNECTIONS)
            tip_ids = [4, 8, 12, 16, 20]
            landmarks = handLms.landmark
            fingers = []
            # Thumb (simple heuristic assuming right hand)
            fingers.append(1 if landmarks[tip_ids[0]].x < landmarks[tip_ids[0]-1].x else 0)
            # Other fingers
            for i in range(1,5):
                fingers.append(1 if landmarks[tip_ids[i]].y < landmarks[tip_ids[i]-2].y else 0)
            fingers_up = fingers.count(1)

    cv2.putText(img, f"Fingers: {fingers_up}", (60, 75), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255,255,255), 3)
    cv2.imshow("Gesture Control", img)
    return fingers_up

def turn_on(device):
    """Turn on LED1/LED2/LED3 by name: 'LED1', 'LED2', 'LED3'"""
    if _arduino is None:
        raise RuntimeError("Arduino not connected. Call connect_arduino() first.")
    if device == "LED1":
        _arduino.write(b'1'); print("💡 LED1 ON")
    elif device == "LED2":
        _arduino.write(b'2'); print("💡 LED2 ON")
    elif device == "LED3":
        _arduino.write(b'3'); print("💡 LED3 ON")
    else:
        raise ValueError("Unknown device: " + str(device))

def turn_off(device="ALL"):
    """Turn off LEDs. device ignored except for message."""
    if _arduino is None:
        raise RuntimeError("Arduino not connected. Call connect_arduino() first.")
    _arduino.write(b'0'); print("❌", device, "OFF")
