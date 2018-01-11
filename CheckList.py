#!/usr/bin/python2
import Define
from datetime import datetime
from datasource import *

#check method
def is_consistent_fingerprint(reports):
    res=1;reason='';fp='';test_suite=''
    for report in reports:
        if fp =='':
            fp = report.test_result.sw.build_fingerprint
            test_suite=report.test_result.suite_plan
        elif fp != report.test_result.sw.build_fingerprint:
            res= 0;reason=str.format('Fingerprint inconsistent in %s, %s' %(test_suite,report.test_result.suite_plan))
            break
    return res,reason

def is_valid_fingerprint_format(reports):
    res = 1;reason = '';
    #valid format: $(BRAND) /$(PRODUCT) /$(DEVICE):$(VERSION.RELEASE) /$(ID) /$(VERSION.INCREMENTAL):$(TYPE) /$(TAGS)
    fp=reports[0].test_result.sw.build_fingerprint
    brand=reports[0].test_result.sw.build_brand
    product=reports[0].test_result.sw.build_product
    device = reports[0].test_result.sw.build_device
    version_release=reports[0].test_result.sw.build_version_release
    build_version_incremental=reports[0].test_result.sw.build_version_incremental
    build_id=reports[0].test_result.sw.build_id
    type='user'
    tags='release-keys'
    exp_fp=str.format("%s/%s/%s:%s/%s/%s:%s/%s" %(brand,product,device,version_release,build_id,build_version_incremental,type,tags))
    if fp != exp_fp:
        res=0
        reason=str.format("%s != %s" %(fp,exp_fp))
    #future task: to compare device id list
    return res,reason

def is_valid_clientId(reports):
    # future task: to compare mada list
    res=0;reason=''
    report_client_id=''
    for report in reports:
        if report.device_info!=None:
            if report.device_info["ro_property"].has_key("ro.com.google.clientidbase"):
                report_client_id=str(report.device_info["ro_property"]["ro.com.google.clientidbase"]["value"])
                break
    if report_client_id!='':
        for client_id in client_id_list:
            if report_client_id==client_id:
                res=1
                break
        if res != 1:
            reason = str.format('Client id %s not found in mada list' % report_client_id)
    else:
        res=0;reason='Report no client id'
    return res,reason

def VTS_AOSP_special_check1(reports):
    res=9;reason=''
    for report in reports:
        if report.test_result.suite_plan == "vts" or report.test_result.suite_plan == "cts-reference-aosp":
            prop_manufacture=str(report.device_info["ro_property"]["ro.product.manufacturer"]["value"])
            if report.test_result.sw.build_manufacturer == prop_manufacture:
                res=1
                break
            else:
                res=0
                reason=str.format('%s != %s' %(report.test_result.sw.build_manufacturer,prop_manufacture))
                break
    return res,reason

def VTS_AOSP_special_check2(reports):
    res=9;reason=''
    for report in reports:
        if report.test_result.suite_plan == "vts" or report.test_result.suite_plan == "cts-reference-aosp":
            prop_model = str(report.device_info["ro_property"]["ro.product.model"]["value"])
            if report.test_result.sw.build_model == prop_model:
                res = 1
                break
            else:
                res = 0
                reason = str.format('%s != %s' % (report.test_result.sw.build_model,prop_model))
                break
    return res, reason

def is_consistent_security_patch(reports):
    res=1;reason='';test_suite=''
    sp=""
    for report in reports:
        if sp =="":
            sp = report.test_result.sw.build_version_security_patch
            test_suite = report.test_result.suite_plan
        elif sp != report.test_result.sw.build_version_security_patch:
            res=0;reason=str.format('Security Patch inconsistent in %s, %s' %(test_suite,report.test_result.suite_plan))
    return res,reason

def is_security_patch_up_to_date(reports):
    res =1;reason = ''
    sp= reports[0].test_result.sw.build_version_security_patch
    sp_year = sp.split('-')[0]
    sp_month = sp.split('-')[1]
    today_year=datetime.today().year
    today_month=datetime.today().month
    if today_year-int(sp_year)==1:
        today_month=today_month+12
    if (today_month-int(sp_month)) > 2:
        res=0;reason=str.format('Security Patch %s out-of-date' %sp)
    return res,reason

def is_all_modules_done(reports):
    res =1;reason = ''
    for report in reports:
        md = report.test_result.modules_done_num
        mt = report.test_result.modules_total_num
        if mt-md != 0:
            res=0;reason+=str.format('%s modules %s/%s; ' %(report.test_result.suite_plan,md,mt))
    return res,reason
def is_all_essential_gms_installed(reports):
    res =1;reason=''
    # old logic from Javier's shell script
    has_device_info=False
    device_info={}
    for report in reports:
        if report.device_info != None:
            has_device_info=True
            device_info=report.device_info.copy()
            break
    if (has_device_info==False):
        res= -1;reason='No GMS info in reports'
    else:
        for app in essential_apps:
            if device_info["package"].has_key(app)==False:
                if reason=='':
                    reason='Missing:'
                res=0;reason+=str.format(' %s;' %app)
    return res,reason

def is_all_must_gms_installed(reports):
    res =1;reason=''
    # old logic
    device_info={}
    for report in reports:
        if report.device_info != None:
            has_device_info=True
            device_info=report.device_info.copy()
            break
    if (has_device_info==False):
        res = -1;reason = 'No GMS info in reports'
    else:
        for app in must_apps:
            if device_info["package"].has_key(app)==False:
                # special rule
                if app=='com.google.android.apps.tachyon' and device_info["feature"]["android.hardware.telephony"]["available"]==False:
                    pass
                elif app=='com.google.android.talk' and device_info["feature"]["android.hardware.telephony"]["available"]==True:
                    pass
                else:
                    if reason == '':
                        reason = 'Missing:'
                    res = 0;reason += str.format(' %s;' % app)
    return res, reason
    # future task: to compare geo table

def is_optional_gms_being_allowed(reports):
    # future task: to compare geo table
    return -1,''

def is_test_pass(reports):
    # future task: create another part for test failures check and set to waiver
    return -1,''

def is_gts_tool_up_to_date(reports):
    return is_tool_version_up_to_date(reports,'gts')
def is_cts_tool_up_to_date(reports):
    return is_tool_version_up_to_date(reports,'cts')
def is_ctsv_tool_up_to_date(reports):
    return is_tool_version_up_to_date(reports,'verifier')
def is_ctsonaosp_tool_up_to_date(reports):
    return is_tool_version_up_to_date(reports,'cts-reference-aosp')
def is_vts_tool_up_to_date(reports):
    return is_tool_version_up_to_date(reports,'vts')
def is_gmsversion_up_to_date(reports):
    gmsversion=''
    is_gmsversion_found=False
    for report in reports:
        if report.device_info != None:
            if report.device_info["ro_property"].has_key("ro.com.google.gmsversion"):
                gmsversion=str(report.device_info["ro_property"]["ro.com.google.gmsversion"]["value"])
                is_gmsversion_found=True
                break
    if is_gmsversion_found==False:
        return 9,''
    left_days=count_left_days("gmsversion",gmsversion)
    return judge_left_days(left_days)

def is_tool_version_up_to_date(reports,test_suite):
    suite_version=''
    suite_plan=''
    is_test_suite_found=False
    for report in reports:
        if report.test_result.suite_plan==test_suite:
            suite_version=report.test_result.suite_version
            is_test_suite_found=True
            break
    if is_test_suite_found==False:
        return 9,''
    if test_suite=='cts-reference-aosp':
        suite_plan='cts'
    else:
        suite_plan=test_suite
    left_days=count_left_days(suite_plan,suite_version)
    return judge_left_days(left_days)

def judge_left_days(left_days):
    if left_days <= 0:      #FAIL
        return 0,str.format('out-of-date: %d' %left_days)
    elif left_days >= 5:    #PASS
        return 1,''
    else:                   #INFO
        return 2,str.format('going to be out-of-date in : %d days' %left_days)

def count_left_days(test_suite,suite_version):
    if close_date_list.has_key(test_suite)==False:
        return -1
    if close_date_list[test_suite].has_key(suite_version)==False:
        return 0
    close_date=close_date_list[test_suite][suite_version]
    if close_date=='-':
        return 99   # no deadline currently
    elif len(close_date.split('/'))!=3:
        return 0    # incorrent date format
    tmp=close_date.split('/')
    d1=datetime(int(tmp[0]),int(tmp[1]),int(tmp[2]))
    d2 = datetime.today()
    return close_date,(d1-d2).days

def check_funding_program(reports):
    res=3;reason=''
    is_gmsexpress_plus_found=False
    is_cleanux_found = False
    for report in reports:
        if report.device_info != None:
            if report.device_info["feature"].has_key("com.google.android.feature.GMSEXPRESS_PLUS_BUILD"):
                is_gmsexpress_plus_found = True
            if report.device_info["feature"].has_key("com.google.android.feature.CLEANUX_BUILD"):
                is_cleanux_found = True

    if(is_gmsexpress_plus_found & is_cleanux_found):
        res=0;reason='Duplicate Defined GMSEXPRESS+ and CLEANUX'
    elif is_cleanux_found:
        res=1
    elif is_gmsexpress_plus_found:
        res=2
    return res,reason

def list_check_points(reports):
    # future task
    return -1,''
def is_valid_cpu_info(reports):
    # future task
    return -1,''
def is_valid_dpi_info(reports):
    # future task
    return -1,''
def is_row_ram(reports):
    # future task
    return -1,''

# define check list
# title,subtitle,check_method,argvs,judge_rule
check_list=[
    ["Fingerprint","is consistent in all test_result.xml", is_consistent_fingerprint,{0:"FAIL",1:"PASS"}],
    ["Fingerprint","is valid format",is_valid_fingerprint_format,{0:"FAIL",1:"PASS"}],
    ["ClientID","is exist in MADA list",is_valid_clientId,{0:"FAIL",1:"PASS"}],
    ["VTS/AOSP special check","is build_manufacturer = ro.product.manufacturer",VTS_AOSP_special_check1,{0:"FAIL",1:"PASS",9:"N/A"}],
    ["VTS/AOSP special check","is build_model = ro.product.model",VTS_AOSP_special_check2,{0:"FAIL",1:"PASS",9:"N/A"}],
    ["Security patch","is consistent in all test_result.xml",is_consistent_security_patch,{0:"FAIL",1:"PASS"}],
    ["Security patch","date.month>=today.month-2", is_security_patch_up_to_date, {0: "FAIL", 1: "PASS"}],
    ["Modules Done","is modules_done/modules_total = 1",is_all_modules_done,{0:"FAIL",1:"PASS"}],
    ["GMS apps ","essential apps check",is_all_essential_gms_installed,{0:"FAIL",1:"PASS"}],
    ["GMS apps ","must apps check",is_all_must_gms_installed,{0:"FAIL",1:"PASS"}],
    ["GMS apps ","optional apps check",is_optional_gms_being_allowed, {0: "FAIL", 1: "PASS"}],
    ["Testing Fails","is failed > 0 && failed item not in waiver list",is_test_pass,{0:"FAIL",1:"PASS"}],
    ["GMS Version","is gmsversion up-to-date ",is_gmsversion_up_to_date,{0:"FAIL",1:"PASS",2:"less than 5 days",9:"N/A"}],
    ["Tool Version","is gts up-to-date ",is_gts_tool_up_to_date,{0:"FAIL",1:"PASS",2:"less than 5 days",9:"N/A"}],
    ["Tool Version","is cts up-to-date",is_cts_tool_up_to_date,{0:"FAIL",1:"PASS",2:"less than 5 days",9:"N/A"}],
    ["Tool Version","is cts on aosp  up-to-date",is_ctsonaosp_tool_up_to_date,{0:"FAIL",1:"PASS",2:"less than 5 days",9:"N/A"}],
    ["Tool Version","is ctsv up-to-date",is_ctsv_tool_up_to_date,{0:"FAIL",1:"PASS",2:"less than 5 days",9:"N/A"}],
    ["Tool Version","is vts up-to-date",is_vts_tool_up_to_date,{0:"FAIL",1:"PASS",2:"less than 5 days",9:"N/A"}],
    ["Funding Program","check CleanUX, GMSEXPRESS feature",check_funding_program,{0:"FAIL",1:"CLEANUX",2:"GMSEXPRESS+",3:"No Funding Program"}],
    ["HomeScreen","Human Check",list_check_points,{0:"Normal",1:"CLEANUX",2:"GMSEXPRESS+",3:"RUSSIA RULE"}],
    ["Other Features", "CPU check", is_valid_cpu_info, {0: "FAIL", 1: "PASS"}],
    ["Other Features", "DPI check", is_valid_dpi_info, {0: "FAIL", 1: "PASS"}],
    ["Other Features", "Low ram check", is_row_ram, {0: "-", 1: "Low RAM"}]
]
