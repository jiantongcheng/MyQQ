# -*- coding: utf-8 -*-
"""MyQQ URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from useradmin import views as useradmin_views
from useradmin import read as useradmin_read
from useradmin import write as useradmin_write
from useradmin import news as useradmin_news
from useradmin import chats as useradmin_chats

from useradmin import common as useradmin_common
from useradmin import vote as useradmin_vote
from useradmin import fivepoint as useradmin_fivepoint

urlpatterns = [
    url(r'^admin/', admin.site.urls),                                       #管理员页面

    url(r'^$', useradmin_views.login),                                      #默认登录页面
    url(r'^login$', useradmin_views.login),                                 #登录页面或登录操作
    url(r'^logout$', useradmin_views.logout),                               #注销操作
    #---下面几种不用判断session---
    url(r'^register$', useradmin_views.register),                           #注册操作
    url(r'register/check$', useradmin_views.register_check),                #检测用户是否注册
    url(r'^forget$', useradmin_views.forget),                               #忘记密码页面或发送校验码到邮箱操作
    url(r'^modify', useradmin_views.modify),                                #通过密码找回，修改密码
    #-----------资料、密码----------------
    url(r'home/readBase$', useradmin_views.readBase),                       #读取基本资料
    url(r'home/modifyBase$', useradmin_views.modifyBase),                   #修改基本资料
    url(r'home/emailVerify_send$', useradmin_views.emailVerify_send),       #向用户邮箱发送校验码
    url(r'home/emailVerify_recv$', useradmin_views.emailVerify_recv),       #验证邮箱认证校验码
    url(r'home/modifyPassword$', useradmin_views.modifyPassword),           #通过旧密码，修改密码
    # ---------联系人------------------
    url(r'home/readContacts$', useradmin_read.readContacts),                #读取联系人列表
    url(r'home/searchContacts$', useradmin_read.searchContacts),            #搜索联系人
    url(r'setting', useradmin_write.user_setting),                          #设置一些参数或状态
    url(r'addFriendApply', useradmin_news.user_add_friend),                 #添加好友申请
    url(r'delRelation', useradmin_news.user_delRelation),                   #删除联系人
    url(r'changeRelation', useradmin_news.user_changeRelation),             #改变联系人关系
    url(r'readNewsByClasstype0', useradmin_news.user_readNewsByClasstype0),     #读取某类消息
    url(r'deleteNew', useradmin_news.user_deleteNew),                       #删除消息
    url(r'responseNew', useradmin_news.user_responseNew),                   #响应消息
    url(r'compromise', useradmin_news.user_compromise),                     #和解
    url(r'check_news', useradmin_news.user_checkNews),                      #检查新消息
    url(r'check_status', useradmin_news.user_checkStatus),                  #检查状态
    url(r'readChats', useradmin_chats.user_readChats),                      #读取聊天记录
    url(r'chatSend', useradmin_chats.user_chatSend),                        #发送消息
    url(r'chatClear', useradmin_chats.user_chatClear),                      #清空消息
    url(r'check_chats', useradmin_chats.user_checkChats),                   #检查新消息
    url(r'read_newChat', useradmin_chats.user_readNewChat),                 #读取新消息
    #----------大厅----------
    url(r'getCalendar', useradmin_common.getCalendar),                      #读取日历
    url(r'getWeather', useradmin_common.getWeather),                        #读取天气
    url(r'getHistory', useradmin_common.getHistory),                        #历史上的今天
    #----------投票----------
    url(r'read_vote', useradmin_vote.readVote),                             #读取投票相关信息
    url(r'vote_invite_check', useradmin_vote.vote_invite_check),            #验证投票邀请码
    url(r'commit_vote', useradmin_vote.commit_vote),                        #提交投票消息

    #----------五子棋------
    url(r'fivepoint_start', useradmin_fivepoint.start),                     #开始对战，机器先下或者用户先下                       
    url(r'fivepoint_userstep', useradmin_fivepoint.userstep),               #用户下子，机器给出对应的子
    url(r'fivepoint_regret', useradmin_fivepoint.regret),                   #悔棋，暂时有问题
    url(r'fivepoint_debug', useradmin_fivepoint.debug_print),               #后台打印调试
    url(r'fivepoint_history', useradmin_fivepoint.history_print),           #下棋步骤打印
    


    # ----------testpost 调试
    # url(r'testpost', useradmin_chats.testpost),
    # url(r'testpost', useradmin_common.testpost),
]
