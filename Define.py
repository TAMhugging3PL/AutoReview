#!/usr/bin/python2
# define keys from test_result.xml
unzip_command_for_windows=""
unzip_command_for_linux=""
keyword_in_xml=\
{
    "build_fingerprint":"",
    "build_brand":"",
    "build_product": "",
    "build_device": "",
    "build_version_release": "",
    "build_version_incremental":"",
    "build_id":"",
    "build_version_security_patch": "",
    "build_manufacturer":"",
    "build_model":"",
    "suite_plan": "",
    "suite_version": "",
    "modules_done": -1,
    "modules_total": -1,
    "failed": -1,
    "pass": -1
}

# classes
class DebugLevel:
    OFF = 0
    ERROR = 1
    INFO = 2
    DEBUG = 3

class Basic():
    def set_properties(self,dict_input_prop):
        for _key in self.__dict__:
            if(dict_input_prop.get(_key)!=None):
                self.__dict__[_key]=dict_input_prop[_key]
class SWImg(Basic):
    def __init__(self):
        self.build_fingerprint=""
        self.build_brand=""
        self.build_product=""
        self.build_device=""
        self.build_version_release=""
        self.build_version_incremental=""
        self.build_id=""
        self.build_version_security_patch=""
        self.build_manufacturer = ""
        self.build_model = ""

    def info(self):
        return("Fingerprint: %s\nBrand: %s\nProduct: %s\nDevice: %s\nVersion Release: %s\nSecurity Patch: %s" \
               %(self.build_fingerprint,self.build_brand,self.build_product,self.build_device,self.build_version_release,self.build_version_security_patch))

class TestResult(Basic):
    def __init__(self,_sw):
        self.sw=_sw
        self.suite_plan=""
        self.suite_version=""
        self.modules_done_num=-1
        self.modules_total_num=-1
        self.pass_num=-1
        self.failed_num=-1
        self.failed_testcases=[]
    def list_fails(self):
        return self.failed_testcases

class TestReport:
    device_info=None
    def __init__(self,_file_name, _test_result,_device_info):
        self.file_name=_file_name
        self.test_result=_test_result
        if _device_info!=None:
            self.device_info=_device_info

class CheckItemBase():
    check_result="AMBIGUROUS"
    def __init__(self,check_item):
        self.title=check_item[0]
        self.subtitle=check_item[1]
        self.check_method=check_item[2]
        self.judge_rule=check_item[3]
        self.detail=""
    def check(self,argvs):
        try:
            res,self.detail=self.check_method(argvs)
            if self.judge_rule.get(res):
                self.check_result=self.judge_rule[res]
        except Exception as e:
            print str.format('Check Error: %s @ %s' %(e,self.check_method))
