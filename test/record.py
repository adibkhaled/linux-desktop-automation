#! /usr/bin/env python3
# 
#  Copyright (c) 2024 Vimec Applied Vision Technology B.V.
# 
"""
To record auto-test test cases.
"""

import os
from record_vcenter import *
import record_vcenter

test_folder = input("Please enter testcase name to record: ")
os.mkdir(test_folder)
os.chdir(test_folder)


def main():
    record_vcenter.clean_dir()

    k_listener = keyboard.Listener(on_press=on_keypress, on_release=on_keyrelease)
    with mouse.Listener(
        on_move=on_move, on_click=on_click, on_scroll=on_scroll
    ) as listener:
        k_listener.start()
        listener.join()


if __name__ == "__main__":
    main()
