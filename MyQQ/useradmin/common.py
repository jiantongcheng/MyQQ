# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.http import HttpResponse
from useradmin.models import userAdmin

import json
import calendar, datetime #日历相关

#抓取天气预报
import requests, random, socket, time, http #http.client
from bs4 import BeautifulSoup

# Create your views here.

# 本函数截取自网络，似乎具有通用性
def get_html(url,data=None):
    """
    模拟浏览器来获取网页的html代码
    """
    header={
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, sdch',
        'Accept-Language': 'zh-CN,zh;q=0.8',
        'Connection': 'keep-alive',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.235'
    }
    #设定超时时间，取随机数是因为防止被网站认为是爬虫
    timeout=random.choice(range(80,180))
    while True:
        try:
            rep=requests.get(url,headers=header,timeout=timeout)
            rep.encoding="utf-8"
            break
        except socket.timeout as e:
            print("3:",e)
            time.sleep(random.choice(range(8,15)))

        except socket.error as e:
            print("4:",e)
            time.sleep(random.choice(range(20,60)))
        # except http.client.BadStatusLine as e:
        #     print("5:",e)
        #     time.sleep(random.choice(range(30,80)))

        # except http.client.IncompleteRead as e:
        #     print("6:",e)
        #     time.sleep(random.choice(range(5,15)))

    return rep.text

# 本函数截取自网络
def get_data_weather(html_txt):
    final=[]
    bs=BeautifulSoup(html_txt,"html.parser")   #创建BeautifulSoup对象
    body=bs.body   #获取body部分
    data=body.find("div",{"id":"7d"}) #找到id为7d的div
    ul=data.find("ul")  #获取ul部分
    li=ul.find_all("li")   #获取所有的li

    for day in li:  #对每个标签中的内容进行遍历
        temp=[]
        date=day.find("h1").string   #获取日期
        temp.append(date)   #将日期添加到temp 中
        inf=day.find_all("p")   #找到li中的所有p标签
        temp.append(inf[0].string)   #将第一个p标签中的内容添加到temp列表中红
        if inf[1].find("span") is None:
            temperature_high=None   #傍晚没有最高气温
        else:
            temperature_high=inf[1].find("span").string  #最高气温
            temperature_high=temperature_high.replace("℃","")
        temperature_lower=inf[1].find("i").string   #找到最低温
        temperature_lower=temperature_lower.replace("℃","")
        temp.append(temperature_high)
        temp.append(temperature_lower)
        final.append(temp)   #将temp添加到final中

    return final

def get_data_history(html_txt):
    final=[]
    bs=BeautifulSoup(html_txt,"html.parser")   #创建BeautifulSoup对象
    body=bs.body   #获取body部分
    ul = body.find("ul", {"id":"container"})
    divs = ul.find_all("div", {"class":"t"})

    for div in divs:
        date = div.find("span").string
        incident = div.find("a").string
        final.append({
            'date': date,
            'incident': incident
        })

    return final

# def testpost(request):

    # ret = {
    #     'stat': 'success',
    # }   

    # return HttpResponse(json.dumps(ret))

def getWeather(request):
    host = request.POST.get('user_name', '')    #后续需要判断该用户是否有效以及是否在线
    url = request.POST.get('url', '')

    html = get_html(url)
    result = get_data_weather(html)
    days = []
    for i in result:
        print(i)        #打印天气情况
        days.append(i)

    ret = {
        'stat': 'success',
        'days': days,
    }   

    return HttpResponse(json.dumps(ret))

def getHistory(request):
    host = request.POST.get('user_name', '')

    html = get_html('http://www.todayonhistory.com')
    result = get_data_history(html)

    ret = {
        'stat': 'success',
        'history': result,
    }   

    return HttpResponse(json.dumps(ret))

def getCalendar(request):
    host = request.POST.get('user_name', '')    #后续需要判断该用户是否有效以及是否在线
    calType = request.POST.get('type', '')
    if calType == '0':                  #查看当天所在的日历
        today = datetime.datetime.today()
        cal = calendar.month(today.year, today.month)

        # print cal
        
        ret = {
            'stat': 'success',
            'cal_table': cal,
            'year': today.year,
            'month': today.month,
            'day': today.day,
        }

    else:                           #查看指定月份的日历
        year = request.POST.get('year', '')
        month = request.POST.get('month', '')
        # print year +  "<<-----" + month
        cal = calendar.month(int(year), int(month))

        
        # print cal
        # print "----->>"

        ret = {
            'stat': 'success',
            'cal_table': cal,
            'year': year,           
            'month': month,
        }   #year和month原样返回

    return HttpResponse(json.dumps(ret))
