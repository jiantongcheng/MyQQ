# -*- coding: utf-8 -*-
"""
读取、搜索联系人
"""
from __future__ import unicode_literals

from django.shortcuts import render
from django.http import HttpResponse
from useradmin.models import userAdmin
from useradmin.dynamic_model import get_user_contacts

import json

# Create your views here.

def searchContacts(request):
    '''
    搜索联系人
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
            if obj.user_status == 0:        #离线状态
                ret = {
                    'stat': 'fail',
                    'reason': '用户名不在线',
                }
                return HttpResponse(json.dumps(ret))
            else:
                searchType = request.POST.get('type', '')
                searchGender = request.POST.get('gender', '')
                searchContent = request.POST.get('content', '')

                if searchGender == 'U':
                    if searchType == 'username':
                        contacts_obj = userAdmin.objects.filter(user_name__contains=searchContent).exclude(setting_permitSearch=0)
                    elif searchType == 'nickname':
                        contacts_obj = userAdmin.objects.filter(user_nickname__contains=searchContent).exclude(setting_permitSearch=0)
                    else:
                        None
                else:
                    if searchGender == 'M':
                        fitGender = 1
                    elif searchGender == 'F':
                        fitGender = 2
                    elif searchGender == 'S':
                        fitGender = 3
                    else:
                        None

                    if searchType == 'username':
                        contacts_obj = userAdmin.objects.filter(user_name__contains=searchContent).filter(user_gender=fitGender).exclude(setting_permitSearch=0)
                    elif searchType == 'nickname':
                        contacts_obj = userAdmin.objects.filter(user_nickname__contains=searchContent).filter(user_gender=fitGender).exclude(setting_permitSearch=0)
                    else:
                        None

                friend = []
                for fri in contacts_obj:
                    if fri.user_name != user_name:      #不包含自己
                        friend.append(
                            {
                            'name': fri.user_name,
                            'nickname': fri.user_nickname,
                            'gender': fri.user_gender
                            # 这里原来想的是加一个字段，表明其是否为我的好友，但更好的做法是交给浏览器端来判断
                            }
                        )

                ret = {
                    'stat': 'success',
                    'count': len(friend),
                    'contacts': friend,
                }

                return HttpResponse(json.dumps(ret))

def readContacts(request):
    '''
    读取联系人列表
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
            contactsClass = get_user_contacts(user_name)
            count_friend = contactsClass.objects.filter(relation__exact=0).count()
            count_stranger = contactsClass.objects.filter(relation__exact=1).count()
            friend_obj = contactsClass.objects.filter(relation__exact=0)
            friend = []
            count_friend_alive = 0
            for fri in friend_obj:
                guest_obj = userAdmin.objects.get(user_name=fri.name)
                status = guest_obj.user_status      #状态是动态数据，需要动态获取
                if status != 0:
                    count_friend_alive += 1
                fri.status = status
                fri.save()
                friend.append(
                    {'name': fri.name,
                    'status': status,           
                    'nickname': fri.nickname,
                    'remark': fri.remark,
                    'email': fri.email,
                    'gender': fri.gender,
                    'sign': fri.sign}
                )

            stranger_obj = contactsClass.objects.filter(relation__exact=1)
            stranger = []
            count_stranger_alive = 0
            for stra in stranger_obj:
                guest_obj = userAdmin.objects.get(user_name=stra.name)
                status = guest_obj.user_status      #状态是动态数据，需要动态获取
                if status != 0:
                    count_stranger_alive += 1
                stra.status = status
                stra.save()
                stranger.append(
                    {'name': stra.name,
                    'status': status,
                    'nickname': stra.nickname,
                    'remark': stra.remark,
                    'gender': stra.gender}
                )

            if obj.user_blacklist == '':
                count_blacklist = 0;
            else:
                blacklist_list = obj.user_blacklist.split(',')
                count_blacklist = len(blacklist_list)
            blacklist = []
            if count_blacklist != 0:
                for name in blacklist_list:
                    blacklist.append({'name':name})

            ret = {
                'stat': 'success',
                'count_friend': count_friend,
                'count_friend_alive': count_friend_alive,
                'count_stranger': count_stranger,
                'count_stranger_alive': count_stranger_alive,
                'count_blacklist': count_blacklist,
                'friend': friend,
                'stranger': stranger,
                'blacklist': blacklist,
            }

            return HttpResponse(json.dumps(ret))
    else:
        None
