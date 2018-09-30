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

urlpatterns = [
    url(r'^admin/', admin.site.urls),                                       #管理员页面

    url(r'^$', useradmin_views.login),                                      #默认为登录页面
    url(r'^register$', useradmin_views.register),                           #注册页面
    url(r'register/check_user_name$', useradmin_views.register_check),      #检测用户是否注册
    url(r'home/modifyPassword$', useradmin_views.modifyPassword),      #修改密码
    url(r'^logout$', useradmin_views.logout),                               #注销后页面，即登录页面
    url(r'^login$', useradmin_views.login),                                 #登录页面
    url(r'^forget$', useradmin_views.forget),                               #忘记密码页面
    url(r'^modify', useradmin_views.modify),                                #修改密码页面
    url(r'home/readBase$', useradmin_views.readBase),                       #读取基本资料
    url(r'home/modifyBase$', useradmin_views.modifyBase),
    url(r'home/emailVerify_send$', useradmin_views.emailVerify_send),
    url(r'home/emailVerify_recv$', useradmin_views.emailVerify_recv),
]
