import cv2
import mediapipe as mp
import vlc
import time
import numpy as np

# --- Media Player Setup ---
media_files = [
    "song1.mp3",
    "song2.mp3",
    "song3.mp3"
]  # Replace with your media file paths

class MediaPlayer:
    def __init__(self, files):
        self.files = files
        self.index = 0
        self.player = vlc.MediaPlayer(self.files[self.index])
        self.is_playing = False
        self.muted = False

    def play(self):
        if not self.is_playing:
            self.player.play()
            self.is_playing = True
            print("Playing:", self.files[self.index])

    def pause(self):
        if self.is_playing:
            self.player.pause()
            self.is_playing = False
            print("Paused")

    def play_pause(self):
        if self.is_playing:
            self.pause()
        else:
            self.play()

    def stop(self):
        self.player.stop()
        self.is_playing = False
        print("Stopped")

    def next_track(self):
        self.stop()
        self.index = (self.index + 1) % len(self.files)
        self.player = vlc.MediaPlayer(self.files[self.index])
        self.play()
        print("Next track:", self.files[self.index])

    def prev_track(self):
        self.stop()
        self.index = (self.index - 1) % len(self.files)
        self.player = vlc.MediaPlayer(self.files[self.index])
        self.play()
        print("Previous track:", self.files[self.index])

    def volume_up(self):
        vol = self.player.audio_get_volume()
        vol = min(vol + 10, 100)
        self.player.audio_set_volume(vol)
        print("Volume up:", vol)

    def volume_down(self):
        vol = self.player.audio_get_volume()
        vol = max(vol - 10, 0)
        self.player.audio_set_volume(vol)
        print("Volume down:", vol)

    def mute_unmute(self):
        if self.muted:
            self.player.audio_set_mute(False)
            self.muted = False
            print("Unmuted")
        else:
            self.player.audio_set_mute(True)
            self.muted = True
            print("Muted")

    def get_status(self):
        status = "Playing" if self.is_playing else "Paused"
        vol = self.player.audio_get_volume()
        track = self.files[self.index].split("/")[-1]
        return f"{track} | {status} | Volume: {vol} | Muted: {self.muted}"

# --- Hand Gesture Recognition ---

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
hands_detector = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.6)

# Finger tip IDs in Mediapipe
FINGER_TIPS = [4, 8, 12, 16, 20]

def fingers_up(hand_landmarks):
    """
    Returns list of 0/1 for fingers (thumb to pinky) indicating if finger is up (1) or down (0).
    Thumb comparison depends on handedness.
    """
    fingers = []

    # Thumb: Check if tip is to the left or right of the IP joint
    # Mediapipe landmarks: thumb_tip=4, thumb_ip=3
    # For right hand, tip.x < ip.x means thumb is open
    if hand_landmarks.landmark[FINGER_TIPS[0]].x < hand_landmarks.landmark[FINGER_TIPS[0] - 1].x:
        fingers.append(1)
    else:
        fingers.append(0)

    # Other fingers: tip.y < pip.y means finger is up
    for i in range(1, 5):
        if hand_landmarks.landmark[FINGER_TIPS[i]].y < hand_landmarks.landmark[FINGER_TIPS[i] - 2].y:
            fingers.append(1)
        else:
            fingers.append(0)
    return fingers

# Detect swipe using movement vector and speed
class SwipeDetector:
    def __init__(self, threshold=0.15, time_window=0.5):
        self.threshold = threshold
        self.time_window = time_window
        self.positions = []
        self.times = []

    def update(self, x_pos):
        current_time = time.time()
        self.positions.append(x_pos)
        self.times.append(current_time)

        # Remove old points beyond time window
        while self.times and (current_time - self.times[0]) > self.time_window:
            self.times.pop(0)
            self.positions.pop(0)

        if len(self.positions) < 2:
            return None

        delta_x = self.positions[-1] - self.positions[0]
        delta_t = self.times[-1] - self.times[0]

        if delta_t == 0:
            return None

        speed = delta_x / delta_t
        if speed > self.threshold:
            return "right"
        elif speed < -self.threshold:
            return "left"
        else:
            return None

# --- Main Application ---

def main():
    cap = cv2.VideoCapture(0)
    mp_hands = mp.solutions.hands

    player = MediaPlayer(media_files)
    swipe_detector = SwipeDetector()

    gesture_cooldown = 1.2  # seconds between recognized gestures
    last_gesture_time = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to capture frame")
            break

        frame = cv2.flip(frame, 1)  # mirror image
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        results = hands_detector.process(rgb_frame)

        h, w, _ = frame.shape
        gesture_text = ""
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

                # Get fingers status
                fingers = fingers_up(hand_landmarks)
                # Calculate hand center x coordinate (average x of all landmarks)
                hand_center_x = np.mean([lm.x for lm in hand_landmarks.landmark])

                current_time = time.time()
                time_since_last = current_time - last_gesture_time

                # Check cooldown to avoid rapid multiple triggers
                if time_since_last > gesture_cooldown:
                    # Gesture recognition rules:

                    # All fingers up = play/pause toggle
                    if fingers == [1, 1, 1, 1, 1]:
                        player.play_pause()
                        gesture_text = "Play/Pause"
                        last_gesture_time = current_time

                    # Thumb only up = volume up
                    elif fingers == [1, 0, 0, 0, 0]:
                        player.volume_up()
                        gesture_text = "Volume Up"
                        last_gesture_time = current_time

                    # Thumb down (all fingers down) = volume down
                    elif fingers == [0, 0, 0, 0, 0]:
                        player.volume_down()
                        gesture_text = "Volume Down"
                        last_gesture_time = current_time

                    # Index finger only up = mute/unmute toggle
                    elif fingers == [0, 1, 0, 0, 0]:
                        player.mute_unmute()
                        gesture_text = "Mute/Unmute"
                        last_gesture_time = current_time

                    # Fist (all fingers down) = stop playback
                    elif fingers == [0, 0, 0, 0, 0]:
                        player.stop()
                        gesture_text = "Stop"
                        last_gesture_time = current_time

                    else:
                        # Detect swipe gestures
                        swipe = swipe_detector.update(hand_center_x)
                        if swipe == "left":
                            player.prev_track()
                            gesture_text = "Previous Track"
                            last_gesture_time = current_time
                        elif swipe == "right":
                            player.next_track()
                            gesture_text = "Next Track"
                            last_gesture_time = current_time
                else:
                    # Continue updating swipe detector to keep history fresh
                    swipe_detector.update(hand_center_x)

        else:
            # No hands detected, reset swipe detector
            swipe_detector.positions.clear()
            swipe_detector.times.clear()

        # Display UI info
        status_text = player.get_status()
        cv2.putText(frame, status_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

        if gesture_text:
            cv2.putText(frame, f"Gesture: {gesture_text}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        cv2.imshow("Gesture Controlled Media Player", frame)

        key = cv2.waitKey(1)
        if key == 27:  # ESC key
            break

    cap.release()
    cv2.destroyAllWindows()
    player.stop()

if __name__ == "__main__":
    main()
