import execjs


# 加密函数(教务系统)
def crypt_jwxt(msg):
    with open("./jscode/conwork.js", encoding="utf-8") as f:
        js = execjs.compile(f.read())
        return js.call("encodeInp", msg)


# 加解密函数(VPN)
def crypt_vpn(msg, salt, mode, basedir):
    with open("./jscode/encrypt.js", "r", encoding="utf-8") as f:
        js_code = f.read()
        ctx = execjs.compile(js_code, cwd=basedir)
    if mode == 0:  # 加密模式
        get_msg = ctx.call("encryptPassword", msg, salt)
    else:  # 解密模式
        get_msg = ctx.call("decryptPassword", msg, salt)
    return get_msg