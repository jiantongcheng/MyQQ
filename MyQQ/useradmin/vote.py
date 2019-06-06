# -*- coding: utf-8 -*-
"""
投票相关
"""
from __future__ import unicode_literals

from django.shortcuts import render
from django.http import HttpResponse
from useradmin.models import userAdmin, vote

#缓存数据库
from django.core.cache import cache
from tool import log_file

import json

# Create your views here.

def readVote(request):
    user_name = request.session.get('username', None)
    vote_id = request.POST.get('id', '')
    obj = vote.objects.filter(vote_id__exact=vote_id).filter(vote_user__exact=user_name)
    if obj:
        act = obj[0].vote_act       #要注意这里的obj[0]
        point = obj[0].vote_point
        # key_name = 'vote_id:'+vote_id
        # if cache.has_key(key_name):
        #     statistics = cache.get(key_name)
        # else:
        #     statistics = 'something error!'
        stat_obj = vote.objects.filter(vote_id__exact=vote_id).filter(vote_user__exact="<TJ>")
        if stat_obj:
            statistics = stat_obj[0].vote_act
        else:
            statistics = 'something error!'

        ret = {
            'stat': 'success',
            'join': 'YES',
            'act': act,
            'statistics': statistics,
            'id': vote_id,
            'point': point,
        }  
    else:
        ret = {
            'stat': 'success',
            'join': 'NO',
            'id': vote_id,
        }  

    return HttpResponse(json.dumps(ret))

def vote_invite_check(request):
    vote_id = request.POST.get('id', '')
    invite = request.POST.get('invite', '')

    if vote_id == '1' and ( invite == "MX-2000" or invite == "61" ):
        check = 'OK'
    elif vote_id == '2' and invite == "yz-2003":
        check = 'OK'
    else:
        check = "FAIL"

    ret = {
        'stat': 'success',
        'check': check,
        'id': vote_id,
    }  

    return HttpResponse(json.dumps(ret))

def commit_vote(request):
    user_name = request.session.get('username', None)
    vote_id = request.POST.get('id', '')
    act = request.POST.get('act', '')
    point = request.POST.get('point', 'NULL')

    exist = vote.objects.filter(vote_id=vote_id).filter(vote_user=user_name).count()

    if exist != 0:      #避免重复提交
        ret = {
            'stat': 'fail',
            'id': vote_id,
        }  

        return HttpResponse(json.dumps(ret))

    log_file(user_name, "Vote:" + vote_id)

    newObj = vote()
    newObj.vote_id = int(vote_id)
    newObj.vote_user = user_name
    newObj.vote_act = act
    newObj.vote_point = point
    newObj.save()

    #将每个用户的投票情况计入到总的统计当中
    stat_obj = vote.objects.filter(vote_id__exact=vote_id).filter(vote_user__exact="<TJ>")  #<TJ>表示统计信息，不可能与用户名冲突
    # key_name = 'vote_id:'+vote_id
    # if cache.has_key(key_name):
    if stat_obj:
        # statistics_dumps = cache.get(key_name)
        # statistics_dict = json.loads(statistics_dumps)
        statistics_dict = json.loads(stat_obj[0].vote_act)
        cnt = statistics_dict['cnt'] + 1
        
        act_arrys = json.loads(act)

        info = []
        for item in statistics_dict['info']:    #statistics_dict['info']是个list
            item[act_arrys[int(item['pos'])-1]['select']] += 1
            info.append(item)
        
        statistics = {
            'cnt': cnt,
            'info': info
        }

        print json.dumps(statistics)

        stat_obj[0].vote_act = json.dumps(statistics)
        stat_obj[0].save()

        # cache.set(key_name, json.dumps(statistics), 3600*24*30)

    else:   #说明是第一个投票的人
        info = []
        act_arrys = json.loads(act)
        for obj in act_arrys:
            item = {}
            item['pos'] = obj['pos']
            item['A'] = 0
            item['B'] = 0
            item['C'] = 0
            item[obj['select']] = 1
            info.append(item)

        statistics = {
            'cnt': 1,
            'info': info
        }

        print json.dumps(statistics)

        stat_obj = vote()
        stat_obj.vote_id = int(vote_id)
        stat_obj.vote_user = "<TJ>"
        stat_obj.vote_act = json.dumps(statistics)
        stat_obj.vote_point = "NULL"
        stat_obj.save()

        # cache.set(key_name, json.dumps(statistics), 3600*24*30)     #如何让其永久有效?

    ret = {
        'stat': 'success',
        'id': vote_id,
    }  

    return HttpResponse(json.dumps(ret))