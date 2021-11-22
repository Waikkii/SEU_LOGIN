import re
import os
import json
import time
import random
import requests
import datetime
from urllib import parse
from tool.login import login
import time
from time import sleep
import logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

with open("./config/acounts.json", "r", encoding="utf-8") as f:
    acounts = json.loads(f.read())

with open("./config/leave.json", "r", encoding="utf-8") as f:
    leave_val = json.loads(f.read())

if "ACOUNTS" in os.environ:
    acounts = os.environ["ACOUNTS"]
if "LEAVE" in os.environ:
    leave_val = os.environ["LEAVE"]

Total_Bark_Key = acounts['Total_Bark_Key']
user_acounts_list = acounts['Users']
user_leave_list = leave_val['Users']

headers = dict()

def get_info(sess, username):
    personal_info_url = 'http://ehall.seu.edu.cn/ygfw/sys/xsqjappseuyangong/modules/wdqj/wdqjbg.do'
    get_personal_info = sess.post(personal_info_url, data={'XSBH': str(username), 'pageSize': '10', 'pageNumber': '1'}, headers=headers)
    return get_personal_info

def get_info_2(sess, SQBH):
    url = "http://ehall.seu.edu.cn/ygfw/sys/xsqjappseuyangong/modules/wdqj/qjxqbd.do"
    headers['Content-Type'] = 'application/x-www-form-urlencoded;charset=utf-8'
    FormData = {'SQBH': SQBH}
    data = parse.urlencode(FormData)
    get_personal_info = sess.post(url, data=data, headers=headers)
    get_personal_info = json.loads(get_personal_info.text)['datas']['qjxqbd']['rows']
    get_personal_info = get_personal_info[0]
    return get_personal_info

# 获取未销假
def getAllNoRemoveLeave(sess, username):
    url = "http://ehall.seu.edu.cn/ygfw/sys/xsqjappseuyangong/modules/leaveApply/getAllNoRemoveLeave.do"
    headers['Content-Type'] = 'application/x-www-form-urlencoded;charset=utf-8'
    FormData = {"requestParamStr": {'XSBH': str(username)}}
    data = parse.urlencode(FormData)

    get_personal_info = sess.post(url, data=data, headers=headers)
    if "data" in get_personal_info.text:
        j = json.loads(get_personal_info.text)['data']
        return addXjApply(sess, j)
    return False


# 销假
def addXjApply(sess, datas):
    global msg_all
    url = "http://ehall.seu.edu.cn/ygfw/sys/xsqjappseuyangong/modules/leaveApply/addXjApply.do"
    headers['Content-Type'] = 'application/x-www-form-urlencoded;charset=utf-8'
    for data in datas:
        now_time = datetime.datetime.now()
        if now_time.strftime("%Y-%m-%d") not in data['QJKSRQ'] and (now_time + datetime.timedelta(days=+1)).strftime(
                "%Y-%m-%d") not in data['QJKSRQ']:
            logger.info("销假: "+data["QJKSRQ"])
            msg_all += "销假: "+data["QJKSRQ"]+"\n"
            post_info = {
                "data": {"SQBH": "52b347e055e348c9abd2394694f3a613", "XSBH": 0, "SHZT": "20", "XJFS": "2",
                         "XJSJ": "", "XJRQ": "", "SQR": "", "SQRXM": "",
                         "THZT": "0"}}
            post_info["data"]["SQBH"] = data["SQBH"]
            post_info["data"]["XSBH"] = int(data["XSBH"])
            post_info["data"]["XJSJ"] = now_time.strftime("%Y-%m-%d %H:%M:%S")
            post_info["data"]["XJRQ"] = now_time.strftime("%Y-%m-%d")
            post_info["data"]["SQR"] = data["XSBH"]
            post_info["data"]["SQRXM"] = data["XM"]
            data = parse.urlencode(post_info)
            get_personal_info = sess.post(url, data=data, headers=headers)
        else:
            if (now_time + datetime.timedelta(days=+1)).strftime("%Y-%m-%d") in data['QJKSRQ']:
                return True
    return False


# 获取未审批
def getAllApplyedLeave(sess, username):
    url = "http://ehall.seu.edu.cn/ygfw/sys/xsqjappseuyangong/modules/leaveApply/getAllApplyedLeave.do"
    headers['Content-Type'] = 'application/x-www-form-urlencoded;charset=utf-8'
    FormData = {"requestParamStr": {'XSBH': str(username)}}
    data = parse.urlencode(FormData)

    get_personal_info = sess.post(url, data=data, headers=headers)
    if "data" in get_personal_info.text:
        j = json.loads(get_personal_info.text)['data']
        return backleaveApply(sess, j)
    return False


# 撤回
def backleaveApply(sess, datas):
    global msg_all
    url = "http://ehall.seu.edu.cn/ygfw/sys/xsqjappseuyangong/modules/leaveApply/backleaveApply.do"
    headers['Content-Type'] = 'application/x-www-form-urlencoded;charset=utf-8'
    for data in datas:
        now_time = datetime.datetime.now()
        # 未审批的今天和明天的不撤回
        if now_time.strftime("%Y-%m-%d") not in data['QJKSRQ'] and (now_time + datetime.timedelta(days=+1)).strftime(
                "%Y-%m-%d") not in data['QJKSRQ']:
            logger.info("撤回: "+data["QJKSRQ"])
            msg_all += "撤回: "+data["QJKSRQ"]+"\n"
            post_info = {"requestParamStr": {"SQBH": data["SQBH"]}}
            data = parse.urlencode(post_info)
            get_personal_info = sess.post(url, data=data, headers=headers)
        else:
            return True
    return False

# 删除草稿
def delleaveApply(sess, datas):
    global msg_all
    url = "http://ehall.seu.edu.cn/ygfw/sys/xsqjappseuyangong/modules/leaveApply/delleaveApply.do"
    headers['Content-Type'] = 'application/x-www-form-urlencoded;charset=utf-8'
    for data in datas:
        if data["SHZT_DISPALY_DISPLAY"] == "草稿":
            logger.info("删除草稿: "+data["QJKSRQ"])
            msg_all += "删除草稿: "+data["QJKSRQ"]+"\n"
            post_info = {"requestParamStr": {"SQBH": data["SQBH"]}}
            data = parse.urlencode(post_info)
            get_personal_info = sess.post(url, data=data, headers=headers)

def leave(sess, id):
    global msg_all
    cookie_url = 'http://ehall.seu.edu.cn/ygfw/sys/swpubapp/indexmenu/getAppConfig.do?appId=5869188708264821&appName=xsqjappseuyangong&v=06154290794922301'
    get_cookie = sess.get(cookie_url)
    cookie = requests.utils.dict_from_cookiejar(sess.cookies)
    c = ""
    for key, value in cookie.items():
        c += key + "=" + value + "; "
    headers['Referer'] = 'http://ehall.seu.edu.cn/ygfw/sys/xsqjappseuyangong/*default/index.do'
    headers['Cookie'] =  c
    
    # 获取未销假
    r = getAllNoRemoveLeave(sess, id)
    if r:
        logger.info("已有请假!  已经存在未销假的请假")
        msg_all += "已有请假!  已经存在未销假的请假"+"\n"
        return

    # 获取未审批
    r = getAllApplyedLeave(sess, id)
    if r:
        logger.info("已有请假!  已经存在未审批的请假")
        msg_all += "已有请假!  已经存在未审批的请假"+"\n"
        return

    # 删除草稿
    get_personal_info = get_info(sess, id)
    raw_personal_info = json.loads(get_personal_info.text)['datas']['wdqjbg']['rows']
    delleaveApply(sess, raw_personal_info)

    get_personal_info = get_info(sess, id)
    if get_personal_info.status_code == 200:
        logger.info('获取前一日信息成功!')
        msg_all += '获取前一日信息成功!'+"\n"
    else:
        logger.info("获取信息失败!")
        msg_all += "获取信息失败!"+"\n"
        return

    raw_personal_info = json.loads(get_personal_info.text)['datas']['wdqjbg']['rows'][0]
    raw_personal_info = get_info_2(sess, raw_personal_info["SQBH"])

    datas = {"QJLX_DISPLAY": "不涉及职能部门", "QJLX": "3bc0d68330fd4d869152238251b867ee", "DZQJSY_DISPLAY": "因事出校（当天往返）",
             "DZQJSY": "763ec35f8f5545c0aa245e8fbc20adb2", "QJXZ_DISPLAY": "因公", "QJXZ": "2", "QJFS_DISPLAY": "请假",
             "QJFS": "1", "YGLX_DISPLAY": "实验", "YGLX": "3", "SQSM": "", "QJKSRQ": "",
             "QJJSRQ": "", "QJTS": "1", "QJSY": "去无线谷", "ZMCL": "", "SJH": "",
             "DZSFLX_DISPLAY": "是", "DZSFLX": "1", "HDXQ_DISPLAY": "九龙湖校区", "HDXQ": "1", "DZSFLN_DISPLAY": "否",
             "DZSFLN": "0", "DZSFLKJSS_DISPLAY": "", "DZSFLKJSS": "", "DZ_SFCGJ_DISPLAY": "", "DZ_SFCGJ": "",
             "DZ_GJDQ_DISPLAY": "", "DZ_GJDQ": "", "QXSHEN_DISPLAY": "", "QXSHEN": "", "QXSHI_DISPLAY": "", "QXSHI": "",
             "QXQ_DISPLAY": "", "QXQ": "", "QXJD": "", "XXDZ": "无线谷", "JTGJ_DISPLAY": "", "JTGJ": "", "CCHBH": "",
             "SQBH": "", "XSBH": "", "JJLXR": "", "JJLXRDH": "",
             "JZXM": "", "JZLXDH": "", "DSXM": "", "DSDH": "", "FDYXM": "",
             "FDYDH": "", "SFDSQ": "0"}
    post_info = {}
    for key, value in datas.items():
        if key in raw_personal_info:
            if raw_personal_info[key] == 'null' or raw_personal_info[key] == None:
                post_info[key] = ''
            else:
                post_info[key] = raw_personal_info[key]
        else:
            post_info[key] = value
    if post_info['QJSY'] == '':
        post_info['QJSY'] = "去无线谷科研"
    post_info['SQBH'] = ''
    now_time = datetime.datetime.now()
    post_info["QJKSRQ"] = (now_time + datetime.timedelta(days=+1)).strftime("%Y-%m-%d 07:00")
    post_info["QJJSRQ"] = (now_time + datetime.timedelta(days=+1)).strftime("%Y-%m-%d 23:00")

    save_url = 'http://ehall.seu.edu.cn/ygfw/sys/xsqjappseuyangong/modules/leaveApply/addLeaveApply.do'
    headers['Content-Type'] = 'application/x-www-form-urlencoded;charset=utf-8'
    FormData = {'data': post_info}
    data = parse.urlencode(FormData)

    save = sess.post(save_url, data=data, headers=headers)

    if "成功" in save.text:
        logger.info("请假成功！")
        msg_all += "请假成功！"+"\n"
        return
    else:
        logger.info("请假失败！")
        msg_all += "请假失败！"+"\n"
        return

def bark_post(Subject, Message, Sckey):
    url = 'https://api.day.app/' + Sckey + '/' + Subject + '/' + Message
    r = requests.get(url)

if __name__ == '__main__':
    msg_all_total = ""
    logger.info("\n===请假===\n")
    msg_all_total += "\n===请假===\n"+"\n"
    url = "https://newids.seu.edu.cn/authserver/login?service=http%3A%2F%2Fehall.seu.edu.cn%2Fqljfwapp3%2Fsys%2FlwWiseduElectronicPass%2Findex.do"
    for user in user_acounts_list:
        if leave_val['ALL'] or user["id"] in user_leave_list:
            msg_all = ""
            logger.info("------------开始【"+user["id"]+"】------------")
            msg_all += "------------开始【"+user["id"]+"】------------"+"\n"
            is_login, ss, user_info = login(url, user["id"], user["pwd"])
            if is_login:
                logger.info("SEU登录成功")
                msg_all += "SEU登录成功"+"\n"
                leave(ss, user["id"])
                msg_all_total += msg_all
            else:
                logger.info("SEU登录失败")
                msg_all += "SEU登录失败"+"\n"
                msg_all_total += msg_all
            if user["barkkey"]!="":
                bark_post('请假', msg_all, user["barkkey"])
                logger.info(user["barkkey"]+"个人推送成功")
            ss.close()
            logger.info("模拟等待10s......")
            sleep(10)
    if Total_Bark_Key!="":
        bark_post('请假ALL', msg_all_total, Total_Bark_Key)
        logger.info(Total_Bark_Key+"管理员推送成功")
