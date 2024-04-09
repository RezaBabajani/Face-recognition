import cv2
import numpy as np
import os
from person_recognition import check_existing_matches, save_encodings
from text_to_speech import greeting


def draw_oval(frame, axes_lengths):
    # Create an empty (all black) mask with the same dimensions as the frame, but only single channel
    mask = np.zeros((frame.shape[0], frame.shape[1]), dtype=np.uint8)

    # Specify the parameters for the vertical oval (ellipse)
    center_coordinates = (frame.shape[1] // 2, frame.shape[0] // 2)  # Center of the frame
    oval_top = center_coordinates[1] - axes_lengths[1]
    oval_bottom = center_coordinates[1] + axes_lengths[1]

    angle = 0  # Angle of rotation of the ellipse in degrees
    start_angle = 0  # Starting angle of the elliptic arc in degrees
    end_angle = 360  # Ending angle of the elliptic arc in degrees
    color = 255  # White color for the ellipse (to keep the inside visible)
    thickness = -1  # Fill the ellipse

    # Draw the vertical oval on the mask
    cv2.ellipse(mask, center_coordinates, axes_lengths, angle, start_angle, end_angle, color, thickness)

    # Create a transparent layer by blending the frame with a black frame, outside the oval area
    transparent_outside_oval = cv2.addWeighted(frame, 0.3, np.zeros_like(frame), 0.3, 0)

    # Use the mask to blend the original frame (inside the oval) with the darkened frame (outside the oval)
    mask_inv = cv2.bitwise_not(mask)
    inside_oval = cv2.bitwise_and(frame, frame, mask=mask)
    outside_oval = cv2.bitwise_and(transparent_outside_oval, transparent_outside_oval, mask=mask_inv)
    final_frame = cv2.add(inside_oval, outside_oval)

    # Draw the white border of the oval over the final frame
    border_thickness = 2  # Thickness of the border
    cv2.ellipse(final_frame, center_coordinates, axes_lengths, angle, 0, 360, (255, 255, 255), border_thickness)

    return final_frame, oval_top, oval_bottom


def load_webcam(configFile, modelFile, axes_length, known_face_encodings, known_face_names):
    # Initialize the webcam
    video_capture = cv2.VideoCapture(1)

    # Load a pre-trained face detector from OpenCV
    # face_cascade = cv2.CascadeClassifier(haarcascade_path)

    # Directory to save the captured frame
    save_directory = "./captured_frames"
    if not os.path.exists(save_directory):
        os.makedirs(save_directory)

    # Initialize variables for the animation
    animate = False
    bar_height = 0  # Current height of the bar
    animation_frames = 20  # Number of frames to complete the animation

    net = cv2.dnn.readNetFromCaffe(configFile, modelFile)

    while True:
        # Grab a single frame of video
        ret, frame = video_capture.read()

        # Check if we successfully got a frame
        if not ret:
            break

        # Detect faces in the frame
        # gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        # faces = face_cascade.detectMultiScale(gray, 1.1, 4)
        # Prepare the frame for detection
        (h, w) = frame.shape[:2]
        blob = cv2.dnn.blobFromImage(cv2.resize(frame, (300, 300)), 1.0, (300, 300), (104.0, 177.0, 123.0))

        # Detect faces
        net.setInput(blob)
        detections = net.forward()

        result, oval_top, oval_bottom = draw_oval(frame, axes_length)

        feedback_text = "Adjust your position."
        # Check each detected face
        for i in range(0, detections.shape[2]):
            confidence = detections[0, 0, i, 2]

            if confidence > 0.5:  # Confidence threshold
                box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                (startX, startY, endX, endY) = box.astype("int")

                # Draw the detected face bounding box
                # cv2.rectangle(result, (startX, startY), (endX, endY), (0, 255, 0), 2)

                face_top = startY
                face_bottom = endY
                # print(f"Face position is between {face_top, face_bottom}")
                # print(f"Oval position is between {oval_top, oval_bottom}")

                # Check if the face is from below the oval to above the oval
                if (oval_top + 10 >= face_top >= oval_top) and \
                   (oval_bottom - 10 <= face_bottom <= oval_bottom):
                    feedback_text = "Position OK."
                    if not animate:
                        animate = True
                        bar_position = 0  # Start the bar at the top of the oval
                    break
                else:
                    animate = False

        if animate:
            # Calculate the new position of the bar based on the current frame
            bar_position += (130 * 2) / animation_frames
            if bar_position >= 130 * 2:
                bar_position = 130 * 2  # Ensure bar does not exceed bottom of the oval
                animate = False  # Stop animation when it reaches the bottom
                # Capture and save the frame within the oval
                mask = np.zeros_like(frame)
                cv2.ellipse(mask, (frame.shape[1] // 2, frame.shape[0] // 2), axes_length, 0, 0, 360, (255, 255, 255), -1)
                captured_region = cv2.bitwise_and(frame, mask)
                name = check_existing_matches(captured_region, known_face_encodings, known_face_names)
                greeting(name)
                # cv2.imwrite(os.path.join(save_directory, f"{name}.jpg"), captured_region)
                break  # Stop the live feed

            # Draw the "bar" animation within the oval
            cv2.line(result, (frame.shape[1] // 2 - axes_length[0], int(oval_top + bar_position)),
                     (frame.shape[1] // 2 + axes_length[0], int(oval_top + bar_position)), (255, 0, 0), 3)
        else:
            frame_count = 0

        # Display the feedback text on the frame
        cv2.putText(result, feedback_text, (50, frame.shape[0] - 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2,
                    cv2.LINE_AA)

        cv2.imshow("Face recognition", result)

        # Hit 'q' on the keyboard to quit!
        key = cv2.waitKey(1)
        if key == ord('q'):
            break
        if key == ord('s'):
            print("save the image")

    video_capture.release()
    cv2.destroyAllWindows()