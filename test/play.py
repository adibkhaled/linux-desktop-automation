#! /usr/bin/env python3
#
#  Copyright (c) 2024 Vimec Applied Vision Technology B.V.
#
"""
Start the auto-test script to run all regression and integration play files.
"""

import os
import traceback
import sys
from record_user import *


sys.path.append("../")


def release_run_test(file_folder):
    if file_folder:
        logging.info("The folder:" + file_folder)
        files = os.listdir(file_folder)
        files = sorted(files, key=lambda x: str(os.path.splitext(x)[0]))
        for filename in files:
            file_path = os.path.join(file_folder, filename)
            logging.info(f"file name is: {file_path}")
            play(file_path)


def clear_error_image(folder_path):
    if os.path.exists(folder_path):
        image_dir = os.listdir(folder_path)
        for images in image_dir:
            if images.endswith(".png"):
                os.remove(os.path.join(folder_path, images))


def make_dir_run_test():
    logging.info("### Test Started!! ### ")
    test_folder = input("Please enter testcase name: ")
    os.chdir(test_folder)
    if not os.path.exists("report"):
        os.makedirs("report")
    report.vrep("start", test_folder)
    play("testcase.play")
    report.vrep("end", test_folder)


def main():
    if len(sys.argv) > 1:
        test_folder = sys.argv[1]
        if test_folder.lower() in ["regression", "integration"]:
            clear_error_image("report/error_images")
            report.vrep("start", test_folder)
            release_run_test(test_folder)
            report.vrep("end", test_folder)
        else:
            logging.info("Please add regression as a file path")
    else:
        make_dir_run_test()


if __name__ == "__main__":
    logging.info("@@@ Start Regression testing @@@@")
    try:
        exit(main())
    except KeyboardInterrupt:
        pass
    except Exception as e:
        logging.debug(e, exc_info=True)
        traceback.print_exc(file=sys.stdout)
    sys.exit(1)
