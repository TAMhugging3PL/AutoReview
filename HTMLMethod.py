#!/usr/bin/python2
def gen_html(content):
    tmp="<!DOCTYPE html><html><head><meta charset = \"UTF-8\"><title>Review Report</title ></head>"
    tmp+=gen_css()
    tmp+=content
    tmp+=gen_javascript()
    tmp+="</html>"
    return tmp

def gen_css():
    tmp = "<Style>"
    tmp+= "body{overflow-y: scroll;font-size:small}"
    tmp+= "div#main {width:70%;min-width:500px; margin-left:15%; padding:10px}"
    tmp+= "div.info {}"
    tmp+= "span.info {display:block;width:95%;text-align:right;font-size:smaller;}"
    tmp +="span.info a {margin-right:2px;color:#555555}"
    tmp+= "table {width:95%;border-width:1px; border-color:black}"
    tmp+= "td, th {min-width:220px; text-align:left; padding:2px; padding-left:6px; background:#eeeeee}"
    tmp+= "th {width:40%; min-width:120px; background:#557baa; color: #ffffff;}"
    tmp += "div.check_list table tr:nth-child(odd) td{background:#ffffff;}"
    tmp += "div.check_list table td {width:28%;min-width:30px;}"
    tmp += "div.check_list table th {width:28%;min-width:30px;background:#7b7b7bde; color: #ffffff;}"
    tmp += "div.check_list table tr td.pass {background:#008900a1}"
    tmp += "div.check_list table tr td.fail {background:#ff7777}"
    tmp+= "</Style>"
    return tmp
def gen_main_content(content):
    return str.format("<body><div id=\"main\">%s</div></body>" %str(content))
def gen_div_info(content):
    return str.format("<span class=\"info\"><a href=\"javascript:hide_div('div_basic_info');\">Basic Info & Report Summary Hide/Un-Hide</a></span><div class=\"info\" id=\"div_basic_info\">%s</div>" %str(content))
def gen_div_checklist(content):
    return str.format("<div class=\"check_list\" id=\"div_check_list\">%s</div>" %str(content))
def gen_tag_td(content):
    return str.format("<td>%s</td>" %str(content))
def gen_tag_td_pass(content):
    return str.format("<td class=\"pass\">%s</td>" %str(content))
def gen_tag_td_fail(content):
    return str.format("<td class=\"fail\">%s</td>" %str(content))
def gen_tag_th(content):
    return str.format("<th>%s</th>" %str(content))
def gen_tag_tr(content):
    return str.format("<tr>%s</tr>" %str(content))
def gen_table(title,name,data):
    tmp = str.format("<h4>%s</h4>" %str(title))
    tmp+= str.format("<table name=\"%s\">"%name)
    if type(data)!=list or len(data)==0:
        tmp+=gen_tag_tr(gen_tag_td("No data"))
    else:
        tmp+= gen_table_content(data)
    tmp+= str.format("</table>")
    return tmp

def gen_table_content(data):
    content=""
    for row in data:
        tr = ""
        is_header = True
        for col in row:
            if is_header:
                tr += gen_tag_th(col)
                is_header = False
            else:
                tr += gen_tag_td(col)
        content += gen_tag_tr(tr)
    return content

def gen_check_table(title,name,data):
    tmp = str.format("<h4>%s</h4>" %str(title))
    tmp+= str.format("<table name=\"%s\">"%name)
    if type(data)!=list or len(data)==0:
        tmp+=gen_tag_tr(gen_tag_td("No data"))
    else:
        tmp+= gen_check_table_content(data)
    tmp+= str.format("</table>")
    return tmp

def gen_input_check_tam_confirm():
    return "<input type=\"checkbox\" class=\"chk_tam_confirm\">"
def gen_input_text_tam_confirm():
    return "<textarea class=\"text_tam_confirm\" rows=\"1\" cols=\"50\" placeholder=\"write your comment\"></textarea>"
def gen_check_table_content(data):
    content=""
    is_header = True
    for row in data:
        tr = ""
        for col in row:
            if is_header:
                tr += gen_tag_th(col)
            else:
                if(col.upper()=="FAIL"):
                    tr += gen_tag_td_fail(col)
                elif(col.upper()=="PASS"):
                    tr += gen_tag_td_pass(col)
                else:
                    tr+= gen_tag_td(col)
        is_header = False
        content += gen_tag_tr(tr)
    return content
def gen_summary_button():
    return "<br/><input type=\"button\" value=\"Summary\" width=\"200px\" height=\"30px\" onclick=\"return check_tam_confirm();\">"
def gen_javascript():
    tmp="<script type= text/javascript>"
    tmp+="function hide_div(elmId)"
    tmp+="{"
    tmp+="  var target=document.getElementById(elmId);"
    tmp+="  if (target.style.display=='none') "
    tmp+="  {"
    tmp+="      target.style.display='block'; "
    tmp+="  }"
    tmp+="  else"
    tmp+="  {"
    tmp+="      target.style.display='none'; "
    tmp+="  }"
    tmp+="}"
    tmp+="function check_tam_confirm()"
    tmp+="{"
    tmp+="chks=document.getElementsByClassName('chk_tam_confirm');"
    tmp+="for(i=0;i<chks.length;i++){"
    tmp+="if(!chks[i].checked)"
    tmp+="{alert('Not confirmed');chks[i].focus();return false;}}"
    tmp+="}"
    tmp+="</script></html>"
    return tmp