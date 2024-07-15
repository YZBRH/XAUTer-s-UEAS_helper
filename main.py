import json
import requests
from bs4 import BeautifulSoup
import ddddocr
import os
import csv
import xlrd
import time
import stdiomask
import sys
import pynput
import colorama

import encode
import select_curriculum


# 检查网络连接状态
def check_internet():
    try:
        response = requests.get("http://www.baidu.com", timeout=5)
        if 200 <= response.status_code < 400:
            flag = 1
        else:
            flag = 0
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
        flag = 0

    if flag != 1:
        print("\033[31m[!]请检查网络连接是否正常\033[0m")
        sys.exit(0)


# 鼠标监听
def Operation_monitoring():
    time.sleep(0.01)
    flag = 0 # 计数
    with pynput.mouse.Events() as event:
        for i in event:
            if isinstance(i, pynput.mouse.Events.Click):
                if "left" in str(i.button) and i.pressed:
                    flag += 1
                    if flag >= 2:
                        return 0
            elif isinstance(i, pynput.mouse.Events.Scroll):
                if i.dy < 0: # 向下
                    return 1
                elif i.dy > 0: # 向上
                    return -1


# WebVPN登录
def vpn_login():
    global pwd_vpn
    url_vpn_login = "https://webvpn.xaut.edu.cn/https/77726476706e69737468656265737421f9f352d23f317d44300d8db9d6562d/authserver/login?service=https://webvpn.xaut.edu.cn/login?cas_login=true "
    response = r_session.get(url_vpn_login)

    soup = BeautifulSoup(response.text, "html.parser")
    execution = soup.find(id="execution")["value"]
    salt = soup.find(id="pwdEncryptSalt")["value"]

    if KeepPwd == "False":  # 未保存密码
        while True:
            pwd_vpn = stdiomask.getpass(prompt='\033[32m[+]请输入WebVPN密码=>\033[0m', mask='*')
            inspect = input("\033[32m[?]确定吗？(输入Y/y以确认)=>\033[0m")
            if inspect == 'Y' or inspect == 'y':
                print("\033[32m[*]保存成功！\033[0m")
                break

    encodepwd = encode.crypt_vpn(pwd_vpn, salt, 0, basedir)
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
        print("\033[32m[*]WebVPN登录成功！\033[0m")
        return
    else:
        print("\033[31m[!]WebVPN登陆失败，请检查账户与密码是否正确！\033[0m")
        sys.exit(0)


# 获取教务系统登录验证码信息
def get_check(url):
    i = 0
    while True:
        i += 1
        if i > 10:
            print("\033[31m[!]ddddocr自动验证码失败失败次数过多，请尝试手动识别！\033[0m")
            sys.exit(0)

        response = r_session.get(url)
        soup = BeautifulSoup(response.text, "html.parser")
        img_src = ""
        if url == url_jwxt_vpn:
            img_src = "https://webvpn.xaut.edu.cn" + soup.find(id="SafeCodeImg")["src"]
        elif url == url_jwxt:
            img_src = "http://jwgl.xaut.edu.cn/jsxsd/verifycode.servlet"
        else:
            print("\033[31m[!]未知网站！\033[0m")
            sys.exit(0)
        img_data = r_session.get(img_src).content
        # 保存验证码至本地
        if not os.path.exists("./img"):
            os.makedirs("./img")
        with open('./img/教务系统验证码.jpg', 'wb') as fp:
            fp.write(img_data)
        if Auto_ID == "True":
            # 使用ddddocr模块自动识别验证码
            check = ddddocr.DdddOcr(show_ad="False").classification(img_data)
            print(f"\033[32m[*]ddddocr自动识别验证码为{check}\033[0m")
        else:
            # 使用更为先进的人眼识别技术
            print("\033[32m[+]验证码下载成功，请手动识别验证码内容\033[0m")
            check = input("\033[32m[+]验证码为：\033[0m")
        if len(check) >= 4:
            return check
        # 验证码获取及验证，验证码图片与源码在同一目录下


# 教务系统登录
def jwxt_login(url):
    global pwd_jwxt
    url_jwxt_login = url + "xk/LoginToXk"  # 教务系统登录接口
    url_jwxt_main = url + "framework/xsMainV.htmlx"  # 主页

    if KeepPwd == "False":  # 未保存密码
        while True:
            pwd_jwxt = stdiomask.getpass(prompt='\033[32m[+]请输入教务系统密码=>\033[0m', mask='*')
            inspect = input("\033[32m[?]确定吗？(输入Y/y以确认)=>\033[0m")
            if inspect == 'Y' or inspect == 'y':
                print("\033[32m[*]保存成功！\033[0m")
                break

    encoded = str(encode.crypt_jwxt(user_jwxt)) + "%%%" + str(encode.crypt_jwxt(pwd_jwxt))
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
        print("\033[32m[*]教务系统登录成功！\033[0m")
    else:
        print("\033[31m[!]教务系统登录失败,请检查账户名、密码及验证码是否正确！\033[0m")
        sys.exit(0)


# 未评教学科补查
def non_evaluation_query_grades(id):
    url_query_grades = url_goal + "yxszzy/yxkc_list"
    response = r_session.get(url_query_grades)
    trs = BeautifulSoup(response.text, "html.parser").find_all("tr")
    flag = 0
    for tr in trs:
        tds = tr.find_all("td")
        if flag <= 1:
            flag += 1
            continue
        if tds[2].text == id:
            score = tds[7].text
            GPA = "0"
            if float(score) >= 95:
                GPA = "5.0"
            elif float(score) >= 60:
                GPA = str(1.5 + (float(score) - 60) / 10)
            data = {
                "成绩": score,
                "绩点": GPA
            }
            return data
    print("\033[31m[!]成绩单中存在未评教数据，且未能查询到实际数据！\033[0m")
    return "NULL"


# 成绩查询
def query_grades(url, term):
    kksj = term  # 开课时间，即查询的时段
    zylx = '0'

    all_GPA = 0  # 总(绩点*学分)
    all_credit = 0  # 总学分
    fail = 0  # 不及格学科

    url_cjcx = url + f"kscj/cjcx_list?kksj={kksj}&zylx={zylx}"  # 成绩查询网址
    response = r_session.get(url_cjcx)
    soup = BeautifulSoup(response.text, "html.parser")
    table = soup.find('table', {'id': 'dataList'})  # 使用ID定位表格

    course_list = []  # 存放课程数据的列表
    print("\033[32m[*]查询中，请稍后......\033[0m")
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
            }  # 数据读取并存入字典

            if new_course["成绩"] == "请评教":
                data = non_evaluation_query_grades(new_course["课程编号"])
                if data == "NULL":  # 无数据
                    flag = -1
                else:  # 更新未评教信息
                    new_course["成绩"] = data["成绩"]
                    new_course["绩点"] = data["绩点"]

            if new_course["绩点"] == '0':
                fail += 1

            if flag != -1:
                all_credit += float(new_course["学分"])
                all_GPA += float(new_course["学分"]) * float(new_course["绩点"])

            i += 1
            course_list.append(new_course)
            # 课程字典数据存入列表
        print(f"\033[32m[*]【{term}】时期的数据查询完成！共查询到{i}条数据！\033[0m")
        print("============================")
        if flag != -1:
            print(f"总学科数:{i}\n不及格学科数:{fail}\n总学分:{all_credit}\n总(学分*绩点):{all_GPA}\n加权平均绩点{all_GPA / all_credit}")
        print("============================")
    else:
        print(f"\033[31m[!]未查询到【{term}】时期的数据!\033[0m")

    return course_list


# 个人信息查询
def person_data(url):
    print("\033[32m[*]查询中......\033[0m")
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
    print("\033[32m[*]查询完毕\033[0m")


# 学期课表导出
def get_curriculum(url, term):
    xnxq01id = term  # 目标学期
    zc = ""
    kbjcmsid = "47A852EDE04746E8913E2D79DBCEBB7F"
    wkbkc = '1'
    xswk = '1'
    url_curriculum = url + f"xskb/xskb_print.do?xnxq01id={xnxq01id}&zc={zc}&kbjcmsid={kbjcmsid}&wkbkc={wkbkc}&xswk={xswk}"
    response = r_session.post(url_curriculum)
    if not os.path.exists("./output"):
        os.makedirs("./output")
    with open("./output/个人学期课表tmp.xls", "wb") as fp:
        fp.write(response.content)
    try:
        # 确保文件内容可读，即数据存在
        workbook = xlrd.open_workbook("./output/个人学期课表tmp.xls")  # 至少读取一个工作表来验证内容
        sheet = workbook.sheet_by_index(0)  # 确保至少能读取一行数据
        sheet.row_values(0)  # 如果到了这一步没有异常，说明文件内容基本可读
        print(f"\033[32m[*]个人学期课表【{term}】导出成功！\033[0m")
        os.replace("./output/个人学期课表tmp.xls", f"./output/个人学期课表【{term}】.xls")  # 数据更新
    except (FileNotFoundError, xlrd.XLRDError):
        # 数据不存在时
        print(f"\033[31m[!]未查询到【{term}】学期课表！\033[0m")
        os.remove("./output/个人学期课表tmp.xls")


# 当周课表
def week_curriculum(url, term):
    t = time.localtime()  # 获取当前时间
    rq = f"{t.tm_year:04d}-{t.tm_mon:02d}-{t.tm_mday:02d}"
    sjmsValue = "47A852EDE04746E8913E2D79DBCEBB7F"
    xnxqid = term
    xswk = "true"
    url_curriculum = url + f"framework/mainV_index_loadkb.htmlx?rq={rq}&sjmsValue={sjmsValue}&xnxqid={xnxqid}&xswk={xswk}"
    # 主页实时课表

    response = r_session.get(url_curriculum)
    if "当前日期不在教学周历内" in response.text:
        print(f"\033[31m[!]学期值{term},查询日期{rq},未查询到数据！\033[0m")
        return "NULL"
    else:
        soup = BeautifulSoup(response.text, "html.parser")
        trs = soup.find_all("tr")
        course_list = []
        teacher_list = []
        class_list = []
        for tr in trs:
            tds = tr.find_all("td")
            if tds:  # 无td数据不记录
                single_course_list = []
                sigle_teacher_list = []
                sigle_class_list = []
                flag = 0  # 标记，排除第一行td数据
                for td in tds:
                    if flag == 0:
                        flag += 1
                        continue

                    # 教室
                    spans = td.find_all("span")
                    if spans == [] or spans is None:  # 不为空则记录，否则置”无
                        sigle_class_list.append("无")
                    else:
                        sigle_class_list.append(spans[5].text)

                    # 老师和课程
                    ps = td.find_all("p")
                    if ps == [] or ps is None:  # 不为空则记录，否则置“无”
                        sigle_teacher_list.append("无")
                        single_course_list.append("无")
                    else:
                        sigle_teacher_list.append(ps[1].text)
                        single_course_list.append(ps[2].text)
                class_list.append(sigle_class_list)
                course_list.append(single_course_list)
                teacher_list.append(sigle_teacher_list)

        data = {
            "course": course_list,
            "teacher": teacher_list,
            "class": class_list
        }
        return data


# 当日课表
def day_curriculum(data):
    if data != "NULL":
        t = time.localtime()  # 获取当前时间
        i = 0  # 课数
        curriculum = ""
        today_time = f"{t.tm_year}年{t.tm_mon}月{t.tm_mday}日"

        if t.tm_wday == 0:
            wday = "星期一"
        elif t.tm_wday == 1:
            wday = "星期二"
        elif t.tm_wday == 2:
            wday = "星期三"
        elif t.tm_wday == 3:
            wday = "星期四"
        elif t.tm_wday == 4:
            wday = "星期五"
        elif t.tm_wday == 5:
            wday = "星期六"
        else:
            wday = "星期天"
        wday += "\n"

        if data['course'][0][t.tm_wday] != "无":
            i += 1
            curriculum += f"\n第一大节(08:00-09:50): \n" \
                          f"课程：{data['course'][0][t.tm_wday]}\n" \
                          f"{data['teacher'][0][t.tm_wday]}\n" \
                          f"教室：{data['class'][0][t.tm_wday]}\n"
        if data['course'][1][t.tm_wday] != "无":
            i += 1
            curriculum += f"\n第二大节(10:10-12:00): \n" \
                          f"课程：{data['course'][1][t.tm_wday]}\n" \
                          f"{data['teacher'][1][t.tm_wday]}\n" \
                          f"教室：{data['class'][1][t.tm_wday]}\n"
        if data['course'][2][t.tm_wday] != "无":
            i += 1
            curriculum += f"\n第三大节(12:10-14:00): \n" \
                          f"课程：{data['course'][2][t.tm_wday]}\n" \
                          f"{data['teacher'][2][t.tm_wday]}\n" \
                          f"教室：{data['class'][2][t.tm_wday]}\n"
        if data['course'][3][t.tm_wday] != "无":
            i += 1
            curriculum += f"\n第四大节(14:10-16:00): \n" \
                          f"课程：{data['course'][3][t.tm_wday]}\n" \
                          f"{data['teacher'][3][t.tm_wday]}\n" \
                          f"教室：{data['class'][3][t.tm_wday]}\n"
        if data['course'][4][t.tm_wday] != "无":
            i += 1
            curriculum += f"\n第五大节(16:10-18:00): \n" \
                          f"课程：{data['course'][4][t.tm_wday]}\n" \
                          f"{data['teacher'][4][t.tm_wday]}\n" \
                          f"教室：{data['class'][4][t.tm_wday]}\n"
        if data['course'][5][t.tm_wday] != "无":
            i += 1
            curriculum += f"\n第六大节(19:00-21:50): \n" \
                          f"课程：{data['course'][5][t.tm_wday]}\n" \
                          f"{data['teacher'][5][t.tm_wday]}\n" \
                          f"教室：{data['class'][5][t.tm_wday]}\n"

        if i > 0:
            greet = f"今日共有{i}节课！\n"
        else:
            greet = f"今日没有课~\n"

        msg = today_time + wday + greet + curriculum
        return msg


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
                print(f"\033[31m[!]未查询到【{term}】时期的数据!\033[0m")
                return exam_list
        print(f"\033[32m[*]【{term}】时期的数据查询完成！共查询到{i}条数据！\033[0m")
    else:
        print(f"\033[31m[!]未查询到【{term}】时期的数据!\033[0m")
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
                print(f"\033[31m[!]未查询到【{term}】时期的数据!\033[0m")
                return textbook_list
        print(f"\033[32m[*]【{term}】时期的数据查询完成！共查询到{i}条数据！\033[0m")
        print(f"\033[32m[*]共计: {money}元！\033[0m")
    else:
        print(f"\033[31m[!]未查询到【{term}】时期的数据!\033[0m")
    return textbook_list


# 导出csv表格
def get_csv(data_list, term, name):
    if data_list:
        keys = list(data_list[0].keys())  # 获取字典中所有键名并用列表保存
        if not os.path.exists("./output"):
            os.makedirs("./output")
        with open(f"./output/{name}【{term}】.csv", "w") as fp:
            csv_writer = csv.DictWriter(fp, fieldnames=keys)
            csv_writer.writeheader()  # 写入表头
            for course in data_list:
                csv_writer.writerow(course)
            print(f"\033[32m[*]{name}【{term}】导出成功！\033[0m")


# 程序初始化
def init():
    global user_vpn, pwd_vpn, user_jwxt, pwd_jwxt, KeepPwd, Auto_ID, default_term, basedir
    print("============================")
    print(
'\033[34m _             ____  ____ \n\
| |__  _   _  | __ )|  _ \ \n\
| \'_ \| | | | |  _ \| |_) | \n\
| |_) | |_| | | |_) |  _ < \n\
|_.__/ \__, | |____/|_| \_\ \n\
       |___/ \n\033[0m')
    print("欢迎使用XAUTer's UEAS_helper！")
    print("在正式使用前请务必仔细阅读README.md文件！")
    print("============================")
    if not os.path.exists("./data"):
        os.makedirs("./data")
    if os.path.isfile("./data/path.txt"):
        # 有路径文件
        with open("./data/path.txt", "r") as path:
            basedir = r"" + path.read().strip()
    if os.path.isfile("./data/init.json"):
        # 有配置文件
        print("\033[32m[*]读取配置文件中......\033[0m")
        with open("./data/init.json", "r") as fp:
            data = json.load(fp)
            KeepPwd = data["KeepPwd"]
            user_vpn = data["User_vpn"]
            pwd_vpn = encode.crypt_vpn(data["Pwd_vpn"], "PF5GE4TI", 1, basedir)
            user_jwxt = data["User_jwxt"]
            pwd_jwxt = encode.crypt_vpn(data["Pwd_jwxt"], "PF5GE4TI", 1, basedir)
            Auto_ID = data["Auto_ID"]
            default_term = data["Default_term"]
    else:
        # 无配置文件
        print("\033[31m[!]未检测到配置文件，请先进行基础配置！\033[0m")
        init_updata()


# 配置文件更新
def init_updata():
    global KeepPwd, user_vpn, pwd_vpn, user_jwxt, pwd_jwxt, Auto_ID, default_term
    data = {}
    # 【保存密码】选项设置
    while True:
        KeepPwd = input("\033[32m[?]是否保存密码?(y/n)=>\033[0m")
        if KeepPwd == 'Y' or KeepPwd == 'y' or KeepPwd == 'N' or KeepPwd == 'n':
            if KeepPwd == 'Y' or KeepPwd == 'y':  # 保存密码至本地
                KeepPwd = "True"
                print("\033[32m[*]【保存密码】已设置为: True\033[0m")
                data["KeepPwd"] = "True"
            else:  # 不保存密码至本地，但每次登录都需要输入一遍密码
                KeepPwd = "False"
                print("\033[32m[*]【保存密码】已设置为: False\033[0m")
                data["KeepPwd"] = "False"
            break
    # 【密码】选项设置
    while True:
        user_vpn = input("\033[32m[+]请输入WebVPN账户=>\033[0m")
        data["User_vpn"] = user_vpn
        if KeepPwd == "False":
            data["Pwd_vpn"] = ""
        else:
            pwd_vpn = stdiomask.getpass(prompt='\033[32m[+]请输入WebVPN密码(密码将会加密存储在init.json文件中)=>\033[0m', mask='*')
            inspect = input("\033[32m[?]确定吗？(输入Y/y以确认)=>\033[0m")
            if inspect == 'Y' or inspect == 'y':
                encodepwd_vpn = encode.crypt_vpn(pwd_vpn, "PF5GE4TI", 0, basedir)
                data["Pwd_vpn"] = encodepwd_vpn
        print("\033[32m[*]保存成功！\033[0m")
        break

    while True:
        user_jwxt = input("\033[32m[+]请输入教务系统账户=>\033[0m")
        data["User_jwxt"] = user_jwxt
        if KeepPwd == "False":
            data["Pwd_jwxt"] = ""
        else:
            pwd_jwxt = stdiomask.getpass(prompt='\033[32m[+]请输入教务系统密码(密码将会加密存储在init.json文件中)=>\033[0m', mask='*')
            inspect = input("\033[32m[?]确定吗？(输入Y/y以确认)=>\033[0m")
            if inspect == 'Y' or inspect == 'y':
                encodepwd_jwxt = encode.crypt_vpn(pwd_jwxt, "PF5GE4TI", 0, basedir)
                data["Pwd_jwxt"] = encodepwd_jwxt
        print("\033[32m[*]保存成功！\033[0m")
        break
    # 【验证码自动识别】选项设置
    while True:
        Auto_ID = input("\033[32m[?]是否使用ddddocr模块自动识别验证码?(y/n)=>\033[0m")
        if Auto_ID == 'Y' or Auto_ID == 'y' or Auto_ID == 'N' or Auto_ID == 'n':
            if Auto_ID == 'Y' or Auto_ID == 'y':
                # 使用自动识别
                Auto_ID = "True"
                print("\033[32m[*]【验证码自动识别】已设置为: True\033[0m")
                data["Auto_ID"] = "True"
            else:
                # 使用人眼识别
                Auto_ID = "False"
                print("\033[32m[*]【验证码自动识别】已设置为: False\033[0m")
                data["Auto_ID"] = "False"
            break
    # 【默认学期】设置
    while True:
        default_term = input("\033[32m[+]请输入默认选择学期(格式xxxx-xxxx-x)=>\033[0m")
        inspect = input("\033[32m[?]确定吗？(输入Y/y以确认)=>\033[0m")
        if inspect == 'Y' or inspect == 'y':
            data["Default_term"] = default_term
            print("\033[32m[*]保存成功！\033[0m")
            break
    if not os.path.exists("./data"):
        os.makedirs("./data")
    with open("./data/init.json", "w") as fp:
        json.dump(data, fp)

    time.sleep(0.5)
    os.system("cls")


# 主菜单
def main_mune(username,num):
    while True:
        os.system("cls")

        if num > 7:
            num = 0
        if num < 0:
            num = 7

        print("=================================")
        print("-------XAUTer's UEAS_helper------")
        print("=================================")
        print(f"        您好！【{username}】！")
        print("=================================")
        if num == 1:
            print("\t\033[34m>1.个 人 成 绩<\033[0m")
        else:
            print("\t 1.个 人 成 绩")
        if num == 2:
            print("\t\033[34m>2.个人信息查询<\033[0m")
        else:
            print("\t 2.个人信息查询")
        if num == 3:
            print("\t\033[34m>3.学 期 课 表<\033[0m")
        else:
            print("\t 3.学 期 课 表")
        if num == 4:
            print("\t\033[34m>4.考试安排信息<\033[0m")
        else:
            print("\t 4.考试安排信息")
        if num == 5:
            print("\t\033[34m>5.教材征订信息<\033[0m")
        else:
            print("\t 5.教材征订信息")
        if num == 6:
            print("\t\033[34m>6.当日课表查询<\033[0m")
        else:
            print("\t 6.当日课表查询")
        if num == 7:
            print("\t\033[34m>7.自 动 选 课<\033[0m")
        else:
            print("\t 7.自 动 选 课")
        if num == 0:
            print("\t\033[34m>0.退 出 程 序<\033[0m")
        else:
            print("\t 0.退 出 程 序")
        print("=================================")

        tmp = Operation_monitoring()
        if tmp == 0:
            return num
        else:
            num += tmp


if __name__ == "__main__":
    KeepPwd = ""  # 保存密码
    Auto_ID = ""  # 自动识别验证码
    user_vpn = ""  # WebVPN账户
    pwd_vpn = ""  # WebVPN密码
    user_jwxt = ""  # 教务系统账户
    pwd_jwxt = ""  # 教务系统密码
    default_term = ""  # 默认学期
    username = ""  # 记录用户名称
    num = 1  # 菜单计数

    basedir = r"C:\Program Files\nodejs"  # node.js位置

    url_jwxt_vpn = "https://webvpn.xaut.edu.cn/http/77726476706e69737468656265737421fae04690692869456a468ca88d1b203b/jsxsd/"
    url_jwxt = "http://jwgl.xaut.edu.cn/jsxsd/"
    # 目标网站

    colorama.init(autoreset=True)

    r_session = requests.session()  # 自动获取会话session，保持会话

    check_internet()
    init()
    response = r_session.get(url_jwxt)
    if response.status_code != 200:
        # 教务系统服务器直连异常
        url_goal = url_jwxt_vpn
        print("\033[31m[!]教务系统服务器直连失败，尝试通过WebVPN连接！\033[0m")

        response = r_session.get(url_jwxt_vpn, verify=False)
        if response.status_code == 200:
            print("\033[32m[*]WebVPN服务器连接成功！\033[0m")
            if response.url != url_jwxt_vpn:
                vpn_login()
        else:
            print("\033[31m[!]服务器炸了，连接失败！\033[0m")
            sys.exit(0)
    else:
        # 教务系统服务器直连正常
        url_goal = url_jwxt

    url_jwxt_main = url_goal + "framework/xsMainV.htmlx"
    response = r_session.get(url_jwxt_main)
    if response.status_code == 200 and response.url == url_jwxt_main and "请先登录系统" not in response.text:
        # 成功进入教务系统
        print("\033[32m[*]教务系统登录成功！\033[0m")
    else:
        # 未能登录教务系统
        jwxt_login(url_goal)
    time.sleep(0.5)
    os.system("cls")

    try:
        # 用户名获取
        response = r_session.get(url_jwxt_main)
        username = BeautifulSoup(response.text, "html.parser").find_all("li")[2].find_all("span")[1].get_text().strip()
    except:
        print("\033[31m[!]出现未知错误，请重启程序\033[0m")
        sys.exit(0)

    try:
        select_curriculum.check(user_vpn, pwd_vpn, user_jwxt, pwd_jwxt)
    except:
        pass

    while True:
        num = main_mune(username,num)
        os.system("cls")  # 清下屏
        if num == 0:  # 退出程序
            print("\033[31m[!]感谢您的使用！期待下次再会！\033[0m")
            sys.exit(0)
        elif num == 1:  # 个人成绩导出
            get_csv(query_grades(url_goal, default_term), default_term, "个人成绩单")
            os.system("pause")
        elif num == 2:  # 个人信息查询
            person_data(url_goal)
            os.system("pause")
        elif num == 3:  # 学期理论课表导出
            get_curriculum(url_goal, default_term)
            time.sleep(1.5)
        elif num == 4:  # 考试安排信息导出
            get_csv(query_exam(url_goal, default_term), default_term, "考试安排信息")
            time.sleep(1.5)
        elif num == 5:  # 教材信息导出
            get_csv(query_textbook(url_goal, default_term), default_term, "教材信息")
            time.sleep(3)
        elif num == 6:  # 当日课表
            print(day_curriculum(week_curriculum(url_goal, default_term)))
            os.system("pause")
        elif num == 7:  # 自动选课
            os.system("cls")
            select_curriculum.select_curriculum_main(url_goal, r_session, user_jwxt, 0.1)
        else:
            print("\033[31m[!]发生未知错误!\033[0m")
            sys.exit(0)