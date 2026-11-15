
import cv2
import mediapipe as mp
import time
import os

from mediapipe.tasks import python
from mediapipe.tasks.python import vision

# --------------------------------
# 1. PROJECT SETTINGS
# --------------------------------

MODEL_PATH = "gesture_recognizer.task"

if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError(
        "Model file not found. Download gesture_recognizer.task "
        "and place it in the project folder."
    )

# --------------------------------
# 2. LOAD MEDIAPIPE MODEL
# --------------------------------

base_options = python.BaseOptions(
    model_asset_path=MODEL_PATH
)

options = vision.GestureRecognizerOptions(
    base_options=base_options,
    running_mode=vision.RunningMode.VIDEO,
    num_hands=2,
    min_hand_detection_confidence=0.5,
    min_hand_presence_confidence=0.5,
    min_tracking_confidence=0.5
)

recognizer = vision.GestureRecognizer.create_from_options(
    options
)

# --------------------------------
# 3. HAND LANDMARK CONNECTIONS
# --------------------------------

connections = [
    (0, 1), (1, 2), (2, 3), (3, 4),
    (0, 5), (5, 6), (6, 7), (7, 8),
    (5, 9), (9, 10), (10, 11), (11, 12),
    (9, 13), (13, 14), (14, 15), (15, 16),
    (13, 17), (17, 18), (18, 19), (19, 20),
    (0, 17)
]

# --------------------------------
# 4. START WEBCAM
# --------------------------------

camera = cv2.VideoCapture(0)

if not camera.isOpened():
    raise RuntimeError(
        "Camera could not be opened. Check camera permissions."
    )

print("Sign Language Recognition Started")
print("Press Q to stop.")

start_time = time.monotonic()

# --------------------------------
# 5. REAL-TIME RECOGNITION
# --------------------------------

try:
    while True:

        success, frame = camera.read()

        if not success:
            print("Unable to read camera frame.")
            break

        # Mirror the camera image
        frame = cv2.flip(frame, 1)

        # Convert BGR to RGB
        rgb_frame = cv2.cvtColor(
            frame, cv2.COLOR_BGR2RGB
        )

        # Create MediaPipe image
        mp_image = mp.Image(
            image_format=mp.ImageFormat.SRGB,
            data=rgb_frame
        )

        # Video timestamp in milliseconds
        timestamp_ms = int(
            (time.monotonic() - start_time) * 1000
        )

        # Recognize gesture
        result = recognizer.recognize_for_video(
            mp_image, timestamp_ms
        )

        # --------------------------------
        # 6. DISPLAY DETECTED HANDS
        # --------------------------------

        if result.hand_landmarks:

            for hand_index, landmarks in enumerate(
                result.hand_landmarks
            ):

                height, width, _ = frame.shape

                points = []

                for landmark in landmarks:
                    x = int(landmark.x * width)
                    y = int(landmark.y * height)
                    points.append((x, y))

                    cv2.circle(
                        frame,
                        (x, y),
                        5,
                        (0, 255, 0),
                        -1
                    )

                # Draw hand connections
                for start, end in connections:
                    cv2.line(
                        frame,
                        points[start],
                        points[end],
                        (255, 0, 0),
                        2
                    )

                # --------------------------------
                # 7. DISPLAY GESTURE PREDICTION
                # --------------------------------

                gesture_name = "Unknown"
                confidence = 0.0

                if (
                    hand_index < len(result.gestures)
                    and result.gestures[hand_index]
                ):

                    prediction = result.gestures[
                        hand_index
                    ][0]

                    gesture_name = prediction.category_name
                    confidence = prediction.score

                # Display prediction
                text = (
                    f"{gesture_name} "
                    f"({confidence * 100:.1f}%)"
                )

                cv2.putText(
                    frame,
                    text,
                    (20, 50 + hand_index * 40),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8,
                    (0, 255, 255),
                    2
                )

        else:
            cv2.putText(
                frame,
                "Show your hand to the camera",
                (20, 50),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 0, 255),
                2
            )

        # Application title
        cv2.putText(
            frame,
            "REAL-TIME GESTURE RECOGNITION",
            (20, frame.shape[0] - 25),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.65,
            (255, 255, 255),
            2
        )

        # Show webcam window
        cv2.imshow(
            "Sign Language Recognition System",
            frame
        )

        # Press Q to exit
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

finally:
    camera.release()
    cv2.destroyAllWindows()
    recognizer.close()
    print("Application stopped.")
