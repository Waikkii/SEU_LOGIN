# encoding=utf-8
import requests
import json
from tool.encrypt import encryptAES
from bs4 import BeautifulSoup

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
    ss.get('http://ehall.seu.edu.cn/login?service=http://ehall.seu.edu.cn/new/index.html')
    res = ss.get('http://ehall.seu.edu.cn/jsonp/userDesktopInfo.json')
    json_res = json.loads(res.text)
    try:
        name = json_res["userName"]
        print(name, "Login Success!")
    except Exception:
        print("Login Fail!")
        return False
    return ss