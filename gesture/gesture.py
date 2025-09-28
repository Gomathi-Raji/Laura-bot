import cv2
import mediapipe as mp





def start_gesture():
    # Setup MediaPipe
    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(max_num_hands=2, min_detection_confidence=0.75)
    mp_draw = mp.solutions.drawing_utils

    # Finger detection function
    def get_finger_status(hand_landmarks, hand_label):
        status = []
        # Thumb (x-axis for horizontal detection)
        if hand_label == 'Right':
            status.append(1 if hand_landmarks.landmark[4].x < hand_landmarks.landmark[3].x else 0)
        else:
            status.append(1 if hand_landmarks.landmark[4].x > hand_landmarks.landmark[3].x else 0)
        # Index, Middle, Ring, Pinky (y-axis)
        for tip in [8, 12, 16, 20]:
            status.append(1 if hand_landmarks.landmark[tip].y < hand_landmarks.landmark[tip - 2].y else 0)
        return ''.join(map(str, status))

    # Gesture mapping
    gesture_map = {
        ("01000", "01000"): print('hi'),
        ("01000", "00100"): "Ambulance",
        ("01100", "01100"): "Fire",
        ("00001", "00001"): "Sick",
        ("10000", "10000"): "Water",
        ("01000", "00000"): "up",
        ("00000", "01000"): "Down",
        ("00001", "01000"): "Danger",
        ("00100", "00100"): "Stop",
        ("00010", "00010"): "Wait"
    }
    print(gesture_map)
    # Webcam
    cap = cv2.VideoCapture("http://10.170.105.110:81/stream")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = hands.process(rgb)

        finger_states = {}
        if result.multi_hand_landmarks and result.multi_handedness:
            for i, hand_landmarks in enumerate(result.multi_hand_landmarks):
                hand_label = result.multi_handedness[i].classification[0].label
                mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                finger_states[hand_label] = get_finger_status(hand_landmarks, hand_label)

            left = finger_states.get("Left", "")
            right = finger_states.get("Right", "")
            gesture = gesture_map.get((left, right), "Unknown")

            cv2.putText(frame, f"Gesture: {gesture}", (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 255), 3)

        cv2.imshow("Two-Hand Gesture Recognition", frame)
        if cv2.waitKey(1) & 0xFF == 27:
            break

    cap.release()
    cv2.destroyAllWindows()

# Run the function
start_gesture()
