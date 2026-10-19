
import cv2
import mediapipe as mp
import math

mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils

camera = cv2.VideoCapture(0)

with mp_hands.Hands(
    max_num_hands=1,
    min_detection_confidence=0.6,
    min_tracking_confidence=0.6
) as hands:

    while camera.isOpened():
        success, frame = camera.read()

        if not success:
            print("Ma9drnach n9raw camera")
            break

        frame = cv2.flip(frame, 1)

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(rgb_frame)

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:

                mp_draw.draw_landmarks(
                    frame,
                    hand_landmarks,
                    mp_hands.HAND_CONNECTIONS
                )

                # رأس السبابة
                index_tip = hand_landmarks.landmark[8]

                # رأس الإبهام
                thumb_tip = hand_landmarks.landmark[4]

                # المسافة بين رأسي الإصبعين
                distance = math.sqrt(
                    (index_tip.x - thumb_tip.x) ** 2
                    + (index_tip.y - thumb_tip.y) ** 2
                )

                if distance < 0.05:
                    cv2.putText(
                        frame,
                        "PINCH DETECTED!",
                        (20, 80),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        1,
                        (0, 255, 0),
                        2
                    )
                else:
                    cv2.putText(
                        frame,
                        "Move fingers together",
                        (20, 80),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.7,
                        (0, 255, 255),
                        2
                    )

        cv2.imshow("ITC - Pinch Detection", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

camera.release()
cv2.destroyAllWindows()
