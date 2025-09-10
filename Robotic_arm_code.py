import time
import math
from adafruit_servokit import ServoKit
import computer_vision_chess as get_pos
import random
import copy

kit = ServoKit(channels=16)
kit.servo[6].set_pulse_width_range(min_pulse = 500, max_pulse = 2550)
kit.servo[0].set_pulse_width_range(min_pulse = 500, max_pulse = 2550) 
kit.servo[1].set_pulse_width_range(min_pulse = 570, max_pulse = 2550)
kit.servo[2].set_pulse_width_range(min_pulse = 550, max_pulse = 2500) 
kit.servo[3].set_pulse_width_range(min_pulse = 500, max_pulse = 2400) # min_pulse = 620, max_pulse = 2530 OR 650, max_pulse = 2550
kit.servo[4].set_pulse_width_range(min_pulse = 600, max_pulse = 2450) #540, 2450
kit.servo[5].set_pulse_width_range(min_pulse = 1050, max_pulse = 2000)

l1 = 12.5
l2 = 12.5
l3 = 12.5


def default():
    kit.servo[0].angle = 90
    kit.servo[1].angle = 90
    kit.servo[2].angle = 90
    kit.servo[3].angle = 90
    kit.servo[4].angle = 90
    kit.servo[5].angle = 100

def sleep_mode():
    '''
    kit.servo[0].angle = 90
    kit.servo[1].angle = 125
    kit.servo[2].angle = 135
    kit.servo[3].angle = 90
    kit.servo[4].angle = 10
    kit.servo[5].angle = 50
    '''
    base, elbow, shoulder, wrist = inverse_k_3d(5.5,-4.3,0,-85) #10,10,-40
    print(base,elbow, shoulder, wrist)
    servos = [0,1,2,3,4]
    target_angle = [base, elbow, shoulder, 90, wrist]
    time.sleep(1.5)
    smooth(servos, target_angle)

def inverse_k_3d(x,y,z,d):
    # inverse kinematic 3DoF (only position, no orientation)
    d = d * math.pi / 180
    
    #elbow calc
    
    xz_angle = math.atan2(z,x)
    
    x = x - (l3 * math.cos(d) * math.cos(xz_angle))
    y = y - (l3 * math.sin(d))
    z = z - (l3 * math.cos(d) * math.sin(xz_angle))
    
    print(x,y,z)
    
    L = math.sqrt((x ** 2) + (y ** 2) + (z ** 2))
    #print(x,y,z,L)
    a = math.acos(((l1 ** 2) + (l2 ** 2) - (L ** 2)) / (2 * l1 * l2))
    beta = math.pi - a # elbow
    
    #shoulder calc
    b = math.atan2((l2 * math.sin(beta)),(l1 + (l2 * math.cos(beta))))
    theta = b + (math.atan2(y,math.sqrt((x**2) + (z**2))))
    
    #base calc
    base = math.atan2(z,x)
    
    #convert for rad to deg
    beta = beta * 180 / math.pi
    theta = theta * 180 / math.pi
    base = (base * 180 / math.pi) + 90
    d = d * 180 / math.pi
    
    phi = 90 - (theta - beta - d)
    return base, theta, beta, phi


def inverse_k_5dof(x,y,z,theta_xz,theta_y):
    #inverse kinematics for 5 DoF
    theta_xz = theta_xz * math.pi / 180
    theta_y = theta_y * math.pi / 180
    
    #elbow calc
    
    x_new = x - (l3 * math.cos(theta_xz) * math.cos(theta_y))
    y_new = y + (l3 * math.cos(theta_xz) * math.sin(theta_y))
    z_new = z + (l3 * math.sin(theta_xz))
    print('New Coordinates:', x_new,y_new,z_new)
    
    xz_angle = math.atan2(z_new,x_new)
    L = math.sqrt((x_new ** 2) + (y_new ** 2) + (z_new ** 2))

    a = math.acos(((l1 ** 2) + (l2 ** 2) - (L ** 2)) / (2 * l1 * l2))
    beta = math.pi - a # elbow
    
    #shoulder calc
    b = math.atan2((l2 * math.sin(beta)),(l1 + (l2 * math.cos(beta))))
    theta = b + (math.atan2(y_new,math.sqrt((x_new**2) + (z_new**2))))
    
    #base calc
    base = math.atan2(z_new,x_new)
    
    #convert for rad to deg
    a = a * 180 / math.pi
    beta = beta * 180 / math.pi
    theta = theta * 180 / math.pi
    base = (base * 180 / math.pi) + 90
    theta_xz = theta_xz * 180 / math.pi
    theta_y = theta_y * 180 / math.pi
    xz_angle = xz_angle * 180 / math.pi
    
    end_v = (x - x_new, y - y_new, z - z_new) #vector of third joint (end effector)
    print("Start:", x_new, y_new, z_new)
    print("End", x, y, z)
    print("vector", end_v)
        
        
    #servo 3 calc attepts 2
    r_zy = math.sqrt((end_v[1]**2) + (end_v[2]**2))
    if end_v[2] == 0:
        s_3 = 90
    
    elif end_v[1] == 0:
        print('y=000000')
        if end_v[2] > 0:
            s_3 = 180
        if end_v[2] < 0:
            s_3 = 0
    else:
        angle_3 = math.atan(end_v[1] / end_v[2])
        print('after tan:', angle_3)
        angle_3 = angle_3 * 180 / math.pi
        print('after conversion:', angle_3)
        s_3 = angle_3 #- xz_angle
        
        if theta_y < 0:
            s_3 = 180 - abs(s_3)
        
        elif end_v[2] > 0:
            s_3 = 180 - abs(s_3)
    
    print('xz-angle:',xz_angle)
    #servo4
    r = 180 - (a + theta)
    print('r=', r)
        
    #servo4 attempt 2
    angle_4 = math.acos(max(-1, min(r_zy / l3, 1)))
    angle_4 = angle_4 * 180 / math.pi
    print(angle_4)
    
    if theta_y < 0:
        angle_4 = 180 - abs(angle_4)
        
    if end_v[2] == 0:
        s_4 = angle_4 + r
    elif end_v[2] > 0:

        s_4 = angle_4 + xz_angle + r
    else:

        s_4 = angle_4 - xz_angle + r

    print(f"s_3: {s_3}, s_4: {s_4}")

    return base, theta, beta, s_3, s_4


def smooth(servos, target_angles, duration=0.7, steps=80, t=1.9): #0.7, 110, 1.9
    # Uses the idea of the sigmoid curve to create smoother movement to end position. accelerate then decelerate.
    start_angles = []
    for i in range(len(servos)):
        start_angles.append(kit.servo[servos[i]].angle)
        
    for i in range(steps + 1):
        r_prog = i/steps
        
        progress = (r_prog**t) / (r_prog**t + ((1 - r_prog)**t)) # function for slower motion at start and finish points
        
        for j in range(len(servos)):
            angle = start_angles[j] + (target_angles[j] - start_angles[j]) * progress
            angle = max(0, min(180, angle))
            #print(f'{servos[j]}: {angle}')
            kit.servo[servos[j]].angle = angle
        time.sleep(duration/steps)
        
def go_to(x,y,z,yaw,pitch, servo_5 = 20, duration = 0.7):
    # shortcut function for moving robotic arm with inverse kin & smooth function
    base, elbow, shoulder, wrist_hor, wrist_vert = inverse_k_5dof(x,y,z,yaw,pitch) #5.1*(grid) + space,13.5,(0*grid), -86
    print('angles:',base,elbow, shoulder, wrist_hor, wrist_vert)
    servos = [0,1,2,3,4,5]
    target_angle = [base, elbow, shoulder, wrist_hor, wrist_vert, servo_5]
    smooth(servos, target_angle, duration)
    
def go_to_manual(x,y,z,yaw,pitch):
    # shortcut function for moving robotic arm with inverse kin without the need of smooth function
    base, elbow, shoulder, wrist_hor, wrist_vert = inverse_k_5dof(x,y,z,yaw,pitch)
    kit.servo[0].angle = base
    kit.servo[1].angle = elbow
    kit.servo[2].angle = shoulder
    kit.servo[3].angle = wrist_hor
    kit.servo[4].angle = wrist_vert
    print()
    
    
'''
kit.servo[5].angle = 20
for i in range(1, 30, 1):
    print(i)
    go_to_manual(3.5*grid + space,10,(0*grid), i, 30)
    time.sleep(0.1)
    
for i in range(29, -30, -1):
    print(i)
    go_to_manual(3.5*grid + space,10,(0*grid), i, 30)
    time.sleep(0.1)

for i in range(-29, 1, 1):
    print(i)
    go_to_manual(3.5*(grid) + space,10,(0*grid), i, 30)
    time.sleep(0.1)
'''


def mouth_hi(angles, rep):
    # Gripper movement to imitate opening and closing mouth while talking
    time.sleep(2)
    for i in range(rep):
        #mouth open time
        m_o_t = random.uniform(0.1, 0.4)
        m_o = random.randint(70, 170)
        m_c_t = random.uniform(0.06, 0.4)
        m_c = random.randint(0, 20)
        
        #open mouth  
        servos = [0,1,2,3,4,5]
        angles[5] = m_o
        smooth(servos, angles, 0.14, 10)
        time.sleep(m_o_t)
        #close mouth
        servos = [0,1,2,3,4,5]
        angles[5] = m_c
        smooth(servos, angles, 0.14, 10)
        time.sleep(m_c_t)


def wave_motion(angles):
    old_angles = angles.copy()
    servos = [0,1,2,3,4,5]
    smooth(servos, angles, 0.7, 25)
    
    angles[3] = 45
    smooth(servos, angles, 0.7, 25)
    time.sleep(0.7)
    
    angles[4] = 150
    angles[3] = 90
    smooth(servos, angles, 0.7, 25)
    time.sleep(0.5)
    
    for i in range(2):
        angles[3] = 130
        smooth(servos, angles, 0.4, 15)
        #time.sleep(0.1)
        
        angles[3] = 50
        smooth(servos, angles, 0.4, 15)
        #time.sleep(0.1)
    
    angles = old_angles.copy()
    smooth(servos, angles, 1, 25)
    time.sleep(0.8)
    return angles
    
#order = ['Red', 'White', 'Black']
def motion(order):
    # function for cube stacking motion of robotic arm 
    order = [w.capitalize() for w in order] # capitalize
    sleep_mode()
    time.sleep(1)
    #default()
    grid = 3.8
    space = 6.5 + 2.5
    pos = get_pos.run_colors() #dictionary of each color
    print("pos:",pos)

    kit.servo[5].angle = 180
    
    for i in range(len(order)):
        
        x_pos = pos[order[i]][0][0]
        z_pos = pos[order[i]][0][1] - 11.4
        ang = math.atan2(z_pos,x_pos)
        r = math.sqrt((x_pos**2) + (z_pos**2))
        
        #Calibration 
#         if z_pos < 12.7 and z_pos > 9:
#             space = space + 1.3
#             print("space added")
        if order[i] == "Red":
            r = r + 2.2 #1.6
            x_pos = r * math.cos(ang)
            z_pos = r * math.sin(ang)
        elif order[i] == "White":
            r = r + 2.4 #1.2
            x_pos = r * math.cos(ang)
            z_pos = r * math.sin(ang)
        elif order[i] == "Black":
            r = r + 1.5
            x_pos = r * math.cos(ang)
            z_pos = r * math.sin(ang)
            
        base, elbow, shoulder, wrist = inverse_k_3d((grid) + space + x_pos,0,(-1*(z_pos)),-40) #10,10,-40
        print(base,elbow, shoulder, wrist)
        servos = [0,1,2,4]
        target_angle = [base, elbow, shoulder, wrist]
        time.sleep(1)
        smooth(servos, target_angle)
        time.sleep(1)
        
        base, elbow, shoulder, wrist = inverse_k_3d((grid) + space + x_pos,-10,(-1*(z_pos)),-40) #10,10,-40
        print(base,elbow, shoulder, wrist)
        servos = [0,1,2,4]
        target_angle = [base, elbow, shoulder, wrist]
        time.sleep(1)
        smooth(servos, target_angle)

        kit.servo[5].angle = 72
        
        if i == 0:
            base, elbow, shoulder, wrist = inverse_k_3d((grid) + space + x_pos,0,(-1*(z_pos)),-40) #10,10,-40
            print(base,elbow, shoulder, wrist)
            servos = [0,1,2,4]
            target_angle = [base, elbow, shoulder, wrist]
            time.sleep(1)
            smooth(servos, target_angle)
            
            base, elbow, shoulder, wrist = inverse_k_3d(grid + space,0,-3.5*grid,-40) #10,10,-40
            print(base,elbow, shoulder, wrist)
            servos = [0,1,2,4]
            target_angle = [base, elbow, shoulder, wrist]
            time.sleep(1)
            smooth(servos, target_angle)
            
        else:
            base, elbow, shoulder, wrist = inverse_k_3d((grid) + space + x_pos,-8.5+ (8 * i),(-1*(z_pos)),-40) #10,10,-40
            print(base,elbow, shoulder, wrist)
            servos = [0,1,2,4]
            target_angle = [base, elbow, shoulder, wrist]
            time.sleep(1)
            smooth(servos, target_angle)
        # at drop off

            base, elbow, shoulder, wrist = inverse_k_3d(grid + space,-8.5 + (8 * i),-3.5*grid,-40) #10,10,-40
            print(base,elbow, shoulder, wrist)
            servos = [0,1,2,4]
            target_angle = [base, elbow, shoulder, wrist]
            time.sleep(1)
            smooth(servos, target_angle)
        
        
        base, elbow, shoulder, wrist = inverse_k_3d(grid + space,-8.5 + (4 * i),-3.5*grid,-40) #10,10,-40
        print(base,elbow, shoulder, wrist)
        servos = [0,1,2,4]
        target_angle = [base, elbow, shoulder, wrist, 180]
        time.sleep(0.4)
        smooth(servos, target_angle)

        kit.servo[5].angle = 180
        time.sleep(0.5)
        
        # DO NOT TOUCH
        base, elbow, shoulder, wrist = inverse_k_3d(grid + space,0 + (5 * i),-3.5*grid,-30) #10,10,-40
        print(base,elbow, shoulder, wrist)
        servos = [0,1,2,4]
        target_angle = [base, elbow, shoulder, wrist]
        time.sleep(1)
        smooth(servos, target_angle)


    sleep_mode()
    kit.servo[5].angle = 70

def awake2():
    #go to awake posititon
    servos = [0,1,2,3,4,5]
    angles = [90.0, 139.6061129850472, 111.9084708148627, 90, 67.30235782981549, 10]
    smooth(servos, angles, 0.7, 60)
    time.sleep(0.78)
    
    #shake head
    servos = [0,1,2,3,4,5]
    angles = [90.0, 139.6061129850472, 111.9084708148627, 90+80, 90, 170]
    smooth(servos, angles, 0.5, 36)
    #time.sleep(0.1)
    
    servos = [0,1,2,3,4,5]
    angles = [90.0, 139.6061129850472, 111.9084708148627, 90-87, 87, 20]
    smooth(servos, angles, 0.7, 50)
    
    #go to awake posititon
    servos = [0,1,2,3,4,5]
    angles = [90.0, 139.6061129850472, 111.9084708148627, 90, 67.30235782981549, 10]
    smooth(servos, angles, 0.5, 30)
    
    time.sleep(0.5)
    
    #up straight
    servos = [0,1,2,3,4,5]
    angles = [90.0, 100, 20, 90, 100, 160]
    smooth(servos, angles, 1.3, 60)
    time.sleep(0.3)
    
    #up straighter
    servos = [0,1,2,3,4,5]
    angles = [90.0, 90, 0, 90, 115, 10]
    smooth(servos, angles, 0.8, 50)
    time.sleep(0.3)
    
    #twist left
    servos = [0,1,2,3,4,5]
    angles = [150,93, 0, 30, 90, 30]
    smooth(servos, angles, 0.7, 60)
    #time.sleep(0.1)
    
    servos = [0,1,2,3,4,5]
    angles = [30,93, 0, 160, 90, 30]
    smooth(servos, angles, 0.7, 60)
    
    time.sleep(0.3)
    
    angles = [90.0, 139.6061129850472, 111.9084708148627, 90, 67.30235782981549, 10]
    smooth(servos, angles, 0.7, 60)


def awake():
    #go to awake posititon
    servos = [0,1,2,3,4,5]
    angles = [90.0, 139.6061129850472, 111.9084708148627, 90, 67.30235782981549, 10]
    smooth(servos, angles, 0.7, 60)
    time.sleep(0.78)
    
    #shake head
    servos = [0,1,2,3,4,5]
    angles = [90.0, 139.6061129850472, 111.9084708148627, 90+80, 90, 170]
    smooth(servos, angles, 0.5, 36)
    #time.sleep(0.1)
    
    servos = [0,1,2,3,4,5]
    angles = [90.0, 139.6061129850472, 111.9084708148627, 90-87, 87, 20]
    smooth(servos, angles, 0.7, 50)
    
    #go to awake posititon
    servos = [0,1,2,3,4,5]
    angles = [90.0, 139.6061129850472, 111.9084708148627, 90, 67.30235782981549, 10]
    smooth(servos, angles, 0.5, 30)
    
    time.sleep(0.5)

    #stretch
    servos = [1,2,3,4,5]
    angles = [90, 6, 30, 140, 180]
    smooth(servos, angles, 0.7, 60)
    time.sleep(0.2)
    
    angles = [93, 0, 150, 30, 50]
    smooth(servos, angles, 0.7, 50)
    #time.sleep(0.1)
    
    servos = [0,1,2,3,4,5]
    angles = [150,93, 0, 30, 90, 30]
    smooth(servos, angles, 0.7, 60)
    #time.sleep(0.1)
    
    servos = [0,1,2,3,4,5]
    angles = [30,93, 0, 160, 90, 30]
    smooth(servos, angles, 0.7, 60)
    
    time.sleep(0.3)
    
    angles = [90.0, 139.6061129850472, 111.9084708148627, 90, 67.30235782981549, 10]
    smooth(servos, angles, 0.7, 60)
    #time.sleep(0.1)


'''
# Pitch MOTION
for j in range(3):
    for i in range(-45, 40):
        elbow, shoulder, wrist = inverse_k(18,12,i) #10,10,-40
        print(elbow, shoulder, wrist)
        servos = [1,2,4]
        target_angle = [elbow, shoulder, wrist]
        time.sleep(0.03)
        kit.servo[1].angle = elbow
        kit.servo[2].angle = shoulder
        kit.servo[4].angle = wrist  

    for i in range(40, -45, -1):
        elbow, shoulder, wrist = inverse_k(18,12,i) #10,10,-40
        print(elbow, shoulder, wrist)
        servos = [1,2,4]
        target_angle = [elbow, shoulder, wrist]
        time.sleep(0.03)
        kit.servo[1].angle = elbow
        kit.servo[2].angle = shoulder
        kit.servo[4].angle = wrist
'''
