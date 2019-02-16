# -*- coding: utf-8 -*-
"""
联系人聊天相关
"""
from __future__ import unicode_literals

from django.shortcuts import render
from django.http import HttpResponse
from useradmin.models import userAdmin
from django.db.models import Count
from useradmin.dynamic_model import get_user_news, get_user_contacts, get_user_chats

import json

# Create your views here.

def insert_chat(host, guest, io, in_status, chat_type, message):
    '''
    类型：工具
    对方有新消息
    '''
    chatHostClass = get_user_chats(host)
    newChatObj = chatHostClass()
    newChatObj.name = guest
    newChatObj.io = io
    if io == 1:     #对输入信息有效
        newChatObj.in_status = in_status
    newChatObj.chat_type = chat_type
    newChatObj.message = message
    #插入的当然是新消息，并且时间是自动添加的

    newChatObj.save()

def user_checkChats(request):
    '''
    类型：接口
    检查新聊天消息
    '''
    host = request.POST.get('user_name', '')
    chatHostClass = get_user_chats(host)
    objs = chatHostClass.objects.filter(in_status=0).values('name')

    cnt_chats = 0
    cnt_users = 0
    chats = {}
    for obj in objs:
        cnt_chats += 1
        name = obj['name']
        try:
            chats[name]
        except KeyError:
            chats[name] = 1
            cnt_users += 1
        else:
            chats[name] += 1

    chats_list = []

    for (key,value) in chats.items():
        chats_list.append(
            {
            'name': key,
            'cnt': value,
            }
        )

    ret = {
        'stat': 'success',
        'cnt_users': cnt_users,
        'cnt_chats': cnt_chats,
        'chats_list': chats_list
    }

    return HttpResponse(json.dumps(ret))

    
def testpost(request):
    '''
    类型：接口
    保留测试用
    '''
    host = request.POST.get('host', '')
    chatHostClass = get_user_chats(host)

    # objs = chatHostClass.objects.filter(in_status=1).only("name", "in_status").values('name').annotate(count=Count('in_status')).values('name', 'count')
    # objs = chatHostClass.objects.all().only("name", "in_status") #搞不懂only
    # objs = chatHostClass.objects.all().defer("message") #搞不懂defer
    # objs = chatHostClass.objects.filter(in_status=1).values('name')   #这样似乎返回的是只有name字段的字典
    objs = chatHostClass.objects.filter(in_status=1).values('name')

    print "--------***----->" + str(objs.count())
    cnt = objs.count()

    cnt_chats = 0
    chats = {}
    for obj in objs:
        cnt_chats += 1
        name = obj['name']
        try:
            chats[name]
        except KeyError:
            chats[name] = 1
        else:
            chats[name] += 1

    ret = {
            'stat': 'success**',
            'cnt': cnt,
            'cnt_chats': cnt_chats,
            'chat': chats
        }

    return HttpResponse(json.dumps(ret))

def user_chatSend(request):
    '''
    类型：接口
    发送聊天消息
    '''
    if request.method == 'POST':
        host = request.POST.get('host', '')
        guest = request.POST.get('guest', '')
        message = request.POST.get('message', '')
        chat_type = request.POST.get('type', '')

        insert_chat(host, guest, 0, None, chat_type, message)
        insert_chat(guest, host, 1, 0, chat_type, message)
        chatHostClass = get_user_chats(host)
        objs = chatHostClass.objects.filter(name=guest).filter(io=0).order_by('-chat_time')[:1]
        chat_time = objs[0].chat_time.strftime("%Y-%m-%d %H:%M:%S")


        status_leave = 0
        if chat_type == '0':  #若为普通消息且guest是离开状态，则自动回复
            guestObj = userAdmin.objects.get(user_name=guest)
            if guestObj.user_status == 2:
                insert_chat(guest, host, 0, None, 1, '-')  #自动消息暂时为空，让浏览器去处理
                insert_chat(host, guest, 1, 1, 1, '-')  #对方应该可以立即看到，就作为已读消息
                status_leave = 1

        ret = {
            'stat': 'success',
            'status_leave': status_leave,
            'chat_time': chat_time
        }

        return HttpResponse(json.dumps(ret))

def user_chatClear(request):
    '''
    类型：接口
    清空聊天消息
    '''
    if request.method == 'POST':
        host = request.POST.get('host', '')
        guest = request.POST.get('guest', '')
        chatHostClass = get_user_chats(host)
        chat_objs = chatHostClass.objects.filter(name=guest)
        chat_objs.delete()

        ret = {
            'stat': 'success',
        }

        return HttpResponse(json.dumps(ret))

def user_readNewChat(request):
    '''
    类型：接口
    读取新聊天消息
    '''
    host = request.POST.get('host', '')
    guest = request.POST.get('guest', '')
    chatHostClass = get_user_chats(host)
    chat_objs = chatHostClass.objects.filter(name=guest).filter(in_status=0).filter(io=1)
    chat_count = chat_objs.count()

    print "---chat_count " + str(chat_count)

    chats = []
    for chat in chat_objs:
        chat_time = chat.chat_time.strftime("%Y-%m-%d %H:%M:%S")
        chats.append(
            {
                'time': chat_time,
                'io': chat.io,
                'type': chat.chat_type,
                'in_status': chat.in_status,
                'message': chat.message
            }
        )

        if chat.io == 1 and chat.in_status == 0:
            chat.in_status = 1      #未读变已读
            chat.save()

    ret = {
        'stat': 'success',
        'count': chat_count,
        'chats': chats,
    }

    return HttpResponse(json.dumps(ret))

        
def user_readChats(request):
    '''
    类型：接口
    读取聊天记录
    '''
    if request.method == 'POST':
        host = request.POST.get('host', '')
        guest = request.POST.get('guest', '')

        chatHostClass = get_user_chats(host)
        chat_objs = chatHostClass.objects.filter(name=guest)
        chat_count = chat_objs.count()

        print "---chat_count " + str(chat_count)

        chats = []
        for chat in chat_objs:
            chat_time = chat.chat_time.strftime("%Y-%m-%d %H:%M:%S")
            chats.append(
                {
                    'time': chat_time,
                    'io': chat.io,
                    'type': chat.chat_type,
                    'in_status': chat.in_status,
                    'message': chat.message
                }
            )

            if chat.io == 1 and chat.in_status == 0:
                chat.in_status = 1      #未读变已读
                chat.save()

        ret = {
            'stat': 'success',
            'count': chat_count,
            'chats': chats,
        }

        return HttpResponse(json.dumps(ret))
