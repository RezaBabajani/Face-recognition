import face_recognition
import pickle
import cv2
import numpy as np


def save_encodings(known_face_encodings, known_face_names):
    """Save the encodings and names to a file."""
    with open('face_encodings_database.pkl', 'wb') as f:
        pickle.dump((known_face_encodings, known_face_names), f)


# Function to find and add a new face
def check_existing_matches(captured_region, known_face_encodings, known_face_names):
    face_encoding = face_recognition.face_encodings(captured_region)[0]
    matches = face_recognition.compare_faces(known_face_encodings, face_encoding, tolerance=0.50)

    if True not in matches:
        # No match found, ask for the name and add the new face encoding along with the name
        name = input("What is your name?")
        known_face_encodings.append(face_encoding)
        known_face_names.append(name)
        save_encodings(known_face_encodings, known_face_names)  # Save the new encodings and names
        return name
    else:
        # A match was found, get the index of the first match
        first_match_index = matches.index(True)
        name = known_face_names[first_match_index]
        return name
