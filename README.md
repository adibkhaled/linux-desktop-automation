# Linux Desktop Automation — Python UI Test Tools

This repository contains small tools and scripts used for automating and recording UI interactions on Linux desktops and for generating GitLab-based test reports.

The project contains two main areas:

- `test/` — UI recording and playback utilities used to capture mouse/keyboard actions and image-based searches for automated tests.
- `git_report/` — scripts used to gather commit/issue information from GitLab and generate test information reports (text and HTML) for reviewers.

This README documents what each script does, basic setup, configuration points and usage examples.

## Contents

- `test/record_vcenter.py` — interactive recorder and simple player for UI testcases (clicks, drag rectangles -> capture images, key presses, verify steps).
- `test/record.py` — small wrapper that starts an interactive recording session using `record_vcenter.py` and saves a new testcase folder with recorded files.
- `test/play.py` — runner for play (test) files. It can run a single testcase interactively or batch-run `regression` / `integration` folders.
- `git_report/common.py` — shared helpers for parsing commit/issue notes, connecting to GitLab and formatting test status.
- `git_report/test_info.py` — builds summaries and HTML/text outputs about test info availability for commits and authors.
- `git_report/send_report.py` — composes and sends email reports (overview/missing test info) and can create a GitLab wiki page for a release.
- `script/requirements.txt` — project Python dependencies (use this to install required packages).

## Quick overview of important scripts

### test/record_vcenter.py

- Record mouse clicks, drag regions (to capture screenshots) and keyboard events.
- Outputs a `*.play` file with commands like `CLICK x,y`, `SEARCH base-...png`, `PRESS Key` and `VERIFY N`.
- The recorder uses `pynput`, `pyautogui`, `mss` and `opencv-python` for capturing and replay.

Basic usage (recording):

1. Set your DISPLAY environment (the script already sets `DISPLAY=:0`) and run the script while interacting with the UI to produce `testcase.play` and captured images.

Playback usage (example):

1. Use the `play()` function by running a small wrapper or importing the module to execute a `.play` file. The script will perform clicks, keypresses and image-based waits.

Notes:
- Right-click during recording will write a `VERIFY` entry and stop the listener.
- Esc will stop keyboard listener while recording.


### test/record.py

- Small wrapper that asks for a testcase name, creates a folder, and starts the recording listeners from `record_vcenter.py`.
- Usage: run `test/record.py` and enter a testcase directory name when prompted. The script will create the folder, change into it, then listen for mouse and keyboard events and save a `testcase.play` and any captured images.

Notes and tips for recording:
- The recorder (`record_vcenter.py`) captures click coordinates and when you draw a rectangle it saves a cropped image (used later for image-search based waits).
- Right-click writes a `VERIFY` entry and stops recording; press Esc to stop keyboard listener.
- Ensure your working directory is writable and that screen-capture tools (mss/opencv) work under your DISPLAY.


### test/play.py

- Runner for recorded `.play` test files and for batch execution of `regression` and `integration` folders.
- Behavior summary:
	- If run with no arguments it will prompt for a testcase name, change into that folder, create a `report/` directory if missing, and run `testcase.play`.
	- If called with an argument `regression` or `integration` it will clear `report/error_images`, start the test report (via `report.vrep("start")`), iterate the folder and call `play()` on each file, then end the report.

Usage examples:

Interactive single testcase:

```bash
python3 test/play.py
# enter the testcase folder name when prompted (folder must contain testcase.play)
```

Batch run regression or integration folder:

```bash
python3 test/play.py regression
python3 test/play.py integration
```

### git_report/test_info.py

- Processes commit/issue details returned from GitLab, generates markdown and HTML reports for missing test information, and creates per-author reports.
- Offers a `main()` entry that can be wired in a cron job to run on specific days and call the reporting flow.

### git_report/send_report.py

- Uses `git_report/common.py` and `git_report/test_info.py` to prepare the final HTML/text reports and send them by SMTP.
- Configure `mailserver` and `sender_email` variables at the top of the file before using in your environment.

## Installation

Create a virtual environment and install required packages. The repository contains `script/requirements.txt` and `script/OS12_requirements.txt` for reference.

Example (macOS / Linux):

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r script/requirements.txt
```

Required modules used by the scripts include (not exhaustive):
- gitlab
- pyautogui
- pynput
- opencv-python (cv2)
- mss


## Contributing

If you'd like to extend these scripts:

- Keep changes small and focused.
- Add unit tests for parsing utilities under `git_report/` where practical.
- Update this README with any new dependencies or configuration options.


## License

See top-of-file copyright headers in the scripts. Keep license and copyright information consistent when redistributing.