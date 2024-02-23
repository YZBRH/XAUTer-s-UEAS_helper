## 1.前言

本程序为初学Python的小菜鸡所做的一款爬虫练习项目，是帮助XAUT的同学们更方便使用教务系统的一款脚本程序，目前已实现一些相对常用功能的自动化（ps：其实一开始想做抢课脚本来着，但是吧选课已经结束了，缺乏样例给我测试¯\_(ツ)_/¯，所以暂时搁置了，下次一定！）

因为只是一个练习之作，肯定还有很多不足，希望大佬轻喷，也欢迎大家的反馈，联系方式在最后~

废话不多说，让我们正式开始吧！ᕕ( ᐛ )ᕗ



## 2.前置环境部署

本程序在Python 3.10.4环境下，使用Pycharm进行编译

### Python模块

在cmd中使用以下命令快捷安装

```cmd
pip install requests
pip install beautifulsoup4
pip install ddddocr
pip install pyfiglet
pip install PyExecJS
pip install xlrd
```

以下是对各个模块在程序中作用的简短概括

```python
import requests  # 进行基本网站交互
from bs4 import BeautifulSoup  # 对html页面进行信息处理
import ddddocr  # 实现简单的验证码自动识别
import pyfiglet  # 生成logo
import os  # 执行一些系统命令，例如清屏cls
import execjs  # 执行js代码
import csv  # 生成csv表格
import xlrd  # 判断下载的xls表格内的数据有效性
```

### CryptoJS导入

首先需要下载Node.js，进入官方网站https://nodejs.org/下载安装程序，然后双击安装程序跟随指引安装即可，建议下载到默认路径，否则您需要更改path.txt文件中的内容为您电脑中Node.js的路径

安装完成Node.js后，在cmd中使用以下命令安装CryptoJs

```cmd
npm install -g crypto-js
```



## 3.如何启动程序？

1.首先打开cmd命令符

2.跳转至目标目录

```cmd
cd <您电脑中XAUTer's UEAS_helper的绝对路径>
```

3.启动程序

```cmd
python main.py
```



## 4.程序主体

程序主逻辑图

![](C:\Users\86156\Downloads\未命名文件.png)



## 5.各部分文件作用

### main.py

程序主体，是实现预期功能的核心代码

### encrypt.js

从WebVPN中获取的前端加密代码，主要用于模拟WebVPN登录过程中对密码部分进行加密的操作

### conwork.js

从教务系统中获取的前端加密代码，主要用于模拟教务系统登录过程中对密码部分进行加密的操作

### cookie.txt

存储登录时的cookie，下次登陆时可直接使用已有cookie从而免登录直接进入系统

### path.txt

存储Node.js所在的位置，默认为“C:\Program Files\nodejs”，如您的Node.js未在默认位置，则需要手动修改其中的路径为您电脑中Node.js的绝对路径

### init.txt

存储配置信息，示例

```
KeepPwd=True  # 表示是否记住密码，若为True则表示将WebVPN和教务系统密码存放至本地，反之若为False，则不会保存密码至本地
User_vpn=114514  # 表示您的WebVPN账户
Pwd_vpn=1234567890  # 表示您的WebVPN密码(将会加密存储在此处)
User_jwxt=114514  # 表示您的教务系统账户
Pwd_jwxt=1234567890  # 表示您的教务系统密码(将会加密存储在此处)
Auto_ID=True  # 表示是否启用ddddocr的验证码自动识别功能，若为True则每次需要输入验证码时，将调用ddddocr自动识别
Default_term=2023-2024-1  # 表示默认的学期选择，格式为xxxx-xxxx-x，两个年份代表学年，需要相邻，且后一个需大于前一个，最后							一个数字表示上下学期，1表示上学期，2表示下学期
```

### 教务系统验证码.jpg

若不启用ddddocr的自动识别功能或其识别有误，您可在此处肉眼辨别验证码进行输入



## 6.目前的功能

### 1.个人成绩

将自动查询指定学期的成绩信息，并以csv表格形式返回查询到的数据

### 2.个人信息查询

将自动查询实时个人信息，包括课程门数、不及格门数、平均学分绩点、专业排名等

### 3.学期课表

将自动导出指定学期的课表信息，并以xls表格形式返回查询到的数据

### 4.考试安排信息

将自动查询指定学期的考试安排信息，并以csv表格形式返回查询到的数据

### 5.教材征订信息

将自动查询指定学期的教材征订信息，并统计总金额，以csv表格返回查询到的教材数据



## 7.可能遇到的问题

### 1.在WebVPN登录过程中，明明账户和密码都正确，却一直登录失败

可能是之前登录WebVPN失败次数过多触发了滑块验证码，只需要在浏览器中手动成功登陆过一次WebVPN即可

### 2.对一开始的配置信息不满意，想要更改可以吗

可以的，有两种方法，一是直接删除init.txt文件然后重启程序，按照程序要求重新设置一遍默认配置即可；二是直接修改init.txt的内容，可参照上文对init.txt文件的介绍来进行修改

### 3.我的Node.js没有安装在默认位置，导致程序无法模拟WebVPN登录怎么办

修改path.txt的内容即可，默认为C:\Program Files\nodejs，将其修改成您下载的Node.js的绝对路径即可

### 4.出现了无法自主解决，该文档中也未提及的问题

可以善用搜索引擎和一些AI大模型（例如：通义千问等），也可以联系作者进行反馈

## 8.关于

本程序由 BR 独立编译完成，将永久开源，已上传至Github([YZBRH/XAUTer-s-UEAS_helper (github.com)](https://github.com/YZBRH/XAUTer-s-UEAS_helper))，觉得好玩好用记得来给我点个小星星啊(✧∇✧)，如有问题欢迎反馈，联系QQ：1947514592