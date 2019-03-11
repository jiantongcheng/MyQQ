# -*- coding: utf-8 -*-
"""
基础操作
包括如下：
登陆、注销、注册、用户名检测、忘记密码、新增密码、读取/修改基本资料、修改密码、邮箱验证等功能
"""
from __future__ import unicode_literals

from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.sessions.models import Session
from useradmin.models import userAdmin
from useradmin.dynamic_model import create_user_contacts, get_user_contacts, create_user_news, get_user_news, create_user_chats, get_user_chats
from django.db import models
from django.core.mail import send_mail
from news import news_contacts_new_count, insert_user_contact
from chats import insert_chat
from write import insert_user_news_classtype2

import random
import datetime
import json

#缓存数据库
from django.core.cache import cache

# Create your views here.

def user_valid(user_name):
    '''
    类型：工具
    查看用户名在数据库中是否存在，若存在则返回相应的模型对象
    '''
    ret = ''
    try:
        obj = userAdmin.objects.get(user_name=user_name)
    except userAdmin.DoesNotExist:
        ret = False
        obj = None
    else:
        ret = True

    return (ret, obj)

def login(request):
    '''
    类型：接口
    进入登录页面或者执行登录操作
    '''
    userName = request.session.get('username', None)  
    first_login = 0
    # print request.session.items()
    # print request.COOKIES
    # request.session.flush()
    # s=Session.objects.all()
    # for i in s:
    #     print i.get_decoded()
    # request.session.set_test_cookie()
    
    alert_info = "None_None"
    #第一次判断
    if userName == None:
        if request.method == 'POST':
            print '...Login...'
            userName = request.POST.get('user_name', '')
            ret, obj = user_valid(userName)
            if ret:
                userPassword = request.POST.get('user_password', '')
                if obj.user_password == userPassword:
                    request.session['username'] = userName
                    first_login = 1
                else:   #密码不正确
                    alert_info = "登录失败!用户名或者密码错误!"
                    userName = None
            else:   #用户名无效
                alert_info = "登录失败!用户名或者密码错误!"
                userName = None
    else:   #在session有效期内再次登录
        ret, obj = user_valid(userName)
        if ret:
            None
        else:
            userName = None

    #多加一个权限判断
    if userName != None:    
        if obj.limit_reason != 0:
            print "-- 1"
            key_name = userName+",limit"
            print key_name
            # cache.set(key_name, "limit", 90)  #调试
            
            if cache.has_key(key_name):
                print "-- 2"
                limit_val = cache.ttl(key_name)
                if limit_val == None:   #说明之前没有设置超时期限，将在这里设置
                    print "-- 3"
                    cache.set(key_name, "limit", 3600)    #3600
                    limit_val = cache.ttl(key_name)

                if obj.limit_reason == 1:
                    alert_info = "登录失败!原因:你输入过敏感词汇！解封剩余时间:"+str(limit_val)+"秒"
                elif obj.limit_reason == 2:
                    alert_info = "登录失败!原因:上次聊天频率太快！解封剩余时间:"+str(limit_val)+"秒"
                elif obj.limit_reason == 3:
                    alert_info = "登录失败!原因:上次聊天信息过多！解封剩余时间:"+str(limit_val)+"秒"
                else:
                    alert_info = "登录失败!原因:未知！"
                
                userName = None
            else:       #说明缓存期限满了，被自动删除了
                obj.limit_reason = 0
                obj.save()      #这里save应该不会影响下面继续使用obj吧？
        else:
            print "-- 4"
            None

    #第二次判断
    if userName != None:
        request.session.set_expiry(600)  #600

        permitAdd = obj.setting_permitAdd
        permitSearch = obj.setting_permitSearch
        levelOrig = obj.user_level
        if levelOrig == 0:
            level = 0
        elif levelOrig < 10:
            level = 1
        elif levelOrig < 30:
            level = 2
        elif levelOrig < 100:
            level = 3
        elif levelOrig < 300:
            level = 4
        else:
            level = 5 
        login_time_last = obj.login_time         # 返回上次的登录时间
        login_time = login_time_last.strftime("%Y-%m-%d %H:%M:%S")
        news_contacts, news_contacts_base, news_contacts_status, news_contacts_chat = news_contacts_new_count(userName, 0)
        #暂不将news_contacts_status和news_contacts_chat作为回复，让浏览器定期获取
        
        if first_login == 1:    
            #第一次登陆需要做的操作
            login_time_now = datetime.datetime.now()+datetime.timedelta(hours=8)    #记住这次的登录时间
            obj.login_time = login_time_now
            obj.user_status = 1     #online
            login_time_last_day = login_time_last.strftime("%Y-%m-%d")
            login_time_now_day = login_time_now.strftime("%Y-%m-%d")
            if login_time_last_day != login_time_now_day:   #说明是当天第一次登陆
                obj.user_level += 1

            obj.save()              #记得save

            #通知小伙伴们，我上线了
            hostClass = get_user_contacts(userName)
            guestObjs = hostClass.objects.exclude(status=0)  #排除离线的家伙们
            for guest in guestObjs:
                guest_name = guest.name
                insert_user_news_classtype2(guest_name, 1, userName)
        
        my_dict = {
            'user': {
                'name': userName,
                'permitAdd': permitAdd,
                'permitSearch': permitSearch,
                'level': level,
                'login_time': login_time,
                'news_hall': 0,
                'news_contacts': news_contacts,
                'news_contacts_base': news_contacts_base,
            },
        }
        return render(request, 'home.html', my_dict)        #进入主页
    else:
        return return_login(request, alert_info)

def return_login(request, alert_info):
    '''
    类型：接口
    进入登陆页面
    '''
    # alert_info = "None_None"
    my_dict = {
            'index': 'index_login',
            'alert': alert_info,
        }
    return render(request, 'index.html', my_dict)       #进入登陆页面

def offline_clean(request):
    '''
    类型：工具
    下线清理，包括session和数据库操作
    '''
    userName = request.session.get('username', None)
    # if userName != None:    #因为加了拦截器，这里不再判断，程序简洁！
    request.session.flush()     #清空session
    ret, obj = user_valid(userName)
    if ret:
        obj.user_status = 0     #offline
        start_time = obj.login_time.strftime("%Y-%m-%d %H:%M:%S")
        # start_time = start_time.strftime("%Y-%m-%d %H:%M:%S")
        start_time = datetime.datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")

        leave_time = datetime.datetime.now()+datetime.timedelta(hours=8)
        leave_time = leave_time.strftime("%Y-%m-%d %H:%M:%S")
        leave_time = datetime.datetime.strptime(leave_time, "%Y-%m-%d %H:%M:%S")

        stride_sec = (leave_time-start_time).seconds
        if stride_sec > 60*30:
            obj.user_level += 3
        elif stride_sec > 60*15:
            obj.user_level += 2
        elif stride_sec > 60*5:
            obj.user_level += 1
        else:
            None
    
        obj.save()              #记得save

        #通知小伙伴们，我下线了
        hostClass = get_user_contacts(userName)
        guestObjs = hostClass.objects.exclude(status=0)  #排除离线的家伙们
        for guest in guestObjs:
            guest_name = guest.name
            insert_user_news_classtype2(guest_name, 0, userName)
        return True
    else:
        return False

def logout(request):
    '''
    类型：接口
    注销操作
    '''
    if request.method == 'POST':
        print "---Logout---"
        if offline_clean(request):
            hint = "None_None"
        else:
            hint = "退出登录失败!"

        ret = {
            'stat': 'success',
            'hint': hint,
        }

        return HttpResponse(json.dumps(ret))

def create_userAdmin(my_form):
    '''
    类型：工具
    创建模型数据，对应数据库表格
    '''
    usr = userAdmin(user_name=my_form['user_name'])
    usr.user_nickname = my_form['user_nickname']
    usr.user_password = my_form['user_password']
    usr.user_email = my_form['user_email']
    usr.user_emailValid = 0
    usr.user_sign = my_form['user_sign']
    usr.user_gender = my_form['user_gender']
    usr.user_blacklist = ''
    usr.user_status = 0
    usr.save()

    create_user_contacts(my_form['user_name'])          #创建联系人表格
    create_user_news(my_form['user_name'])          #创建news
    create_user_chats(my_form['user_name'])         #创建聊天表格

    return 0

def register_check(request):
    '''
    类型：接口
    检测用户名是否已被注册
    '''
    if request.method == 'GET':
        print "-----------------------GET"
        user_name = request.GET.get('user_name', '')
    elif request.method == 'POST':
        print "-----------------------POST"
        user_name = request.POST.get('user_name', '')
    else:
        None

    ret, _Null_ = user_valid(user_name)
    if ret:
        ret = "Exist."
    else:
        ret = "NotExist."

    ret = user_name + ":" + ret

    return HttpResponse(ret)

def modifyPassword(request):
    '''
    类型：接口
    修改密码
    '''
    if request.method == 'POST':
        userName = request.session.get('username', None)  
        user_old_password = request.POST.get('user_old_password', '')
        user_new_password = request.POST.get('user_new_password', '')
        ret, obj = user_valid(userName)
        if ret:
            if obj.user_password != user_old_password:
                ret = {
                    'stat': 'fail',
                    'hint': '修改失败，原密码不正确!',
                }
            else:
                obj.user_password = user_new_password
                obj.save()
                ret = {
                    'stat': 'success',
                    'hint': '修改成功，请重新登录！',
                }
        else:
            ret = {
                'stat': 'fail',
                'hint': '修改失败，原因：用户名不存在！',
            }

        return HttpResponse(json.dumps(ret))
    else:
        None

def modifyBase(request):
    '''
    类型：接口
    修改基本资料
    '''
    if request.method == 'POST':
        userName = request.session.get('username', None)  
        user_nickname = request.POST.get('user_nickname', '')
        user_email = request.POST.get('user_email', '')
        user_sign = request.POST.get('user_sign', '')
        user_gender = request.POST.get('user_gender', '')
        ret, obj = user_valid(userName)
        if ret:
            obj.user_nickname = user_nickname
            obj.user_email = user_email
            obj.user_sign = user_sign
            obj.user_gender = user_gender
            obj.save()
            ret = {
                'stat': 'success',
            }
        else:
            ret = {
                'stat': 'fail',
                'reason': '修改失败，原因：用户名不存在！',
            }
        return HttpResponse(json.dumps(ret))
    else:
        None
    
def readBase(request):
    '''
    类型：接口
    读取用户基本信息
    '''
    if request.method == 'POST':
        userName = request.session.get('username', None)  
        ret, obj = user_valid(userName)
        if ret:
            timeOrig = obj.register_time + datetime.timedelta(hours=8)  #转化为北京时间
            register_time = timeOrig.strftime("%Y-%m-%d %H:%M:%S")

            ret = {
                'stat': 'success',
                'user_nickname': obj.user_nickname,
                'user_email': obj.user_email,
                'user_emailValid': obj.user_emailValid,
                'user_sign': obj.user_sign,
                'user_gender': obj.user_gender,
                'register_time': register_time

                # 'user_status': obj.user_status,
                # 'setting_permitSearch': obj.setting_permitSearch,
                # 'setting_permitAdd': obj.setting_permitAdd,
            }
        else:
            ret = {
                'stat': 'fail',
                'reason': '用户名不存在',
            }
        return HttpResponse(json.dumps(ret))
    else:
        None

def emailVerify_send(request):
    '''
    类型：接口
    邮箱验证码发送
    '''
    if request.method == 'POST':
        userName = request.session.get('username', None)
        ret, obj = user_valid(userName)
        if ret:
            if obj.user_emailValid == 1:
                ret = {
                    'stat': 'fail',
                    'hint': '邮箱已通过验证！',
                }
            else:           #产生随机数，发送给email账号，并记录时间
                valid = False
                if obj.forget_randomint == 0:
                    valid = True
                else:   #此时需要判断时间的有效性
                    fit_forget_time =  obj.forget_time.replace(tzinfo=None)
                    nowTime = datetime.datetime.now()
                    diff = (nowTime - fit_forget_time).seconds
                    if diff < 60:       #说明用户操作太频繁
                        valid = False   
                    else:
                        valid = True

                if valid == True:
                    user_email = obj.user_email                 #获取用户邮箱
                    random_num = random.randint(100000,999999)     #生成随机数
                    obj.forget_randomint = random_num            #保存随机数
                    obj.forget_time = datetime.datetime.now()    #保存当前时间
                    obj.forget_trycnt = 0                        #清空尝试计数
                    obj.save()

                    mail_subject = 'MyQ, 邮箱绑定验证'
                    mail_content = '您的验证码是' +str(random_num) + ',请尽快确认！'
                    mail_from = "MyQ Robot <330755770@qq.com>"
                    mail_to = user_email
                    send_mail(mail_subject, mail_content, mail_from, [mail_to], fail_silently=False)

                    ret = {
                        'stat': 'success',
                        'hint': '',
                    }
                else:
                    ret = {
                        'stat': 'fail',
                        'hint': '操作太频繁，请稍后再试！',
                    }
        else:
            ret = {
                'stat': 'fail',
                'hint': '用户名不存在',
            }
        return HttpResponse(json.dumps(ret))
    else:
        None

def emailVerify_recv(request):
    '''
    类型：接口
    邮箱验证码接收
    '''
    if request.method == 'POST':
        userName = request.session.get('username', None)
        ret, obj = user_valid(userName)
        if ret:
            if obj.user_emailValid == 1:
                ret = {
                    'stat': 'fail',
                    'hint': '邮箱已通过验证！',
                }
            else:           
                verify_code = request.POST.get('verify_code', '')
                if obj.forget_randomint == 0:
                    ret = {
                        'stat': 'fail',
                        'hint': '验证失败，原因：超时！',
                    }
                elif str(obj.forget_randomint) == verify_code: #初步满足要求
                    fit_forget_time =  obj.forget_time.replace(tzinfo=None)
                    nowTime = datetime.datetime.now()
                    diff = (nowTime - fit_forget_time).seconds
                    if diff < 60*5:     #N分钟内有效
                        ret = {
                            'stat': 'success',
                            'hint': '',
                        }
                        obj.user_emailValid = 1
                        obj.user_level += 10     #经验值+10
                    else:
                        ret = {
                            'stat': 'fail',
                            'hint': '验证失败，原因：超时！',
                        }
                    obj.forget_randomint = 0    #将随机数置为无效

                else:
                    ret = {
                        'stat': 'fail',
                        'hint': '验证失败，原因：校验码不正确！',
                    }
                    obj.forget_randomint = 0    #将随机数置为无效
                obj.save()
        else:
            ret = {
                'stat': 'fail',
                'hint': '用户名不存在',
            }
        return HttpResponse(json.dumps(ret))
    else:
        None

def register(request):
    '''
    类型：接口
    注册新用户
    '''
    if request.method == 'POST':
        print 'post_register'
        my_form = {}
        my_form['user_name'] = request.POST.get('user_name', '')
        my_form['user_nickname'] = request.POST.get('user_nickname', '')
        my_form['user_password'] = request.POST.get('user_password', '')
        my_form['user_email'] = request.POST.get('user_email', '')
        my_form['user_sign'] = request.POST.get('user_sign', '')
        my_form['user_gender'] = request.POST.get('user_gender', '')

        # for key,value in my_form.items:     #这里会报错?! 'builtin_function_or_method' object is not iterable
        
        # for key, value in zip(my_form.iterkeys(), my_form.itervalues()):
        #     print(key, value)
        alert_info = "None_None"

        ret, _Null_ = user_valid(my_form['user_name'])
        if ret or my_form['user_name'] == "MyQ_jiantong":   #暂且将MyQ_jiantong作为管理员
            ret = "index_register"
            alert_info = '注册失败！用户名\'' + my_form['user_name'] + '\'已存在！'
        else:
            if userAdmin.objects.email_used(my_form['user_email']) == True:
                ret = "index_register"
                alert_info = '注册失败！Email: \'' + my_form['user_email'] + '\'已存在！'
            else:
                ret = "index_login"
                create_userAdmin(my_form)
                insert_user_contact(my_form['user_name'], 'MyQ_jiantong', 0)
                insert_user_contact('MyQ_jiantong', my_form['user_name'], 0)
                message = "您好，欢迎来到MyQ，我是管理员建通，有事您叫我^_^"
                insert_chat(my_form['user_name'], 'MyQ_jiantong', 1, 0, 0, message)
                alert_info = "注册成功，请登录！"

        my_dict = {
            'index': ret,
            'alert': alert_info,
        }
    else:
        print 'no_post_register'
        my_dict = {
            'index': 'index_register',
            'alert': "None_None",
        }
    
    return render(request, 'index.html', my_dict)

def forget(request):
    '''
    类型：接口
    忘记密码
    '''
    alert_info = "None_None"
    if request.method == 'POST':
        print 'tttttt_forget'
        userName = request.POST.get('user_name', '')
        ret, obj = user_valid(userName)
        if ret:     #发送修改页面链接到用户邮箱
            if obj.user_emailValid == 0:
                alert_info = "对不起，该用户绑定的邮箱没有通过验证，无法通过此方式修改密码！"
            else:
                print obj.forget_randomint
                print obj.forget_time
                valid = False

                if obj.forget_randomint == 0:
                    valid = True
                else:   #此时需要判断时间的有效性
                    fit_forget_time =  obj.forget_time.replace(tzinfo=None)
                    nowTime = datetime.datetime.now()
                    diff = (nowTime - fit_forget_time).seconds
                    if diff < 60:       #说明用户操作太频繁
                        valid = False   
                    else:
                        valid = True

                if valid == True:
                    user_email = obj.user_email                 #获取用户邮箱
                    random_num = random.randint(100000,999999)     #生成随机数
                    obj.forget_randomint = random_num            #保存随机数
                    obj.forget_time = datetime.datetime.now()    #保存当前时间
                    obj.forget_trycnt = 0                        #清空尝试计数
                    obj.save()

                    mail_subject = 'MyQ, 修改密码页面链接'
                    mail_content = '请尽快进入该链接页面修改用户密码：' + 'http://192.168.11.130:8081/modify?userName=' + userName +'&randInt='+str(random_num)
                    mail_from = "MyQ Robot <330755770@qq.com>"
                    mail_to = user_email
                    send_mail(mail_subject, mail_content, mail_from, [mail_to], fail_silently=False)
                    
                    print userName + ":" + user_email + ":" + str(random_num)     #需要将数字转换为字符串
                    alert_info = "已向用户("+userName+")绑定的邮箱发送链接，请尽快登录邮箱查看" + str(random_num)
                else:
                    alert_info = "操作太频繁，请稍后再试！"
        else:
            alert_info = "用户名不存在!"

    my_dict = {
        'alert': alert_info,
    }
    return render(request, 'forget.html', my_dict)        

def modify(request):
    '''
    类型：接口
    通过密码找回，修改密码
    '''
    valid = False

    if request.method == 'GET':
        alert_info = "None_None"
        user_name = request.GET.get('userName', '')
        random_str = request.GET.get('randInt', '0')
        random_int = int(random_str)
        print "----modify:"
        print user_name
        print random_int

        ret, obj = user_valid(user_name)
        if ret:
            if obj.user_emailValid == 0:
                print "emailValid == 0"
                valid = False
            elif obj.forget_randomint == 0:
                print "randomint == 0"
                valid = False
            elif obj.forget_randomint == random_int:    #初步满足要求
                fit_forget_time =  obj.forget_time.replace(tzinfo=None)
                nowTime = datetime.datetime.now()
                diff = (nowTime - fit_forget_time).seconds
                print diff
                if diff < 60*5:         #N分钟内打开链接有效
                    valid = True
                else:
                    valid = False
                    obj.forget_randomint = 0    #将随机数置为无效
                    obj.save()

            else:       #说明随机数有，但不符合
                print "---------here"
                print obj.forget_randomint
                print random_int
                valid = False
                obj.forget_trycnt = obj.forget_trycnt + 1
                if obj.forget_trycnt >= 3:      #存在恶意修改他人密码的可能
                    print "Alert!!!!! forget_trycnt >= 3"
                    obj.forget_randomint = 0    #将随机数置为无效
                    obj.save()
        else:
            print "user_name is not exist"
            valid = False

        if valid == True:       #有权限进入修改密码页面
            my_dict = {
                'rand_int': random_int,
                'user_name': user_name,
                'alert': alert_info,
                'success': 0,
            }
            return render(request, 'modify.html', my_dict)      
    elif request.method == 'POST':
        user_name = request.POST.get('user_name', '')
        rand_str = request.POST.get('rand_int', '')
        rand_int = int(rand_str)
        print "-----------------------------------"
        print rand_int
        success = 0
        alert_info = "None_None"

        ret, obj = user_valid(user_name)
        if ret:
            if obj.forget_randomint == 0:
                alert_info = "修改密码失败，原因：超时!"
                success = 0;
            elif obj.forget_randomint != rand_int:
                #对校验码不一致的情况零容忍，因为此时是POST方式
                alert_info = "修改密码失败，原因：校验码不一致!"
                success = 0;
                obj.forget_randomint = 0
                obj.save()
            else:   #初步满足要求
                fit_forget_time =  obj.forget_time.replace(tzinfo=None)
                nowTime = datetime.datetime.now()
                diff = (nowTime - fit_forget_time).seconds
                if diff < 60*10:    #N分钟内有效
                    success = 1
                else:
                    alert_info = "修改密码失败，原因：超时!"
                    success = 0
                    obj.forget_randomint = 0
                    obj.save()
        else:
            alert_info = "修改密码失败，原因：该用户名未注册!"
            success = 0

        if success == 1:
            user_new_password = request.POST.get('user_password', '')
            obj.user_password = user_new_password
            obj.forget_randomint = 0    #既然修改成功，这里就清零吧
            obj.save()
            alert_info = "密码修改成功！"

        my_dict = {
            'user_name': user_name,
            'alert': alert_info,
            'success': success
        }
        return render(request, 'modify.html', my_dict)     
