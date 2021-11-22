import re
import os
import json
import time
import gevent
from gevent import monkey#打补丁（把下面有可能有IO操作的单独做上标记）
monkey.patch_all()
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
    acounts = os.environ["ACOUNTS"]
if "LECTURE" in os.environ:
    lecture_val = os.environ["LECTURE"]

Total_Bark_Key = acounts['Total_Bark_Key']
user_acounts_list = acounts['Users']
user_lecture_list = lecture_val['Users']

headers = dict()

def sbsplit(str):
    #考虑
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

def lecture(session, id, whitelist, blacklist, location, master_barkkey, barkkey):
    global msg_all

    if whitelist!="":
        logger.info("指定白名单过滤："+str(sbsplit(whitelist)))
    elif blacklist!="":
        logger.info("未找到指定白名单，开启黑名单过滤模式："+str(sbsplit(blacklist)))
    else:
        logger.info("未找到指定白名单和黑名单，不进行过滤")

    if location!="":
        logger.info("指定地点为"+str(sbsplit(location)))
    else:
        logger.info("未找到指定地点，不进行过滤")

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
            bark_temp_url = 'https://api.day.app/' + master_barkkey + '/' + '讲座' + '/' + id + '已超过最大运行次数，未抢到讲座'
            requests.get(bark_temp_url)
            continued = False
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

                if counter==1 and choose_flag and location_flag and time_flag:
                    logger.info("可抢讲座名："+str(item['JZMC'])+"，讲座日期："+str(item['JZSJ'])+"，讲座地点："+str(item['JZDD']))
                    
                
                if choose_flag and location_flag and time_flag and (lecture_signal != '0'):
                    wid = item['WID']
                    url = f'http://ehall.seu.edu.cn/gsapp/sys/jzxxtjapp/hdyy/yySave.do?paramJson=%7B%22HD_WID%22%3A%22{wid}%22%7D'
                    result = session.get(url, verify = False)
                    success = json.loads(result.content.decode())['success']
                    if success == True:
                        logger.info(id + "讲座预订成功！讲座名："+str(item['JZMC'])+"，讲座日期："+str(item['JZSJ'])+"，讲座地点："+str(item['JZDD']))
                        if master_barkkey!="":
                            bark_post(item, id, master_barkkey)
                        if barkkey!="":
                            bark_post(item, id, barkkey)
                        continued = False
                        break
        except Exception as e:
            logger.info(e)
            pass

def bark_post(item, id, Sckey):
    mail_title = '讲座'
    mail_content = id + '讲座预订成功，信息如下：\n' + \
        f'讲座名称：{item["JZMC"]}\n' + \
        f'讲座时间：{item["JZSJ"]}\n' + \
        f'讲座地点：{item["JZDD"]}\n' + \
        f'主讲人：{item["ZJR"]}'
    url = 'https://api.day.app/' + Sckey + '/' + mail_title + '/' + mail_content
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
        lecture(ss, user["id"], useruser["whitelist"], user["blacklist"], user["location"], Total_Bark_Key, barkkey)
    else:
        logger.info("SEU登录失败")
        msg_all += "SEU登录失败"+"\n"
    if barkkey!="":
        bark_post('讲座', msg_all, barkkey)
    ss.close()

if __name__ == '__main__':
    msg_all = ""
    logger.info("\n===讲座===\n")
    msg_all += "\n===讲座===\n"+"\n"
    url = "https://newids.seu.edu.cn/authserver/login?goto=http://my.seu.edu.cn/index.portal"
    gevent_queue = []
    for user in user_lecture_list:
        gevent_queue.append(gevent.spawn(gevent_do, user))
    logger.info(f'开启{len(gevent_queue)}线程>>>>>>')
    gevent.joinall(gevent_queue)
