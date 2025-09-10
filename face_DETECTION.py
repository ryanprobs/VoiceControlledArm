import cv2
import computer_vision_eye as cv_eye
import Robotic_arm_code as move
import time
import detect_recognition as face2name
import stop_flag
import mediapipe as mp
import wave_d


def p_step(offset, max_step = 50, scale = 0.02):
    #calibrate face following movement, (still very bad)

    if offset > 180:
        scale = 0.135 #0.135
    elif offset > 50:
        scale = 0.1 #0.1
    else:
        scale = 0.07 #0.07
    step = scale * (abs(offset))
    
    return min(step, max_step)


def follow_faces(rec=False, stop=True):
    # face following and wave gesture detection function
    
    servos = [0,1,2,3,4,5]
    angles = [90.0, 139.6061129850472, 111.9084708148627, 90, 67.30235782981549, 10]
    # Load Haar cascade
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    
    mp_drawing = mp.solutions.drawing_utils
    mp_hands = mp.solutions.hands
    
    # Start webcam
    cap = cv2.VideoCapture(0)
    
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    center_area= 20 #pixels
    
    last_move_time = time.time()
    lag = 0.5
    frame_count = 0
    center_count = 0
    centered = False
    
    with mp_hands.Hands(
        min_detection_confidence=0.6,
        min_tracking_confidence=0.6,
        max_num_hands=1
    ) as hands:       

        while True:
            frame_count +=1
            ret, frame = cap.read()
            
            if not ret:
                break
            
            frame = cv2.rotate(frame, cv2.ROTATE_180)
            if frame_count == 5:
                frame_count = 0
                
                # Convert to grayscale
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

                # Detect faces
                faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)
                
                if isinstance(faces, tuple) or len(faces) == 0:
                    faces = []
                    
                print("faces found:",len(faces))
                current_time = time.time()
                dt = current_time - last_move_time
                if len(faces) > 0 and dt > lag:
                    (x, y, w, h) = faces[0]
                    face_center_x = x + (w // 2)
                    face_center_y = y + (h // 2)
                    
                    frame_center_x = frame_width // 2
                    frame_center_y = frame_height // 2
                    
                    offset_x = face_center_x - frame_center_x
                    offset_y = face_center_y - frame_center_y
                
                    if abs(offset_x) > center_area:
                        steps = p_step(offset_x)
                        print("x steps:", steps)
                        print("offset:", offset_x)
                        if offset_x < 0:
                            # move base right
                            angles[0] = max(min(angles[0] + steps, 180), 0)
                        else:
                            #move base left
                            angles[0] = max(min(angles[0] - steps, 180), 0)

                    if abs(offset_y) > center_area:
                        steps = p_step(offset_y)
                        print("y steps:", steps)
                        if offset_y < 0:
                            # move up
                            angles[4] = max(min(angles[4] + steps, 180), 0)
                        
                        else:
                            #move down
                            angles[4] = max(min(angles[4] - steps, 180), 0)
                
                    # Draw rectangles
                    for (x, y, w, h) in faces:
                        cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
                        # Draw face dot
                        cv2.circle(frame, (x+(w//2),y+(h//2)), 5, (0,255,0), -1)
                    
                    #move
                    servos = [0,1,2,3,4,5]
                    move.smooth(servos, angles, 0.6, 20)
                    last_move_time = current_time
                    
                    # do the gutti AhAHahhaHAaaa~~
                    if abs(offset_x) <= center_area and abs(offset_y) <= center_area:
                        center_count +=1
                    else:
                        center_count = 0
                    
                    if center_count >= 2:
                        print("Face is centered")
                        centered = True
                        center_count = 0
                        if stop:
                            if rec:
                                print("Executing face recognition")
                                name, result, angles = face2name.recognize(cap, angles)
                                return name, angles, result
                            elif not rec:
                                return angles
                        elif stop_flag.stop_flag: # if stop must be false, when it keeps going after centered
                            break
                        elif not stop_flag.stop_flag:
                            #check for wave
                            print('checking for wave')
                            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                            image.flags.writeable = False
                            results = hands.process(image)

                            # Convert back to BGR for OpenCV
                            image.flags.writeable = True
                            #frame = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
                            
                            # If hand found
                            if results.multi_hand_landmarks:
                                for hand_landmarks in results.multi_hand_landmarks:
                                    # Optional: comment out for more FPS
                                    mp_drawing.draw_landmarks(
                                        frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                                    
                                    wave_check = wave_d.detect_wave(frame, hand_landmarks)
                                    print('__WAVE CHECK___:', wave_check)
                                    if wave_check:
                                        angles = move.wave_motion(angles)
                    
                # Draw center area
                cv2.rectangle(frame, ((frame_width-center_area)//2, (frame_height-center_area)//2), ((frame_width+center_area)//2, (frame_height+center_area)//2), (0, 255, 0), 2)
                
                # Show result
                cv2.imshow('Face Detection', frame)

            # Press 'q' to quit
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    # Cleanup
    cap.release()
    cv2.destroyAllWindows()
