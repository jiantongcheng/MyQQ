# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.http import HttpResponse
from useradmin.models import userAdmin

# Create your views here.

def login(request):
    login = request.session.get('Login', 'no')
    
    if login == 'no':
        alert_info = "None_None"
        if request.method == 'POST':
            print 'tttttt_login'
            try:
                user_name = request.POST.get('user_name', '')
                obj = userAdmin.objects.get(user_name=user_name)
            except userAdmin.DoesNotExist:
                alert_info = "登录失败！用户名或者密码错误!"
            else:
                user_password = request.POST.get('user_password', '')
                if obj.user_password == user_password:
                    request.session['Login'] = 'yes'
                    login = 'yes'
                else:
                    alert_info = "登录失败！用户名或者密码错误!"
    # -------------------------------------------------#
    if login == 'yes':
        my_dict = {
            'user': {
                'name': user_name,
                'bottle': {
                    'new': 5,
                    'total': 10,
                },
                'hall':{
                    'new': 1,
                },
                'email':{
                    'new': 2,
                    'total': 3,
                },
            },
        }
        return render(request, 'home.html', my_dict)        #进入主页
    else:
        my_dict = {
            'index': 'index_login',
            'alert': alert_info,
        }

    return render(request, 'index.html', my_dict)

def logout(request):
    request.session['Login'] = 'no'

    return login(request)

def create_userAdmin(my_form):
    usr = userAdmin(user_name=my_form['user_name'])
    usr.user_nickname = my_form['user_nickname']
    usr.user_password = my_form['user_password']
    usr.user_email = my_form['user_email']
    usr.user_sign = my_form['user_sign']
    usr.user_gender = my_form['user_gender']

    usr.save()
    return 0

def register_check(request):

    if request.method == 'GET':
        print "-----------------------GET"
        user_name = request.GET.get('user_name', '')
    elif request.method == 'POST':
        print "-----------------------POST"
        user_name = request.POST.get('user_name', '')
    else:
        None

    try:
        userAdmin.objects.get(user_name=user_name)
    except userAdmin.DoesNotExist:
        ret = "NotExist."
    else:
        ret = "Exist."

    ret = user_name + ":" + ret

    return HttpResponse(ret)


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

        try:
            userAdmin.objects.get(user_name=my_form['user_name'])
        except userAdmin.DoesNotExist:
            ret = "index_login"
            create_userAdmin(my_form)
            alert_info = "注册成功，请登录！"
        else:
            ret = "index_register"
            alert_info = '注册失败！用户名\'' + my_form['user_name'] + '\'已存在！'

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
