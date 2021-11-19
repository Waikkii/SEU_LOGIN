# encoding=utf-8
import requests
import json
from tool.encrypt import encryptAES
from bs4 import BeautifulSoup
import logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

def login(url, id, pwd):
    ss = requests.Session()
    form = {"username": id}
    res = ss.get(url)
    soup = BeautifulSoup(res.text, 'html.parser')
    attrs = soup.select('[tabid="01"] input[type="hidden"]')
    for k in attrs:
        if k.has_attr('name'):
            form[k['name']] = k['value']
        elif k.has_attr('id'):
            form[k['id']] = k['value']
    form['password'] = encryptAES(pwd, form['pwdDefaultEncryptSalt'])
    res = ss.post(url, data=form)
    res.encoding = 'utf-8'
    ss.get('http://ehall.seu.edu.cn/login?service=http://ehall.seu.edu.cn/new/index.html')
    res_test = ss.get('http://ehall.seu.edu.cn/jsonp/userDesktopInfo.json')
    json_res_test = json.loads(res_test.text)
    try:
        name = json_res_test["userName"]
        logger.info(name + "Login Success!")
    except Exception:
        logger.info("Login Fail!")
        return False, ss, res_test
    return True, ss, res
