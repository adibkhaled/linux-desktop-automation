#! /usr/bin/env python3
#
#  Copyright (c) 2024 Vimec Applied Vision Technology B.V.
#
"""
Runs UI actions (click, scroll, input, assert, wait) using pyautogui and pynput in vCenter
"""
import pathlib
import os
import sys
import time
import cv2
import mss
import mss.tools


# pyautogui and pynput should be imported after DISPLAY is defined (line 9),
# otherwise they will not work.
os.environ["DISPLAY"] = ":0"

import pyautogui
from pynput import mouse
from pynput import keyboard
import report

try:
    from PIL import Image
except ImportError:
    import Image
import pytesseract
from report import logging


def clean_dir():
    for file in os.listdir("."):
        if os.path.isfile(file) and file.endswith("play"):
            os.remove(file)
    for file in os.listdir("."):
        if os.path.isfile(file) and file.endswith("png"):
            os.remove(file)


def search_screen(image, precision=0.8):
    with mss.mss() as sct:
        # Select a valid monitor (1 if available, otherwise 0)
        monitor_index = 1 if len(sct.monitors) > 1 else 0
        monitor = sct.monitors[monitor_index]

        # Take screenshot using grab()
        sct_img = sct.grab(monitor)
        screenshot_path = "scrshot.png"
        mss.tools.to_png(sct_img.rgb, sct_img.size, output=screenshot_path)

    # Load screenshot and template
    img_scr = cv2.imread(screenshot_path, 0)
    template = cv2.imread(image, 0)

    # Clean up screenshot file
    if os.path.exists(screenshot_path):
        os.remove(screenshot_path)

    if template is None:
        raise FileNotFoundError(f"No image found to search screen for. {image}")

    # Match template
    res = cv2.matchTemplate(img_scr, template, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, max_loc = cv2.minMaxLoc(res)

    return max_loc if max_val >= precision else [-1, -1]


def check_dir(dir, image):
    if os.path.exists(dir):
        logging.info(f"{dir} folder found!")
        image = os.path.join(dir, image)
    else:
        logging.info(f"No {dir} folder found! Read from the current dir")
        image = image
    return image


def loop_screen(image, wait_time):
    image = check_dir("image", image)
    status = 1
    while wait_time > 0:
        pos = search_screen(image)
        if pos[0] == 0 and pos[1] == 0:
            logging.info("Not a correct image to search.")
            wait_time = 0
        elif pos[0] != -1:
            logging.info(f"Position : {pos[0]}, {pos[1]}")
            pyautogui.moveTo(pos[0], pos[1], 0.5)
            pyautogui.click()
            wait_time = 0
            status = 0
        else:
            logging.info(f"{image} not found yet, waiting...")
            time.sleep(0.5)
            wait_time -= 0.5
    if wait_time < 0.5 and pos[0] == -1:
        logging.info(f"\n{image} not found, Timed out..\n")
    return status


def create_rect(left_press, top_press, left_release, top_release):
    x = min(left_release, left_press)
    y = min(top_release, top_press)
    width = abs(left_release - left_press)
    height = abs(top_release - top_press)
    return x, y, width, height


def save_image(left_press, top_press, x, y):
    image_count = 0
    top_release = y
    left_release = x
    output = ""
    # Detecting dragging mouse and drawing a rectangular:
    if top_release != top_press and left_release != left_press:
        image_count += 1
        logging.info(
            f"Drawn {top_press} to {top_release} and {left_press} to {left_release}"
        )

        x = min(left_release, left_press)
        y = min(top_release, top_press)
        width = abs(left_release - left_press)
        height = abs(top_release - top_press)

        # Save an image of the dimensions user drawn.
        with mss.mss() as sct:
            monitor = {
                "count": image_count,
                "top": y,
                "left": x,
                "width": width,
                "height": height,
            }
            output = "base-{count}-{top}x{left}_{width}x{height}.png".format(**monitor)
            sct_img = sct.grab(monitor)
            mss.tools.to_png(sct_img.rgb, sct_img.size, output=output)
            return output


def save_image_for_player(top, left, width, height):
    with mss.mss() as sct:
        monitor = {"top": top, "left": left, "width": width, "height": height}
        output = "test-{top}x{left}_{width}x{height}.png".format(**monitor)
        sct_img = sct.grab(monitor)
        mss.tools.to_png(sct_img.rgb, sct_img.size, output=output)
        return output


# Used for detecting double click.
prev_click = time.time()

# Used for counting images to be saved.
IMAGE_COUNT = 0
OUTPUT_FILE = "testcase.play"
IS_PLAYING = 0

ms = mouse.Controller()
kb = keyboard.Controller()


def error_image(output):
    error_dir = "report/error_images"
    if not os.path.exists(error_dir):
        os.makedirs(error_dir)
    new_output_path = pathlib.Path(error_dir).joinpath(output)
    pathlib.Path(output).rename(new_output_path)
    return new_output_path


def get_coordinates_and_text_info(line):
    base = line.strip().split(" ")[1]
    top = int(base.split("-")[2].split("x")[0])
    left = int(base.split("-")[2].split("x")[1].split("_")[0])
    width = int(base.split("-")[2].split("x")[1].split("_")[1])
    height = int(base.split("-")[2].split("x")[2].split(".")[0])
    text_base = line.strip().split(":", 1)[1]
    return top, left, width, height, text_base


def assert_match(expected_text, status, failed_test, input_file):
    logging.info("Assert match!")
    logging.info(f"Actual and expected text is: {expected_text}")
    failed_test = "N"
    status = 1
    return status, failed_test, input_file


def assert_not_match(expected_text, actual_text, status, failed_test, input_file):
    logging.info("Assert not match!")
    logging.info(f"Actual text is-{expected_text}-but expected is-{actual_text}-")
    failed_test = "Y"
    status = 2
    return status, failed_test, input_file


def no_assert(status, failed_test, input_file):
    logging.info("No assertion found")
    failed_test = "N"
    status = 0
    return status, failed_test, input_file


# **************************************************** *******************************
# @function play(input_file)
# @parameter input_file
# @comment This function is read the .play file from regession folder
# @comment if conent has "Assert" then it will send a status to create a report
# @comment if conent has "Saerch" then go to loopScreen(image, wait_time) function to search text
# @comment if conent has "PRESS" to kb press and release
# @comment if conent has "CLICK" to ms press and release
# @comment if conent has "SCROLL" to ms scroll
# @comment if conent has "SLEEP" to sleep
# **************************************************** ********************************
def perform_search(i):
    search_key = i.strip().split(" ")[1]
    logging.info(search_key)
    status = loop_screen(search_key, 2)
    if status == 0:
        return True
    return False


def perform_sleep(i):
    time.sleep(int(i.strip().split(" ")[1]))


def perform_unknown(i):
    logging.info("Unknown command, exiting." + str(i))
    sys.exit()


def perform_key(i):
    if "." not in i:
        current_key = i.strip().split(" ")[2]
        kb.press(current_key)
        kb.release(current_key)
    else:
        current_key = i.strip()
        key_to_press = getattr(keyboard.Key, str(current_key.split(".")[1]))
        kb.press(key_to_press)
        kb.release(key_to_press)


def perform_click(i):
    click = (
        int(i.strip().split(",")[0].split(" ")[1]),
        int(i.strip().split(",")[1]),
    )
    time.sleep(0.1)
    ms.position = click
    ms.press(mouse.Button.left)
    ms.release(mouse.Button.left)
    time.sleep(0.3)


def perform_assert(i, status, failed_test, input_file):
    top, left, width, height, text_base = get_coordinates_and_text_info(i)
    output = save_image_for_player(top, left, width, height)
    text = pytesseract.image_to_string(Image.open(output))
    text_expected = text.strip()

    if text_base == text_expected:
        os.remove(output)
        return assert_match(text_expected, status, failed_test, input_file)
    elif text_base != text_expected:
        input_file = error_image(output)
        return assert_not_match(
            text_expected, text_base, status, failed_test, input_file
        )
    else:
        return no_assert(status, failed_test, input_file)


def perform_scroll(i):
    scroll = (
        int(i.strip().split(",")[0].split(" ")[1]),
        int(i.strip().split(",")[1]),
    )
    ms.scroll(scroll[0], scroll[1])


def perform_select(i):
    image = "image/" + str(i.strip().split(" ")[1])
    if pyautogui.locateAllOnScreen(image, grayscale=True, confidence=0.9) is not None:
        logging.info(image)
        pyautogui.click(image)


def perform_wait(i):
    image_file = "image/" + str(i.strip().split(" ")[1])
    logging.info(image_file)
    t_end = time.time() + 60 * 2

    while time.time() < t_end:
        try:
            logging.info(
                f"Found the alert message: {pyautogui.locateCenterOnScreen(image_file)}"
            )
            break
        except pyautogui.ImageNotFoundException:
            logging.info("No alert message found")
            time.sleep(5)
        if time.time() >= t_end:
            break


def perform_cmd(i):
    cmd = str(i.strip().split(":")[1])
    os.system(f"{cmd}")


def perform_hotkey(i):
    hkey = str(i.strip().split("+")[0].split(" ")[1])
    pyautogui.hotkey(hkey, str(i.strip().split("+")[1]))


def perform_verify_cmd(i, status, failed_test, input_file):
    cmd = str(i.strip().split(":")[1])
    text_expected = str(i.strip().split(":")[3])
    text_base = os.popen(f"{cmd}").read()

    if text_expected.strip() in text_base:
        return assert_match(text_expected, status, failed_test, input_file)
    else:
        output = save_image_for_player(1, 1, 1, 1)  # Dummy image
        input_file = error_image(output)
        try:
            os.remove(output)
        except FileNotFoundError:
            pass
        return assert_not_match(
            text_expected, text_base, status, failed_test, input_file
        )


def play(input_file):
    status = 0
    failed_test = 0
    global IS_PLAYING
    report.vrep_ltg("start", status, input_file)
    actions = [
        ("SEARCH", perform_search),
        ("ASSERT", perform_assert),
        ("PRESS", perform_key),
        ("CLICK", perform_click),
        ("SCROLL", perform_scroll),
        ("SLEEP", perform_sleep),
        ("SELECT", perform_select),
        ("WAIT", perform_wait),
        ("VERIFY_CMD", perform_verify_cmd),
        ("CMD", perform_cmd),
        ("HOTKEY", perform_hotkey),
    ]

    with open(input_file, "r", encoding="utf-8") as file:
        content = file.readlines()

    for line in content:
        IS_PLAYING = 1
        for keyword, function in actions:
            if keyword in line:
                if keyword in ["ASSERT", "VERIFY_CMD"]:
                    status, failed_test, input_file = function(
                        line, status, failed_test, input_file
                    )
                    break
                else:
                    function(line)
                    break
        else:
            perform_unknown(line)

    if failed_test == "Y":
        report.vrep_ltg("end", 2, input_file)
    else:
        report.vrep_ltg("end", status, input_file)
