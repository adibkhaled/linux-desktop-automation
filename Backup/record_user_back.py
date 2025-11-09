#!/usr/bin/env python3
# 
#  Copyright (c) 2024 Vimec Applied Vision Technology B.V.
# 

import struct
import cv2
import os
import sys
import time
import mss
import mss.tools
import tkinter as tk

import numpy as np

os.environ['DISPLAY'] = ':0'
os.chdir('/home/vimec/tests')

# pyautogui and pynput should be imported after DISPLAY is defined (line 9),
# otherwise they will not work.

import pyautogui
from pynput import mouse
from pynput import keyboard


def clean_dir():          
    for file in os.listdir("."):
        if os.path.isfile(file) and file.endswith("play"):
            os.remove(file) 
    for file in os.listdir("."):
        if os.path.isfile(file) and file.endswith("png"):
            os.remove(file) 


def searchScreen(image, precision=0.8):
    with mss.mss() as sct:
        filename = sct.shot(output='scrshot.png')

        img_scr = cv2.imread(filename, 0)
        template = cv2.imread(image, 0)
        if template is None:
            raise FileNotFoundError('No image found to search screen for. {}'.format(image))

        res = cv2.matchTemplate(img_scr, template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
        if max_val < precision:
            return [-1, -1]
        return max_loc


def loopScreen(image, wait_time):
    status = 1
    while wait_time > 0:
        pos = searchScreen(image)
        if pos[0] == 0 and pos[1] == 0:
            print("Not a correct image to search.")
            wait_time = 0

        elif pos[0] != -1:
            print("position : ", pos[0], pos[1])
            pyautogui.moveTo(pos[0], pos[1], 0.5)
            pyautogui.click()
            wait_time = 0
            status = 0

        else:
            print(f"{image} not found yet, waiting.")
            time.sleep(0.5)
            wait_time -= 0.5
    if wait_time < 0.5 and pos[0] == -1:
        print(f"\n{image} not found, Timed out..\n")   
    return status


def create_rect(left_press, top_press, left_release, top_release):
    x = min(left_release, left_press)
    y = min(top_release, top_press)
    width = abs(left_release - left_press)
    height = abs(top_release - top_press)

    return x, y, width, height


def on_move(x, y):
    pass
    # print ("Mouse moved to ({0}, {1})".format(x, y))


# Used for detecting double click.
prev_click = time.time()

# Used for counting images to be saved.
image_count = 0
output_file = "testcase.play"
is_playing = 0


def on_click(x, y, button, pressed):
    global prev_click
    global top_press
    global left_press
    global image_count

    double_click = False

    if pressed:
        print('Mouse clicked at ({0}, {1}) with {2}'.format(x, y, button))

    # When left button is pressed:    
    if button == mouse.Button.left and pressed:
        top_press = y
        left_press = x
        current_click = time.time()
        click_diff = current_click - prev_click
        if click_diff < 0.15:
            double_click = True
        prev_click = current_click    

    # When left button is released:    
    if button == mouse.Button.left and not pressed:
        click_data = "CLICK " + str(x)+","+str(y)+"\n"
        with open(output_file, 'a') as file:
            file.write(click_data)

        top_release = y
        left_release = x
        
        # Detecting dragging mouse and drawing a rectangular:
        if top_release != top_press and left_release != left_press:
            image_count += 1
            print("Drawn {} to {} and {} to {}".format
                (top_press, top_release, left_press, left_release))

            x, y, width, height =\
                create_rect(left_press, top_press, left_release, top_release)

            # Save an image of the dimensions user drawn.
            with mss.mss() as sct:
                monitor = {"count": image_count, "top": y, "left": x, "width": width, "height": height}
                output = "base-{count}-{top}x{left}_{width}x{height}.png".format(**monitor)
                sct_img = sct.grab(monitor)
                mss.tools.to_png(sct_img.rgb, sct_img.size, output=output)

            image_data = "SEARCH "+output+"\n"
            with open(output_file, 'a') as file:
                file.write(image_data)
    
    if double_click:
        print("Double Clicked..>>>>>>>")
        # create_window(x,y)

    if button == mouse.Button.right:
        # pyautogui.confirm(text='', title='', buttons=['OK', 'Cancel'])
        
        with open(output_file, 'a') as file:
            file.write("VERIFY "+str(image_count)+"\n")
        return False


def on_scroll(x, y, dx, dy):
    print('Mouse scrolled at ({0}, {1})({2}, {3})'.format(x, y, dx, dy))


def on_keypress(key):
    try:
        print('alphanumeric key {0} pressed'.format(
            key.char))
    except AttributeError:
        print('special key {0} pressed'.format(
            key))


def on_keyrelease(key):
    global is_playing
    print('{0} released'.format(
        key))
    # If normal character, not a special character, ex a,b,c, etc
    if hasattr(key, 'char'):
        key_data = "PRESS Key " + key.char + "\n"
    # If a special character: ex shift, tab, backspace, etc
    else:
        key_data = "PRESS " + str(key) + "\n"
    with open(output_file, 'a') as file:
        if not is_playing:
            file.write(key_data)

    if key == keyboard.Key.esc:
        # Stop listener
        return False