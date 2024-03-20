import requests

# 发送短信(需自行配置),此处为短信宝(http://console.smsbao.com/#/login)接口
def send(phone, text):
    user = "yourusername"
    key = "yourkey"
    text = "【yoursign】" + text
    url = f"https://api.smsbao.com/sms?u={user}&p={key}&m={phone}&c={text}"
    response = requests.get(url)

    statusStr = {
        '0': '短信发送成功',
        '-1': '参数不全',
        '-2': '服务器空间不支持,请确认支持curl或者fsocket,联系您的空间商解决或者更换空间',
        '30': '密码错误',
        '40': '账号不存在',
        '41': '余额不足',
        '42': '账户已过期',
        '43': 'IP地址限制',
        '50': '内容含有敏感词'
    }
    print(f"{statusStr[response.text]}\n")
    print(text)
