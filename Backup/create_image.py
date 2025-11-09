#!/usr/bin/env python3
# 
#  Copyright (c) 2024 Vimec Applied Vision Technology B.V.
# 

import pyautogui


im = pyautogui.screenshot(region=(521, 284, 605, 18))
im.save(r"screenshot.png")
print(pyautogui.locateCenterOnScreen("screenshot.png", confidence=0.9))
pyautogui.click("screenshot.png")
