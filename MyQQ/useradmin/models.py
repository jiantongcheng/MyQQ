# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
import django.utils.timezone as timezone

# Create your models here.

class userAdmin(models.Model):
    user_name = models.CharField('aa', max_length=32)           #用户名

    user_nickname = models.CharField('bb', max_length=32)       #昵称
    user_password = models.CharField('cc', max_length=32)       #密码
    user_email = models.EmailField()                            #邮箱
    user_emailValid = models.IntegerField(default=0)            #邮箱有效性
    user_sign = models.IntegerField(default=0)                  #星座
    user_gender = models.IntegerField(default=3)                #性别

    #忘记密码
    forget_randomint = models.IntegerField(default=0)     #随机数，作为修改密码页面的识别码,0无效
    forget_trycnt = models.IntegerField(default=0)        #用户尝试次数限制，防止恶意破解
    forget_time = models.DateTimeField(auto_now=False, auto_now_add=False, default = timezone.now)      #页面链接有效时间

    def __unicode__(self):
            return self.user_name

