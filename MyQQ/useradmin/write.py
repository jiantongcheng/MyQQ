# -*- coding: utf-8 -*-
"""
修改用户设置或状态
"""
from __future__ import unicode_literals

from django.shortcuts import render
from django.http import HttpResponse
from useradmin.models import userAdmin
from useradmin.dynamic_model import get_user_news, get_user_contacts

import json

# Create your views here.

def insert_user_news_classtype2(host, action, guest):
    '''
    类型：工具
    通知我的非离线的联系人，我的状态改变了
    '''
    hostClass = get_user_news(host)
    host_news = hostClass()
    # host_news.status  不重要
    host_news.classtype = 2
    host_news.action = action
    host_news.info_main = guest
    host_news.save()

    return True

def user_setting(request):
    '''
    类型：接口
    修改用户设置或状态
    '''
    if request.method == 'POST':
        user_name = request.session.get('username', None)
        try:
            obj = userAdmin.objects.get(user_name=user_name)
        except userAdmin.DoesNotExist:
            ret = {
                'stat': 'fail',
                'reason': '用户名不存在',
            }
            
            return HttpResponse(json.dumps(ret))
        else:
            items_json = request.POST.get('items', '')
            items_dict = json.loads(items_json)

            for key,value in items_dict.items():
                if key == 'setting_permitSearch':
                    obj.setting_permitSearch = value
                elif key == 'setting_permitAdd':
                    obj.setting_permitAdd = value
                elif key == 'setting_status':       #设置状态
                    if obj.user_status != value:    #防止重复修改及通知
                        obj.user_status = value
                        #此时要去通知联系人列表中在线和离开状态的朋友，我的状态如何
                        hostClass = get_user_contacts(user_name)
                        guestObjs = hostClass.objects.exclude(status=0)  #排除离线的家伙们
                        for guest in guestObjs:
                            guest_name = guest.name
                            insert_user_news_classtype2(guest_name, value, user_name)
                else:
                    None

            obj.save()

            ret = {
                'stat': 'success',
            }
            
            return HttpResponse(json.dumps(ret))