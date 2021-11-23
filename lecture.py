import re
import os
import json
import time
import threading
import requests
from urllib import parse
from tool.login import login
import logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

with open("./config/acounts.json", "r", encoding="utf-8") as f:
    acounts = json.loads(f.read())

with open("./config/lecture.json", "r", encoding="utf-8") as f:
    lecture_val = json.loads(f.read())

if "ACOUNTS" in os.environ:
    acounts = json.loads(os.environ["ACOUNTS"])
if "LECTURE" in os.environ:
    lecture_val = json.loads(os.environ["LECTURE"])

Total_Bark_Key = acounts['Total_Bark_Key']
user_acounts_list = acounts['Users']
user_lecture_list = lecture_val['Users']

headers = dict()

def sbsplit(str):
    #，
    #,
    #,空格
    #三种情况
    if "， " in str:
        return str.split('， ')
    elif "，" in str:
        return str.split('，')
    elif ", " in str:
        return str.split(', ')
    elif "," in str:
        return str.split(',')
    elif " " in str:
        return str.split(' ')
    else:
        return [str]

def lecture(session, whitelist, blacklist, location, msg_all):
    if whitelist!="":
        logger.info("指定白名单过滤："+str(sbsplit(whitelist)))
        msg_all += "指定白名单过滤："+"\n"
    elif blacklist!="":
        logger.info("未找到指定白名单，开启黑名单过滤模式："+str(sbsplit(blacklist)))
        msg_all += "未找到指定白名单，开启黑名单过滤模式："+str(sbsplit(blacklist))+"\n"
    else:
        logger.info("未找到指定白名单和黑名单，不进行过滤")
        msg_all += "未找到指定白名单和黑名单，不进行过滤"+"\n"

    if location!="":
        logger.info("指定地点为"+str(sbsplit(location)))
        msg_all += "指定地点为"+str(sbsplit(location))+"\n"
    else:
        logger.info("未找到指定地点，不进行过滤")
        msg_all += "未找到指定地点，不进行过滤"+"\n"

    continued = True
    counter = 0
    while continued:
        url = 'http://ehall.seu.edu.cn/appShow?appId=5736122417335219'
        session.get(url)

        url = 'http://ehall.seu.edu.cn/gsapp/sys/jzxxtjapp/modules/hdyy/hdxxxs.do'
        form_data = {
            'pageNumber': 1,
            'pageSize': 12
        }
        json_data = json.dumps(form_data)
        result = session.post(url, data = json_data, verify = False)
        counter = counter + 1
        if counter>=2:
            logger.info(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())+" 已超过最大运行次数，未抢到讲座")
            msg_all += time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())+" 已超过最大运行次数，未抢到讲座"+"\n"
            break
        logger.info(f'第{counter}次循环。')
        time.sleep(0.5)
        try:
            lecture_list = json.loads(result.content.decode())['datas']['hdxxxs']['rows']
            for item in lecture_list:
                lecture_type = item['JZXL_DISPLAY']
                lecture_place = item['JZDD']
                lecture_signal = item['YYRS']

                if whitelist!="":
                    choose_flag = lecture_type[-2:] in sbsplit(whitelist)
                elif blacklist!="":
                    choose_flag = lecture_type[-2:] not in sbsplit(blacklist)
                else:
                    choose_flag=True

                if location!="":
                    location_flag=False
                    for loca in sbsplit(location):
                        if loca in lecture_place:
                            location_flag=True
                            break
                else:
                    location_flag=True

                time_flag=item['YYKSSJ'].split(" ")[0]==time.strftime("%Y-%m-%d", time.localtime())
                
                if choose_flag and location_flag and time_flag:
                    if counter==1:
                        logger.info("可抢讲座名："+str(item['JZMC'])+"，讲座日期："+str(item['JZSJ'])+"，讲座地点："+str(item['JZDD']))
                        msg_all += "可抢讲座名："+str(item['JZMC'])+"，讲座日期："+str(item['JZSJ'])+"，讲座地点："+str(item['JZDD'])+"\n"
                    wid = item['WID']
                    url = f'http://ehall.seu.edu.cn/gsapp/sys/jzxxtjapp/hdyy/yySave.do?paramJson=%7B%22HD_WID%22%3A%22{wid}%22%7D'
                    result = session.get(url, verify = False)
                    success = json.loads(result.content.decode())['success']
                    if success == True:
                        success_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                        logger.info(success_time+" 讲座预订成功！讲座名："+str(item['JZMC'])+"，讲座日期："+str(item['JZSJ'])+"，讲座地点："+str(item['JZDD']))
                        msg_all += success_time+" 讲座预订成功！讲座名："+str(item['JZMC'])+"，讲座日期："+str(item['JZSJ'])+"，讲座地点："+str(item['JZDD'])+"\n"
                        continued = False
                        break
        except Exception as e:
            logger.info(e)
            msg_all += e
            pass

    return msg_all

def bark_post(Subject, Message, Sckey):
    url = 'https://api.day.app/' + Sckey + '/' + Subject + '/' + Message
    r = requests.get(url)

def gevent_do(user):
    for a in user_acounts_list:
        if a['id']==user["id"]:
            pwd=a['pwd']
            barkkey=a['barkkey']
    msg_all = ""
    logger.info("------------开始【"+user["id"]+"】------------")
    msg_all += "------------开始【"+user["id"]+"】------------"+"\n"
    is_login, ss, user_info = login(url, user["id"], pwd)
    if is_login:
        logger.info("SEU登录成功")
        msg_all += "SEU登录成功"+"\n"
        msg_out = lecture(ss, user["whitelist"], user["blacklist"], user["location"], msg_all)
        bark_post('讲座', msg_out, Total_Bark_Key)
        bark_post('讲座', msg_out, barkkey)
    else:
        logger.info("SEU登录失败")
        msg_all += "SEU登录失败"+"\n"
        bark_post('讲座', msg_all, Total_Bark_Key)
        bark_post('讲座', msg_all, barkkey)
    ss.close()

if __name__ == '__main__':
    msg_all = ""
    logger.info("\n===讲座===\n")
    msg_all += "\n===讲座===\n"+"\n"
    url = "https://newids.seu.edu.cn/authserver/login?goto=http://my.seu.edu.cn/index.portal"
    threads = []
    for user in user_lecture_list:
        threads.append(threading.Thread(target=gevent_do, args=(user,)))
    logger.info(f'开启{len(threads)}线程>>>>>>')
    
    for t in threads:
        t.setDaemon(True)
        t.start()

    for t in threads:
        t.join()
