import re
import os
import json
import time
import requests
from urllib import parse
from tool.login import login
from datetime import date, timedelta, datetime
import logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

with open("./config/acounts.json", "r", encoding="utf-8") as f:
    acounts = json.loads(f.read())

with open("./config/admission.json", "r", encoding="utf-8") as f:
    admission = json.loads(f.read())

if "ACOUNTS" in os.environ:
    acounts = os.environ["ACOUNTS"]
if "ADMISSION" in os.environ:
    admission = os.environ["ADMISSION"]

Total_Bark_Key = acounts['Total_Bark_Key']
user_acounts_list = acounts['Users']
user_admmsion_list = admission['Users']

headers = dict()
headers['Referer'] =  'http://ehall.seu.edu.cn/qljfwapp3/sys/lwWiseduElectronicPass/index.do'

#通用url
cookie_url = 'http://ehall.seu.edu.cn/qljfwapp3/sys/funauthapp/api/getAppConfig/lwWiseduElectronicPass-5824595920058328.do'
base_addr = 'http://ehall.seu.edu.cn/'
application = base_addr + 'qljfwapp3/sys/lwWiseduElectronicPass/modules/application.do'
queryNextDayInschoolCount = base_addr + 'qljfwapp3/sys/lwWiseduElectronicPass/modules/application/queryNextDayInschoolCount.do'
validateApply = base_addr + 'qljfwapp3/sys/lwWiseduElectronicPass/api/validateApply.do'

# 申请url
T_APPLY_LIMITE_QUERY = base_addr + 'qljfwapp3/sys/lwWiseduElectronicPass/modules/application/T_APPLY_LIMITE_QUERY.do'
applicationSave = base_addr + 'qljfwapp3/sys/lwWiseduElectronicPass/modules/application/applicationSave.html?av=30000'
undefined = base_addr + 'qljfwapp3/sys/emapcomponent/file/getUploadedAttachment/undefined.do'
hqdqryyqsbxx = base_addr + 'qljfwapp3/sys/lwWiseduElectronicPass/modules/application/hqdqryyqsbxx.do'
SEX = base_addr + 'qljfwapp3/code/2d7772bc-4fb3-4e2c-a224-6df948cce897/SEX.do'
ID_TYPE = base_addr + 'qljfwapp3/code/2d7772bc-4fb3-4e2c-a224-6df948cce897/ID_TYPE.do'
STATUS = base_addr + 'qljfwapp3/code/2d7772bc-4fb3-4e2c-a224-6df948cce897/STATUS.do'
hqsqjzsj = base_addr + 'qljfwapp3/sys/lwWiseduElectronicPass/modules/application/hqsqjzsj.do'
queryFirstUserTaskToolbar = base_addr + 'qljfwapp3/sys/emapflow/definition/queryFirstUserTaskToolbar.do?defKey=lwWiseduElectronicPass.MainFlow'

# 填写url
COMMON_STATE = base_addr + 'qljfwapp3/code/2d7772bc-4fb3-4e2c-a224-6df948cce897/COMMON_STATE.do'
pass_campus = base_addr + 'qljfwapp3/code/038e533b-1c26-4572-9320-b8f2efa3f2d1.do'
SQLY = base_addr + 'qljfwapp3/code/2d7772bc-4fb3-4e2c-a224-6df948cce897/SQLY.do'
uploadTempFile = base_addr + 'qljfwapp3/sys/emapcomponent/file/uploadTempFile.do'

# startFlow
startFlow = base_addr + 'qljfwapp3/sys/emapflow/tasks/startFlow.do'

def get_info(sess):
    url = 'http://ehall.seu.edu.cn/qljfwapp3/sys/emapflow/*default/index/queryUserTasks.do'
    headers['Content-Type'] = 'application/x-www-form-urlencoded;charset=utf-8'
    FormData = {'taskType': 'ALL_TASK', "nodeId": "usertask1", "appName": "lwWiseduElectronicPass",
                "module": "modules",
                "page": "application",
                "action": "getApplicationData",
                "*order": "-CREATED_AT",
                "pageSize": 10000,
                "pageNumber": 1
                }
    data = parse.urlencode(FormData)
    get_personal_info = sess.post(url, data=data, headers=headers)
    return get_personal_info

def get_info2(sess, WID):
    url = 'http://ehall.seu.edu.cn/qljfwapp3/sys/lwWiseduElectronicPass/modules/application/getStuApplicationDatas.do'
    headers['Content-Type'] = 'application/json; charset=UTF-8'
    FormData = {'WID': WID}
    data = parse.urlencode(FormData)

    get_personal_info = sess.post(url, data=data, headers=headers)
    return json.loads(get_personal_info.text)['datas']['getStuApplicationDatas']['rows'][0]

# 撤回
def callback(sess, datas):
    global msg_all
    url = 'http://ehall.seu.edu.cn/qljfwapp3/sys/emapflow/tasks/callback.do'
    url2 = 'http://ehall.seu.edu.cn/qljfwapp3/sys/emapflow/definition/queryUserTaskToolbar.do?taskId='
    headers['Content-Type'] = 'application/x-www-form-urlencoded'
    now_time = datetime.now()
    for data in datas:
        if False or (now_time.strftime("%Y-%m-%d") not in data['IN_SCHOOL_TIME'] and (now_time + timedelta(days=+1)).strftime("%Y-%m-%d") not in data['IN_SCHOOL_TIME']):
            # FLOWSTATUS：1-审核中；2-已驳回；3-已完成；4-草稿；5-已终止；6-已撤回；0-未知状态
            if data["FLOWSTATUSNAME"] == "审核中": 
                commands = json.loads(sess.get(url2 + str(data['TASKID']), headers=headers).text)['commands']
                if len(commands) > 0:
                    logger.info("撤回: " + data["IN_SCHOOL_TIME"])
                    msg_all += "撤回: " + data["IN_SCHOOL_TIME"]+"\n"
                    post_info = {
                        "formData": {},
                        "sendMessage": "true",
                        "id": "callback",
                        "commandType": "callback",
                        "execute": "do_callback",
                        "name": "撤回",
                        "url": "/sys/emapflow/tasks/callback.do",
                        "buttonType": "warning",
                        "taskId": str(data["TASKID"]),
                        "defKey": str(data["DEFKEY"]),
                        "flowComment":"" 
                    }
                    sess.post(url, data=parse.urlencode(post_info), headers=headers)  

# 删除草稿
def deleteInstance(sess, datas):
    global msg_all
    url = 'http://ehall.seu.edu.cn/qljfwapp3/sys/emapflow/tasks/deleteInstance.do'
    url2 = 'http://ehall.seu.edu.cn/qljfwapp3/sys/lwWiseduElectronicPass/modules/application/T_ELECTRONIC_PASS_CHECKIN_DELETE.do'
    headers['Content-Type'] = 'application/x-www-form-urlencoded; charset=UTF-8'
    for data in datas:
        if data["FLOWSTATUSNAME"] == "已撤回" or data["FLOWSTATUSNAME"] == "已驳回":
            logger.info("删除: " + data["IN_SCHOOL_TIME"])
            msg_all += "删除: " + data["IN_SCHOOL_TIME"]+"\n"
            post_info = {
                "processInstanceId": str(data["PROCESSINSTANCEID"]),
                "isDelete": "true",
                "appName": "lwWiseduElectronicPass",
                "defKey": str(data["DEFKEY"])
            }
            info = (sess.post(url, data=parse.urlencode(post_info), headers=headers).text)
            if "true" in info:
                post_info = {
                    "T_ELECTRONIC_PASS_CHECKIN_DELETE": {"WID":data['WID']}
                }
                (sess.post(url2, data=parse.urlencode(post_info), headers=headers).text)


def askForAdimission(sess, id, user_info):
    global msg_all
    sess.get(cookie_url)
    cookie = requests.utils.dict_from_cookiejar(sess.cookies)
    c = ""
    for key, value in cookie.items():
        c += key + "=" + value + "; "

    headers['Cookie'] = c

    get_personal_info = get_info(sess)
    if get_personal_info.status_code == 200:
        logger.info('获取前一日信息成功!')
        msg_all += "获取前一日信息成功!"+"\n"
    else:
        logger.info("获取信息失败!")
        msg_all += "获取信息失败!"+"\n"
        return

    callback(sess, json.loads(get_personal_info.text)['datas']['queryUserTasks']['rows'])

    get_personal_info = get_info(sess)
    deleteInstance(sess, json.loads(get_personal_info.text)['datas']['queryUserTasks']['rows'])
    
    get_personal_info = get_info(sess)
    raw_personal_info = json.loads(get_personal_info.text)['datas']['queryUserTasks']['rows']

    if len(raw_personal_info) == 0:
        logger.info("之前没有上报!")
        msg_all += "之前没有上报!"+"\n"
        return
    raw_personal_info = raw_personal_info[0]

    now_time = datetime.now()
    if  raw_personal_info["FLOWSTATUSNAME"] == "已完成" and (now_time + timedelta(days=+1)).strftime("%Y-%m-%d")  in raw_personal_info['IN_SCHOOL_TIME']:
        logger.info("已存在通过的申请")
        msg_all += "已存在通过的申请"+"\n"
        return
    valid = sess.post(validateApply, {'userid': id, 'campus': str(raw_personal_info['CAMPUS']), 'beginTime': (now_time + timedelta(days=+1)).strftime("%Y-%m-%d")}).text
    if "false" in valid:
        logger.info("存在通行证")
        msg_all += "存在通行证"+"\n"
        return
    raw_personal_info2 = get_info2(sess, raw_personal_info['WID'])

    # 健康码
    if raw_personal_info['YL6'] == '' or raw_personal_info['YL6'] == "" or raw_personal_info['YL6'] == None:
        logger.info("上一次入校没有健康码")
        msg_all += "上一次入校没有健康码"+"\n"
        return
    scope = raw_personal_info['YL6'][:-1]
    filetoken = raw_personal_info['YL6']

    # 通行时间生成
    today_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    logger.info('当前时间：' + today_time)
    msg_all += '当前时间：' + today_time+"\n"

    tomorrow_year = (date.today() + timedelta(days=1)).strftime("%Y")
    tomorrow_month = (date.today() + timedelta(days=1)).strftime("%m")
    tomorrow_day = (date.today() + timedelta(days=1)).strftime("%d")
    tomorrow = str(tomorrow_year) + "-" + str(tomorrow_month) + "-" + str(tomorrow_day)
    tomorrow_begin_time = str(tomorrow_year) + "-" + str(tomorrow_month) + "-" + str(tomorrow_day) + " 06:00:00"
    tomorrow_end_time = str(tomorrow_year) + "-" + str(tomorrow_month) + "-" + str(tomorrow_day) + " 23:00:00"
    logger.info('明天日期：' + tomorrow)
    msg_all += '明天日期：' + tomorrow+"\n"
    logger.info('通行开始时间：' + tomorrow_begin_time)
    msg_all += '通行开始时间：' + tomorrow_begin_time+"\n"
    logger.info('通行结束时间：' + tomorrow_end_time)
    msg_all += '通行结束时间：' + tomorrow_end_time+"\n"

    # 申请按键模拟发包
    LIMITE_QUERY = sess.post(T_APPLY_LIMITE_QUERY, {'USER_ID': id}).text
    
    if len(json.loads(LIMITE_QUERY)['datas']['T_APPLY_LIMITE_QUERY']['rows']) == 0:
        logger.info("你现在暂时不满足申请条件，若有疑问请联系院系辅导员")
        msg_all += "你现在暂时不满足申请条件，若有疑问请联系院系辅导员"+"\n"
        return

    sess.get(applicationSave)
    sess.post(application, {'*json': '1'})
    sess.post(undefined)
    data = sess.post(hqdqryyqsbxx, {'USERID': id}).text
    data = json.loads(data)['datas']['hqdqryyqsbxx']['rows']
    
    if len(data) == 0:
        logger.info("您今天还没有提交每日健康申报，请先在健康申报系统中完成填报，再进行进校预约")
        msg_all += "您今天还没有提交每日健康申报，请先在健康申报系统中完成填报，再进行进校预约"+"\n"
        return
    else:
        if data[0]['CHECKED'] !="YES":
            logger.info("您今天还没有提交每日健康申报，请先在健康申报系统中完成填报，再进行进校预约")
            msg_all += "您今天还没有提交每日健康申报，请先在健康申报系统中完成填报，再进行进校预约"+"\n"
            return
        else:
            user_info_re = re.search('{"deptName":.*}', user_info.text).group()
            user_info_json = json.loads(user_info_re)
            if user_info_json['stuZslx'] =="XWZS" and data[0]['IS_YPKYRX']=="0":
                logger.info("校医院对您健康信息研判结果为不可进校，如有疑问请联系院系管理员")
                msg_all += "校医院对您健康信息研判结果为不可进校，如有疑问请联系院系管理员"+"\n"
                return
            elif user_info_json['stuZslx']=="XWZS" and data[0]['IS_14D_ZNJ'] == "0":
                logger.info("您在宁未满14天，不允许入校")
                msg_all += "您在宁未满14天，不允许入校"+"\n"
                return

    sess.post(SEX)
    sess.post(ID_TYPE)
    sess.post(STATUS)
    sess.post(hqsqjzsj)
    sess.get(queryFirstUserTaskToolbar)
    logger.info('申请中>>>>>>')
    msg_all += '申请中>>>>>>'+"\n"

    # 填写过程模拟发包
    sess.post(COMMON_STATE)
    sess.post(pass_campus)
    sess.post(SQLY)
    sess.post(uploadTempFile,
        {'scope': scope, 'fileToken': filetoken, 'size': '0', 'type': 'jpg,jpeg,png',
        'storeId': 'image',
        'isSingle': '0', 'fileName': '', 'files[]': '苏康码.png'}
    )
    submit1 = base_addr + 'qljfwapp3/sys/emapcomponent/file/saveAttachment/' + str(
        scope) + '/' + str(filetoken) + '.do'
    submit2 = base_addr + 'qljfwapp3/sys/emapcomponent/file/getUploadedAttachment/' + str(
        filetoken) + '.do'

    sess.post(submit1, {'attachmentParam': str({"storeId": "image", "scope": scope, "fileToken": filetoken})})
    sess.post(submit2)
    sess.post(queryNextDayInschoolCount, {'DEPT_CODE': str(raw_personal_info['DEPT_CODE']), 'PERSON_TYPE': str(raw_personal_info['PERSON_TYPE'])})
    valid = sess.post(validateApply, {'userid': id, 'campus': str(raw_personal_info['CAMPUS']), 'beginTime': (now_time + timedelta(days=+1)).strftime("%Y-%m-%d")}).text

    if "false" in valid:
        logger.info("存在通行证")
        msg_all += "存在通行证"+"\n"
        return

    datas = {
        "WID": "",
        "CREATED_AT": "",
        "CZR": "",
        "CZZXM": "",
        "CZRQ": "",
        "IS_FLOW": "1",
        "STATUS_DISPLAY": "审核中",
        "STATUS": "2",
        "USER_ID": "",
        "USER_NAME": "",
        "STUDENT_ID": "",
        "GENDER_CODE_DISPLAY": "",
        "GENDER_CODE": "",
        "PHONE_NUMBER": "",
        "MAJOR_CODE": "",
        "MAJOR": "",
        "CLASS": "",
        "ID_TYPE_DISPLAY": "",
        "ID_TYPE": "",
        "ID_NO": "",
        "PERSON_TYPE_DISPLAY": "",
        "PERSON_TYPE": "",
        "DEPT_CODE": "",
        "DEPT_NAME": "",
        "STUDENT_TYPE_DISPLAY": "",
        "STUDENT_TYPE": "",
        "PYFS_DISPLAY": "",
        "XXXS_DISPLAY": "",
        "JTBG_ADDRESS": "",
        "ZS_ADDRESS": "",
        "SFFHFHYQ_DISPLAY": "是",
        "SFFHFHYQ": "1",
        "NFZHGRFH_DISPLAY": "是",
        "NFZHGRFH": "1",
        "YL2_DISPLAY": "校内住宿",
        "YL2": "XNZS",
        "DZ_SFYJCS4": "无",
        "DZ_SFYJCS1": "无",
        "DZ_SFYJCS2": "否",
        "DZ_SFYJCS3": "否",
        "SFYZNJJJGL": "",
        "DZ_JRSTZK_DISPLAY": "正常",
        "DZ_JRSTZK": "正常",
        "SFJBZJHBXLXTJ_DISPLAY": "",
        "SFJBZJHBXLXTJ": "",
        "LXFS": "",
        "YL7": "",
        "CAMPUS_DISPLAY": "",
        "CAMPUS": "",
        "IN_SCHOOL_TIME": "",
        "OFF_SCHOOL_TIME": "",
        "SDLY": "",
        "RESSON_DISPLAY": "",
        "RESSON": "",
        "SQ_REASON_DISPLAY": "",
        "SQ_REASON": "",
        "QTGZ": "",
        "REMARK": "",
        "TIMES": "",
        "YL1": "",
        "YL4": "",
        "YL3_DISPLAY": "",
        "YL3": "",
        "YL6": "",
        "userType": "false",
        "stuType": "true"
    }
    post_info = {
        "WID": "",
        "CREATED_AT": today_time,
        "CZR": "",
        "CZZXM": "",
        "CZRQ": "",
        "IS_FLOW": "1",
        "STATUS_DISPLAY": "审核中",
        "STATUS": "2",
        "userType": "false",
        "stuType": "true",
        "IN_SCHOOL_TIME": tomorrow_begin_time,
        "OFF_SCHOOL_TIME": tomorrow_end_time
    }
    for key, value in datas.items():
        if key in post_info:
            continue
        if key in raw_personal_info:
            if raw_personal_info[key] == 'null' or raw_personal_info[key] == None or raw_personal_info[key] == '' or raw_personal_info[key] == "":
                post_info[key] = ''
            else:
                post_info[key] = raw_personal_info[key]
        elif key in raw_personal_info2:
            if raw_personal_info2[key] == 'null' or raw_personal_info2[key] == None or raw_personal_info2[key] == '' or raw_personal_info2[key] == "":
                post_info[key] = ''
            else:
                post_info[key] = raw_personal_info2[key]
        else:
            post_info[key] = ''

    logger.info('模拟提交中>>>>>>')
    msg_all += '模拟提交中>>>>>>'+"\n"

    startFlow_data = {
        'formData': str(post_info),
        'sendMessage': 'true',
        'id': 'start',
        'commandType': 'start',
        'execute': 'do_start',
        'name': '提交',
        'url': '/sys/emapflow/tasks/startFlow.do',
        'buttonType': 'success',
        'taskId': '',
        'defKey': 'lwWiseduElectronicPass.MainFlow'
    }

    # startFlow
    startFlow_response = sess.post(startFlow, startFlow_data)
    logger.info(startFlow_response.text)
    msg_all += startFlow_response.text+"\n"
    if "true" in startFlow_response.text:
        logger.info("入校申请成功")
        msg_all += "入校申请成功"+"\n"
        return
    else:
        logger.info("入校申请失败")
        msg_all += "入校申请失败"+"\n"
        return

def bark_post(Subject, Message, Sckey):
    url = 'https://api.day.app/' + Sckey + '/' + Subject + '/' + Message
    r = requests.get(url)

if __name__ == '__main__':
    msg_all_total = ""
    logger.info("\n===入校===\n")
    msg_all_total += "\n===入校===\n"+"\n"
    url = "https://newids.seu.edu.cn/authserver/login?service=http%3A%2F%2Fehall.seu.edu.cn%2Fqljfwapp3%2Fsys%2FlwWiseduElectronicPass%2Findex.do"
    for user in user_acounts_list:
        if user["id"] in user_admmsion_list:
            msg_all = ""
            logger.info("------------开始【"+user["id"]+"】------------")
            msg_all += "------------开始【"+user["id"]+"】------------"+"\n"
            is_login, ss, user_info = login(url, user["id"], user["pwd"])
            if is_login:
                logger.info("SEU登录成功")
                msg_all += "SEU登录成功"+"\n"
                askForAdimission(ss, user["id"], user_info)
                msg_all_total += msg_all
            else:
                logger.info("SEU登录失败")
                msg_all += "SEU登录失败"+"\n"
                msg_all_total += msg_all
            if user["barkkey"]!="":
                bark_post('入校', msg_all, user["barkkey"])
            ss.close()
    if Total_Bark_Key!="":
        bark_post('入校ALL', msg_all_total, Total_Bark_Key)
