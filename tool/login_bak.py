import execjs
import logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

with open("./tool/encrypt.js") as f:
    js_content = f.read()

f = open("./tool/encrypt.js", 'r', encoding='UTF-8')
line = f.readline()
js = ''
while line:
    js = js + line
    line = f.readline()

def encryptAES(data, salt):
    ctx = execjs.compile(js)
    password = ctx.call('_ep', data, salt)
    logger.info("Encrypted passwd:" + password)
    return password
