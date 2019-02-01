# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.sessions.models import Session
from useradmin.models import userAdmin
from useradmin.dynamic_model import create_user_contacts, get_user_contacts, create_user_news, get_user_news, create_user_chats, get_user_chats
from django.db import models
from django.core.mail import send_mail
from news import news_contacts_new_count
from write import insert_user_news_classtype2

import random
import datetime
import json

# Create your views here.

#查看用户名在数据库中是否存在
def user_valid(user_name):
    ret = ''
    try:
        obj = userAdmin.objects.get(user_name=user_name)
    except userAdmin.DoesNotExist:
        ret = False
        obj = None
    else:
        ret = True

    return (ret, obj)

#进入登录页面或者执行登录操作
def login(request):
    userName = request.session.get('username', None)  
    first_login = 0
    # print request.session.items()
    # print request.COOKIES
    # request.session.flush()
    # s=Session.objects.all()
    # for i in s:
    #     print i.get_decoded()
    # request.session.set_test_cookie()
    
    #第一次判断
    if userName == None:
        alert_info = "None_None"
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

    #第二次判断
    if userName != None:
        request.session.set_expiry(600)  #600

        permitAdd = obj.setting_permitAdd
        permitSearch = obj.setting_permitSearch
        login_time = obj.login_time         # 返回上次的登录时间
        news_contacts, news_contacts_base, news_contacts_status, news_contacts_chat = news_contacts_new_count(userName, 0)
        #暂不将news_contacts_status和news_contacts_chat作为回复，让浏览器定期获取
        
        if first_login == 1:
            obj.login_time = datetime.datetime.now()    #记住这次的登录时间
            obj.user_status = 1     #online
            obj.status_heart = 2    #打算数据库周期事件定为30秒，所以心跳没了之后1分钟左右视为超时
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
                'login_time': login_time,
                'news_hall': 0,
                'news_contacts': news_contacts,
                'news_contacts_base': news_contacts_base,
            },
        }
        return render(request, 'home.html', my_dict)        #进入主页
    else:
        return return_login(request)

#进入登陆页面
def return_login(request):
    alert_info = "None_None"
    my_dict = {
            'index': 'index_login',
            'alert': alert_info,
        }
    return render(request, 'index.html', my_dict)       #进入登陆页面

#下线清理，包括session和数据库
def offline_clean(request):
    userName = request.session.get('username', None)
    # if userName != None:    #因为加了拦截器，这里不再判断，程序简洁！
    request.session.flush()     #清空session
    ret, obj = user_valid(userName)
    if ret:
        obj.user_status = 0     #offline
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

#注销操作
def logout(request):
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

#检测用户名是否已被注册
def register_check(request):
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

#修改密码
def modifyPassword(request):
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

# 修改基本资料
def modifyBase(request):
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
    
#读取用户基本信息
def readBase(request):
    if request.method == 'POST':
        userName = request.session.get('username', None)  
        ret, obj = user_valid(userName)
        if ret:
            register_time = obj.register_time.strftime("%Y-%m-%d %H:%M:%S")
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

#邮箱验证码发送
def emailVerify_send(request):
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

#邮箱验证码接收
def emailVerify_recv(request):
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

#注册新用户
def register(request):
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
        if ret:
            ret = "index_register"
            alert_info = '注册失败！用户名\'' + my_form['user_name'] + '\'已存在！'
        else:
            if userAdmin.objects.email_used(my_form['user_email']) == True:
                ret = "index_register"
                alert_info = '注册失败！Email: \'' + my_form['user_email'] + '\'已存在！'
            else:
                ret = "index_login"
                create_userAdmin(my_form)
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

#忘记密码
def forget(request):
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
