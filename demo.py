import json
from tool.login import login

with open("./config/acounts.json", "r", encoding="utf-8") as f:
    userconfigs_list = json.loads(f.read())['Users']

def Customized_Scripts(session):
    print("Test")

if __name__ == '__main__':
    url = "https://newids.seu.edu.cn/authserver/login?goto=http://my.seu.edu.cn/index.portal"
    for user in userconfigs_list:
        is_login, ss, user_info = login(url, user["id"], user["pwd"])
        if is_login:
            Customized_Scripts(ss)
