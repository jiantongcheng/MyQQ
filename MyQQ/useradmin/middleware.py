# -*- coding: utf-8 -*- 
from django.shortcuts import render, HttpResponse, redirect, HttpResponseRedirect
import json

try:
    from django.utils.deprecation import MiddlewareMixin  # Django 1.10.x
except ImportError:
    MiddlewareMixin = object  # Django 1.4.x - Django 1.9.x

class WolfMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if request.path == '/login' or request.path == '/':    #登录界面或者登录操作
            pass
        elif request.path == '/register':           #注册操作
            pass
        elif request.path == '/register/check':     #检查用户名是否被注册
            pass
        elif request.path == '/forget':             #忘记密码页面
            pass
        elif request.path == '/modify':             #通过密码找回修改密码   
            pass
        else:
            if request.path != '/check_news':   #非心跳消息，即常规请求，需要更新session有效期
                request.session.set_expiry(600)
            
            if request.session.get('username', None):
                pass
            else:
                print "SESSION_INVALID"
                ret = {
                    'stat': 'fail',
                    'reason': 'SESSION_INVALID',
                }
                return HttpResponse(json.dumps(ret))