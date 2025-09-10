import cv2
import os
import glob
import numpy as np

cap = cv2.VideoCapture(0)  # 0 = /dev/video0

if not cap.isOpened():
    print("Cannot open camera")
    exit()

image_folder = '/home/ryan/Downloads/Robotic_Arm/images'
os.makedirs(image_folder, exist_ok=True)

#takes 10 immages of checkered board for calibration
for i in range(10):
    ret, frame = cap.read()
    if not ret:
        print("Can't receive frame (stream end?). Exiting ...")
        break
    
    filename = f"{image_folder}/image_{i+1}.jpg"
    cv2.imwrite(filename, frame)
    cv2.waitKey(500)

# --- Step 1: Chessboard Setup ---
num_cols = 7   # inner corners across
num_rows = 7   # inner corners down
chessboard_size = (num_cols, num_rows)

# Create a single set of 3D points for the chessboard (Z = 0 since it's flat)
num_corners = num_cols * num_rows
one_chessboard_3d_points = np.zeros((num_corners, 3), dtype=np.float32)

# Fill in the X and Y coordinates
index = 0
for y in range(num_rows):
    for x in range(num_cols):
        one_chessboard_3d_points[index, 0] = x * 3.8
        one_chessboard_3d_points[index, 1] = y * 3.8
        # Z stays 0
        index += 1
#print(one_chessboard_3d_points)

# --- Step 2: Prepare storage for all data ---
all_3d_points = []  # Real world 3D points
all_2d_points = []  # 2D image points

# --- Step 3: Load and process all calibration images ---
images = glob.glob('/home/ryan/Downloads/Robotic_Arm/images/*.jpg')  # Path to your calibration images
#print(images)
show_img = False
for filename in images:
    image = cv2.imread(filename)
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Try to find chessboard corners
    #print(f'processing {filename}')
    found, corners = cv2.findChessboardCorners(gray_image, chessboard_size, None)
    print(found)
    #print(f'found? {corners}')

    if found:
        # Save 3D points
        all_3d_points.append(one_chessboard_3d_points)

        # Improve corner accuracy
        refined_corners = cv2.cornerSubPix(
            gray_image, corners,
            winSize=(11, 11),
            zeroZone=(-1, -1),
            criteria=(cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
        )

        # Save 2D points
        print("Refined corners:", refined_corners)
        all_2d_points.append(refined_corners)

    if found:
        # Draw corners on the original image (in color)
        cv2.drawChessboardCorners(image, chessboard_size, corners, found)
        cv2.putText(image, "Corners Found", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    else:
        cv2.putText(image, "Corners NOT Found", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

    # Show result with/without corners
    if show_img == False and found == True:
        show_img = True
        cv2.imshow('Corner Detection Result', image)
        cv2.imshow('Grayscale Image', gray_image)
        # Wait for key press
        key = cv2.waitKey(0)  # press any key to go to next image

cv2.destroyAllWindows()
    
# --- Step 4: Run camera calibration ---
image_size = gray_image.shape[::-1]  # (width, height)
success, camera_matrix, dist_coeffs, rvecs, tvecs = cv2.calibrateCamera(
    all_3d_points, all_2d_points, image_size, None, None)


# save calibration results
np.savez("calib_data.npz", mtx=camera_matrix, dist=dist_coeffs, corners=refined_corners, rvec=rvecs, tvec=tvecs)

# --- Step 6: Print results ---
print("✅ Calibration successful!" if success else "❌ Calibration failed.")
print("\nCamera Matrix (Intrinsic parameters):\n", camera_matrix)
print("\nDistortion Coefficients:\n", dist_coeffs)


data = np.load("calib_data.npz")
mtx=data['mtx']
dist=data['dist']


while True:
    ret, frame = cap.read()
    if not ret:
        break

    h, w = frame.shape[:2]
    new_mtx, roi = cv2.getOptimalNewCameraMatrix(mtx, dist, (w,h), 1, (w,h))
    undistorted = cv2.undistort(frame, mtx, dist, None, new_mtx)
    x, y, w, h = roi
    undistorted = undistorted[y:y+h, x:x+w]

    cv2.imshow('Undistorted Live', undistorted)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
