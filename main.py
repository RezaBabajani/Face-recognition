from loading_webcam import load_webcam
import pickle

haarcascade_path = './models/haarcascade_frontalface_default.xml'

# Load the DNN model
modelFile = "./models/res10_300x300_ssd_iter_140000.caffemodel"
configFile = "./models/deploy.prototxt"

axes_lengths = (95, 130)  # (width, height) of the ellipse

# Attempt to load an existing face encodings database
try:
    with open('face_encodings_database.pkl', 'rb') as f:
        known_face_encodings, known_face_names = pickle.load(f)
except (FileNotFoundError, EOFError):
    known_face_encodings = []  # Initialize an empty list for face encodings
    known_face_names = []  # Initialize an empty list for names

load_webcam(configFile, modelFile, axes_lengths, known_face_encodings, known_face_names)