# -*- coding: utf-8 -*-
"""
模型，对应数据库
"""
from __future__ import unicode_literals

from django.db import models
import django.utils.timezone as timezone

# Create your models here.

class userAdminManager(models.Manager):       
    '''
    自定义管理器
    '''
    def email_used(self, email):
        cnt = self.filter(user_email__exact=email).count()
        if cnt > 0:
            return True
        else:
            return False

# class userContactsManager(models.Manager):
    

class userAdmin(models.Model):
    '''
    用户基本资料
    '''
    user_name = models.CharField('aa', unique=True, max_length=32)           #用户名

    user_nickname = models.CharField('bb', max_length=32)       #昵称
    user_password = models.CharField('cc', max_length=32)       #密码
    user_email = models.EmailField(unique=True)                            #邮箱，也是唯一
    user_emailValid = models.IntegerField(default=0)            #邮箱有效性 0 无效 1 有效， 无效邮箱的用户无法参与很多业务
    user_sign = models.IntegerField(default=0)                  #星座
    user_gender = models.IntegerField(default=3)                #性别，1 男 2 女 3 保密
    user_status = models.IntegerField(default=0)                #状态，0:offline, 1:online, 2:leave
    # status_heart = models.IntegerField(default=1)       
    #登陆之后被赋予某个值，每次心跳到来也赋相同的值，mysql数据库周期事件每次减一，减到零后将user_status置为0   
    #有了handle_time之后，也许就不需要status_heart字段了

    register_time = models.DateTimeField(auto_now=False, auto_now_add=True) #注册时间
    login_time = models.DateTimeField(auto_now=False, auto_now_add=False, default = timezone.now)   #登陆时间
    handle_time = models.DateTimeField(auto_now=True, auto_now_add=False)   #操作时间

    user_blacklist = models.CharField('blacklist', max_length=1024)   #黑名单，以逗号分隔

    #忘记密码
    forget_randomint = models.IntegerField(default=0)     #随机数，作为修改密码页面的识别码,0无效
    forget_trycnt = models.IntegerField(default=0)        #用户尝试次数限制，防止恶意破解
    forget_time = models.DateTimeField(auto_now=False, auto_now_add=False, default = timezone.now)      #页面链接有效时间

    #内部设置
    setting_permitSearch = models.IntegerField(default=1)   #是否允许他人搜索到我，0禁止，1允许
    setting_permitAdd = models.IntegerField(default=0)  #被他人添加好友的方式，0无条件允许，1需要验证

    objects = userAdminManager()

    def __unicode__(self):
            return self.user_name

class user_contacts(models.Model):
    '''
    抽象类，联系人列表
    '''
    name = models.CharField('username', unique=True, max_length=32)         #用户名唯一
    relation = models.IntegerField(default=0)   #0:friend, 1:stranger
    status = models.IntegerField(default=0)     #0:offline, 1:online, 2:leave
    nickname = models.CharField('nickname', max_length=32)
    remark = models.CharField('remark', max_length=32, default='')      #备注信息，方便记忆
    email = models.EmailField(unique=True)
    gender = models.IntegerField(default=3)     #性别，1 男 2 女 3 保密
    sign = models.IntegerField(default=0)       #星座
    #chat_status 是否打开了聊天窗口

    class Meta:
        abstract = True
        ordering=['relation','status','remark', 'nickname']     #排序

class user_chats(models.Model):
    '''
    抽象类，聊天
    '''
    name = models.CharField('username', max_length=32)      #聊天对象
    io = models.IntegerField(default=0)     #方向,0表示out, 1表示in
    chat_time = models.DateTimeField(auto_now=False, auto_now_add=True) #时间
    chat_type = models.IntegerField(default=0)  #类型，0表示普通消息 1表示自动消息(如离开状态发送的消息)
    in_status = models.IntegerField(default=0)  #输入消息的状态，0表示新消息，1表示已读
    message = models.CharField('message', max_length=128)   #信息内容

    class Meta:
        abstract = True
        ordering=['name','chat_time']     #排序

class user_news(models.Model):
    '''
    抽象类，信息
    '''
    news_time = models.DateTimeField(auto_now=False, auto_now_add=True) #时间
    classtype = models.IntegerField(default=0) 
    #class和type都是关键字，所以用classtype表示信息的类型
    #0:联系人信息 
        #1:聊天消息-------不需要了吧?放在user_chat表中好了..
    #2:联系人上下线、离开消息，属于阅后即焚
    status = models.IntegerField(default=0)  
    #0.0表示新消息, 0.1表示旧消息但未操作, 0.2表示被用户同意，0.3表示被用户拒绝
        #1.X 这里出现的聊天消息就是新消息，用户读取后将转移到user_chat表中
    #2.X 没有新旧一说，阅后即焚
    action = models.IntegerField(default=0) # classtype和action组合才有意义
    #0.0 添加好友请求 0.1 对方接受请求 0.2 对方拒绝请求 0.3 对方已成为好友 0.4 对方将你设置为黑名单
    #0.5 对方想和你和解(撤销黑名单为陌生人) 0.6 对方接受和解 0.7 对方拒绝和解
    #0.10~19 预留
        #1.0 普通消息 1.1 自动消息(如离开状态发送的消息)
    #2.0 离线 2.1 上线 2.2 离开 ---与user_contacts表的status对应
    info_main = models.CharField('info_main', max_length=32)    #同样是和上述组合才有意义
    info_minor = models.CharField('info_minor', max_length=128)

    class Meta:
        abstract = True
        ordering=['news_time']     #排序

