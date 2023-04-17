import os
import base64
import face_recognition
from datetime import datetime, timedelta
from jose import jwt, JWTError
from fastapi import Request

SECRET_KEY = "Ifpsq6BYAbMfb74VogyUxZPFmrylCh77Oe8LTLo7neQgq5vhUQ3CQa3mqvV30nOp"
ALGORITHM = "HS256"


def save_image_base64(img_base64: str, file_path: str):
    with open(file_path, 'wb') as file:
        file.write(base64.b64decode(img_base64))


def get_face_count(img_str: str) -> int:
    image = face_recognition.load_image_file(img_str)
    faces = face_recognition.face_locations(image)
    
    return len(faces)


def check_face(user_image_path: str, temp_image_path: str) -> bool:
    try:
        user = face_recognition.load_image_file(user_image_path)
        temp = face_recognition.load_image_file(temp_image_path)
        
        biden_encoding = face_recognition.face_encodings(user)[0]
        unknown_encoding = face_recognition.face_encodings(temp)[0]

        results = face_recognition.compare_faces([biden_encoding], unknown_encoding)
        os.remove(temp_image_path)
        
        return results[0]
    except:
        return False
    
    
def gen_test_token(test_id: int, time: timedelta) -> str:
    encode = {"test_id": test_id, "exp": datetime.utcnow() + time + timedelta(minutes=10)}
    
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)


def check_test_token(request: Request, test_id: int) -> bool:
    try:
        token = request.cookies.get('test_token')
        if token is None:
            return False
        payload = jwt.decode(token=token, key=SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("test_id") != test_id:
            return False
        return True
    except JWTError:
        return False
    
    
def get_score(procent: float) -> int:
    if procent >= 90:
        return 5
    elif procent >= 80: 
        return 4
    elif procent >=60:
        return 3
    else:
        return 2
    