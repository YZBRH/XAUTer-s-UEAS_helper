# 前言

​	本程序一切数据来源于[教务系统](http://jwgl.xaut.edu.cn/jsxsd/)，如使用本程序得到的数据与官方网站不符，请以官方为准。

​	本程序为个人开发自用，仅供学习交流使用，一切风险和因非法操作导致的不良后果将由使用者承担，开发者对此不负任何责任。

​	使用该程序即表示同意以上信息。

# 环境要求

​	windows10及以上系统

​	python 3.10.4

​	requests等python模块

​	Node.js及CryptoJS模块

# 环境配置指南

本程序已完成封装，双击exe启动，作为用户您仅需要关注Node.js部分，无需安装python

## python 3.10.4安装

​	本程序在python 3.10.4环境下编写[python 3.10.4安装教程](https://blog.csdn.net/qq_46388354/article/details/124970760)

## python模块安装	

```
pip install -r requirements.txt  # 在"requirements.txt"文件所处的路径下启动cmd，并输入该命令
```

## Node.js及CryptoJS模块安装

​	[Node.js安装及配置教程](https://blog.csdn.net/WHF__/article/details/129362462)(Node.js建议安装在默认路径，否则在接下来使用WebVPN登录前可能需要先配置Node.js的绝对路径)。

​	如果您的Node.js不在默认路径并无法使用WebVPN，请修改"./data/path.txt"文件的内容为您电脑中Node.js的绝对路径(不包括引号)，即"Node.exe"文件所在的目录。

```
npm install -g crypto-js  # 在cmd中输入该命令安装CryptoJS模块
```

# 使用手册

## 首次启动

​	在您的前置工作均已完成且未出错后，在程序目录下双击"start.bat"或"start.exe"即可启动程序。

​	首次启动时，请您按照程序指引进行初始信息配置，该配置文件将本地储存在"./data/init.json"文件中，若您需要更新或更改您的配置信息，可直接删除该文件并重启程序，这将重新进行初始信息配置。

​	在菜单页面中，您需要使用鼠标滚轮进行上下选择，双击鼠标左键即可确认选择/。

​	若有像"(Y/y)"这样的提示，输入"Y"或者"y"并按下回车即表示同意和确认，否则表示不同意。

### 关于配置信息解释

​	【保存密码】----------即是否将密码存储至本地init.json文件中，若选择"Y"，则密码将会以加密形式存储在init.json，并在登陆时进行调用。

​	【WebVPN】----------使用XAUT统一身份认证系统的账户及密码，保证在教务系统仅对内网开放期间也能正常访问使用，若不需要使用WebVPN，此项可不配置(最好不留空，乱输即可)。

​	【教务系统】----------主体登录，不解释。

​	【ddddocr模块】----自动识别验证码的一个python模块，可不使用，若不使用该模块，在每次登录时需人眼识别"./image/教务系统验证码.jpg"文件，并手动输入验证码。

​	【默认选择学期】----影响大部分有关"学年学期"的功能，包括但不限于查成绩，查课表，格式为xxxx-xxxx-x，例如2023-2024-1表示2023-2024学年的上半学期，2023-2024-2表示2023-2024学年的下半学期，两个年份需要相邻，“-”不能省略。

​	以上配置信息均在"./data/init.json"文件内。

## 个人成绩

​	将查询【默认选择学期】的所有可查询成绩信息，并以csv格式保存在"./output"文件夹内，此外，程序还将自动计算加权平均绩点和挂科数等，若存在"未评教"信息，程序将尝试查询实际成绩，并以实际成绩替换"未评教"。

## 个人信息查询

​	将查询实时绩点，专业排名，挂科数等。

## 学期课表

​	将查询【默认选择学期】的学期理论课表，并以csv格式保存在"./output"文件夹内。

## 考试安排信息

​	将查询【默认选择学期】的考试安排信息，并以csv格式保存在"./output"文件夹内。

## 教材征订信息

​	将查询【默认选择学期】的教材征订信息，并以csv格式保存在"./output"文件夹内，程序还将计算总金额(并不完全准确，请以实际收费为准)。

## 当日课表查询

​	将查询当日课表信息。

## 自动选课

​	因一些原因，该功能仅对少数人员开放，您需要许可证才能够使用，请先联系作者获取许可证(若您已获得许可证，请将其放置于"./data"文件夹下)。

​	使用自动选课前，您需要先添加一些预选课，这些预选课即为您想要选择的课程，可通过“添加预选课”功能进行添加，您需要依次输入“开课学年学期”(格式与【默认选择学期】一致)，“课程名称或编号”，“教师姓名”三个参数，其中，除"开课学年学期"参数外，其他两个参数可留空(支持模糊查询，留空代表全查询)，程序将自动查询符合条件的课程，输入课程对应的序号并按下回车即可选择添加。

​	需要注意的是，程序将仅查询并返回前10条符合条件的数据，所以您需要尽可能缩小您的搜索范围，您所添加的课程在本轮选课中也可能未开放导致选课失败，所以在选课正式开始之前，您需要留意本轮""预览选课"内容。

​	如果您对添加的预选课并不满意而想要修改，可通过"删除预选课"功能进行删除，当然，如果数据量较大，您也可以直接删除"./data/preselection.json"文件，您的预选课信息保存在此处

​	当您做好了准备，您就可以开始自动选课了，当然，您还需要再确认一下您的预选课信息，并选择选科轮次，若选课轮次可查询到但还未开放选课，程序将持续进行监听，直至选课开始并完成预订选课。

​	选课期间的产生的重要信息将会保存在"./output/log.txt"文件中，您可以直观地看到在何时选课成功或失败。

​	请您不要完全相信本程序，在自动选课结束后，请您亲自登录教务系统网站查询选课信息。

# 一些可能遇到的问题

### 在WebVPN登录过程中，明明账户和密码都正确，却一直登录失败

可能是之前登录WebVPN失败次数过多触发了滑块验证码，只需要在浏览器中手动成功登陆过一次WebVPN即可

### 我的Node.js没有安装在默认位置，导致程序无法模拟WebVPN登录怎么办

修改path.txt的内容即可，默认为C:\Program Files\nodejs，将其修改成您下载的Node.js的绝对路径即可

### 出现了无法自主解决，该文档中也未提及的问题

可以善用搜索引擎和一些AI大模型（例如：通义千问等），也可以及时联系作者进行反馈

# 关于

​	本程序由 BR 独立编译完成，除选课部分外的代码将永久开源，已上传至[Github](https://github.com/YZBRH/XAUTer-s-UEAS_helper)，觉得好玩好用记得来给我点个star啊(✧∇✧)，如有问题欢迎反馈，可联系[QQ](1947514592)

# 更新日志

[V1.0](2024.02.23)首版本发布

[V1.1](2024.02.24)优化登录流程，现在登录时会首先尝试直连，直连失败后再使用WebVPN进行连接

[V2.0](2024.03.19)增加"自动选课"功能，封装代码，修复了一些BUG，改善了程序运行逻辑

[V2.1](2024.03.20)优化代码结构与模块引用，减小了文件体积

[V2.2](2024.06.14)添加颜色，显示更加直观

[V2.3](2024.06.29)更新了菜单选择方式

[V2.4](2024.07.02)修复了选课部分中，在选课未开放时启用“开始选课”功能无法进行监听

[V2.5](2024.07.02)修复了在部分windows设备上，换颜色转义不生效问题

[V2.6](2024.07.02)优化了开始选课功能的代码逻辑，现在可以更方便的进行持续监听

[V2.7](2024.07.03)增加了选课部分的断连重试机制，优化了日志写入

[V2.8](2024.07.03)修复了有时添加预选课在未查询缺失相应提示信息

