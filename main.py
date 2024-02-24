import requests
from bs4 import BeautifulSoup
import ddddocr
import pyfiglet
import os
import execjs
import csv
import xlrd
import time

basedir = r"C:\Program Files\nodejs"  # node.js位置

url_jwxt_vpn = "https://webvpn.xaut.edu.cn/http/77726476706e69737468656265737421fae04690692869456a468ca88d1b203b/jsxsd/"
url_jwxt = "http://jwgl.xaut.edu.cn/jsxsd/"
# 目标网站

KeepPwd = ""  # 保存密码
Auto_ID = ""  # 自动识别验证码
user_vpn = ""  # WebVPN账户
pwd_vpn = ""  # WebVPN密码
user_jwxt = ""  # 教务系统账户
pwd_jwxt = ""  # 教务系统密码
default_term = ""  # 默认学期
r_session = requests.session()  # 自动获取会话session，保持会话
username = ""  # 记录用户名称


# 加密函数(教务系统)
def encode(msg):
    with open("./conwork.js", encoding="utf-8") as f:
        js = execjs.compile(f.read())
        return js.call("encodeInp", msg)


# 加解密函数(VPN)
def crypt(msg, salt, mode):
    with open("./encrypt.js", "r", encoding="utf-8") as f:
        js_code = f.read()
    ctx = execjs.compile(js_code, cwd=basedir)
    if mode == 0:  # 加密模式
        get_msg = ctx.call("encryptPassword", msg, salt)
    else:  # 解密模式
        get_msg = ctx.call("decryptPassword", msg, salt)
    return get_msg


# WebVPN登录
def vpn_login():
    global cookie, pwd_vpn
    url_vpn_login = "https://webvpn.xaut.edu.cn/https/77726476706e69737468656265737421f9f352d23f317d44300d8db9d6562d/authserver/login?service=https://webvpn.xaut.edu.cn/login?cas_login=true "
    response = r_session.get(url_vpn_login)

    soup = BeautifulSoup(response.text, "html.parser")
    execution = soup.find(id="execution")["value"]
    salt = soup.find(id="pwdEncryptSalt")["value"]

    if KeepPwd == "False":  # 未保存密码
        while True:
            pwd_vpn = input("请输入密码=>")
            inspect = input("确定吗？(输入Y/y以确认)=>")
            if inspect == 'Y' or inspect == 'y':
                print("保存成功！")
                break

    encodepwd = crypt(pwd_vpn, salt, 0)
    form_data = {
        "username": user_vpn,
        "password": encodepwd,
        "captcha": "",
        "rememberMe": "true",
        "_eventId": "submit",
        "cllt": "userNameLogin",
        "dllt": "generalLogin",
        "lt": "",
        "execution": execution
    }
    # 登录表单数据
    r_session.post(url_vpn_login, data=form_data)
    response = r_session.get("https://webvpn.xaut.edu.cn/")
    if response.url == "https://webvpn.xaut.edu.cn/":
        print("WebVPN登录成功！")
        return
    else:
        print("WebVPN登陆失败，请检查账户与密码是否正确！")
        exit(0)


# 获取教务系统登录验证码信息
def get_check(url):
    response = r_session.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    img_src = ""
    if url == url_jwxt_vpn:
        img_src = "https://webvpn.xaut.edu.cn" + soup.find(id="SafeCodeImg")["src"]
    elif url == url_jwxt:
        img_src = "http://jwgl.xaut.edu.cn/jsxsd/verifycode.servlet"
    else:
        print("未知网站！")
        exit(0)
    img_data = r_session.get(img_src).content
    # 保存验证码至本地
    with open('./教务系统验证码.jpg', 'wb') as fp:
        fp.write(img_data)
    if Auto_ID == "True":
        # 使用ddddocr模块自动识别验证码
        check = ddddocr.DdddOcr(show_ad="False").classification(img_data)
        print(f"ddddocr自动识别验证码为{check}")
    else:
        # 使用更为先进的人眼识别技术
        print("验证码下载成功，请手动识别验证码内容")
        check = input("验证码为：")
    return check
    # 验证码获取及验证，验证码图片与源码在同一目录下


# 教务系统登录
def jwxt_login(url):
    global pwd_jwxt
    url_jwxt_login = url + "xk/LoginToXk"  # 教务系统登录接口
    url_jwxt_main = url + "framework/xsMainV.htmlx"  # 主页

    if KeepPwd == "False":  # 未保存密码
        while True:
            pwd_jwxt = input("请输入密码=>")
            inspect = input("确定吗？(输入Y/y以确认)=>")
            if inspect == 'Y' or inspect == 'y':
                print("保存成功！")
                break

    encoded = str(encode(user_jwxt)) + "%%%" + str(encode(pwd_jwxt))
    # encoded数据，实际上采用base64编码，但此处选择调用conwork.js中的加密函数

    check = get_check(url)
    # 获取验证码相关信息

    form_data = {
        "userAccount": user_jwxt,
        "userPassword": pwd_jwxt,
        "RANDOMCODE": check,
        "encoded": encoded
    }
    # 登录表单数据

    r_session.post(url_jwxt_login, data=form_data)
    response = r_session.get(url_jwxt_main)
    # 登录数据POST发送至./xk/LoginToXk接口，从./framework/xsMainV.htmlx接口进行个人主页信息GET获取
    if response.status_code == 200 and response.url == url_jwxt_main:
        # 登录成功
        print("教务系统登录成功！")
    else:
        print("教务系统登录失败,请检查账户名、密码及验证码是否正确")
        exit(0)


# 成绩查询
def query_grades(url, term):
    kksj = term  # 开课时间，即查询的时段
    zylx = "0"

    url_jwxt_cj_cx = url + "kscj/cjcx_list?" + "kksj=" + kksj + "&" + "zylx=" + zylx  # 成绩查询网址
    response = r_session.get(url_jwxt_cj_cx)
    soup = BeautifulSoup(response.text, "html.parser")

    table = soup.find('table', {'id': 'dataList'})  # 使用ID定位表格
    course_list = []  # 存放课程数据的列表
    print("查询中，请稍后......")
    if table is not None and "未查询到数据" not in table.td:
        flag = 0  # 标记是不是第一行表头
        i = 0  # 统计数量
        table_rows = table.find_all('tr')  # 存放所有的tr标签数据
        for tr in table_rows:
            if flag == 0:
                flag = 1
                continue
            # 此处作用是排除第一条tr数据

            tds = tr.find_all('td')
            # 找出tr标签下所有td标签数据
            new_course = {
                "序号": tds[0].text.strip(),  # 序号
                "开课学期": tds[1].text.strip(),  # 开课学期
                "课程编号": tds[2].text.strip(),  # 课程编号
                "课程名称": tds[3].text.strip(),  # 课程名称
                "成绩": tds[4].text.strip(),  # 成绩
                "成绩标识": tds[5].text.strip(),  # 成绩标识
                "学分": tds[6].text.strip(),  # 学分
                "总学时": tds[7].text.strip(),  # 总学时
                "绩点": tds[8].text.strip(),  # 绩点
                "补重学期": tds[9].text.strip(),  # 补重学期
                "考核方式": tds[10].text.strip(),  # 考核方式
                "考试性质": tds[11].text.strip(),  # 考试性质
                "课程属性": tds[12].text.strip(),  # 课程属性
                "课程性质": tds[13].text.strip(),  # 课程性质
                "通选课类别": tds[14].text.strip()  # 通识课类别
            }
            # 数据读取并存入字典

            i += 1
            course_list.append(new_course)
            # 课程字典数据存入列表
        print(f"【{term}】时期的数据查询完成！共查询到{i}条数据！")
    else:
        print(f"未查询到【{term}】时期的数据!")

    return course_list


# 个人信息查询
def person_data(url):
    print("查询中......")
    print("============================")
    url_person_data = url + "yxszzy/yxszzy_grxx_ck"
    response = r_session.get(url_person_data)
    tds = BeautifulSoup(response.text, "html.parser").find_all("td")
    print(tds[1].get_text())
    print(tds[2].get_text())
    print(tds[3].get_text())
    print(tds[4].get_text())
    print(tds[6].get_text())
    print(tds[7].get_text())
    print(tds[8].get_text())
    print("============================")
    print("查询完毕")


# 学期课表导出
def get_curriculum(url, term):
    xnxq01id = term  # 目标学期
    zc = ""
    kbjcmsid = "47A852EDE04746E8913E2D79DBCEBB7F"
    wkbkc = '1'
    xswk = '1'
    url_curriculum = url + "xskb/xskb_print.do?" + "xnxq01id=" + xnxq01id + "&" + "zc=" + zc + "&" + "kbjcmsid=" + kbjcmsid + "&" + "wkbkc=" + wkbkc + "&" + "xswk=" + xswk
    response = r_session.post(url_curriculum)
    with open("./个人学期课表tmp.xls", "wb") as fp:
        fp.write(response.content)
    try:
        # 确保文件内容可读，即数据存在
        workbook = xlrd.open_workbook("./个人学期课表tmp.xls")  # 至少读取一个工作表来验证内容
        sheet = workbook.sheet_by_index(0)  # 确保至少能读取一行数据
        data = sheet.row_values(0)  # 如果到了这一步没有异常，说明文件内容基本可读
        print(f"个人学期课表【{term}】导出成功！")
        os.replace("./个人学期课表tmp.xls", f"./个人学期课表【{term}】.xls")  # 数据更新
    except (FileNotFoundError, xlrd.XLRDError):
        # 数据不存在时
        print(f"未查询到【{term}】学期课表！")
        os.remove("./个人学期课表tmp.xls")


# 考试安排信息查询
def query_exam(url, term):
    url_exam = url + "xsks/xsksap_list"
    form_data = {
        "xqlbmc": "",
        "xnxqid": term
    }
    response = r_session.post(url_exam, data=form_data)
    soup = BeautifulSoup(response.text, "html.parser")
    table = soup.find("table", {"id": "dataList"})
    exam_list = []
    if table is not None:
        flag = 0  # 标记是不是第一行表头
        i = 0  # 统计数量
        table_rows = table.find_all('tr')  # 存放所有的tr标签数据
        for row in table_rows:
            if flag == 0:
                flag += 1
                continue
            tds = row.find_all("td")
            if "未查询到数据" not in tds[0].text:
                new_exam = {
                    "序号": tds[0].text.strip(),
                    "校区": tds[1].text.strip(),
                    "考试校区": tds[2].text.strip(),
                    "考试场次": tds[3].text.strip(),
                    "课程编号": tds[4].text.strip(),
                    "课程名称": tds[5].text.strip(),
                    "授课教师": tds[6].text.strip(),
                    "考试时间": tds[7].text.strip(),
                    "考场": tds[8].text.strip(),
                    "座位号": tds[9].text.strip(),
                    "准考证号": tds[10].text.strip(),
                    "备注": tds[11].text.strip(),
                    "操作": tds[12].text.strip()
                }
                i += 1
                exam_list.append(new_exam)  # 字典数据存入列表
            else:
                print(f"未查询到【{term}】时期的数据!")
                return exam_list
        print(f"【{term}】时期的数据查询完成！共查询到{i}条数据！")
    else:
        print(f"未查询到【{term}】时期的数据!")
    return exam_list


# 教材信息查询
def query_textbook(url, term):
    url_textbook = url + "nxsjc/xsjcqr"
    form_data = {
        "xnxqid": term,
        "kkyx": '',
        "kcmc": '',
        "skjs": '',
        "xxdm": "10700"
    }
    response = r_session.post(url_textbook, data=form_data)
    soup = BeautifulSoup(response.text, "html.parser")
    table = soup.find(class_="layui-table")
    textbook_list = []
    if table is not None:
        flag = 0  # 标记是不是第一行表头
        i = 0  # 统计数量
        money = 0  # 记录总金额
        table_rows = table.find_all('tr')  # 存放所有的tr标签数据
        for row in table_rows:
            if flag == 0:
                flag += 1
                continue
            tds = row.find_all("td")
            if "未查询到数据" not in tds[0].text:
                new_textbook = {
                    "课程编号": tds[0].text.strip(),
                    "课程名称": tds[1].text.strip(),
                    "ISBN书号": tds[2].text.strip(),
                    "教材名称": tds[3].text.strip(),
                    "定价": tds[4].text.strip(),
                    "版次": tds[5].text.strip(),
                    "出版社": tds[6].text.strip(),
                    "上课教师": tds[7].text.strip(),
                    "上课院系": tds[8].text.strip(),
                    "征订状态": tds[9].text.strip(),
                    "操作": tds[10].text.strip()
                }
                i += 1
                money += float(tds[4].text.strip())
                textbook_list.append(new_textbook)  # 字典数据存入列表
            else:
                print(f"未查询到【{term}】时期的数据!")
                return textbook_list
        print(f"【{term}】时期的数据查询完成！共查询到{i}条数据！")
        print(f"共计: {money}元！")
    else:
        print(f"未查询到【{term}】时期的数据!")
    return textbook_list


# 导出csv表格
def get_csv(data_list, term, name):
    if data_list:
        keys = list(data_list[0].keys())  # 获取字典中所有键名并用列表保存
        with open(f"./{name}【{term}】.csv", "w") as fp:
            csv_writer = csv.DictWriter(fp, fieldnames=keys)
            csv_writer.writeheader()  # 写入表头
            for course in data_list:
                csv_writer.writerow(course)
            print(f"{name}【{term}】导出成功！")


# 程序初始化
def init():
    global user_vpn, pwd_vpn, user_jwxt, pwd_jwxt, KeepPwd, Auto_ID, default_term, cookie, basedir
    logo = pyfiglet.figlet_format("by  B R")
    print("============================")
    print(logo)
    print("============================")
    print("欢迎使用XAUTer's UEAS_helper！")
    print("在正式使用前请务必仔细阅读README.md文件！")
    print("============================")
    if os.path.isfile("./path.txt"):
        # 有路径文件
        with open("./path.txt", "r") as path:
            basedir = r"" + path.read().strip()
    if os.path.isfile("./init.txt"):
        # 有配置文件
        print("读取配置文件中......")
        with open("./init.txt", "r") as fp:
            init_list = fp.readlines()
            KeepPwd = init_list[0][8::].strip()
            user_vpn = init_list[1][9::].strip()
            pwd_vpn = crypt(init_list[2][8::].strip(), "PF5GE4TI", 1)
            user_jwxt = init_list[3][10::].strip()
            pwd_jwxt = crypt(init_list[4][9::].strip(), "PF5GE4TI", 1)
            Auto_ID = init_list[5][8::].strip()
            default_term = init_list[6][13::].strip()
    else:
        # 无配置文件
        print("未检测到配置文件，请先进行基础配置！")
        init_updata()


# 配置文件初始化
def init_updata():
    global KeepPwd, user_vpn, pwd_vpn, user_jwxt, pwd_jwxt, Auto_ID, default_term, cookie
    fp = open("./init.txt", "w")
    # 【保存密码】选项设置
    while True:
        KeepPwd = input("是否保存密码?(y/n)=>")
        if KeepPwd == 'Y' or KeepPwd == 'y' or KeepPwd == 'N' or KeepPwd == 'n':
            if KeepPwd == 'Y' or KeepPwd == 'y':  # 保存密码至本地
                KeepPwd = "True"
                print("【保存密码】已设置为: True")
                fp.write("KeepPwd=True\n")
            else:  # 不保存密码至本地，但每次登录都需要输入一遍密码
                KeepPwd = "False"
                print("【保存密码】已设置为: False")
                fp.write("KeepPwd=False\n")
            break
    # 【密码】选项设置
    while True:
        user_vpn = input("请输入WebVPN账户=>")
        fp.write(f"User_vpn={user_vpn}\n")
        if KeepPwd == "False":
            fp.write("Pwd_vpn=\n")
        else:
            pwd_vpn = input("请输入WebVPN密码(密码将会加密存储在init.txt文件中)=>")
        inspect = input("确定吗？(输入Y/y以确认)=>")
        if inspect == 'Y' or inspect == 'y':
            encodepwd_vpn = crypt(pwd_vpn, "PF5GE4TI", 0)
            fp.write(f"Pwd_vpn={encodepwd_vpn}\n")
            print("保存成功！")
            break

    while True:
        user_jwxt = input("请输入教务系统账户=>")
        fp.write(f"User_jwxt={user_jwxt}\n")
        if KeepPwd == "False":
            fp.write("Pwd_jwxt=\n")
        else:
            pwd_jwxt = input("请输入教务系统密码(密码将会加密存储在init.txt文件中)=>")
        inspect = input("确定吗？(输入Y/y以确认)=>")
        if inspect == 'Y' or inspect == 'y':
            encodepwd_jwxt = crypt(pwd_jwxt, "PF5GE4TI", 0)
            fp.write(f"Pwd_jwxt={encodepwd_jwxt}\n")
            print("保存成功！")
            break
    # 【验证码自动识别】选项设置
    while True:
        Auto_ID = input("是否使用ddddocr模块自动识别验证码?(y/n)=>")
        if Auto_ID == 'Y' or Auto_ID == 'y' or Auto_ID == 'N' or Auto_ID == 'n':
            if Auto_ID == 'Y' or Auto_ID == 'y':
                # 使用自动识别
                Auto_ID = "True"
                print("【验证码自动识别】已设置为: True")
                fp.write("Auto_ID=True\n")
            else:
                # 使用人眼识别
                Auto_ID = "False"
                print("【验证码自动识别】已设置为: False")
                fp.write("Auto_ID=False\n")
            break
    # 【默认学期】设置
    while True:
        default_term = input("请输入默认选择学期(格式xxxx-xxxx-x)=>")
        inspect = input("确定吗？(输入Y/y以确认)=>")
        if inspect == 'Y' or inspect == 'y':
            fp.write(f"Default_term={default_term}\n")
            print("保存成功！")
            break
    fp.close()
    time.sleep(1)
    os.system("cls")

# 主菜单
def main_mune():
    while True:
        print("============================")
        print("\t1.个 人 成 绩")
        print("\t2.个人信息查询")
        print("\t3.学 期 课 表")
        print("\t4.考试安排信息")
        print("\t5.教材征订信息")
        print("\t0.退 出 程 序")
        print("============================")
        select = input(":=>")
        if '0' <= select <= '5':
            return select


if __name__ == "__main__":
    url_goal = ""
    init()
    response = r_session.get(url_jwxt)
    if response.status_code != 200:
        # 教务系统服务器直连异常
        print("教务系统服务器直连失败，尝试通过WebVPN连接！")

        response = r_session.get(url_jwxt_vpn)
        if response.status_code == 200:
            print("WebVPN服务器连接成功！")
            url_goal = url_jwxt_vpn
            if response.url != url_jwxt_vpn:
                vpn_login()
        else:
            print("服务器炸了，连接失败！")
            exit(0)
    else:
        # 教务系统服务器直连正常
        url_goal = url_jwxt

    url_jwxt_main = url_goal + "framework/xsMainV.htmlx"
    response = r_session.get(url_jwxt_main)
    if response.status_code == 200 and response.url == url_jwxt_main:
        # 成功进入教务系统
        print("教务系统登录成功！")
    else:
        # 未能登录教务系统
        jwxt_login(url_goal)

    while True:
        response = r_session.get(url_jwxt_main)
        username = BeautifulSoup(response.text, "html.parser").find_all("li")[2].find_all("span")[
                1].get_text().strip()
        print("============================")
        print(f"你好！【{username}】,欢迎使用XAUTer's UEAS_helper！")
        select = main_mune()
        os.system("cls")  # 清下屏
        if select == '0':  # 退出程序
            print("感谢您的使用！期待下次再会！")
            exit(0)
        elif select == '1':  # 个人成绩导出
            get_csv(query_grades(url_goal, default_term), default_term, "个人成绩单")
        elif select == '2':  # 个人信息查询
            person_data(url_goal)
        elif select == '3':  # 学期理论课表导出
            get_curriculum(url_goal, default_term)
        elif select == '4':  # 考试安排信息导出
            get_csv(query_exam(url_goal, default_term), default_term, "考试安排信息")
        elif select == '5':  # 教材信息导出
            get_csv(query_textbook(url_goal, default_term), default_term, "教材信息")
        else:
            print("发生未知错误!")
            exit(0)
