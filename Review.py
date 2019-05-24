#!/usr/bin/python2
import os
import sys
import json
import time
from datetime import datetime
from Define import *
from Common import *
from CheckList import *
from datasource import *
import socket

#global variables
test_reports=[]
reports_sorting_rule={'gts':0,'cts':1,'cts-reference-aosp':2,'verifier':3,'vts':4}
debug_level=DebugLevel.ERROR

def main():
    try:
        if False and socket.gethostname()=="S17B005376-NB":  #spirit's pc local test
            debug_log("unzip",DebugLevel.DEBUG)
            unzip_all(".")
            time.sleep(1)
        get_reports()
        output()
        #region #debug msg
        for report in test_reports:
            debug_log("*************************************************************************************************",DebugLevel.INFO)
            debug_log(report.test_result.suite_plan,DebugLevel.INFO)
            debug_log(report.test_result.sw.info(),DebugLevel.INFO)
            debug_log("Modules_Total: %d" % report.test_result.modules_total_num, DebugLevel.INFO)
            debug_log("Modules_Done: %d" % report.test_result.modules_done_num,DebugLevel.INFO)
            debug_log("Pass: %d" %report.test_result.pass_num, DebugLevel.INFO)
            debug_log("Fails: %d" %report.test_result.failed_num,DebugLevel.INFO)
            if report.test_result.failed_num>0:
                debug_log(report.test_result.list_fails(),DebugLevel.INFO)
            if report.device_info!=None:
                debug_log("Density: %s" %report.device_info["density_dpi"],DebugLevel.INFO)
        #endregion
    except Exception as e:
        debug_log("Error: "+str(e),DebugLevel.ERROR)

def get_reports():
    root0="./"
    device_info_folder_name="device-info-files"
    for root, dirs, files in os.walk(root0):
        for file in files:
            #existed test_result.xml is the must condition of being a valid report
            if file.endswith("test_result.xml"):
                test_result = get_test_result(file, root)
                device_info = get_device_info(device_info_folder_name, root)
                report = TestReport(str(root).lstrip(root0), test_result, device_info)
                insert_report_by_sorting_rule(report)
                break

def insert_report_by_sorting_rule(report):
    if len(test_reports) > 0:
        idx = 0
        for tmp in test_reports:
            plan1 = tmp.test_result.suite_plan
            plan2 = report.test_result.suite_plan
            if reports_sorting_rule[plan1] > reports_sorting_rule[plan2]:
                test_reports.insert(idx, report)
                return
            else:
                idx += 1
    test_reports.append(report)

def get_test_result(file, root):
    test_result = None
    xml_content = parse_test_result(os.path.join(root, file))
    sw = SWImg()
    sw.set_properties(xml_content)
    test_result = TestResult(sw)
    test_result.set_properties(xml_content)
    return test_result

def get_device_info(device_info_folder_name, root):
    device_info = None
    device_info_path = os.path.join(root, device_info_folder_name)
    if os.path.isdir(device_info_path):
        debug_log(" device info existed in %s" % root, DebugLevel.DEBUG)
        device_info = parse_device_info(device_info_path)
    return device_info

def parse_device_info(device_info_path):
    device_info={}
    for root,dirs, files in os.walk(device_info_path):
        for file in files:
            #BUG001
            if file.endswith('LibraryDetailDeviceInfo.deviceinfo.json'):
                continue
            fo=open(os.path.join(device_info_path,file))
            data=json.load(fo)
            if len(data)>0 and data.keys()>0:
                get_pairs_from_sub_layer(data)
                debug_log(data, DebugLevel.DEBUG)
                #one layer with uni-identified key such as {"width_pixels": 1080,"height_pixels": 1920,...}
                device_info = merge_two_dicts(device_info, data)
    return device_info

# sub layer as a list with duplicate keys such as
# {"ro_property":[{"name": "ro.com.google.clientidbase","value": "android-vsun"},
#       {"name": "ro.com.google.gmsversion","value": "7.0_r11"},...]}
def get_pairs_from_sub_layer(data):
    _value = data.values()[0]
    if len(data.keys()) >1 or type(_value)!=list or len(_value)==0:
        return
    if type(_value[0])!=dict:
        return
    layer2_data={}
    layer2_name = data.keys()[0]
    for layer2_dict in _value:
        if layer2_dict.get("name"):
            tmp={}
            for _key in layer2_dict:
                if _key != "name":
                    tmp.setdefault(_key,layer2_dict[_key])
            layer2_data.setdefault(str(layer2_dict["name"]),tmp)
    debug_log(layer2_data,DebugLevel.DEBUG)
    data[layer2_name]=layer2_data.copy()

def parse_test_result(filename):
    fo = open(filename, "r")
    test_summary={}
    test_case_tmp={}
    failed_testcases=[]
    for line in fo.readlines():
        line=line.strip()
        if(line.startswith('<') and line.endswith('>')):
            parse_test_result_line(test_summary, failed_testcases, line,test_case_tmp)
    if(len(failed_testcases)>0):
        test_summary.setdefault("failed_testcases",failed_testcases)
    fo.close()
    return test_summary

def parse_test_result_line(test_summary, failed_testcases, line,test_case_tmp):
    line = line.lstrip('<').rstrip('>').rstrip('/')
    if(line.startswith("Result") or line.startswith("Build") or line.startswith("Summary")):
        for _key in keyword_in_xml:
            if (line.find(_key) >= 0):
                _type = type(keyword_in_xml[_key])
                _tmp = get_keypvalue(_key, line)
                if _type==int:
                    _prop = str(_tmp[0])+"_num"
                    _value = int(_tmp[1])
                else:
                    _prop = str(_tmp[0])
                    _value = str(_tmp[1])
                test_summary.setdefault(_prop, _value)
    elif line.startswith('Module'):
        val=get_xmlnode_attribuite(line,"Module","name")
        if test_case_tmp.has_key('test_module_name'):
            test_case_tmp['test_module_name']=val
        else:
            test_case_tmp.setdefault('test_module_name',val)
        val=get_xmlnode_attribuite(line,"Module"," abi")
        if test_case_tmp.has_key('test_module_abi'):
            test_case_tmp['test_module_abi']=val
        else:
            test_case_tmp.setdefault('test_module_abi',val)
    elif line.startswith('TestCase'):
        val=get_xmlnode_attribuite(line,"TestCase","name")
        if test_case_tmp.has_key('test_case_name'):
            test_case_tmp['test_case_name'] = val
        else:
            test_case_tmp.setdefault('test_case_name',val)
    elif line.find("result=\"fail\"")>=0:
        failitem={}
        failitem.setdefault('module',test_case_tmp['test_module_name'])
        failitem.setdefault('abi', test_case_tmp['test_module_abi'])
        failitem.setdefault('test_case', test_case_tmp['test_case_name'])
        failitem.setdefault('test_item', get_xmlnode_attribuite(line,"Test","name"))
        failed_testcases.append(failitem)
        return

def get_xmlnode_attribuite(line,xml_node,attr):
    res=""
    if(line.startswith(xml_node)):
        res=line[line.index(attr+"=\"")+len(attr+"=\""):]
        res=res[:res.index("\"")]
    return res

def gen_table_basic_info():
    report_basic_info = \
        [
            ["Fingerprint", test_reports[0].test_result.sw.build_fingerprint],
            ["Brand", test_reports[0].test_result.sw.build_brand],
            ["Product", test_reports[0].test_result.sw.build_product],
            ["Security Patch", test_reports[0].test_result.sw.build_version_security_patch]
        ]
    if test_reports[0].device_info != None:
        #non-china
        if test_reports[0].device_info["ro_property"].has_key("ro.com.google.clientidbase"):
            report_basic_info.append(
                ["ClientId", str(test_reports[0].device_info["ro_property"]["ro.com.google.clientidbase"]["value"])])
            report_basic_info.append(
                ["GMS Version", str(test_reports[0].device_info["ro_property"]["ro.com.google.gmsversion"]["value"])])
        #china
        else:
            report_basic_info.append(
                ["ClientId", ""])
            report_basic_info.append(
                ["GMS Version", ""])
    table_title = str.format("BASIC INFO")
    table_name = "tb_basic_info"
    return str({"table_title": table_title, "table_name": table_name, "table_data": report_basic_info})

def gen_table_report_summary():
    res=""
    for report in test_reports:
        if res!="":
            res+=","
        report_summary = \
            [
                ["Test Report", str.format("%s.zip" % report.file_name)],
                ["Test Suite", str.format(
                    "%s (%s)" % (report.test_result.suite_plan.upper(), report.test_result.suite_version.upper()))],
                ["Modules Done / Total",
                 str.format("%s/%s" % (report.test_result.modules_done_num, report.test_result.modules_total_num))],
                ["Pass", report.test_result.pass_num],
                ["Fails", report.test_result.failed_num]
            ]
        table_title = str.format("%s REPORT" % report.test_result.suite_plan.upper())
        table_name = "tb" + report.test_result.suite_plan
        res+= str({"table_title": table_title, "table_name": table_name, "table_data": report_summary})
    return res

def gen_table_check_list():
    res=""
    check_list_result = []
    for li in check_list:
        check_item=CheckItemBase(li)
        check_item.check(test_reports)
        check_list_result.append([str(check_item.title),str(check_item.subtitle),str(check_item.check_result),str(check_item.detail)])

    table_title = "CHECK LIST"
    table_name = "tb_check_list"
    res += str({"table_title": table_title, "table_name": table_name, "table_data": check_list_result})
    return res

def gen_table_failure_list():
    res=""
    failure_list=[]
    for report in test_reports:
        if report.test_result.failed_num<=0:
            continue
        non_waived_testcase=[]
        waiver_testcase=[]
        suite_plan=report.test_result.suite_plan
        suite_version=report.test_result.suite_version
        build_version=report.test_result.sw.build_version_release
        for testcase in report.test_result.failed_testcases:
            is_waiver = False
            for waiver in waiver_list:
                if   build_version==waiver['build_version'] and \
                    suite_plan==waiver['suite_plan'] and \
                    suite_version== waiver['suite_version'] and \
                    testcase['module']==waiver['module'] and\
                    testcase['test_case']==waiver['test_case'] and\
                    testcase['test_item']==waiver['test_item']:
                        waiver_testcase.append(testcase)
                        is_waiver=True
                        break
            if is_waiver==False:
                non_waived_testcase.append(testcase)

        failure_info={
                        'filename': str.format("%s.zip" %report.file_name),\
                        'suite_plan':suite_plan,\
                        'suite_version':suite_version,\
                        'build_version':build_version,\
                        'failure_cases':non_waived_testcase,\
                        'waiver_cases':waiver_testcase
                      }
        failure_list.append(failure_info)
    table_title = "FAILURE TEST CASES"
    table_name = "tb_failure_list"
    res += str({"table_title": table_title, "table_name": table_name, "table_data": failure_list})
    return res

def output():
    if len(test_reports) == 0:
        return
    tmp="basic_tables=[\n"
    tmp+=gen_table_basic_info()+",\n"
    tmp+=gen_table_report_summary()+"\n"
    tmp+="];\n"
    tmp+="check_list="+gen_table_check_list()+";\n"
    tmp+="failure_list="+gen_table_failure_list()+";\n"
    report_name=str.format("report_%s_%s.html" %(test_reports[0].test_result.sw.build_brand,test_reports[0].test_result.sw.build_product))
    insert_data_into_file("template.html","    //data from test reports",report_name,tmp)

def insert_data_into_file(source_file,key_word,output_file,value):
    f = open(source_file, "r")
    contents = f.readlines()
    f.close()
    index = 0
    for line in contents:
        index = index + 1
        if line.startswith(key_word):
            break
    contents.insert(index, value)
    f = open(output_file, "w")
    contents = "".join(contents)
    f.write(contents)
    f.close()

def debug_log(msg,lv):
    if(debug_level>=lv):
        print(msg)

main()
#test
