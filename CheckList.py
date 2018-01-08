#!/usr/bin/python2
import Define
from datetime import datetime

#define check list
#title,subtitle,check_method,argvs,judge_rule

def is_consistent_fingerprint(reports):
    fp=""
    for report in reports:
        if fp =="":
            fp = report.test_result.sw.build_fingerprint
        elif fp != report.test_result.sw.build_fingerprint:
            return 0
    return 1

def is_valid_fingerprint_format(fingerprint):
    return 1

def is_valid_clientId(fake):
    return -1

def VTS_AOSP_special_check1(reports):
    for report in reports:
        if report.test_result.suite_plan == "vts" or report.test_result.suite_plan == "cts-reference-aosp":
            if report.test_result.sw.build_manufacturer == report.device_info["ro_property"]["ro.product.manufacturer"]["value"]:
                return 1
            else:
                return 0
    return 2

def VTS_AOSP_special_check2(reports):
    for report in reports:
        if report.test_result.suite_plan == "vts" or report.test_result.suite_plan == "cts-reference-aosp":
            if report.test_result.sw.build_model == report.device_info["ro_property"]["ro.product.model"]["value"]:
                return 1
            else:
                return 0
    return 2

def is_consistent_security_patch(reports):
    sp=""
    for report in reports:
        if sp =="":
            sp = report.test_result.sw.build_version_security_patch
        elif sp != report.test_result.sw.build_version_security_patch:
            return 0
    return 1

def is_security_patch_up_to_date(reports):
    sp= reports[0].test_result.sw.build_version_security_patch
    sp_month=sp.split('-')[1]
    if (datetime.today().month-int(sp_month)) <= 2:
        return 1
    else:
        return 0
def is_all_modules_done(reports):
    for report in reports:
        md=report.test_result.modules_done_num
        mt=report.test_result.modules_total_num
        if mt-md != 0:
            return 0
    return 1

check_list=[
    ["Fingerprint","is consistent in all test_result.xml", is_consistent_fingerprint,{0:"FAIL",1:"PASS"}],
    ["Fingerprint","is valid format",is_valid_fingerprint_format,{0:"FAIL",1:"PASS"}],
    ["ClientID","is exist in MADA list",is_valid_clientId,{0:"FAIL",1:"PASS"}],
    ["VTS/AOSP special check","is build_manufacturer = ro.product.manufacturer",VTS_AOSP_special_check1,{0:"FAIL",1:"PASS",2:"N/A"}],
    ["VTS/AOSP special check","is build_model = ro.product.model",VTS_AOSP_special_check2,{0:"FAIL",1:"PASS",2:"N/A"}],
    ["Security patch","is consistent in all test_result.xml",is_consistent_security_patch,{0:"FAIL",1:"PASS"}],
    ["Security patch","date.month>=today.month-2", is_security_patch_up_to_date, {0: "FAIL", 1: "PASS"}],
    ["Modules Done","is modules_done/modules_total = 1",is_all_modules_done,{0:"FAIL",1:"PASS"}],
    ["GMS apps check","essential/must/optional: ro.product.locale.region compare with geo table",is_valid_fingerprint_format,{0:"FAIL",1:"PASS"}],
    ["Testing Fails","is failed > 0 && failed item not in waiver list",is_valid_fingerprint_format,{0:"FAIL",1:"PASS"}],
    ["GMS Version","left days to closed",is_valid_fingerprint_format,{0:"FAIL",1:"PASS"}],
    ["Tool Version","GTS left days to closed ",is_valid_fingerprint_format,{0:"FAIL",1:"PASS"}],
    ["Tool Version","CTS left days to closed",is_valid_fingerprint_format,{0:"FAIL",1:"PASS"}],
    ["Tool Version","CTS on AOSP left days to closed",is_valid_fingerprint_format,{0:"FAIL",1:"PASS"}],
    ["Tool Version","CTSV left days to closed",is_valid_fingerprint_format,{0:"FAIL",1:"PASS"}],
    ["Tool Version","VTS left days to closed",is_valid_fingerprint_format,{0:"FAIL",1:"PASS"}],
    ["Funding Program","check CleanUX, GMSEXPRESS feature",is_valid_fingerprint_format,{0:"FAIL",1:"PASS"}],
    ["HomeScreen","Human Check",is_valid_fingerprint_format,{0:"FAIL",1:"PASS"}],
    ["Other Features", "CPU check", is_valid_fingerprint_format, {0: "FAIL", 1: "PASS"}],
    ["Other Features", "DPI check", is_valid_fingerprint_format, {0: "FAIL", 1: "PASS"}],
    ["Other Features", "Low ram check", is_valid_fingerprint_format, {0: "FAIL", 1: "PASS"}]
]
