import io
import cv2
import base64 
import numpy as np
import face_recognition
from PIL import Image


def save_image_base64(img_base64: str, file_path: str):
    with open(file_path, 'wb') as file:
        file.write(base64.b64decode(img_base64))


def get_face_count(img_str: str) -> int:
    image = face_recognition.load_image_file(img_str)
    faces = face_recognition.face_locations(image)
    
    return len(faces)