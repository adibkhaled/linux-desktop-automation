#! /usr/bin/env python3
# 
#  Copyright (c) 2024 Vimec Applied Vision Technology B.V.
# 
"""
Report script to generate the auto-test HTML report
"""

import os
import datetime
import logging

# Get the time from system and strored it in the report page
t = datetime.datetime.now()
gStartDatumTijd = t.strftime("%Y-%m-%d %H:%M:%S")
GFILE_NAME = ""
GIMG_TAG = 1
GTIME = t

TEST_TOTAL = 0
TEST_OK = 0
TEST_NOK = 0
TEST_NO = 0

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("v-center-testing.log", "w", "utf-8"),
        logging.StreamHandler(),
    ],
)

RESPORT_DIR = "report/"
if not os.path.exists(RESPORT_DIR):
    os.makedirs(RESPORT_DIR)

# **************************************************** ********************************
# @function vwrite_totals(value)
# @parameter value
# @comment Write passed value when generating report.
# **************************************************** ********************************
def vwrite_totals():
    with open(RESPORT_DIR + str(GFILE_NAME) + "", "r", encoding='utf-8') as file:
        # read a list of lines into data
        data = file.readlines()
    data[8] = (
        "<tr class='testTOT'><td>Total</td><td> " + str(TEST_TOTAL) + " </td></tr>\n"
    )
    data[9] = "<tr class='testOK'><td>OK</td><td> " + str(TEST_OK) + " </td></tr>\n"
    data[10] = "<tr class='testNOK'><td>NOK</td><td> " + str(TEST_NOK) + " </td></tr>\n"
    data[11] = (
        "<tr class='testNO'><td>NO Assert</td><td> " + str(TEST_NO) + " </td></tr>\n"
    )
    # and write everything back
    with open(RESPORT_DIR + str(GFILE_NAME) + "", "w", encoding='utf-8') as file:
        file.writelines(data)
        file.close()


def v_write_file(value):
    report = open(RESPORT_DIR + str(GFILE_NAME) + "", "a", encoding='utf-8')
    report.write(str(value))
    report.close()


# **************************************************** ********************************
# @function set_start_time(time), get_start_time()
# @parameter time
# @comment set time and get time
# **************************************************** ********************************
def set_start_time(time):
    global GTIME
    GTIME = time


def get_start_time():
    return GTIME


# **************************************************** ********************************
# @function duration_cal_seconds(time_start,time_end)
# @parameter time_start, time_end
# **************************************************** ********************************
def duration_cal_seconds(time_start, time_end):
    duration_time = time_start - time_end
    mins = int(round(duration_time.total_seconds(), 0))
    return mins


# **************************************************** ********************************
# @function vrep(rep)
# @parameter rep
# @comment rep = 'start' : Start writing html code when generating report.
# @comment rep = 'end' : Write end html code when generating report.
# **************************************************** ********************************
def vrep(rep, test_folder):
    logging.info("File starting: %s", test_folder)
    if rep == "start":
        global GFILE_NAME
        global TEST_TOTAL
        global TEST_OK
        global TEST_NOK
        global TEST_NO

        TEST_TOTAL = 0
        TEST_OK = 0
        TEST_NOK = 0
        TEST_NO = 0

        GFILE_NAME = (
            "vReport_"
            + str(t.strftime("%Y.%m%d.%H%M.%S"))
            + "."
            + str(test_folder)
            + ".html"
        )

        v_write_file("<HTML>\n<HEAD><META http-equiv='Content-Type' content='text/html; charset=UTF-8'/><TITLE>Auto Test Report</TITLE>\n")
        v_write_file('<style>td{vertical-align:top;padding:3px}body{font-family:"Segoe UI", Frutiger, "Frutiger Linotype", "Dejavu Sans", "Helvetica Neue", Arial, sans-serif}table{border-collapse:collapse}table,th,td{border:1px solid black}font{margin-left:3px;font-family:Consolas,"Andale Mono WT","Andale Mono","Bitstream Vera Sans Mono","Nimbus Mono L",Monaco,"Courier New",monospace;line-height:15px}img{margin-top:5px}font.mtsHeader {font-family: inherit}table.envInfo{margin-bottom: 10px}.testOK td{background-color:#BBF54A}.testNOK td{background-color:#FF5933}.testNO td{background-color:#E2E2E2}.testTOT td{font-weight:bold}.envInfo td:first-child,.testTOT td:first-child{width:100px}</style>\n')
        v_write_file("</HEAD>\n<BODY>\n")
        v_write_file("<BR/><H2>Test Report</H2>\n")
        v_write_file("<TABLE border='1' style='font-size:11px;' class='envInfo'>")
        v_write_file(
            "<TR><TD> Start date</TD><TD> " + str(gStartDatumTijd) + "</TD></TR>"
        )
        v_write_file("<TR><TD> Test </TD><TD> " + str(test_folder) + "</TD></TR>")

        v_write_file("</TABLE>\n")

        v_write_file("<table  border='1' style='font-size:11px;' class='envInfo'>\n")
        v_write_file(
            "<tr class='testTOT'><td>Totaal</td><td> "
            + str(TEST_TOTAL)
            + " </td></tr>\n"
        )
        v_write_file(
            "<tr class='testOK'><td>OK</td><td> " + str(TEST_OK) + " </td></tr>\n"
        )
        v_write_file(
            "<tr class='testNOK'><td>NOK</td><td> " + str(TEST_NOK) + " </td></tr>\n"
        )
        v_write_file(
            "<tr class='testNO'><td>NO Assert</td><td> " + str(TEST_NO) + " </td></tr>\n"
        )
        v_write_file("</table>\n")
        v_write_file(
            "<TABLE border='1' style='font-size:11px;' width='100%' cellpadding='0' cellspacing='0'>\n"
        )
        v_write_file(
            "<TABLE border='1' style='font-size:11px;' width='100%' cellpadding='0' cellspacing='0'>\n"
        )
        v_write_file(
            "<TR><TH > Test File Name </TH><TH> Start Test Time </TH><TH> Duration of Test </TH><TH> Result(s)</TH><TH> Screenshot </TH></TR>"
        )

    if rep == "end":
        v_write_file("</TABLE>\n</BODY>\n</HTML>\n")
        logging.info("@@@@@@@@@@@ Done report @@@@@@@@@@@@")


# **************************************************** *******************************
# @function vrep_ltg(rep,ftg_status,test_folder)
# @parameter rep start end
# @parameter ftg_status
# @parameter test_folder
# @comment This function is called with rep='start' at the beginning of a readline and test_folder name and test start_time are written.
# @comment This function is called with rep='end' at the end of a readline and the ftg_status(testcase status) is written.
# @comment If ftg_status = 0 "NO" with html code is written out. This is used which test cases does not have Assertion.
# @comment If ftg_status = 1 "OK" with html code is written out.
# @comment If ftg_status = 2 "NOK" with html code is written out.
# **************************************************** ********************************
def vrep_ltg(rep, ftg_status, test_folder):
    global GIMG_TAG
    global TEST_TOTAL
    global TEST_OK
    global TEST_NOK
    global TEST_NO
    if rep == "start":
        GIMG_TAG = 1
        v_write_file("<TR>\n")
        dt_start = datetime.datetime.now()
        set_start_time(dt_start)
        _dt = dt_start.strftime("%d-%m-%Y %H:%M:%S")
        v_write_file("<TD width='40%' title='Testcase'>" + str(test_folder) + "</TD>\n")
        v_write_file("<TD width='20%' title='time'>" + str(_dt) + "</TD>\n")

    if rep == "end":
        TEST_TOTAL = TEST_TOTAL + 1
        img_src = '<img src="../' + str(test_folder) + '">'
        dt_end = datetime.datetime.now()
        v_write_file(
            "<TD width= '20%' title='Seconds:"
            + str(duration_cal_seconds(dt_end, get_start_time()))
            + "' >"
            + str(duration_cal_seconds(dt_end, get_start_time()))
            + "</TD>\n"
        )
        if ftg_status == 1:
            v_write_file("<TD width='20%' bgcolor='#CCFF33'>OK</a></TD>\n")
            v_write_file("<TD width='20%'>" "</TD>\n")
            TEST_OK = TEST_OK + 1
            logging.info("### %s ### is PASS!!", test_folder)
        elif ftg_status == 2:
            v_write_file("<TD width='20%' bgcolor='#FF3333'>NOK</a></TD>\n")
            v_write_file("<TD width='20%'>" + img_src + "</img></TD>\n")
            TEST_NOK = TEST_NOK + 1
            logging.info("### %s ### is FAIL!!", test_folder)
        elif ftg_status == 0:
            v_write_file("<TD width='20%' bgcolor='#FFFFFF'>NO</a></TD>\n")
            v_write_file("<TD width='20%'>" "</TD>\n")
            TEST_NO = TEST_NO + 1
            logging.info("### %s ### is PASS without assertion!" , test_folder)

        v_write_file("</TR>\n")
        vwrite_totals()
