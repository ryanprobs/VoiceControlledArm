import cv2
import numpy as np
import Robotic_arm_code as move
import random
import time
import os
import face_recognition
import pickle


def video():
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        flipped = cv2.rotate(frame, cv2.ROTATE_180)
        cv2.imshow('flipped', flipped)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


def path():
    # idle motion, NOT FINISHED
    #move.default()
    move.sleep_mode()
    time.sleep(2)
    while True:
        yaw_change = random.uniform(-1.2, 1.2)
        pitch_change = random.uniform(-1.2, 1.2)
        mouth_change = random.randint(10, 50)
        move.go_to(14,15,0, 0, -5, mouth_change, 0.5)
        time.sleep(0.3)


def save_face(name):
    # Used with Robert's feature: User gives their name and can manually take picture of their
    #  face for future facial recognition
    
    #create folder
    f_name = name
    b_path = '/home/ryan/Downloads/Robotic_Arm/faces'
    f_path = os.path.join(b_path, f_name)
    os.makedirs(f_path, exist_ok=True)
    
    #take the picture
    cap = cv2.VideoCapture(0)
    img_counter = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        frame = cv2.rotate(frame, cv2.ROTATE_180)
        cv2.imshow("Press 's' to save, 'q' to quit", frame)

        key = cv2.waitKey(1)
        if key == ord('s'):
            filename = f"{name}_{img_counter}.jpg"
            folder = f'/home/ryan/Downloads/Robotic_Arm/faces/{name}'
            os.makedirs(folder, exist_ok=True)
            path = os.path.join(folder, filename)
            cv2.imwrite(path, frame)
            print(f"Saved {filename}")
            img_counter += 1
        elif key == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    
    
    #save encodings
    ryan_encodings = []
    ryan_name = []
    num_img = len([f for f in os.listdir(b_path) if f.lower().endswith(".jpg")])
    for i in range(0, (img_counter-1)):
        #img = cv2.imread(f"ryan_{i}.jpg")
        #img_rotated = cv2.flip(img, -1)
        #cv2.imwrite(f"ryan_{i}.jpg", img_rotated)
        
        image = face_recognition.load_image_file(f"/home/ryan/Downloads/Robotic_Arm/faces/{name}/{name}_{i}.jpg")
        encodings = face_recognition.face_encodings(image)
        
        if encodings:  # Make sure a face was detected
            ryan_encodings.append(encodings[0])
            ryan_name.append(name)
        else:
            print(f"No face found in image {i}.jpg")

    with open(f"faces_encodings/{name}_enc.pkl", "wb") as f:
        pickle.dump((ryan_encodings, ryan_name), f)

#save_face('tom')
