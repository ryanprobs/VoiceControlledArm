import face_recognition
import cv2
import pickle
from pathlib import Path
import Robotic_arm_code as move
import time
import copy


path = Path('/home/ryan/Downloads/Robotic_Arm/faces')
# append each saved names this names list 
names = [f.name for f in path.iterdir() if f.is_dir()]
#print(names)

enc_dict = {}
for i in range(len(names)):
    with open(f"faces_encodings/{names[i]}_enc.pkl", "rb") as f:
        encodings, name = pickle.load(f)

    enc_dict[name[0].lower()] = encodings # save facial encoding of each person to enc_dict by name


def recognize(video, angles):
    # Function for facial recognition
    # capture director and current servo angles input
    
    frame_count = 0
    trial_count = 0
    n_repetitions = 0 # up to 2
    identified = False
    first = False
    success = False
    attempt = 0
    unknown_count = 0
    name = None
    while True:
        frame_count += 1
        ret, frame = video.read()
        if not ret:
            break
        
        #flip frame and convert to rgb
        frame = cv2.flip(frame, -1)
        if frame_count == 2:
            
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            # Resize for faster processing
            small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
            rgb_small = small_frame[:, :, ::-1]  # BGR to RGB
            
        #     print("Frame dtype:", rgb_small.dtype)
        #     print("Frame shape:", rgb_small.shape)

            # Find faces & encodings in current frame
            face_locations_small = face_recognition.face_locations(rgb_small)
            face_locations = [(top*4, right*4, bottom*4, left*4) for (top, right, bottom, left) in face_locations_small]
            
            print("Locations found:", len(face_locations))
            #print("face Locations:", face_locations)
            
            
            # ERRORROROROROROROROROROROROROOROOR
            try:
                face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)
            except Exception as e:
                print("Encoding error:", e)
                face_encodings = []
                
            name_list = []
            #prev_name = 'qqq'
            
            if identified:
                first = True
                prev_name = name
                identified = False
            
            for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
                    
                # Compare with known faces
                name = "Unknown"
                face_in_frame = 0
                
                for i in range(len(names)):

                    matches = face_recognition.compare_faces(enc_dict[names[i]], face_encoding, tolerance = 0.38)
                
                    if True in matches: # ideally there should only be one match thoughout all the names, if not, names will be the match furthest into the list
                        #match_index = matches.index(True)
                        name = names[i]
                        identified = True
                        name_list.append(names[i])
                        face_in_frame += 1
                        break

                # Draw box and label
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
                cv2.putText(frame, name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 255), 2)
                
                
            if name == "Unknown" and face_encodings:
                n_repetitions = 0
                unknown_count += 1
                if unknown_count >= 5:
                    success = False # found face but cant recognize
                    break
            else:
                unknown_count = 0
                
            if not face_encodings:
                unknown_count = 0

            if first == True and identified == True:
                if prev_name == name:
                    n_repetitions += 1
                else:
                    n_repetitions = 0
            elif identified == False:
                n_repetitions = 0
                
            print("Unknown rep:", unknown_count)
            
            if n_repetitions == 4: # 3
                success = True # found and recognized face
                break
            
            trial_count += 1
            if trial_count >= 15:
                #angle servo[3] and servo [4]
                attempt += 1
                if attempt == 1:
                    print("ATEMPT NUMBER 1: I can't seem to recognize you")
                    
                    time.sleep(1)
                    servos = [0,1,2,3,4,5]
                    old_angles = angles.copy()
                    
                    angles[2] = angles[2] + 15
                    angles[4] = angles[4] + 33
                    #angles[3] = angles[3] + 15
                    move.smooth(servos, angles, 0.8, 14)
                    time.sleep(0.6)
                    
                    angles[4] = angles[4] - 11
                    angles[3] = angles[3] - 50
                    move.smooth(servos, angles, 0.6, 40)
                    time.sleep(0.85)
                    
                    angles[3] = angles[3] + 90
                    #angles[4] = angles[4] - 4
                    move.smooth(servos, angles, 1, 60)
                    time.sleep(0.7)
                    
                    move.smooth(servos, old_angles, 0.5, 30)
                    time.sleep(1)
                    angles = old_angles.copy()
                    
                elif attempt == 2:
                    print("ATEMPT NUMBER 2: who the fuck are you")
                    
                    time.sleep(1)
                    servos = [0,1,2,3,4,5]
                    og_angles = old_angles.copy()

                    old_angles[0] = old_angles[0] + 23
                    old_angles[3] = old_angles[3] - 50 - 3
                    old_angles[4] = old_angles[4] - 5 - 3
                    move.smooth(servos, old_angles, 0.6, 30)
                    time.sleep(0.8)

                    old_angles[0] = old_angles[0] - 46
                    old_angles[3] = old_angles[3] + 100
                    old_angles[4] = old_angles[4] + 3
                    move.smooth(servos, old_angles, 1, 40)
                    time.sleep(0.8)

                    move.smooth(servos, og_angles, 0.6, 30)
                    angles = og_angles.copy()
                else:
                    print("give the fuck up")
                    attempt = 0
                    success = None # cant find face at all
                                    
                trial_count = 0
            
            frame_count = 0
            
        cv2.imshow("Face Recognition", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    video.release()
    cv2.destroyAllWindows()
    return name, success, angles


def take_pics():
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
            filename = f"jerry_{img_counter}.jpg"
            cv2.imwrite(filename, frame)
            print(f"Saved {filename}")
            img_counter += 1
        elif key == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
