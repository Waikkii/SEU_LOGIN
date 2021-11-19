import js2py
context = js2py.EvalJs()
import logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

with open("./tool/encrypt.js") as f:
    js_content = f.read()

def encryptAES(data, salt):
    context.execute(js_content)
    result = context.encryptAES(data, salt)
    logger.info("Encrypted passwd:" + result)
    return result
