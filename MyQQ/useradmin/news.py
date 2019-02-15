# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.http import HttpResponse
from useradmin.models import userAdmin
from useradmin.dynamic_model import get_user_news, get_user_contacts, get_user_chats

import json

# Create your views here.

def news_contacts_new_count(host, act_type):      #联系人新消息,act_type=0表示所有消息，=1表示基本消息，=2表示聊天消息
    
    if act_type == 0:
        newsHostClass = get_user_news(host)
        cnt_base = newsHostClass.objects.filter(classtype=0).filter(status=0).count()
        cnt_status = newsHostClass.objects.filter(classtype=2).count()
        chatsHostClass = get_user_chats(host)
        cnt_chat = chatsHostClass.objects.filter(in_status=0).filter(io=1).count()
        cnt = cnt_base + cnt_status + cnt_chat

        return (cnt, cnt_base, cnt_status, cnt_chat)

    elif act_type == 1:
        newsHostClass = get_user_news(host)
        cnt_base = newsHostClass.objects.filter(classtype=0).filter(status=0).count()
        return cnt_base
    elif act_type == 2:
        chatsHostClass = get_user_chats(host)
        cnt_chat = chatsHostClass.objects.filter(in_status=0).filter(io=1).count()
        return cnt_chat        
    else:
        None
        
    # return cnt

def user_checkNews(request):
    if request.method == 'POST':
        host = request.POST.get('user_name', '')
        host_obj, exist = userAdmin.objects.get_or_create(user_name=host)
        if exist == True:
            ret = {
                'stat': 'fail',
                'reason': 'host is not exist',
            }
        else:
            # host_obj.status_heart = 2       #更新心跳初始值
            # host_obj.save()

            news_contacts, news_contacts_base, news_contacts_status, news_contacts_chat = news_contacts_new_count(host, 0)

            ret = {
                'stat': 'success',
                'news_contacts': news_contacts,         
                'news_contacts_base': news_contacts_base,
                'news_contacts_status': news_contacts_status,
                'news_contacts_chat': news_contacts_chat
            }

        return HttpResponse(json.dumps(ret))

def user_checkStatus(request):
    if request.method == 'POST':
        host = request.POST.get('user_name', '')
        newsHostClass = get_user_news(host)
        statusObjs = newsHostClass.objects.filter(classtype=2)
        status_list = []
        cnt = 0
        for status in statusObjs:
            cnt += 1
            status_list.append(
                {
                    'name': status.info_main,
                    'status': status.action
                }
            )
            status.delete()     #阅后即焚
        
        ret = {
            'stat': 'success',
            'cnt': cnt,
            'status_list': status_list
        }

        return HttpResponse(json.dumps(ret))

def change_user_contact(host, guest, relation):
    placeholder, exist = userAdmin.objects.get_or_create(user_name=host)
    if exist == True:
        ret = {
            'stat': 'fail',
            'reason': 'host is not exist',
        }
    else:
        hostClass = get_user_contacts(host)
        usr_host, new = hostClass.objects.get_or_create(name=guest)
        if new == True:
            ret = {
                'stat': 'fail',
                'reason': 'guest is not exist',
            }
        else:
            usr_host.relation = relation
            usr_host.save()

            ret = {
                'stat': 'success',
            }

    return ret

def delete_user_contact(host, guest):   #host必须存在，guest可以不存在
    placeholder, exist = userAdmin.objects.get_or_create(user_name=host)
    if exist == True:
        ret = {
            'stat': 'fail',
            'reason': 'host is not exist',
        }
    else:
        hostClass = get_user_contacts(host)
        usr_host, new = hostClass.objects.get_or_create(name=guest)
        if new == True:     #原本就不存在
            ret = {
                'stat': 'success',
            }
        else:
            usr_host.delete()           #删除
            ret = {
                'stat': 'success',
            }

    return ret

def insert_user_contact(host, guest, relation):
    usr_guest = userAdmin.objects.get(user_name=guest)
    # if usr_guest.user_emailValid == 0:    #不添加未认证的用户
    if usr_guest.user_emailValid == 1:    
        return False
    else:
        usr_hostClass = get_user_contacts(host)
        usr_host, new = usr_hostClass.objects.get_or_create(name=usr_guest.user_name)
        if new == True:
            print "-------------add new relation------"
            usr_host.relation = relation
            usr_host.status = usr_guest.user_status
            usr_host.nickname = usr_guest.user_nickname
            usr_host.remark = ''  #注释默认为空
            usr_host.email = usr_guest.user_email
            usr_host.gender = usr_guest.user_gender
            usr_host.sign = usr_guest.user_sign
        else:   #已经存在时只改变关系
            usr_host.relation = relation

        usr_host.save()
        return True

def insert_user_news_classtype0(host, action, guest):
    hostClass = get_user_news(host)
    host_news = hostClass()
    host_news.status = 0
    host_news.classtype = 0
    host_news.action = action
    host_news.info_main = guest
    host_news.save()

    return True

def user_deleteNew(request):
    if request.method == 'POST':
        host = request.session.get('username', None)
        newsId = request.POST.get('id', '')
        hostClass = get_user_news(host)
        news_obj, exist = hostClass.objects.get_or_create(id=newsId)
        if exist == True:
            ret = {
                'stat': 'fail',
                'reason': 'news id is not exist',
            }
        else:
            news_obj.delete()
            ret = {
                'stat': 'success',
            }
        
        return HttpResponse(json.dumps(ret))

def user_compromise(request):
    if request.method == 'POST':
        dst_username = request.POST.get('dst', '')
        src_username = request.POST.get('src', '')

        insert_user_news_classtype0(dst_username, 5, src_username)
        
        ret = {
            'stat': 'success',
        }

        return HttpResponse(json.dumps(ret))


def user_responseNew(request):
    if request.method == 'POST':
        host = request.session.get('username', None)
        newsId = request.POST.get('id', '')
        hostClass = get_user_news(host)
        news_obj, exist = hostClass.objects.get_or_create(id=newsId)
        if exist == True:
            ret = {
                'stat': 'fail',
                'reason': 'news id is not exist',
            }
        else:
            response = request.POST.get('response', '')
            response_num = int(response)  #千万要注意数据类型

            if response_num == 1 or response_num == 6:
                news_obj.status = 2
            elif response_num == 2 or response_num == 7:
                news_obj.status = 3
            else:
                None
            news_obj.save()
            guest = request.POST.get('guest', '')
            
            print "-------" + response
            if response_num == 1:   #接受好友请求
                insert_user_contact(host, guest, 0)
                insert_user_contact(guest, host, 0)
                # insert_user_news_classtype0(guest, 3, host)
            elif response_num == 6:  #接受和解请求,从黑名单变为陌生人
                insert_user_contact(host, guest, 1)
                insert_user_contact(guest, host, 1)
                delete_user_blacklist(host, guest)
                delete_user_blacklist(guest, host)
            else:
                None

            insert_user_news_classtype0(guest, response_num, host)

            ret = {
                'stat': 'success',
            }

            return HttpResponse(json.dumps(ret))

def user_readNewsByClasstype0(request):
    if request.method == 'POST':
        host = request.session.get('username', None)
        hostClass = get_user_news(host)
        news_objs = hostClass.objects.filter(classtype=0)
        news_count = news_objs.count()
        news = []
        for new in news_objs:
            news_time = new.news_time.strftime("%Y-%m-%d %H:%M:%S")
            news.append(
                {
                    'id': new.id,
                    'status': new.status,
                    'action': new.action,
                    'username': new.info_main,
                    'time': news_time
                }
            )

            if new.status == 0:
                new.status = 1
                new.save()

        ret = {
            'stat': 'success',
            'count': news_count,
            'news': news,
        }

        return HttpResponse(json.dumps(ret))

def user_add_friend(request):
    if request.method == 'POST':
        dst_username = request.POST.get('dst', '')
        dst_obj = userAdmin.objects.get(user_name=dst_username)
        src_username = request.POST.get('src', '')

        if dst_obj.setting_permitAdd == 0:      #无条件允许，热烈欢迎
        # 需要往dst发送news，表明对方成为你的好友了,不需要往src发送news，就用这里的OK表示成功
            insert_user_contact(dst_username, src_username, 0)
            insert_user_contact(src_username, dst_username, 0)
            insert_user_news_classtype0(dst_username, 3, src_username)
            ok_wait_fail = "ok"
        elif dst_obj.setting_permitAdd == 1:    #需要验证
            insert_user_contact(src_username, dst_username, 1)      #有这种意图也算陌生人吧
            insert_user_news_classtype0(dst_username, 0, src_username)
            ok_wait_fail = "wait"
        else:
            None
        ret = {
            'stat': 'success',
            'resp': ok_wait_fail,
        }

        if ok_wait_fail == 'ok':    # 添加好友成功，需要提供一些信息
            ret['name'] = dst_obj.user_name
            ret['nickname'] = dst_obj.user_nickname
            ret['status'] = dst_obj.user_status
            ret['gender'] = dst_obj.user_gender
            ret['email'] = dst_obj.user_email
            ret['sign'] = dst_obj.user_sign
        
        return HttpResponse(json.dumps(ret))
    
def user_delRelation(request):
    if request.method == 'POST':
        host = request.POST.get('host', '')
        guest = request.POST.get('guest', '')
        
        ret = delete_user_contact(host, guest)

        return HttpResponse(json.dumps(ret))

def insert_user_blacklist(host, guest):
    user_host, exist = userAdmin.objects.get_or_create(user_name=host)
    if exist == True:
        ret = {
            'stat': 'fail',
            'reason': 'host is not exist',
        }
    else:
        blacklist = user_host.user_blacklist
        if blacklist == '':
            user_host.user_blacklist = guest
        else:
            user_host.user_blacklist = blacklist + "," + guest

        user_host.save()

        ret = {
            'stat': 'success',
        }

        return ret

def delete_user_blacklist(host, guest):
    user_host, exist = userAdmin.objects.get_or_create(user_name=host)
    if exist == True:
        ret = {
            'stat': 'fail',
            'reason': 'host is not exist',
        }
    else:
        blacklist = user_host.user_blacklist
        if blacklist != '':
            blacklist_new = ""
            blacklist_list = blacklist.split(",")
            for name in blacklist_list:
                if guest != name:           #排除
                    blacklist_new += name + ","

            if blacklist_new != "":     #去除最右边逗号
                blacklist_new.strip(",")
            user_host.user_blacklist = blacklist_new
            print "blacklist_new: " + blacklist_new
            user_host.save()
        ret = {
            'stat': 'success',
        }

    return HttpResponse(json.dumps(ret))

def user_changeRelation(request):
    if request.method == 'POST':
        host = request.POST.get('host', '')
        guest = request.POST.get('guest', '')
        relation = request.POST.get('relation', '')
        if relation == '2':   #黑名单
            ret = delete_user_contact(host, guest)   #从好友或者陌生人列表删除
            if ret['stat'] == 'success':
                ret = insert_user_blacklist(host, guest)    #插入到黑名单
                if ret['stat'] == 'success':
                    insert_user_news_classtype0(guest, 4, host)     #设置为黑名单，要提醒一下对方
                    insert_user_blacklist(guest, host)    #互相的，你也成为了对方的黑名单
                    delete_user_contact(guest, host)    #从对方的可能存在的关系中删除
        else:       #只能是好友到陌生人的转变关系吧
            ret = change_user_contact(host, guest, relation)

        ret['relation'] = relation     #回传，方便浏览器端

        return HttpResponse(json.dumps(ret))
        