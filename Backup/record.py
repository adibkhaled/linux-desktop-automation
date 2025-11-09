#!/usr/bin/env python3
# 
#  Copyright (c) 2024 Vimec Applied Vision Technology B.V.
# 

from record_user import *
import os

test_folder = input("Please enter testcase name: ")
os.mkdir(test_folder)
os.chdir(test_folder)


def main():
    #global output_file

    clean_dir()

    k_listener = keyboard.Listener(on_press=on_keypress, on_release=on_keyrelease)
    with mouse.Listener(on_move=on_move, on_click=on_click, on_scroll=on_scroll) as listener:
        k_listener.start()
        listener.join()

    time.sleep(2)
    print("\nListeners terminated,")
    print("Now will play the recorded steps..\n")

    if os.path.isfile(output_file):
        play(output_file)
    else:
        print("No play file found.")

    print("Record is done")


if __name__ == '__main__':
    main()
