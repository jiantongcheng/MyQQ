# -*- coding: utf-8 -*-
#!/usr/bin/env python
import os
import sys

import requests
import getpass
import re
import json
import random
import time
import pickle
import threading
import redis
from bs4 import BeautifulSoup

URL_BASE = "http://192.168.0.11:8000/"
URL_LOGIN = URL_BASE + "login"
URL_REGISTER = URL_BASE + "register"

Session = None
Payload_common = None

News_base = 0
News_Contacts = 0
Event_inform = None

Redis_Pool = None

GENDER_LIST = [None, '男', '女', '保密']
SIGN_LIST = ['保密', '水瓶', '双鱼', '白羊', '金牛', '双子', '巨蟹', '狮子', '处女', '天秤', '天蝎', '射手', '摩羯']      

# 写文件，封装函数
def tool_writefile(name, content):
    f = open(name, "w")
    f.write(content)
    f.close()

# 私人业务，同学会相关
def auto_register():
    print "======注册工厂======"

    for i in range(100,301):
        name = "yaozhong" + str(i)
        print "------>name: " + name

        s = requests.Session()
        r = s.get(URL_REGISTER)
        csrftoken = r.cookies['csrftoken']

        passwd = "123456"
        nickname = name
        email = name + "@qq.com"
        gender = 3
        sign = 0

        payload = {
            'user_name': name,
            'user_nickname': nickname,
            'user_password': passwd,
            'user_email': email,
            'user_sign': sign,
            'user_gender': gender,
            'csrfmiddlewaretoken': csrftoken,
        }

        r = s.post(URL_BASE+"register", data=payload)
        print "POST '注册', ACK: " + str(r.status_code)

        if r.status_code == 200:
            if "注册成功" in r.content:
                print "===恭喜，注册成功"
            else:
                print "===失败"
        else:
            print "===非200"
        
        time.sleep(1)
    
    return 0

# 注册操作
def register():
    print "======注册(输入:Q/q退出)======"
    s = requests.Session()
    r = s.get(URL_REGISTER)
    csrftoken = r.cookies['csrftoken']

    # ---^_^: 对输入的用户名进行本地检测和后台检测
    while True:
        ret = raw_input("请输入用户名: ")
        if ret == 'q' or ret == 'Q':
            print "退出注册流程"
            return -1
        elif len(ret) < 6 or len(ret) > 16:
            print "长度必须在6~16位"
            continue
        elif not re.match('[A-Za-z_]{1}\w*$', ret):
            print "内容必须由字母、数字、下划线组成，且不能由数字开头"
            continue
        else:
            print "===检测是否注册..."
            payload = {
                'user_name': ret,
                'csrfmiddlewaretoken': csrftoken,
            }

            r = s.post(URL_BASE+"register/check", data=payload)
            print "POST '检测是否注册', ACK: " + str(r.status_code)
            print r.content
            if r.status_code == 200:
                if "NotExist." in r.content:
                    print "===恭喜，未注册"
                    break
                else:
                    print "===" + ret + " 已被注册!"
    name = ret
    # ---^_^: 记录到全局变量，供后续使用
    global Payload_common
    global Session
    Session = s
    Payload_common = {
        'user_name': name,
        'csrfmiddlewaretoken': csrftoken,
    }

    # ---^_^: 对输入的密码进行本地检测
    while True:
        ret = getpass.getpass("请输入密码: ")
        if ret == 'q' or ret == 'Q':
            print "退出注册流程"
            return -1
        elif len(ret) < 6 or len(ret) > 16:
            print "长度必须在6~16位"
            continue
        elif not re.match('\w+$', ret):
            print "内容必须由字母或数字或下划线组成"
            continue
        else:
            break
    passwd = ret

    # ---^_^: 对输入的昵称进行本地检测
    while True:
        ret = raw_input("请输入昵称: ")
        if ret == 'q' or ret == 'Q':
            print "退出注册流程"
            return -1
        elif len(ret) < 3 or len(ret) > 8:
            print "长度必须在3~8位"
            continue
        elif not re.match(u'[\u4e00-\u9fa5\w]+$', ret.decode("utf-8")):
            print "内容必须由字母、数字、下划线或中文组成"
            continue
        else:
            break
    nickname = ret

    print "另外系统将为您临时随机生成以下信息:"

    random_num = random.randint(100000,999999)
    email = str(random_num) + "@tmp.com"
    print "Email: " + email

    gender = random.randint(1,len(GENDER_LIST)-1)
    print "性别: " + GENDER_LIST[gender]

    sign = random.randint(0,len(SIGN_LIST)-1)
    print "星座: " + SIGN_LIST[sign]

    payload = {
        'user_name': name,
        'user_nickname': nickname,
        'user_password': passwd,
        'user_email': email,
        'user_sign': sign,
        'user_gender': gender,
        'csrfmiddlewaretoken': csrftoken,
    }

    r = s.post(URL_BASE+"register", data=payload)
    print "POST '注册', ACK: " + str(r.status_code)
    # tool_writefile("tmp.txt", r.content)

    if r.status_code == 200:
        if "注册成功" in r.content:
            print "===注册成功!"
        else:
            print "===注册失败"
            bs=BeautifulSoup(r.content,"html.parser")   #创建BeautifulSoup对象
            body=bs.body   #获取body部分
            div = body.find('div', id='myAlertContent')
            print div.string

            return -2
            
    return 0

# 模拟web页面被关闭后再次打开的情况，用可能存在的会话相关信息再次登录
def login_pre():
    try:
        with open("pickle-obj", "r") as f:
            obj = pickle.load(f)
            if obj == True:
                global Payload_common
                global Session
                obj = pickle.load(f)
                Session = obj
                obj = pickle.load(f)
                Payload_common = obj
            else:
                return -1
    except:
        return -1

    print "===用缓存再次登录"
    r = Session.post(URL_LOGIN, data=Payload_common)
    print "POST '登录', ACK: " + str(r.status_code)

    bs=BeautifulSoup(r.content,"html.parser")   #创建BeautifulSoup对象
    body=bs.body   #获取body部分

    if r.content.find('登录页面') != -1:
        print "===登录失败!"
        div = body.find('div', id='myAlertContent')
        print div.string

        with open("pickle-obj", "w") as f:
            pickle.dump(False, f)
        return -2

    print "===登录成功"
    a = body.find('a', text=re.compile("Lv"))
    print a.string 

    return 0
    
# 登录操作
def login_init():
    """
    功能: 登陆
    返回: -2 登录失败 -1 主动退出, 0 登陆成功
    """
    print "======登录(输入:Q/q退出)======"
    while True:
        ret = raw_input("请输入用户名: ")
        if ret == 'q' or ret == 'Q':
            print "退出登录流程"
            return -1
        elif len(ret) < 6 or len(ret) > 16:
            print "长度必须在6~16位"
            continue
        elif not re.match('[A-Za-z_]{1}\w*$', ret):
            print "内容必须由字母、数字、下划线组成，且不能由数字开头"
            continue
        else:
            break
    name = ret

    while 1:
        ret = getpass.getpass("请输入密码: ")
        if ret == 'q' or ret == 'Q':
            print "退出登录流程"
            return -1
        elif len(ret) < 6 or len(ret) > 16:
            print "长度必须在6~16位"
            continue
        elif not re.match('\w+$', ret):
            print "内容必须由字母或数字或下划线组成"
            continue
        else:
            break
    passwd = ret

    #进行登陆操作
    print "===正在登录..."
    s = requests.Session()
    r = s.get(URL_LOGIN)
    csrftoken = r.cookies['csrftoken']

    payload = {
        'user_name': name,
        'user_password': passwd,
        'csrfmiddlewaretoken': csrftoken,
    }
    r = s.post(URL_LOGIN, data=payload)
    print "POST '登录', ACK: " + str(r.status_code)

    bs=BeautifulSoup(r.content,"html.parser")   #创建BeautifulSoup对象
    body=bs.body   #获取body部分

    if r.content.find('登录页面') != -1:
        print "===登录失败!"
        div = body.find('div', id='myAlertContent')
        print div.string
        return -2
        
    print "===登录成功"
    a = body.find('a', text=re.compile("Lv"))
    print a.string
    # ---^_^---
    global Payload_common
    global Session
    Session = s
    Payload_common = {
        'user_name': name,
        'csrfmiddlewaretoken': csrftoken,
    }

    # 登录成功，将一些对象持久化
    with open("pickle-obj", "w") as f:
        pickle.dump(True, f)
        pickle.dump(Session, f)
        pickle.dump(Payload_common, f)

    return 0

# 退出登录
def post_logout():
    r = Session.post(URL_BASE+"logout", data=Payload_common)
    print "POST '退出登录', ACK: " + str(r.status_code)
    resp = json.loads(r.content)
    if resp['stat'] == 'success':
        print "===成功"
        return 0
    else:
        print "===失败"
        return -2

# 读取基本资料
def post_readBase():
    r = Session.post(URL_BASE+"home/readBase", data=Payload_common)
    print "POST '读取基本资料', ACK: " + str(r.status_code)
    resp = json.loads(r.content)
    if resp['stat'] == 'success':
        print "注册时间: " + str(resp['register_time'])
        print "星座: " + str(resp['user_sign'])
        print "性别: " + str(resp['user_gender'])
        print "昵称: " + str(resp['user_nickname'])
        print "Email是否校验: " + ("是" and resp['user_emailValid'] or "否" )
        print "邮箱: " + str(resp['user_email'])
    else:
        print "===失败"

#读取联系人信息
def post_readContacts():
    r = Session.post(URL_BASE+"home/readContacts", data=Payload_common)
    print "POST '读取联系人', ACK: " + str(r.status_code)
    resp = json.loads(r.content)
    if resp['stat'] == 'success':
        print "好友: " + str(resp['count_friend']) + ", 在线: " + str(resp['count_friend_alive'])
        print "陌生人: " + str(resp['count_stranger']) + ", 在线: " + str(resp['count_stranger_alive'])
        print "黑名单: " + str(resp['count_blacklist'])
        if resp['count_friend'] > 0:
            print "好友列表:"
            for fri in resp['friend']:
                print "------>"
                print "  用户名: " + str(fri['name'])
                print "  性别: " + GENDER_LIST[int(fri['gender'])]
                print "  星座: " + SIGN_LIST[int(fri['sign'])]
        # 陌生人和黑名单详情暂时略过
    else:
        print "===失败"

    return 0

#获取天气情况
def post_getWeather():
    global Redis_Pool
    if Redis_Pool == None:
        # print "Redis_Pool...First"
        Redis_Pool = redis.ConnectionPool(host='127.0.0.1', port=6379, db=0)

    if Redis_Pool:
        # print "Redis_Pool..."
        rds = redis.Redis(connection_pool=Redis_Pool)
        stamp = rds.get('weather-stamp')
        current_stamp = time.strftime("%Y-%m-%d", time.localtime())
        if stamp == current_stamp:
            info = rds.get("weather-info")
            info_obj = pickle.loads(info)
            for day in info_obj:
                print day[0]
                print day[1]
                if day[2]:
                    print str(day[3]) + "~" + str(day[2])
                else:
                    print str(day[3])

            return 0
    
    url_hangzhou = 'http://www.weather.com.cn/weather/101210101.shtml'
        
    payload = Payload_common.copy()
    payload['url'] = url_hangzhou

    r = Session.post(URL_BASE+"getWeather", data=payload)
    print "POST '读取杭州天气', ACK: " + str(r.status_code)
    resp = json.loads(r.content)
    if resp['stat'] == 'success':
        for day in resp['days']:
            print day[0]
            print day[1]
            if day[2]:
                print str(day[3]) + "~" + str(day[2])
            else:
                print str(day[3])
        # 将resp字典对象存在redis数据库中
        if rds:
            info = pickle.dumps(resp['days'])
            rds.set("weather-info", info)
            rds.set("weather-stamp", current_stamp)
            return 0
        else:
            return 1
    else:
        return -1

# 修改密码业务
def post_modifyPassword():
    print "======修改密码(输入:Q/q退出)======"
    ret = getpass.getpass("请输入原密码:")
    if ret == 'q' or ret == 'Q':
        print "放弃..."
        return -1
    elif len(ret) < 6 or len(ret) > 16:
        print "长度必须在6~16位"
        return -1
    elif not re.match('\w+$', ret):
        print "内容必须由字母或数字或下划线组成"
        return -1
    else:
        None
    oldpswd = ret

    while True:
        ret = getpass.getpass("请输入新密码:")
        if ret == 'q' or ret == 'Q':
            print "放弃..."
            return -1
        elif len(ret) < 6 or len(ret) > 16:
            print "长度必须在6~16位"
            continue
        elif not re.match('\w+$', ret):
            print "内容必须由字母或数字或下划线组成"
            continue
        else:
            None
        newpswd = ret

        ret = getpass.getpass("请再次确认新密码:")
        if ret == 'q' or ret == 'Q':
            print "放弃..."
            return -1
        elif len(ret) < 6 or len(ret) > 16:
            print "长度必须在6~16位"
            continue
        elif not re.match('\w+$', ret):
            print "内容必须由字母或数字或下划线组成"
            continue
        else:
            None

        if newpswd != ret:
            print "两次密码不一致"
            continue
        else:
            break

    payload = Payload_common.copy()
    payload['user_old_password'] = oldpswd
    payload['user_new_password'] = newpswd

    r = Session.post(URL_BASE+"home/modifyPassword", data=payload)
    print "POST '修改密码', ACK: " + str(r.status_code)
    resp = json.loads(r.content)
    if resp['stat'] == 'success':
        print "===成功，请重新登录"
        return 0
    else:
        print resp['hint']
        return -2

# 发送心跳消息
def post_heart():
    r = Session.post(URL_BASE+"check_news", data=Payload_common)
    if r.status_code != 200:
        print "check_new返回状态码: " + str(r.status_code) 
        return -2
    
    resp = json.loads(r.content)
    if resp['stat'] == 'success':
        global News_Contacts
        global News_base
        if int(resp['news_contacts']) != News_Contacts or int(resp['news_contacts_base']) != News_base:
            News_Contacts = int(resp['news_contacts'])
            News_base = int(resp['news_contacts_base'])
            print "发现有未读base消息: " + str(News_base) + "条"
            print "发现有未读联系人消息: " + str(News_Contacts) + "条"

            return 1
        else:
            return 0
    elif resp['stat'] == 'fail':
        if resp['reason'] == 'SESSION_INVALID':
            print "因为您长时间没有操作页面或者有非法操作，请重新登录^_^"
        else:
            print "something error@check_news back"

        return -3        
    else:
        None

#心跳线程，定期查看有无新消息
def thread_heart():
    global Event_inform
    exit_flag = 0
    print "======Heart Start====="
    while exit_flag == 0:
        rt = post_heart()
        if rt < 0:
            break

        for i in range(1,6):
            if Event_inform.isSet():
                Event_inform.clear()
                exit_flag = 1
                break
            time.sleep(1)

    print "======Heart End====="

#登陆成功后进行的操作
def login_main():
    global Event_inform
    Event_inform = threading.Event()

    tid = threading.Thread(target=thread_heart)
    tid.setDaemon(True)
    tid.start()

    flag = None     #flag优先于ret

    while True:
        if flag == None:
            ret = hint('login')
        else:
            ret = None

        if ret == 'q' or ret == 'Q':
            sys.exit()
        elif flag == 'logout' or ret == 'logout':
            # 需要停止心跳线程 
            Event_inform.set()
            tid.join()

            rt = post_logout()
            if rt == 0:     #退出成功，需要清理一些东西
                with open("pickle-obj", "w") as f:
                    pickle.dump(False, f)   #清除缓存
            break
        elif ret == '1':
            post_readBase()
        elif ret == '2':
            rt = post_modifyPassword()
            if rt == 0:  #修改成功，需要重新登录
                flag = 'logout'
                continue
        elif ret == '3':
            rt = post_readContacts()
        elif ret == '4':
            rt = post_getWeather()
        else:
            None

        flag = None

    return 0  

# 命令提示
def hint(flag):
    if flag == 'main':
        ret = raw_input(
"""
---^_^:首页---
1: 注册 2: 登录 Q/q: 退出
--->""")
        return ret
    elif flag == "login":
        ret = raw_input(
"""
------^_^:Home页面------
1: 查看基本资料 2: 修改密码
3: 查看联系人列表 4: 获取杭州天气
logout: 注销 Q/q: 强退
--->""")
        return ret
    else:
        return "无效的参数!"

# 主运行逻辑
if __name__ == "__main__":
    flag = None     #flag优先于ret

    while True:
        if flag == None:
            ret = hint('main')
        else:
            ret = None

        if ret == 'q' or ret == 'Q':
            sys.exit()
        elif ret == '1':
            rt = register()
            if rt == 0:
                flag = "login"      #注册成功，跳转到login逻辑
                continue 
        elif flag == "login" or ret == '2':
            rt = login_pre()
            if rt == -1 or rt == -2:
                rt = login_init()

            if rt == 0:
                login_main()
        else:
            None
        
        flag = None
