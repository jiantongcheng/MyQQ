# -*- coding: utf-8 -*- 
"""
中间件，主要用于session和心跳处理，也做为拦截器
"""
from django.shortcuts import render, HttpResponse, redirect, HttpResponseRedirect
from views import offline_clean
import json, time

try:
    from django.utils.deprecation import MiddlewareMixin  # Django 1.10.x
except ImportError:
    MiddlewareMixin = object  # Django 1.4.x - Django 1.9.x

class WolfMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if request.path == '/login' or request.path == '/':    #登录界面或者登录操作
            pass
        elif request.path == '/register':                       #注册操作
            pass
        elif request.path == '/register/check':                 #检查用户名是否被注册
            pass
        elif request.path == '/forget':                         #忘记密码页面
            pass
        elif request.path == '/modify':                         #通过密码找回修改密码   
            pass
        else:
            if request.path != '/check_news':                   #非心跳消息，即常规请求，需要更新session有效期
                if request.session.get('username', None):
                    curr_tm = int(time.time())
                    request.session['timesec'] = curr_tm
                    request.session.set_expiry(600)              #600
                    pass
                else:
                    print "SESSION_INVALID"
                    ret = {
                        'stat': 'fail',
                        'reason': 'SESSION_INVALID',
                    }
                    return HttpResponse(json.dumps(ret))
            else:       #check_news, 相当于心跳
                pass_flag = 0

                if request.session.get('username', None):
                    #要判断即将过期的情况，这样才能销毁session以及做些数据库操作
                    curr_tm = int(time.time())
                    last_tm = request.session.get('timesec', None)
                    if last_tm:
                        span_tm = curr_tm - last_tm
                        if span_tm >= (600-15):   #小于session期限15秒左右
                            print '---------over'
                            offline_clean(request)
                            pass_flag = 0
                        else:
                            pass_flag = 1
                    else:
                        pass_flag = 1
                    
                else:       #session无效，不通过
                    pass_flag = 0

                if pass_flag == 1:
                    pass
                else:
                    print "SESSION_INVALID or ..."      #已经过期或即将过期
                    ret = {
                        'stat': 'fail',
                        'reason': 'SESSION_INVALID',
                    }
                    return HttpResponse(json.dumps(ret))