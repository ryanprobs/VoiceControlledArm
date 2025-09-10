import os
import sys
import subprocess

if "RUNNING_WITH_ALSA_FILTER" not in os.environ:
    os.environ["RUNNING_WITH_ALSA_FILTER"] = "1"
    cmd = [sys.executable] + sys.argv
    # Run the script and capture stderr
    result = subprocess.run(cmd, stderr=subprocess.PIPE, text=True)
    # Print all lines that don't contain ALSA
    for line in result.stderr.splitlines():
        if "ALSA" not in line:
            print(line, file=sys.stderr)
    sys.exit(0)

import speech_recognition as sr
import serial
from gtts import gTTS
import random
import time
import Robotic_arm_code as move
import stop_flag

# KEYWORD LISTS
colors = ['red', 'white', 'black']
tower_list = ['make a tower', 'tower', 'towel']

def say(words):
    tts = gTTS(words, lang='en')
    tts.save("speak.mp3")
    os.system("mpg123 speak.mp3")  # Make sure mpg123 is installed


def color_l():
    order = []
    #initiation
    r = sr.Recognizer()
    mic = sr.Microphone()
    print("Start talking!")
    
    # START LISTENING
    while True:
        order = []
        
        # MIC INPUT
        with mic as source:
            audio = r.listen(source)
        try:
            words = r.recognize_google(audio).lower()
            print(words)
            w_list = words.split()
            
            for i in range(len(w_list)):
                if w_list[i] in colors:
                    order.append(w_list[i])
            print("current order:", order)
            if len(order) == len(set(order)) and len(order) == 3:
                print("finished order:", order)
                return order

        except sr.UnknownValueError:
            time.sleep(0.5)   


def yes_or_no():
    #initiation
    r = sr.Recognizer()
    mic = sr.Microphone()
    print("Start talking!")
    
    # START LISTENING
    while True:
        
        # MIC INPUT
        with mic as source:
            audio = r.listen(source)
        try:
            words = r.recognize_google(audio).lower()
            print(words)
            if words == 'yes' or words == 'no':
                return words

        except sr.UnknownValueError:
            time.sleep(0.5)  


def start_stack():
    #initiation
    r = sr.Recognizer()
    mic = sr.Microphone()
    print("Start talking!")
    
    # START LISTENING
    while True:
        # MIC INPUT
        with mic as source:
            audio = r.listen(source)
        try:
            words = r.recognize_google(audio).lower()
            print(words)
            if 'start' in words:
                break

        except sr.UnknownValueError:
            time.sleep(0.5)


def mouth():
    
    #initiation
    r = sr.Recognizer()
    mic = sr.Microphone()
    print("Start talking!")
    
    # START LISTENING
    while True:

        # MIC INPUT
        with mic as source:
            audio = r.listen(source)
        try:
            words = r.recognize_google(audio).lower()
            print(words)
            return words
       
        except sr.UnknownValueError:
            time.sleep(0.5)


def start_listen():
    #key_a = {'wake up': wake}
    
    #initiation
    r = sr.Recognizer()
    mic = sr.Microphone()
    print("Start talking!")
    
    # START LISTENING
    while True:
        
        # MIC INPUT
        with mic as source:
            audio = r.listen(source)
        try:
            words = r.recognize_google(audio).lower()
            print(words)
            
            #goodmorning(words)
            if "wake up" in words:
                break
       
        except sr.UnknownValueError:
            time.sleep(0.5)


def main_listen():
    
    #initiation
    r = sr.Recognizer()
    mic = sr.Microphone()
    print("Start talking!")
    prev = time.time()
    slept = False
    
    # START LISTENING
    while True:
        # MIC INPUT
            
        with mic as source:
            audio = r.listen(source)
        try:
            words = r.recognize_google(audio).lower()
            print(words)
            
            if "hey robert" in words:
                #on_robert()
                prev = time.time()
                return 0            
            
            elif "hey rob" in words:
                #on_rob()
                prev = time.time()
                return 1
       
        except sr.UnknownValueError:
            time.sleep(0.5)
        
        rn = time.time()
        if rn - prev >= 10 and slept == False:
            move.sleep_mode()
            slept = True


def on_robert(client):
        #initiation
    r = sr.Recognizer()
    mic = sr.Microphone()
    print("robert mic on")
    
    prev = time.time()
    
    # START LISTENING
    while True:
        # MIC INPUT
        with mic as source:
            audio = r.listen(source)
        try:
            prompt = r.recognize_google(audio).lower()
            print(prompt)
            
            if prompt.lower() in ["quit", "exit", "bye"]:
                break
            
            if prompt.strip() != "":
                response = client.chat.completions.create(
                    model="gpt-4o-mini",  # fast + cheap model
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant."},
                        {"role": "user", "content": prompt}
                    ]
                )
                
                reply = say(response.choices[0].message.content)
                print("AI:", reply)
                prev = time.time()

        except sr.UnknownValueError:
            time.sleep(0.5)
        
        rn = time.time()
        if rn - prev >= 11:
            move.sleep_mode()
            print('exit robert, enter main')
            return None
    

def on_rob():
    #look for keywords
    # want it to: go back to sleep, follow my face and wave, stack the cubes, what's my name
    
    key_commands = {
        "sleep": 0,
        "follow my face": 1,
        "stack the cubes": 2,
        "name": 3,
        "turn off": 4
    }
    
    #initiation
    r = sr.Recognizer()
    mic = sr.Microphone()
    print("rob mic on")
    
    prev = time.time()
    
    # START LISTENING
    while True:
        # MIC INPUT
        with mic as source:
            audio = r.listen(source)
        try:
            words = r.recognize_google(audio).lower()
            print(words)
            
            for key, action in key_commands.items():
                if key in words:
                    return action
       
        except sr.UnknownValueError:
            time.sleep(0.5)
        
        rn = time.time()
        if rn - prev >= 11:
            move.sleep_mode()
            print('exit rob, enter main')
            return None


def wait_stop():
    r = sr.Recognizer()
    mic = sr.Microphone()
    print("Start talking!")
    
    prev = time.time()
    
    # START LISTENING
    while True:
        # MIC INPUT
        with mic as source:
            audio = r.listen(source)
        try:
            words = r.recognize_google(audio).lower()
            print(words)
            
            if 'stop' in words:
                stop_flag.stop_flag = True
                break
       
        except sr.UnknownValueError:
            time.sleep(0.5)
