#!/usr/bin/python2
import os

def unzip(file_list):
    cmd=""
    for file_name in file_list:
        cmd="C:\\\"Program Files\"\\7-Zip\\7z.exe  x "+file_name
        os.popen(cmd)

def unzip_all(filepath):
    ls = []
    get_files_by_type(filepath,"zip", ls)
    unzip(ls)

def get_files_by_type(filepath, filetype, ls):
    filelist = os.listdir(filepath)
    for tmp in filelist:
        pathtmp = os.path.join(filepath, tmp)
        if True == os.path.isdir(pathtmp):
            get_files_by_type(pathtmp,"zip", ls)
        elif pathtmp[pathtmp.rfind('.') + 1:].lower() == filetype:
            ls.append(pathtmp)

def get_keypvalue(attr,line):
    catch=line
    if(catch.find(attr)):
        idx=catch.index(attr)
        catch=catch[idx:]
        if(catch.find(' ')):
            idx=catch.find(' ')
            catch=catch[:idx]
        if(catch.find("=")):
            idx=catch.index("=")
            _key=str(catch[:idx]).lstrip("\"").rstrip("\"").lstrip("'").rstrip("'")
            _val=str(catch[idx+1:]).lstrip("\"").rstrip("\"").lstrip("'").rstrip("'")
            return [_key,_val]
    return None
def set_properties(dict_properties,prop_name,prop_value):
    if (dict_properties.get(prop_name) != None):
        dict_properties[prop_name] = prop_value

def merge_two_dicts(x, y):
    z = x.copy()   # start with x's keys and values
    z.update(y)    # modifies z with y's keys and values & returns None
    return z

#get specific key's value of a list composed by dict
#ex: li=[{'key':'x','value':'value1'},{'key':'y','value':'value2'}..
#get_value_by_key(li,'key','x','value') -> output: value1
def get_value_by_key(li,key_name, key_match, prop_name):
    if len(li)==0:
        return None
    if type(li[0])!=dict:
        return None
    for tmp in li:
        if tmp.get(key_name) and tmp.get(prop_name):
            if tmp[key_name]==key_match:
                return tmp[prop_name]
    return None
