
import streamlit as st
import cv2
import mediapipe as mp
import tempfile
import os
from collections import Counter, deque

# -----------------------------------------
# PAGE CONFIGURATION
# -----------------------------------------

st.set_page_config(
    page_title="Human Activity Recognition",
    page_icon="🏃",
    layout="wide"
)

st.title("🏃 Human Activity Recognition System")
st.write(
    "Upload a video to detect human body posture "
    "and recognize basic activities."
)

st.info(
    "Educational prototype: activity labels are estimated "
    "from body pose and movement. Results may be inaccurate."
)

# -----------------------------------------
# MEDIAPIPE SETUP
# -----------------------------------------

mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils

# -----------------------------------------
# CALCULATE BODY ANGLE
# -----------------------------------------

def calculate_angle(a, b, c):
    """
    Calculate angle at point b using three body landmarks.
    """

    import math

    angle = math.degrees(
        math.atan2(c[1] - b[1], c[0] - b[0]) -
        math.atan2(a[1] - b[1], a[0] - b[0])
    )

    angle = abs(angle)

    if angle > 180:
        angle = 360 - angle

    return angle


# -----------------------------------------
# ACTIVITY RECOGNITION
# -----------------------------------------

def recognize_activity(landmarks, ankle_history):

    # Get required landmarks
    left_shoulder = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value]
    right_shoulder = landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value]

    left_wrist = landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value]
    right_wrist = landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value]

    left_hip = landmarks[mp_pose.PoseLandmark.LEFT_HIP.value]
    right_hip = landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value]

    left_knee = landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value]
    right_knee = landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value]

    left_ankle = landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value]
    right_ankle = landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value]

    required = [
        left_shoulder, right_shoulder,
        left_wrist, right_wrist,
        left_hip, right_hip,
        left_knee, right_knee,
        left_ankle, right_ankle
    ]

    if any(point.visibility < 0.5 for point in required):
        return "Unknown"

    # Check whether hands are raised
    hands_raised = (
        left_wrist.y < left_shoulder.y or
        right_wrist.y < right_shoulder.y
    )

    if hands_raised:
        return "Hands Raised"

    # Calculate left and right knee angles
    left_angle = calculate_angle(
        (left_hip.x, left_hip.y),
        (left_knee.x, left_knee.y),
        (left_ankle.x, left_ankle.y)
    )

    right_angle = calculate_angle(
        (right_hip.x, right_hip.y),
        (right_knee.x, right_knee.y),
        (right_ankle.x, right_ankle.y)
    )

    average_angle = (left_angle + right_angle) / 2

    # Calculate ankle movement over recent frames
    ankle_x = (left_ankle.x + right_ankle.x) / 2
    ankle_history.append(ankle_x)

    movement = 0

    if len(ankle_history) >= 8:
        movement = sum(
            abs(ankle_history[i] - ankle_history[i - 1])
            for i in range(1, len(ankle_history))
        )

    # Basic rule-based activity classification
    if movement > 0.12:
        return "Walking"

    if average_angle < 135:
        return "Sitting"

    if average_angle > 150:
        return "Standing"

    return "Unknown"


# -----------------------------------------
# VIDEO PROCESSING
# -----------------------------------------

def process_video(input_path, output_path):

    cap = cv2.VideoCapture(input_path)

    if not cap.isOpened():
        raise ValueError("Unable to open uploaded video.")

    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    if width <= 0 or height <= 0:
        cap.release()
        raise ValueError("Invalid video dimensions.")

    if fps <= 0:
        fps = 20

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")

    writer = cv2.VideoWriter(
        output_path,
        fourcc,
        fps,
        (width, height)
    )

    if not writer.isOpened():
        cap.release()
        raise ValueError("Unable to create output video.")

    activity_counts = Counter()
    ankle_history = deque(maxlen=12)

    progress = st.progress(0)
    status = st.empty()

    processed_frames = 0

    try:
        with mp_pose.Pose(
            static_image_mode=False,
            model_complexity=1,
            enable_segmentation=False,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        ) as pose:

            while True:

                success, frame = cap.read()

                if not success:
                    break

                # Convert BGR to RGB
                rgb_frame = cv2.cvtColor(
                    frame,
                    cv2.COLOR_BGR2RGB
                )

                # Detect body pose
                results = pose.process(rgb_frame)

                activity = "No Person Detected"

                if results.pose_landmarks:

                    landmarks = results.pose_landmarks.landmark

                    activity = recognize_activity(
                        landmarks,
                        ankle_history
                    )

                    # Draw body landmarks
                    mp_drawing.draw_landmarks(
                        frame,
                        results.pose_landmarks,
                        mp_pose.POSE_CONNECTIONS
                    )

                else:
                    ankle_history.clear()

                activity_counts[activity] += 1

                # Display activity on video
                cv2.rectangle(
                    frame,
                    (10, 10),
                    (450, 65),
                    (20, 20, 20),
                    -1
                )

                cv2.putText(
                    frame,
                    "Activity: " + activity,
                    (20, 48),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.9,
                    (0, 255, 0),
                    2
                )

                writer.write(frame)

                processed_frames += 1

                if total_frames > 0:
                    progress.progress(
                        min(processed_frames / total_frames, 1.0)
                    )

                status.write(
                    f"Processed frames: {processed_frames}"
                )

    finally:
        cap.release()
        writer.release()

    progress.progress(1.0)
    status.success("Video processing completed!")

    return activity_counts, processed_frames


# -----------------------------------------
# SIDEBAR
# -----------------------------------------

st.sidebar.title("HAR Navigation")

page = st.sidebar.radio(
    "Choose Module",
    [
        "Dashboard",
        "Activity Recognition",
        "About Project"
    ]
)

st.sidebar.markdown("---")
st.sidebar.write("Python | OpenCV | MediaPipe | Streamlit")


# -----------------------------------------
# DASHBOARD
# -----------------------------------------

if page == "Dashboard":

    st.subheader("Project Dashboard")

    st.write(
        "This application detects a human body in video frames "
        "and estimates basic physical activities."
    )

    col1, col2, col3 = st.columns(3)

    col1.metric("Activity Categories", "4")
    col2.metric("Pose Detection", "MediaPipe")
    col3.metric("Video Analysis", "Enabled")

    st.subheader("Recognized Activities")

    activities = [
        "🧍 Standing",
        "🪑 Sitting",
        "🚶 Walking",
        "🙌 Hands Raised"
    ]

    for activity in activities:
        st.write("•", activity)

    st.warning(
        "The activity labels are based on simple pose rules. "
        "They are not guaranteed to be correct."
    )


# -----------------------------------------
# ACTIVITY RECOGNITION MODULE
# -----------------------------------------

elif page == "Activity Recognition":

    st.subheader("Upload Your Video")

    uploaded_video = st.file_uploader(
        "Choose a video file",
        type=["mp4", "avi", "mov", "mkv"]
    )

    if uploaded_video is not None:

        st.video(uploaded_video)

        if st.button("Start Activity Recognition", type="primary"):

            input_path = None
            output_path = None

            try:

                # Save uploaded video temporarily
                with tempfile.NamedTemporaryFile(
                    delete=False,
                    suffix=".mp4"
                ) as input_file:

                    input_file.write(uploaded_video.getvalue())
                    input_path = input_file.name

                # Create output video path
                output_file = tempfile.NamedTemporaryFile(
                    delete=False,
                    suffix=".mp4"
                )

                output_path = output_file.name
                output_file.close()

                st.write("Processing video. Please wait...")

                counts, total = process_video(
                    input_path,
                    output_path
                )

                st.success("Activity recognition completed!")

                st.subheader("Processed Video")

                with open(output_path, "rb") as video_file:
                    video_bytes = video_file.read()

                st.video(video_bytes)

                st.download_button(
                    "Download Processed Video",
                    data=video_bytes,
                    file_name="human_activity_output.mp4",
                    mime="video/mp4"
                )

                st.subheader("Activity Statistics")

                col1, col2 = st.columns(2)

                col1.metric("Total Processed Frames", total)

                detected_frames = sum(
                    count for activity, count in counts.items()
                    if activity not in [
                        "No Person Detected",
                        "Unknown"
                    ]
                )

                col2.metric("Classified Frames", detected_frames)

                st.write("### Activity Frame Counts")

                for activity, count in counts.most_common():

                    percentage = (
                        count / total * 100
                        if total > 0 else 0
                    )

                    st.write(
                        f"**{activity}:** {count} frames "
                        f"({percentage:.1f}%)"
                    )

                    st.progress(percentage / 100)

            except Exception as error:

                st.error(f"Processing error: {error}")

            finally:

                # Delete temporary input and output files
                for path in [input_path, output_path]:

                    if path and os.path.exists(path):
                        try:
                            os.remove(path)
                        except OSError:
                            pass


# -----------------------------------------
# ABOUT PROJECT
# -----------------------------------------

elif page == "About Project":

    st.subheader("About Human Activity Recognition")

    st.write("""
    Human Activity Recognition (HAR) is a computer vision
    application that identifies physical activities from
    images or video.

    ### Technologies Used

    - Python
    - Streamlit
    - OpenCV
    - MediaPipe

    ### Working Process

    1. Upload a video.
    2. Extract video frames.
    3. Detect the human body.
    4. Extract body pose landmarks.
    5. Analyze body posture and movement.
    6. Estimate an activity.
    7. Display the processed video and statistics.

    ### Limitations

    - Uses basic rules instead of a trained activity classifier.
    - Works best when one person is clearly visible.
    - Occlusion and camera angles can affect results.
    - It does not recognize every human activity.
    """)

    st.info(
        "This project is intended for learning and demonstration."
    )


# -----------------------------------------
# FOOTER
# -----------------------------------------

st.divider()

st.caption(
    "Human Activity Recognition System | "
    "Python + OpenCV + MediaPipe"
)
