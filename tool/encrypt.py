import js2py
context = js2py.EvalJs()

with open("./tool/encrypt.js") as f:
    js_content = f.read()

def encryptAES(data, salt):
    context.execute(js_content)
    result = context.encryptAES(data, salt)
    print("Encrypted passwd:", result)
    return result