import cv2
import mediapipe as mp
import numpy as np

def main_function(input_data):

    return "Processed result for: " + str(input_data)

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
hands = mp_hands.Hands(static_image_mode=False, max_num_hands=1, min_detection_confidence=0.5)

canvas = None
drawing_color = (255, 255, 255)
eraser_thickness = 50

def count_fingers(hand_landmarks):
    tips = [mp_hands.HandLandmark.INDEX_FINGER_TIP, mp_hands.HandLandmark.MIDDLE_FINGER_TIP]
    dips = [mp_hands.HandLandmark.INDEX_FINGER_DIP, mp_hands.HandLandmark.MIDDLE_FINGER_DIP]
    open_fingers = []
    for tip, dip in zip(tips, dips):
        if hand_landmarks.landmark[tip].y < hand_landmarks.landmark[dip].y:
            open_fingers.append(tip)
    return open_fingers

cap = cv2.VideoCapture(0)

previous_position = None
mode = "surf"
is_drawing = False

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    height, width, _ = frame.shape

    if canvas is None:
        canvas = np.zeros((height, width, 3), dtype=np.uint8)

    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    results = hands.process(rgb_frame)

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            index_finger_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
            index_x, index_y = int(index_finger_tip.x * width), int(index_finger_tip.y * height)

            open_fingers = count_fingers(hand_landmarks)

            if len(open_fingers) == 1:
                mode = "draw"
                is_drawing = True
                if previous_position is not None:
                    cv2.line(canvas, previous_position, (index_x, index_y), drawing_color, 5)
                previous_position = (index_x, index_y)

            elif len(open_fingers) == 2:
                mode = "erase"
                is_drawing = False
                previous_position = None
                cv2.circle(canvas, (index_x, index_y), eraser_thickness, (0, 0, 0), -1)

            else:
                mode = "surf"
                is_drawing = False
                previous_position = None

    else:
        mode = "surf"
        is_drawing = False
        previous_position = None

    combined = cv2.addWeighted(frame, 0.5, canvas, 0.5, 0)

    cv2.putText(combined, f"Mode: {mode}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    cv2.imshow("Virtual Whiteboard", combined)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
