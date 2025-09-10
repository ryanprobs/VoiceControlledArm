import computer_vision_chess as get_pos
import computer_vision_eye as eye
import speech_recognition_test as talk
import Robotic_arm_code as move
import threading
import time
import face_DETECTION as scan
import random
import os
from openai import OpenAI

# Grab API key from environment variable
client = OpenAI(api_key="place_your_own_api_here")

def start_up():
    print("Running startup...")
    #move.default()
    #time.sleep(1.5)
    
    #move.awake2() # parameter to continue after stretch

words = {'n': None}
def listen_yn():
    words['n'] = talk.yes_or_no()
    
say_name = {'n': None}
def l_name():
    say_name['n'] = talk.mouth()

which = {'n': None}
def rob_or_robert():
    which['n'] = talk.main_listen()

order = {'n':None}
def find_order():
    order['n'] = talk.color_l()


if __name__ == "__main__":
    move.default()
    time.sleep(1.6)
    move.sleep_mode()
    talk.start_listen()
    
    start_up()

    move.smooth([0,1,2,3,4,5],[90.0, 139.6061129850472, 111.9084708148627, 90, 67.30235782981549, 10], 0.7, 20)
    print('done startup')
    time.sleep(1)
    
    #initiate scanning... look for "RYAN"
    name, angles, result = scan.follow_faces(True, True) #recognition, stop
    
    #if face is found and recognized
    if result == True:
        voice = threading.Thread(target=talk.say, args=(f"Hi {name}, how can I help you?",))
        mouth = threading.Thread(target=move.mouth_hi, args=(angles,3,))
        voice.start()
        mouth.start()
        mouth.join()
        voice.join()
    
    elif result == None:
        voice = threading.Thread(target=talk.say, args=(f"Can't find your face so ima go back to sleep, byeeeeeeeeeeeee.",))
        mouth = threading.Thread(target=move.mouth_hi, args=(angles,5,))
        voice.start()
        mouth.start()
        mouth.join()
        voice.join()
        move.sleep_mode()
    # if face is found but not recognized
    elif result == False:
        speeches = ["I'm not sure I know you yet. Would you like me to remember you for next time?",
                  "Hmm... I don't recognize your face. want me to save you in my memory?"]
        speech = speeches[random.randint(0,len(speeches)-1)]
        #words = talk.yes_or_no
        voice = threading.Thread(target=talk.say, args=(speech,))
        mouth = threading.Thread(target=move.mouth_hi, args=(angles,6,))
        listen_t = threading.Thread(target=listen_yn, args=())
        voice.start()
        mouth.start()
        voice.join() #wait till it finishes speaking then start listening
        mouth.join()
        listen_t.start()
        listen_t.join()
        
        print("word:", words)
        if words['n'] == 'yes':
            speech = "Yayy yayy yayyyy, What is your name?"
            voice = threading.Thread(target=talk.say, args=(speech,))
            mouth = threading.Thread(target=move.mouth_hi, args=(angles,3,))
            listen = threading.Thread(target=l_name, args=())
            voice.start()
            mouth.start()
            voice.join() #wait till it finishes speaking then start listening
            listen.start()
            listen.join()
            
            print(say_name['n'])
            
            time.sleep(0.5)
            speech = "Okay,now enter 's' to take the picture and enter 'q' once youre done taking at least 5 pictures!"
            mouth = threading.Thread(target=move.mouth_hi, args=(angles,7,))
            voice = threading.Thread(target=talk.say, args=(speech,))
            voice.start()
            mouth.start()
            #mouth.join()
            #voice.join()
            
            
            eye.save_face(say_name['n'])#still in progress
            
            time.sleep(0.5)
            speech = f"Thanks, {say_name['n']}. Your face has been recorded!!!"
            mouth = threading.Thread(target=move.mouth_hi, args=(angles,4,))
            voice = threading.Thread(target=talk.say, args=(speech,))
            voice.start()
            mouth.start()
            
        else:
            speech = "Okay, no pictures then"
            mouth = threading.Thread(target=move.mouth_hi, args=(angles,3,))
            voice = threading.Thread(target=talk.say, args=(speech,))
            voice.start()
            mouth.start()
            mouth.join()
    # done with start ups, now MAIN
    # always listen, follow face for maybe a minute
    off = False
    while True:
        if off == True:
            break
        listen = threading.Thread(target=rob_or_robert, args=())
        listen.start()
        listen.join()
        
        angles = [90.0, 139.6061129850472, 111.9084708148627, 90, 67.30235782981549, 10]
        move.smooth([0,1,2,3,4,5],angles, 0.7, 20)

        #angles = scan.follow_faces(False, True)#recognition, stop
        l = ['Robert', 'Rob']
        print(l[which['n']], 'Activated')
        if which['n'] == 1: #rob
            on = True
            command = talk.on_rob()
            while on:
                #do the command
                if command == 0: #go to sleep
                    speech = f"Goodnight, {name}"
                    mouth = threading.Thread(target=move.mouth_hi, args=(angles,2,))
                    voice = threading.Thread(target=talk.say, args=(speech,))
                    voice.start()
                    mouth.start()
                    voice.join()
                    move.sleep_mode()
                    on = False
                    
                    
                    
                elif command == 1: # follow face
                    speech = "Sure thing"
                    mouth = threading.Thread(target=move.mouth_hi, args=(angles,1,))
                    voice = threading.Thread(target=talk.say, args=(speech,))
                    voice.start()
                    mouth.start()
                    voice.join()
                    
                    angles = scan.follow_faces(False, False)
                    angles = [90.0, 139.6061129850472, 111.9084708148627, 90, 67.30235782981549, 10]
                    move.smooth([0,1,2,3,4,5],angles, 0.7, 20)
                    
                elif command == 2: #stack them cubes
                    speech = "can't really say no can I... Please kindly name the order."
                    mouth = threading.Thread(target=move.mouth_hi, args=(angles,6,))
                    voice = threading.Thread(target=talk.say, args=(speech,))
                    listen_t = threading.Thread(target=find_order, args=())
                    voice.start()
                    mouth.start()
                    voice.join()
                    mouth.join()
                    listen_t.start() #get the color order
                    listen_t.join()
                    
                    print("UPDATED ORDER:", order['n'])
                    
                    speech = "Got it, now set me up and say, start!"
                    mouth = threading.Thread(target=move.mouth_hi, args=(angles,5,))
                    voice = threading.Thread(target=talk.say, args=(speech,))
                    listen_t = threading.Thread(target=talk.start_stack, args=())
                    voice.start()
                    mouth.start()
                    voice.join()
                    mouth.join()
                    listen_t.start() #get the color order
                    listen_t.join()
                
                    move.motion(order['n'])
                    on = False
                
                elif command == 3: # what's my name
                    speech = "Hmmm, let's see!"
                    mouth = threading.Thread(target=move.mouth_hi, args=(angles,2,))
                    voice = threading.Thread(target=talk.say, args=(speech,))
                    voice.start()
                    mouth.start()
                    mouth.join()
                    voice.join()
                
                    name, angles, result = scan.follow_faces(True, True) #recognition, stop

                    if result == True:
                        voice = threading.Thread(target=talk.say, args=(f"Ah! your name is {name}",))
                        mouth = threading.Thread(target=move.mouth_hi, args=(angles,3,))
                        #listen_t = threading.Thread(target=listen, args=())
                        voice.start()
                        mouth.start()
                        voice.join()
                        mouth.join()
                    
                    elif result == None:
                        voice = threading.Thread(target=talk.say, args=(f"Can't find your face so ima go back to sleep, byeee e e.",))
                        mouth = threading.Thread(target=move.mouth_hi, args=(angles,5,))
                        voice.start()
                        mouth.start()
                        voice.join()
                        mouth.join()
                        time.sleep(0.5)
                        move.sleep_mode()
                        on = False
                    
                    # if face is found but not recognized
                    elif result == False:
                        speeches = ["I'm not sure I know you yet. Would you like me to remember you for next time?",
                                  "Hmm... I don't recognize your face. want me to save you in my memory?"]
                        speech = speeches[random.randint(0,len(speeches)-1)]
                        #words = talk.yes_or_no
                        voice = threading.Thread(target=talk.say, args=(speech,))
                        mouth = threading.Thread(target=move.mouth_hi, args=(angles,6,))
                        listen_t = threading.Thread(target=listen_yn, args=())
                        voice.start()
                        mouth.start()
                        voice.join() #wait till it finishes speaking then start listening
                        mouth.join()
                        listen_t.start()
                        listen_t.join()
                        
                        print("word:", words)
                        if words['n'] == 'yes':
                            speech = "Yayy yayy yayyyy, What is your name?"
                            voice = threading.Thread(target=talk.say, args=(speech,))
                            mouth = threading.Thread(target=move.mouth_hi, args=(angles,3,))
                            listen = threading.Thread(target=l_name, args=())
                            voice.start()
                            mouth.start()
                            voice.join() #wait till it finishes speaking then start listening
                            mouth.join()
                            listen.start()
                            listen.join()
                            
                            print(say_name['n'])
                            
                            time.sleep(0.5)
                            speech = "Okay,now enter 's' to take the picture and enter 'q' once youre done taking at least 5 pictures!"
                            mouth = threading.Thread(target=move.mouth_hi, args=(angles,7,))
                            voice = threading.Thread(target=talk.say, args=(speech,))
                            voice.start()
                            mouth.start()
                            
                            
                            eye.save_face(say_name['n'])#still in progress
                            
                            time.sleep(0.5)
                            speech = f"Thanks, {say_name['n']}. Your face has been recorded!!!"
                            mouth = threading.Thread(target=move.mouth_hi, args=(angles,4,))
                            voice = threading.Thread(target=talk.say, args=(speech,))
                            voice.start()
                            mouth.start()
                            voice.join()
                            mouth.join()
                            
                        else:
                            speech = "Okay, no pictures then"
                            mouth = threading.Thread(target=move.mouth_hi, args=(angles,3,))
                            voice = threading.Thread(target=talk.say, args=(speech,))
                            voice.start()
                            mouth.start()
                            mouth.join()
                            voice.join()
                                  
                elif command == 4:
                    print("Turning off...")
                    move.sleep_mode()
                    off = True
                    break
                else: # took too long, sleep, go out of on_rob(), into main
                    on = False
                    break
                if on:
                    command = talk.on_rob()
            

        elif which['n'] == 0: #robert
            on = True
            command = talk.on_robert(client)
