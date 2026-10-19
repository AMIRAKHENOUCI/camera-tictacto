import math
import time

import cv2
import mediapipe as mp


class HandController:
    """
    Lit la camera, detecte la main et donne :
      - cursor           : (x, y) en pixels de la fenetre pygame (ou None)
      - pinching         : True tant que pouce + index sont colles
      - clicked          : True UNIQUEMENT a la frame ou le pinch commence
      - gesture          : "open" (main ouverte), "fist" (poing) ou None
      - gesture_progress : 0.0 -> 1.0 pendant qu'on maintient le geste
      - gesture_event    : "open" / "fist" a la frame ou le geste est valide
    """

    PINCH_ON = 0.30     # ratio en dessous duquel on considere "pinch"
    PINCH_OFF = 0.45    # ratio au dessus duquel on relache (hysteresis)
    MARGIN = 0.15       # zone morte sur les bords de la camera
    SMOOTH = 0.35       # 0 = tres lent, 1 = pas de lissage
    HOLD_TIME = 1.5     # secondes a maintenir main ouverte / poing
    EXTENDED = 1.4      # doigt tendu si distance(poignet, bout) > 1.4 x distance(poignet, base)

    def __init__(self, cam_index=0, show_preview=True):
        self.cap = cv2.VideoCapture(cam_index)
        self.available = self.cap.isOpened()

        if self.available:
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

        self.mp_hands = mp.solutions.hands
        self.mp_draw = mp.solutions.drawing_utils
        self.hands = self.mp_hands.Hands(
            max_num_hands=1,
            min_detection_confidence=0.6,
            min_tracking_confidence=0.6,
        )

        self.show_preview = show_preview

        self.cursor = None
        self.pinching = False
        self.clicked = False

        self.gesture = None
        self.gesture_progress = 0.0
        self.gesture_event = None
        self._gesture_start = 0.0
        self._gesture_fired = False

    @staticmethod
    def _dist(a, b):
        return math.hypot(a.x - b.x, a.y - b.y)

    def _finger_states(self, lm):
        """Retourne [index, majeur, annulaire, auriculaire] -> True si tendu."""
        wrist = lm[0]
        pairs = ((8, 5), (12, 9), (16, 13), (20, 17))
        states = []

        for tip, base in pairs:
            d_tip = self._dist(wrist, lm[tip])
            d_base = self._dist(wrist, lm[base])
            states.append(d_tip / max(d_base, 1e-6) > self.EXTENDED)

        return states

    @staticmethod
    def _detect_gesture(states, ratio):
        if all(states) and ratio > 0.6:
            return "open"
        if not any(states):
            return "fist"
        return None

    def _update_gesture(self, gesture, now):
        self.gesture_event = None

        if gesture != self.gesture:
            self.gesture = gesture
            self._gesture_start = now
            self._gesture_fired = False
            self.gesture_progress = 0.0
            return

        if gesture is None:
            return

        self.gesture_progress = min((now - self._gesture_start) / self.HOLD_TIME, 1.0)

        # Se declenche une seule fois, il faut relacher le geste pour recommencer
        if self.gesture_progress >= 1.0 and not self._gesture_fired:
            self._gesture_fired = True
            self.gesture_event = gesture

    def update(self, width, height):
        """A appeler une fois par frame dans la boucle pygame."""
        self.clicked = False
        self.gesture_event = None

        if not self.available:
            return

        ok, frame = self.cap.read()
        if not ok:
            return

        frame = cv2.flip(frame, 1)
        results = self.hands.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        now = time.time()

        if results.multi_hand_landmarks:
            hand = results.multi_hand_landmarks[0]
            lm = hand.landmark

            thumb, index = lm[4], lm[8]

            # Distance pouce-index relative a la taille de la main
            hand_size = self._dist(lm[0], lm[9])
            ratio = self._dist(thumb, index) / max(hand_size, 1e-6)

            # Geste (main ouverte / poing)
            states = self._finger_states(lm)
            gesture = self._detect_gesture(states, ratio)
            self._update_gesture(gesture, now)

            # Curseur = milieu entre pouce et index (stable pendant le pinch)
            mx = (thumb.x + index.x) / 2
            my = (thumb.y + index.y) / 2

            span = 1 - 2 * self.MARGIN
            nx = min(max((mx - self.MARGIN) / span, 0), 1)
            ny = min(max((my - self.MARGIN) / span, 0), 1)
            target = (nx * width, ny * height)

            if self.cursor is None:
                self.cursor = target
            else:
                self.cursor = (
                    self.cursor[0] + (target[0] - self.cursor[0]) * self.SMOOTH,
                    self.cursor[1] + (target[1] - self.cursor[1]) * self.SMOOTH,
                )

            # Pinch (desactive quand on fait un poing, pour eviter un faux click)
            was_pinching = self.pinching

            if not self.pinching and ratio < self.PINCH_ON:
                self.pinching = True
            elif self.pinching and ratio > self.PINCH_OFF:
                self.pinching = False

            if self.pinching and not was_pinching:
                self.clicked = True

            if self.show_preview:
                self.mp_draw.draw_landmarks(
                    frame, hand, self.mp_hands.HAND_CONNECTIONS
                )

                if self.pinching:
                    label, color = "PINCH", (0, 255, 0)
                elif gesture == "open":
                    label, color = "OPEN HAND", (255, 200, 0)
                elif gesture == "fist":
                    label, color = "FIST", (0, 100, 255)
                else:
                    label, color = f"ratio {ratio:.2f}", (0, 255, 255)

                cv2.putText(frame, label, (15, 40),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
        else:
            self.cursor = None
            self.pinching = False
            self._update_gesture(None, now)

        if self.show_preview:
            cv2.imshow("ITC - Camera", cv2.resize(frame, (320, 240)))
            cv2.waitKey(1)

    def close(self):
        self.hands.close()
        if self.available:
            self.cap.release()
        cv2.destroyAllWindows()