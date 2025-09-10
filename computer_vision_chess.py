import cv2
import os
import glob
import numpy as np


data = np.load("calib_data.npz")
mtx=data['mtx']
dist=data['dist']
corners_refined=data['corners']
rvec=data['rvec'][0]
tvec=data['tvec'][0]

#print(data['rvec'])

def run():
    # detect and get the coodinate of the largest black coled blob

    chessboard_size = (7, 7)  # (columns, rows of inner corners)
    square_size = 3.8         # square size in real-world units 3.8
    cap = cv2.VideoCapture(2)  # 0 = /dev/video0

    if not cap.isOpened():
        print("Cannot open camera")
        exit()

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Undistort image
        h, w = frame.shape[:2]
        new_mtx, roi = cv2.getOptimalNewCameraMatrix(mtx, dist, (w,h), 1, (w,h))
        undistorted = cv2.undistort(frame, mtx, dist, None, new_mtx)
        x, y, w, h = roi
        undistorted = undistorted[y:y+h, x:x+w]

        # detect black blob
        hsv = cv2.cvtColor(undistorted, cv2.COLOR_BGR2HSV)
        lower_black = (0, 0, 0)
        upper_black = (180, 255, 50)
        mask = cv2.inRange(hsv, lower_black, upper_black)

        #print(mask.shape)

        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        #print('contour:', contours)

        if contours:
            largest = max(contours, key=cv2.contourArea)
            M = cv2.moments(largest)
            if M["m00"] != 0:
                cx = int(M["m10"] / M["m00"])
                cy = int(M["m01"] / M["m00"])
                cv2.circle(undistorted, (cx, cy), 5, (0, 255, 0), -1)

                print(f"Object image position: ({cx}, {cy})")
        
        # map 2D image point to 3D on chessboard plane (Z = 0)
                # Build rotation matrix from rvec
                R, _ = cv2.Rodrigues(rvec)
                #Rt = np.column_stack((R, tvec))  # 3x4 matrix

                # Get inverse projection matrix
                inv_mtx = np.linalg.inv(mtx)

                # convert image point to normalized camera coordinates
                uv1 = np.array([[cx], [cy], [1]], dtype=np.float32)
                cam_coords = inv_mtx @ uv1

                # solve for s in: s * cam_coords = R * X + t, Z = 0
                # solve for s * cam_coords = R_2D * X + t
                r1 = R[:, 0]
                r2 = R[:, 1]
                t = tvec.reshape(3)

                A = np.column_stack((r1, r2))
                b = (cam_coords.flatten() * t[2])[:2] - t[:2]

                X = np.linalg.solve(A[:2, :], b)
                object_pos = np.array([X[0], X[1], 0])

                print("Estimated 3D position on chessboard plane:", object_pos)

                # Display position on image
                cv2.putText(undistorted, f"({object_pos[0]:.2f}, {object_pos[1]:.2f})",
                            (cx + 10, cy - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)
        
        
        cv2.imshow('Undistorted Live', undistorted)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cv2.destroyAllWindows()
    
    return object_pos

def run_colors():
    #grab coordinates of each colored blocks
    cap = cv2.VideoCapture(2)  # 0 = /dev/video0

    color_bgr_map = {
        "Red": (0, 0, 255),
        "Green": (0, 255, 0),
        "White": (255, 255, 255),
        "Black": (0, 0, 0)
    }

    object_positions = {
        "Red": [],
        "Green": [],
        "White": [],
        "Black": []
    }

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Undistort image
        h, w = frame.shape[:2]
        new_mtx, roi = cv2.getOptimalNewCameraMatrix(mtx, dist, (w, h), 1, (w, h))
        undistorted = cv2.undistort(frame, mtx, dist, None, new_mtx)
        x, y, w, h = roi
        undistorted = undistorted[y:y + h, x:x + w]

        # Convert to HSV
        hsv = cv2.cvtColor(undistorted, cv2.COLOR_BGR2HSV)

        # Define HSV masks
        lower_red1 = np.array([0, 100, 100])
        upper_red1 = np.array([10, 255, 255])
        lower_red2 = np.array([160, 100, 100])
        upper_red2 = np.array([180, 255, 255])
        mask_red = cv2.inRange(hsv, lower_red1, upper_red1) | cv2.inRange(hsv, lower_red2, upper_red2)

        lower_green = np.array([40, 50, 50])
        upper_green = np.array([80, 255, 255])
        mask_green = cv2.inRange(hsv, lower_green, upper_green)

        lower_white = np.array([0, 0, 200])
        upper_white = np.array([180, 30, 255])
        mask_white = cv2.inRange(hsv, lower_white, upper_white)

        lower_black = np.array([0, 0, 0])
        upper_black = np.array([180, 255, 50])
        mask_black = cv2.inRange(hsv, lower_black, upper_black)

        # Combine all masks
        masks = {
            "Red": mask_red,
            "Green": mask_green,
            "White": mask_white,
            "Black": mask_black
        }

        for color_name, mask in masks.items():
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            if not contours:
                continue #skip to next color if no contour of this color is found
            
            contour = max(contours, key=cv2.contourArea)
            if cv2.contourArea(contour) < 100:
                continue #skip if contour is too small

            M = cv2.moments(contour)
            if M["m00"] == 0:
                continue
            cx = int(M["m10"] / M["m00"])
            cy = int(M["m01"] / M["m00"])

            # mark the center of each color
            cv2.circle(undistorted, (cx, cy), 5, color_bgr_map[color_name], -1)

            # Estimate 3D position on chessboard plane (Z = 0)
            R, _ = cv2.Rodrigues(rvec)
            inv_mtx = np.linalg.inv(mtx)
            uv1 = np.array([[cx], [cy], [1]], dtype=np.float32)
            cam_coords = inv_mtx @ uv1

            r1 = R[:, 0]
            r2 = R[:, 1]
            t = tvec.reshape(3)

            A = np.column_stack((r1, r2))
            b = (cam_coords.flatten() * t[2])[:2] - t[:2]

            try:
                X = np.linalg.solve(A[:2, :], b)
            except np.linalg.LinAlgError:
                continue  # Skip if matrix is singular

            object_pos = np.array([X[0], X[1], 0])
            if len(object_positions[color_name]) == 0:
                object_positions[color_name].append(object_pos)
            else:
                object_positions[color_name][0]=object_pos

            # Draw label
            label = f"{color_name}: ({object_pos[0]:.1f}, {object_pos[1]:.1f})"
            cv2.putText(undistorted, label, (cx + 10, cy - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, color_bgr_map[color_name], 2)

        cv2.imshow('Undistorted Live', undistorted)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    print("obj pos:",object_positions)
    return object_positions


#run_colors()
# print(pos)
