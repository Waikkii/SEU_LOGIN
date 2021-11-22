import re
import os
import json
import time
import random
import requests
from urllib import parse
from tool.login import login
import logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

with open("./config/acounts.json", "r", encoding="utf-8") as f:
    acounts = json.loads(f.read())

with open("./config/report.json", "r", encoding="utf-8") as f:
    report_val = json.loads(f.read())

if "ACOUNTS" in os.environ:
    acounts = os.environ["ACOUNTS"]
if "REPORT" in os.environ:
    report_val = os.environ["REPORT"]

Total_Bark_Key = acounts['Total_Bark_Key']
user_acounts_list = acounts['Users']
user_report_list = report_val['Users']

headers = dict()

def get_wendu_info(sess, header):
    personal_info_url = 'http://ehall.seu.edu.cn/qljfwapp2/sys/lwReportEpidemicSeu/modules/dailyReport/getMyDailyReportDatas.do'
    get_personal_info = sess.post(personal_info_url, data={'rysflb': 'BKS', 'pageSize': '10', 'pageNumber': '1'},
                                  headers=header)
    return get_personal_info

def report(sess):
    global cookie_url 
    global msg_all
    province='江苏省'
    city='南京市'
    district='江宁区'
    LAT='31.88373374938965'
    LON='118.80831146240234'
    try:
        cookie_url = 'http://ehall.seu.edu.cn/qljfwapp2/sys/lwReportEpidemicSeu/configSet/noraml/getRouteConfig.do'
        get_cookie = sess.get(cookie_url)
        weu = requests.utils.dict_from_cookiejar(get_cookie.cookies)['_WEU']
        cookie = requests.utils.dict_from_cookiejar(sess.cookies)
        headers['Referer'] = 'http://ehall.seu.edu.cn/qljfwapp2/sys/lwReportEpidemicSeu/index.do'
        headers['Cookie'] =  '_WEU=' + weu + '; MOD_AUTH_CAS=' + cookie['MOD_AUTH_CAS'] + ';'
        get_personal_info = get_wendu_info(sess, headers)
        if get_personal_info.status_code == 403:
            raise
    except:
        cookie_url2 = 'http://ehall.seu.edu.cn/qljfwapp2/sys/itpub/common/changeAppRole/lwReportEpidemicSeu/20200223030326996.do'
        get_cookie = sess.get(cookie_url2)
        weu = requests.utils.dict_from_cookiejar(get_cookie.cookies)['_WEU']
        cookie = requests.utils.dict_from_cookiejar(sess.cookies)
        headers['Referer'] = 'http://ehall.seu.edu.cn/qljfwapp2/sys/lwReportEpidemicSeu/index.do'
        headers['Cookie'] =  '_WEU=' + weu + '; MOD_AUTH_CAS=' + cookie['MOD_AUTH_CAS'] + ';'
        get_personal_info = get_wendu_info(sess, headers)

    if get_personal_info.status_code == 200:
        logger.info('获取前一日信息成功!')
        msg_all += '获取前一日信息成功!'+"\n"
    else:
        logger.info("获取信息失败!")
        msg_all += '获取信息失败!'+"\n"
        return

    get_personal_info.encoding = 'utf-8'
    raw_personal_info = re.search('"rows":\[\{(.*?)}', get_personal_info.text).group(1)
    try:
        DZ_DQWZ = re.search('"DZ_DQWZ":"(.*?)"', raw_personal_info).group(1)
    except:
        DZ_DQWZ = ''
    raw_personal_info = json.loads('{' + raw_personal_info + '}')

    datas = "USER_ID=&PHONE_NUMBER=&IDCARD_NO=&GENDER_CODE=&DZ_MQSFWYSBL=&EMERGENCY_CONTACT_PERSON=&DZ_JQSTZK_DISPLAY=&DZ_ZHLKRQ=&REMARK=&EMERGENCY_CONTACT_NATIVE=&DZ_YXBMSFYSH_DISPLAY=&DZ_JRSFFS=&DZ_JTQY_DISPLAY=&DZ_GLJSSJ=&DZ_GLKSSJ=&EMERGENCY_CONTACT_HOME=&RYSFLB=&DZ_YSGLJZSJ=&DZ_YS_GLJZDCS_DISPLAY=&DZ_MQZNJWZ=&DZ_YWQTXGQK=&LOCATION_PROVINCE_CODE_DISPLAY=&DZ_SFDK=&HEALTH_STATUS_CODE=&DZ_DBRQ=&DZ_SFYJCS6_DISPLAY=&LOCATION_DETAIL=&DZ_WJZYMYY_DISPLAY=&DZ_SZWZLX=&DZ_SDXQ_DISPLAY=&DZ_JRSFYXC_DISPLAY=&DZ_DQWZ_QX=&DZ_DTWJTW=&DZ_JQSTZK=&DZ_WJZYMQTYY=&DZ_JJXFBD_CS_DISPLAY=&DZ_YS_GLJZDSF_DISPLAY=&DZ_WD=&DZ_SFYJCS10=&LOCATION_PROVINCE_CODE=&DZ_SZWZLX_DISPLAY=&HEALTH_STATUS_CODE_DISPLAY=&DZ_YXBMSFYSH=&DZ_SZWZ_GJ_DISPLAY=&DZ_SFYJCS8_DISPLAY=&BY6=&BY5=&DZ_SFLXBXS=&BY4=&BY3=&BY2=&DZ_YJZCDDGNRQ=&BY1=&DZ_JTFS=&DZ_QZ_GLJZDCS_DISPLAY=&DZ_MQSFWYSBL_DISPLAY=&DZ_JRSFYXC=&LOCATION_COUNTY_CODE=&DZ_SFYJCS2_DISPLAY=&DZ_QZ_GLJZDSF=&MENTAL_STATE=&DZ_SFDXBG=&IS_SEE_DOCTOR_DISPLAY=&BY14=&BY15=&BY12=&BY13=&BY18=&BY19=&BY16=&BY17=&DZ_XYYYPJG_DISPLAY=&DZ_DQWZ_JD=&BY10=&BY11=&DZ_JRSFFS_DISPLAY=&DZ_JRSTZK_DISPLAY=&CZR=&DZ_QZGLJZSJ=&DZ_YXBMCPQKSM=&DZ_SFYJCS9_DISPLAY=&CZZXM=&BY20=&HEALTH_UNSUAL_CODE_DISPLAY=&DZ_YMJZRQ1=&DZ_ZHJCGGRYSJ=&DZ_YMJZRQ2=&CLASS_CODE=&DZ_SYJTGJ_DISPLAY=&DZ_QZ_GLJZDCS=&DZ_SFGL=&DEPT_CODE=&CHECKED=&DZ_GLDQ=&CREATED_AT=&DZ_SFYJCS7_DISPLAY=&USER_NAME=&LOCATION_CITY_CODE=&BY7=&MEMBER_HEALTH_STATUS_CODE=&BY8=&BY9=&DZ_MDDSZSF_DISPLAY=&DZ_QZ_GLJZDSF_DISPLAY=&DZ_JCQKSM=&GENDER_CODE_DISPLAY=&DZ_SFYBH=&DZ_GLDCS=&DZ_GLDSF_DISPLAY=&DZ_GLDSF=&DZ_YXBMCPJG_DISPLAY=&DZ_SFYJCS10_DISPLAY=&DZ_DQWZ_WD=&DZ_DQWZ=&DZ_SFYJCS3_DISPLAY=&EMERGENCY_CONTACT_PHONE=&DZ_YS_GLJZDCS=&DZ_GLSZDQ=&DZ_MDDSZCS_DISPLAY=&DZ_JTFS_DISPLAY=&DZ_JRSTZK=&DZ_SFDXBG_DISPLAY=&DZ_SMJTQK=&DZ_WJZYMYY=&DZ_SFYSH_DISPLAY=&DZ_JJXFBSJ=&DZ_JSDTCJTW=&USER_NAME_EN=&DZ_SZXQ_DISPLAY=&DZ_JJXFBD_SF_DISPLAY=&DZ_MDDSZCS=&DZ_MDDSZSF=&MEMBER_HEALTH_UNSUAL_CODE=&DZ_CCBC=&DZ_SZWZ_GJ=&DZ_SFYBH_DISPLAY=&DZ_YS_GLJZDSF=&DZ_SFYSH=&IS_SEE_DOCTOR=&DZ_GLDQ_DISPLAY=&DZ_MQSFWQRBL=&CLASS=&MEMBER_HEALTH_STATUS_CODE_DISPLAY=&DZ_SFYJCS1_DISPLAY=&SAW_DOCTOR_DESC=&DZ_ZDYPJG_DISPLAY=&DZ_XYYSFYSH_DISPLAY=&DZ_ZHJCHZSJ=&DZ_ZZSM=&DZ_SFGL_DISPLAY=&DZ_DQWZ_SF=&DZ_GRYGLSJ1=&DZ_DTWSJCTW=&DZ_YWQTXGQK_DISPLAY=&DZ_GRYGLSJ2=&DZ_SFYJCS5_DISPLAY=&DZ_DQWZ_CS=&DZ_TWDS=&DZ_SZXQ=&DZ_XYYYPJG=&MENTAL_STATE_DISPLAY=&DZ_ZHJCGRYSJ1=&DZ_ZHJCGRYSJ2=&DZ_SYJTGJ=&HEALTH_UNSUAL_CODE=&DZ_XYYSFYSH=&CZRQ=&LOCATION_COUNTY_CODE_DISPLAY=&DZ_SFYJCS4=&DZ_SFYJCS3=&DZ_BRYWYXFH=&DZ_SFYJCS2=&DZ_SFYJCS1=&WID=&DZ_MQSFWQRBL_DISPLAY=&DEPT_NAME=&DZ_QKSM=&DZ_SFYJCS9=&DZ_SFYJCS8=&DZ_SFYJCS7=&DZ_SFYJCS6=&DZ_SFYJCS5=&DZ_BRYWYXFH_DISPLAY=&DZ_SDXQ=&LOCATION_CITY_CODE_DISPLAY=&DZ_SFLXBXS_DISPLAY=&DZ_ZDYPJG=&DZ_SZWZXX=&DZ_JJXFBD_CS=&DZ_JTQY=&MEMBER_HEALTH_UNSUAL_CODE_DISPLAY=&DZ_YXBMCPJG=&DZ_JJXFBD_SF=&DZ_SFYJCS4_DISPLAY=&DZ_GLDCS_DISPLAY=&DZ_YMJZD1=&NEED_CHECKIN_DATE=&DZ_YMJZD2="
    datas = parse.parse_qs(datas, keep_blank_values=True)
    post_key = []
    for data in datas:
        post_key.append(data)

    post_info = {}
    for key in post_key:
        if key in raw_personal_info:
            if raw_personal_info[key] == 'null' or raw_personal_info[key] == None:
                post_info[key] = ''
            else:
                post_info[key] = raw_personal_info[key]
        else:
            post_info[key] = ''

    post_info['DZ_DQWZ'] = DZ_DQWZ
    post_info['DZ_SFYBH'] = '0'
    post_info['DZ_DBRQ'] = time.strftime("%Y-%m-%d", time.localtime())
    post_info['CREATED_AT'] = time.strftime("%Y-%m-%d %H:%M", time.localtime())
    post_info['NEED_CHECKIN_DATE'] = time.strftime("%Y-%m-%d", time.localtime())
    post_info['DZ_SFLXBXS'] = ''
    post_info['DZ_ZDYPJG'] = ''
    post_info['DZ_JSDTCJTW'] = '36.%d' % random.randint(0, 4)
    if district != '':
        post_info['DZ_DQWZ_WD'] = LON  # 经度, ,
        post_info['DZ_DQWZ'] = province + ', ' + city + ', ' + district
        post_info['DZ_DQWZ_QX'] = district
        post_info['DZ_DQWZ_SF'] = province
        post_info['DZ_DQWZ_CS'] = city
        post_info['DZ_DQWZ_JD'] = LAT  # 纬度
    save_url = 'http://ehall.seu.edu.cn/qljfwapp2/sys/lwReportEpidemicSeu/modules/dailyReport/T_REPORT_EPIDEMIC_CHECKIN_SAVE.do'
    save = sess.post(save_url, data=post_info, headers=headers)
    if save.status_code == 200:
        logger.info('打卡成功!')
        msg_all += "打卡成功"+"\n"
        return
    else:
        logger.info("打卡失败!")
        msg_all += "打卡失败"+"\n"
        return

def bark_post(Subject, Message, Sckey):
    url = 'https://api.day.app/' + Sckey + '/' + Subject + '/' + Message
    r = requests.get(url)

if __name__ == '__main__':
    msg_all_total = ""
    logger.info("\n===上报===\n")
    msg_all_total += "\n===上报===\n"+"\n"
    url = "https://newids.seu.edu.cn/authserver/login?service=http%3A%2F%2Fehall.seu.edu.cn%2Fqljfwapp3%2Fsys%2FlwWiseduElectronicPass%2Findex.do"
    for user in user_acounts_list:
        if report_val['ALL'] or user["id"] in user_report_list:
            msg_all = ""
            logger.info("------------开始【"+user["id"]+"】------------")
            msg_all += "------------开始【"+user["id"]+"】------------"+"\n"
            is_login, ss, user_info = login(url, user["id"], user["pwd"])
            if is_login:
                logger.info("SEU登录成功")
                msg_all += "SEU登录成功"+"\n"
                report(ss)
                msg_all_total += msg_all
            else:
                logger.info("SEU登录失败")
                msg_all += "SEU登录失败"+"\n"
                msg_all_total += msg_all
            if user["barkkey"]!="":
                bark_post('上报', msg_all, user["barkkey"])
                logger.info(user["barkkey"]+"个人推送成功")
            ss.close()
    if Total_Bark_Key!="":
        bark_post('上报ALL', msg_all_total, Total_Bark_Key)
        logger.info(Total_Bark_Key+"管理员推送成功")
