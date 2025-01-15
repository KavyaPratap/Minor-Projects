import cv2
import numpy as np
import mediapipe as mp
import screeninfo

# Get the screen resolution
screen = screeninfo.get_monitors()[0]
screen_width, screen_height = screen.width, screen.height

# Initialize Mediapipe Hand model with higher detection confidence
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.85)
mp_draw = mp.solutions.drawing_utils

# Set up full-screen drawing canvas
canvas = np.ones((screen_height, screen_width, 3), dtype=np.uint8) * 255  # White canvas
color = (0, 0, 0)  # Default color black
thickness = 5
prev_x, prev_y = None, None  # Previous points for smooth lines

# Colors at the top
colors = [(0, 0, 0), (0, 255, 0), (0, 0, 255), (255, 0, 0), (255, 255, 0)]
color_boxes = [(i * 100 + 50, 50) for i in range(len(colors))]

# Initialize camera
cap = cv2.VideoCapture(0)

# Low-pass filter parameters for smoothing
alpha = 0.2  # Smoothing factor (between 0 and 1)
smoothed_x, smoothed_y = None, None

while cap.isOpened():
    ret, frame = cap.read()
    frame = cv2.flip(frame, 1)
    frame = cv2.resize(frame, (screen_width, screen_height))  # Resize to full screen
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(frame_rgb)

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            index_finger_tip = hand_landmarks.landmark[8]
            middle_finger_tip = hand_landmarks.landmark[12]
            ring_finger_tip = hand_landmarks.landmark[16]
            h, w, _ = frame.shape
            index_x, index_y = int(index_finger_tip.x * w), int(index_finger_tip.y * h)
            middle_x, middle_y = int(middle_finger_tip.x * w), int(middle_finger_tip.y * h)
            ring_x, ring_y = int(ring_finger_tip.x * w), int(ring_finger_tip.y * h)
            if smoothed_x is None and smoothed_y is None:
                smoothed_x, smoothed_y = index_x, index_y
            else:
                smoothed_x = int(alpha * index_x + (1 - alpha) * smoothed_x)
                smoothed_y = int(alpha * index_y + (1 - alpha) * smoothed_y)

            # Count number of fingers up
            fingers_up = [
                hand_landmarks.landmark[8].y < hand_landmarks.landmark[7].y,  # Index finger
                hand_landmarks.landmark[12].y < hand_landmarks.landmark[11].y,  # Middle finger
                hand_landmarks.landmark[16].y < hand_landmarks.landmark[15].y   # Ring finger
            ]

            if sum(fingers_up) == 3:  # 3 fingers for color selection
                for i, (cx, cy) in enumerate(color_boxes):
                    if abs(cx - smoothed_x) < 50 and abs(cy - smoothed_y) < 50:
                        color = colors[i]
                        prev_x, prev_y = None, None  # Reset previous points to avoid unwanted lines

            elif sum(fingers_up) == 2:  # 2 fingers for navigating
                prev_x, prev_y = None, None  

            elif sum(fingers_up) == 1:  # 1 finger for drawing
                if prev_x is None and prev_y is None:
                    prev_x, prev_y = smoothed_x, smoothed_y
                cv2.line(canvas, (prev_x, prev_y), (smoothed_x, smoothed_y), color, thickness)
                prev_x, prev_y = smoothed_x, smoothed_y
            
            # Clear the canvas if only the middle finger is up
            if fingers_up[1] and not fingers_up[0] and not fingers_up[2]:
                canvas = np.ones((screen_height, screen_width, 3), dtype=np.uint8) * 255  # Clear canvas to white
    for i, (cx, cy) in enumerate(color_boxes):
        cv2.rectangle(frame, (cx - 50, cy - 50), (cx + 50, cy + 50), colors[i], -1)
    frame = cv2.addWeighted(frame, 0.5, canvas, 0.5, 0)

    cv2.imshow("Air Canvas", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
