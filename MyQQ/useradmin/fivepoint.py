# -*- coding: utf-8 -*-
"""
wuziqi by chengjiantong 2020.2.29
"""

from __future__ import unicode_literals

import os
import sys
import time

import random

from django.shortcuts import render
from django.http import HttpResponse

import json

import pickle, redis


class Match():
    '''
    变量命名规则——
    1. 小写b打头，后跟大写字母的为布尔型变量
    2. 全大写的变量类似于宏，不去改变
    3. 大写字母打头，后跟小写字母的变量为实例运行期间不会变或者一次对局过程中不会变的变量
    '''
    # Peer_name = None        #对家名称
    # Peer_level = None       #对家等级
    # History_score = None    #历史比分, X:Y, 我方在前，对方在后
    # bMy_turn = None         #True 我方下 False 对方下
    # bTrust = None           #是否托管


    Start_time = None       #开始时间
    spend_sec = None        #花费的秒数

    matrix = None           #矩阵棋盘, 规定1子先下, 2子后下
    My_point = None         #取值1/2，代表我方的棋子
    Peer_point = None
    last_my_coord = None
    last_peer_coord = None

    regret_flag = 0

    noidea_cnt = 0

    wrong_cnt = 0
    wrong2_cnt = 0
    dbg_cnt = 0
    dbg_list = []

    magicsmile_cnt = 0
    willdie_cnt = 0
    willwin_cnt = 0
    warning = 0

    random_flag = 0

    something_print = 0
    something_print2 = 0
    # ---^_^---

    __SIDELENGTH = 15
    # __MAXPOINT = 15*15
    __last_coord = None       #元组，上次坐标点，用于悔棋
    __cnt_point = None        #当前下的棋子数

    M_index = (None, None, [], [], [])  
    P_index = (None, None, [], [], [])  
    M_Attr = {'W':[], 'ZW':[], 'G':[], 'A+X':[], 'O':[], 'D':[]}
    P_Attr = {'W':[], 'ZW':[], 'G':[], 'A+X':[], 'O':[], 'D':[]}

    history_track = {'start': None, 'crd_list':[]} #start的值取My/Peer

    dict_point = {} #针对单个点字典集合，key为元组坐标，值的形式为[attr, val, [Y,Z,Z,Q,N,Z,Z,N]]
    associate_point = [] #成员为元组坐标
    associate_cnt = 0
    LX_cnt_Total = 0
    My_LX_crd_tier = [[], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], []]
    My_LX_crd_tier_first = 0
    Peer_LX_crd_tier = [[], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], []]
    Peer_LX_crd_tier_first = 0
    LX_Active = ""  #联想主动权掌握者，取值My 或者Peer
    
    class My2():
        def __init__(self, coords, direction, attr=None, rel_coords=None, attract_coords=None, back_coords=None, other=None, special_coords=None):
            self.coords = coords    #元组类型，不可变
            self.attr = attr
            self.direction = direction
            self.rel_coords = rel_coords    #列表类型，可变
            self.attract_coords = attract_coords    #列表类型，可变
            self.back_coords = back_coords  #列表类型，可变
            self.other = other
            self.special_coords = special_coords

    class My3():
        def __init__(self, coords, direction, attr=None, rel_coords=None, attract_coords=None, back_coords=None, other=None):
            self.coords = coords    #元组类型，不可变
            self.attr = attr
            self.direction = direction
            self.rel_coords = rel_coords    #列表类型，可变
            self.attract_coords = attract_coords    #列表类型，可变
            self.back_coords = back_coords  #列表类型，可变
            self.other = other

    class My4():
        def __init__(self, coords, direction, attr=None, rel_coords=None, attract_coords=None, back_coords=None, other=None):
            self.coords = coords    #元组类型，不可变
            self.attr = attr
            self.direction = direction
            self.rel_coords = rel_coords    #列表类型，可变
            self.attract_coords = attract_coords    #列表类型，可变
            self.back_coords = back_coords  #列表类型，可变
            self.other = other

    class Peer2():
        def __init__(self, coords, direction, attr=None, rel_coords=None, attract_coords=None, back_coords=None, other=None, special_coords=None):
            self.coords = coords    #元组类型，不可变
            self.attr = attr
            self.direction = direction
            self.rel_coords = rel_coords    #列表类型，可变
            self.attract_coords = attract_coords    #列表类型，可变
            self.back_coords = back_coords  #列表类型，可变
            self.other = other
            self.special_coords = special_coords

    class Peer3():
        def __init__(self, coords, direction, attr=None, rel_coords=None, attract_coords=None, back_coords=None, other=None):
            self.coords = coords    #元组类型，不可变
            self.attr = attr
            self.direction = direction
            self.rel_coords = rel_coords    #列表类型，可变
            self.attract_coords = attract_coords    #列表类型，可变
            self.back_coords = back_coords  #列表类型，可变
            self.other = other

    class Peer4():
        def __init__(self, coords, direction, attr=None, rel_coords=None, attract_coords=None, back_coords=None, other=None):
            self.coords = coords    #元组类型，不可变
            self.attr = attr
            self.direction = direction
            self.rel_coords = rel_coords    #列表类型，可变
            self.attract_coords = attract_coords    #列表类型，可变
            self.back_coords = back_coords  #列表类型，可变
            self.other = other
        
    def print_MP_Attr(self, MP):
        if MP == 'M':
            for mp in self.M_Attr['W']:
                print "---***---***---***---***---***---***---***---My---> W " 
                print "coords: " + str(mp.coords) + " direction: " + mp.direction
                print "rel_coords: " + str(mp.rel_coords)
                print "attract_coords: " + str(mp.attract_coords)
                print "back_coords: " + str(mp.back_coords)

            for mp in self.M_Attr['ZW']:
                print "---***---***---***---***---***---***---***---My---> ZW " 
                print "coords: " + str(mp.coords) + " direction: " + mp.direction
                print "rel_coords: " + str(mp.rel_coords)
                print "attract_coords: " + str(mp.attract_coords)
                print "back_coords: " + str(mp.back_coords)

            for mp in self.M_Attr['G']:
                print "---***---***---***---***---***---***---***---My---> G " 
                print "coords: " + str(mp.coords) + " direction: " + mp.direction
                print "rel_coords: " + str(mp.rel_coords)
                print "attract_coords: " + str(mp.attract_coords)
                print "back_coords: " + str(mp.back_coords)

            for mp in self.M_Attr['A+X']:
                print "---***---***---***---***---***---***---***---My---> A+X " 
                print "coords: " + str(mp.coords) + " direction: " + mp.direction
                print "rel_coords: " + str(mp.rel_coords)
                print "attract_coords: " + str(mp.attract_coords)
                print "back_coords: " + str(mp.back_coords)

            # for mp in self.M_Attr['O']:
            #     print "---***---***---***---***---***---***---***---My---> O " 
            #     print "coords: " + str(mp.coords) + " direction: " + mp.direction
            #     print "rel_coords: " + str(mp.rel_coords)
            #     print "attract_coords: " + str(mp.attract_coords)
            #     print "back_coords: " + str(mp.back_coords)
        else:
            for mp in self.P_Attr['W']:
                print "---***---***---***---***---***---***---***---***---***---Peer---> W " 
                print "coords: " + str(mp.coords) + " direction: " + mp.direction
                print "rel_coords: " + str(mp.rel_coords)
                print "attract_coords: " + str(mp.attract_coords)
                print "back_coords: " + str(mp.back_coords)

            for mp in self.P_Attr['ZW']:
                print "---***---***---***---***---***---***---***---***---***---Peer---> ZW " 
                print "coords: " + str(mp.coords) + " direction: " + mp.direction
                print "rel_coords: " + str(mp.rel_coords)
                print "attract_coords: " + str(mp.attract_coords)
                print "back_coords: " + str(mp.back_coords)

            for mp in self.P_Attr['G']:
                print "---***---***---***---***---***---***---***---***---***---Peer---> G " 
                print "coords: " + str(mp.coords) + " direction: " + mp.direction
                print "rel_coords: " + str(mp.rel_coords)
                print "attract_coords: " + str(mp.attract_coords)
                print "back_coords: " + str(mp.back_coords)

            for mp in self.P_Attr['A+X']:
                print "---***---***---***---***---***---***---***---***---***---Peer---> A+X " 
                print "coords: " + str(mp.coords) + " direction: " + mp.direction
                print "rel_coords: " + str(mp.rel_coords)
                print "attract_coords: " + str(mp.attract_coords)
                print "back_coords: " + str(mp.back_coords)

            # for mp in self.P_Attr['O']:
            #     print "---***---***---***---***---***---***---***---Peer---> O " 
            #     print "coords: " + str(mp.coords) + " direction: " + mp.direction
            #     print "rel_coords: " + str(mp.rel_coords)
            #     print "attract_coords: " + str(mp.attract_coords)
            #     print "back_coords: " + str(mp.back_coords)


    #打印相关类数据
    def print_MP_class(self, MP, num=None):
        if MP == 'M':
            if num == None:
                print self.M_Attr

            if num == 1:
                #---^_^---
                print "=================================================="
                for coord, info in self.dict_point.items():
                    attr = info[0]; val = info[1]; dirs = info[2]
                    if val == self.My_point:
                        print str(coord) + ": " + attr + ": " + str(dirs)
            elif num == 2:
                print "======>Length of My2: " + str(len(self.M_index[2]))
                for my in self.M_index[2]:
                    print "==========="
                    print "coords: " + str(my.coords) + " direction: " + my.direction + " attr: " + my.attr
                    print "rel_coords: " + str(my.rel_coords)
                    print "attract_coords: " + str(my.attract_coords)
                    print "back_coords: " + str(my.back_coords)
                    print "special_coords: " + str(my.special_coords)
            elif num == 3:
                print "======>Length of My3: " + str(len(self.M_index[3]))
                for my in self.M_index[3]:
                    print "==========="
                    print "coords: " + str(my.coords) + " direction: " + my.direction + " attr: " + my.attr
                    print "rel_coords: " + str(my.rel_coords)
                    print "attract_coords: " + str(my.attract_coords)
                    print "back_coords: " + str(my.back_coords)
            elif num == 4:
                print "======>Length of My4: " + str(len(self.M_index[4]))
                for my in self.M_index[4]:
                    print "==========="
                    print "coords: " + str(my.coords) + " direction: " + my.direction + " attr: " + my.attr
                    print "rel_coords: " + str(my.rel_coords)
                    print "attract_coords: " + str(my.attract_coords)
                    print "back_coords: " + str(my.back_coords)
            else:
                None

            # print "\==M==/"
        elif MP == 'P':
            if num == None:
                print self.P_Attr

            if num == 1:
                print "=================================================="
                for coord, info in self.dict_point.items():
                    attr = info[0]; val = info[1]; dirs = info[2]
                    if val == self.Peer_point:
                        print str(coord) + ": " + attr + ": " + str(dirs)
            elif num == 2:
                print "======>Length of Peer2: " + str(len(self.P_index[2]))
                for my in self.P_index[2]:
                    print "==========="
                    print "coords: " + str(my.coords) + " direction: " + my.direction + " attr: " + my.attr
                    print "rel_coords: " + str(my.rel_coords)
                    print "attract_coords: " + str(my.attract_coords)
                    print "back_coords: " + str(my.back_coords)
                    print "special_coords: " + str(my.special_coords)
            elif num == 3:
                print "======>Length of Peer3: " + str(len(self.P_index[3]))
                for my in self.P_index[3]:
                    print "==========="
                    print "coords: " + str(my.coords) + " direction: " + my.direction + " attr: " + my.attr
                    print "rel_coords: " + str(my.rel_coords)
                    print "attract_coords: " + str(my.attract_coords)
                    print "back_coords: " + str(my.back_coords)
            elif num == 4:
                print "======>Length of Peer4: " + str(len(self.P_index[4]))
                for my in self.P_index[4]:
                    print "==========="
                    print "coords: " + str(my.coords) + " direction: " + my.direction + " attr: " + my.attr
                    print "rel_coords: " + str(my.rel_coords)
                    print "attract_coords: " + str(my.attract_coords)
                    print "back_coords: " + str(my.back_coords)
            else:
                None
            # print "\==P==/"
        else:
            None
    
    #构造函数
    def __init__(self, mypoint):     
        self.Start_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        self.__start_sec = int(time.time())
        self.spend_sec = 0

        self.__cnt_point = 0
        self.clear_chessboard()
        self.My_point = mypoint == 2 and 2 or 1
        self.Peer_point = mypoint == 2 and 1 or 2
        self.history_track['start'] = mypoint == 2 and 'Peer' or 'My'
        self.history_track['crd_list'] = []


        for attr in self.M_Attr:
            self.M_Attr[attr] = []

        for attr in self.P_Attr:
            self.P_Attr[attr] = []

        for pos in range(2,5):
            self.M_index[pos][:] = []

        for pos in range(2,5):
            self.P_index[pos][:] = []

        self.dict_point = {}
        self.associate_point = []



    #更新花费时间
    def update_spend(self):     
        curr_tm = int(time.time())
        self.spend_sec = curr_tm - self.__start_sec

    #清空棋盘
    def clear_chessboard(self):
        self.matrix = [
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
        ]

    #优雅地打印棋盘
    def pretty_chessboard(self):
        for i in range(0, self.__SIDELENGTH):
            print self.matrix[self.__SIDELENGTH-1-i]

    def check_distance_long(self, crd_1, crd_2):
        x_1 = crd_1[0]
        y_1 = crd_1[1]
        x_2 = crd_2[0]
        y_2 = crd_2[1]

        ret = False

        long_var = 6

        if x_1 >= x_2:
            minus = x_1 - x_2
            if minus > long_var:
                ret = True
            if y_1 >= y_2:
                minus = y_1 - y_2
                if minus > long_var:
                    ret = True
            else:
                minus = y_2 - y_1
                if minus > long_var:
                    ret = True
        else:
            minus = x_2 - x_1
            if minus > long_var:
                ret = True
            if y_1 >= y_2:
                minus = y_1 - y_2
                if minus > long_var:
                    ret = True
            else:
                minus = y_2 - y_1
                if minus > long_var:
                    ret = True

        # if ret == True:
        #     print "===> crd_new: " + str(crd_1) + ", crd_last: " + str(crd_2)

        return ret

    '''
    功能: 下棋子
    参数: coord: 元组形式的坐标, val: 值
    返回值: 正确返回0, 错误返回负数
    '''
    def set_point(self, coord, val):  
        if val != 1 and val != 2 and val != 0:
            return -1   #参数错误
        if coord[0] >= self.__SIDELENGTH or coord[1] >= self.__SIDELENGTH:
            return -1
        x = coord[0]
        y = coord[1]

        if val != 0:
            if self.matrix[y][x] != 0:
                return -2   #已经有棋子存在
            self.__last_coord = coord       #记住当前下的棋子位置
            self.__cnt_point += 1
            if self.My_point == val:
                self.last_my_coord = coord
            else:
                self.last_peer_coord = coord

        else:   #悔棋
            if self.matrix[y][x] == 0:
                return -2   #没有棋子怎么悔棋? 一般来说不应该发生
            self.__last_coord = None        #不允许连续悔棋,所以清空
            self.__cnt_point -= 1
            
        self.matrix[y][x] = val

        return 0

    def set_my_point(self, coord, lx_flag=0):
        ret = self.set_point(coord, self.My_point)
        if ret == 0:
            self.history_track['crd_list'].append(("my", coord, lx_flag))
        else:
            print "set__my_point fail:" + str(ret) + " coord: " + str(coord)
            self.wrong2_cnt += 1
        return ret

    def set_peer_point(self, coord, lx_flag=0):
        ret = self.set_point(coord, self.Peer_point)
        if ret == 0:
            self.history_track['crd_list'].append(("PEER", coord, lx_flag))
        else:
            print "set__peer_point fail:" + str(ret) + " coord: " + str(coord)
            self.wrong2_cnt += 1
        return ret

    def update_MP(self, obj):
        class_name = obj.__class__.__name__
        coord = obj.coords[0]
        direction = obj.direction
        rel_coords = []
        attract_coords = []
        back_coords = []
        special_coords = []

        if class_name == "My4" or class_name == "Peer4":
            length = 4
            distance = 1
            ret_str = self.get_point_seq(coord, direction, length, distance)
            
            if ret_str == 'HYYYYH':
                attr = 'D'  #Die
                obj.attract_coords = None
                obj.rel_coords = None
                back_coords = self.get_coord_pack(coord, direction, (-1, 4))
                obj.back_coords = back_coords[:]
            else:
                attr = 'W'  #Win
                # print "===zzzzzzzzzzzzzzzz===>" + str(coord) + ", dir:" + str(direction)
                # print "   "

                if ret_str[0:5] == 'ZYYYY':
                    coord1 = self.get_coord(coord, direction, -1)
                elif ret_str[1:6] == 'YYYYZ':
                    coord1 = self.get_coord(coord, direction, 4)
                else:
                    self.pretty_chessboard()
                    print str(self.history_track['crd_list'])
                    print "  "
                    print str(self.associate_point)
                    print "  "
                    self.print_MP_class('M', 3)
                    print "  "
                    self.print_MP_class('M', 4)
                    print "  "
                    print "=========Error: " + ret_str[0:6]
                
                # print "   "

                attract_coords.append(coord1)
                rel_coords.append(coord1)
                obj.attract_coords = attract_coords[:]  #是新创建，不是引用
                obj.rel_coords = rel_coords[:]  

                if ret_str[0:6] == 'ZYYYYZ':
                    obj.other = 'WW'    #表示稳操胜券
                else:
                    obj.other = None

            obj.attr = attr
        elif class_name == "My3" or class_name == "Peer3":
            length = 3
            distance = 2
            # 'XXYYYXX'
            ret_str = self.get_point_seq(coord, direction, length, distance)
            if ret_str[1:6] == 'HYYYH' or ret_str[1:7] == 'HYYYZH' or ret_str[0:6] == 'HZYYYH':
                attr = 'D'
                obj.attract_coords = None
                obj.rel_coords = None
                if ret_str[1:6] == 'HYYYH':
                    back_coords = self.get_coord_pack(coord, direction, (-1, 3))
                elif ret_str[1:7] == 'HYYYZH':
                    back_coords = self.get_coord_pack(coord, direction, (-1, 4))
                elif ret_str[0:6] == 'HZYYYH':
                    back_coords = self.get_coord_pack(coord, direction, (-2, 3))
                else:
                    None
                obj.back_coords = back_coords[:]
            elif ret_str[2:7] == 'YYYZY' or ret_str[0:5] == 'YZYYY':
                attr = 'W'
                if ret_str[2:7] == 'YYYZY':
                    coord1 = self.get_coord(coord, direction, 3)
                    back_coords = self.get_coord_pack(coord, direction, (4, ))
                else:
                    coord1 = self.get_coord(coord, direction, -1)
                    back_coords = self.get_coord_pack(coord, direction, (-2, ))
                attract_coords.append(coord1)
                rel_coords.append(coord1)
                obj.attract_coords = attract_coords[:]  
                obj.rel_coords = rel_coords[:]
                obj.back_coords = back_coords[:]

                if ret_str[0:7] == 'YZYYYZY':
                    obj.other = 'WW'    #表示稳操胜券
                else:
                    obj.other = None
            elif ret_str[0:7] == 'ZZYYYZZ' or ret_str[0:6] == 'ZZYYYZ' or ret_str[1:7] == 'ZYYYZZ':
                attr = 'ZW' #很可能赢
                if ret_str[0:7] == 'ZZYYYZZ':
                    coord1 = self.get_coord(coord, direction, -2)
                    coord2 = self.get_coord(coord, direction, -1)
                    coord3 = self.get_coord(coord, direction, 3)
                    coord4 = self.get_coord(coord, direction, 4)
                    attract_coords.append(coord2)
                    attract_coords.append(coord3)
                    rel_coords.append(coord1)
                    rel_coords.append(coord2)
                    rel_coords.append(coord3)
                    rel_coords.append(coord4)
                    self.other = 1
                elif ret_str[0:6] == 'ZZYYYZ':
                    coord1 = self.get_coord(coord, direction, -2)
                    coord2 = self.get_coord(coord, direction, -1)
                    coord3 = self.get_coord(coord, direction, 3)
                    attract_coords.append(coord2)
                    rel_coords.append(coord1)
                    rel_coords.append(coord2)
                    rel_coords.append(coord3)
                    back_coords = self.get_coord_pack(coord, direction, (4, ))
                    obj.back_coords = back_coords[:]
                    self.other = 0
                else:
                    coord1 = self.get_coord(coord, direction, -1)
                    coord2 = self.get_coord(coord, direction, 3)
                    coord3 = self.get_coord(coord, direction, 4)
                    attract_coords.append(coord2)
                    rel_coords.append(coord1)
                    rel_coords.append(coord2)
                    rel_coords.append(coord3)
                    back_coords = self.get_coord_pack(coord, direction, (-2, ))
                    obj.back_coords = back_coords[:]
                    self.other = 0
                obj.attract_coords = attract_coords[:] 
                obj.rel_coords = rel_coords[:]
            elif ret_str[0:6] == "ZZYYYH" or ret_str[1:7] == 'HYYYZZ' or ret_str[0:7] == 'HZYYYZH':
                attr = 'G' #Guide
                if ret_str[0:6] == "ZZYYYH":
                    coord1 = self.get_coord(coord, direction, -2)
                    coord2 = self.get_coord(coord, direction, -1)
                    special_coords.append(coord2)
                    back_coords = self.get_coord_pack(coord, direction, (3, ))
                elif ret_str[1:7] == 'HYYYZZ':
                    coord1 = self.get_coord(coord, direction, 3)
                    coord2 = self.get_coord(coord, direction, 4)
                    special_coords.append(coord1)
                    back_coords = self.get_coord_pack(coord, direction, (-1, ))
                elif ret_str[0:7] == 'HZYYYZH':
                    coord1 = self.get_coord(coord, direction, -1)
                    coord2 = self.get_coord(coord, direction, 3)
                    back_coords = self.get_coord_pack(coord, direction, (-2, 4))

                attract_coords.append(coord1)
                attract_coords.append(coord2)
                rel_coords.append(coord1)
                rel_coords.append(coord2)
                obj.attract_coords = attract_coords[:] 
                obj.rel_coords = rel_coords[:]
                obj.back_coords = back_coords[:]
                obj.special_coords = special_coords[:]
            else:
                if class_name == "My3":
                    print "Something error(My3): " + ret_str
                else:
                    print "Something error(Peer3): " + ret_str
                print "coords: " + str(coord) + " direction: " + direction
                # self.pretty_chessboard()
                # self.print_MP_class('M', 2)
                # self.print_MP_class('M', 3)
                # self.print_MP_class('M', 4)
                # self.print_MP_class('P', 2)
                # self.print_MP_class('P', 3)
                # self.print_MP_class('P', 4)
            obj.attr = attr

        elif class_name == "My2" or class_name == "Peer2":
            length = 2
            distance = 3
            #'XXX YY XXX'
            #'012 34 567
            ret_str = self.get_point_seq(coord, direction, length, distance)
            if ret_str[2:6] == 'HYYH' or ret_str[2:7] == 'HYYZH' \
                    or ret_str[1:6] == 'HZYYH' or ret_str[2:8] == 'HYYZZH' \
                    or ret_str[0:6] == 'HZZYYH' or ret_str[1:7] == 'HZYYZH' \
                    or ret_str[0:6] == 'HYZYYH' or ret_str[2:8] == 'HYYZYH':
                # print "2D"
                attr = 'D'
                obj.attract_coords = None
                obj.rel_coords = None
                if ret_str[2:6] == 'HYYH':
                    back_coords = self.get_coord_pack(coord, direction, (-1, 2))
                elif ret_str[2:7] == 'HYYZH':
                    back_coords = self.get_coord_pack(coord, direction, (-1, 3))
                elif ret_str[1:6] == 'HZYYH':
                    back_coords = self.get_coord_pack(coord, direction, (-2, 2))
                elif ret_str[2:8] == 'HYYZZH':
                    back_coords = self.get_coord_pack(coord, direction, (-1, 4))
                elif ret_str[0:6] == 'HZZYYH':
                    back_coords = self.get_coord_pack(coord, direction, (-3, 2))
                elif ret_str[1:7] == 'HZYYZH':
                    back_coords = self.get_coord_pack(coord, direction, (-2, 3))
                elif ret_str[0:6] == 'HYZYYH':
                    back_coords = self.get_coord_pack(coord, direction, (-3, 2, -2))
                elif ret_str[2:8] == 'HYYZYH':
                    back_coords = self.get_coord_pack(coord, direction, (-1, 4, 3))
                else:
                    None
                obj.back_coords = back_coords[:]
            elif ret_str[3:8] == 'YYZYY' or ret_str[0:5] == 'YYZYY':
                attr = 'W'
                if ret_str[3:8] == 'YYZYY':
                    coord1 = self.get_coord(coord, direction, 2)
                    back_coords = self.get_coord_pack(coord, direction, (3, 4))
                else:
                    coord1 = self.get_coord(coord, direction, -1)
                    back_coords = self.get_coord_pack(coord, direction, (-2, -3))
                attract_coords.append(coord1)
                rel_coords.append(coord1)
                obj.attract_coords = attract_coords[:]  
                obj.rel_coords = rel_coords[:]
                obj.back_coords = back_coords[:]

                if ret_str[0:8] == 'YYZYYZYY':
                    obj.other = 'WW'    #表示稳操胜券
                else:
                    obj.other = None
            elif ret_str[2:8] == 'ZYYZYZ' or ret_str[0:6] == 'ZYZYYZ':
                attr = 'ZW' #很可能赢
                if ret_str[2:8] == 'ZYYZYZ':
                    coord1 = self.get_coord(coord, direction, 2)
                    attract_coords.append(coord1)
                    coord2 = self.get_coord(coord, direction, -1)
                    coord3 = self.get_coord(coord, direction, 4)
                    rel_coords.append(coord1)
                    rel_coords.append(coord2)
                    rel_coords.append(coord3)
                    back_coords = self.get_coord_pack(coord, direction, (3, ))
                else:
                    coord1 = self.get_coord(coord, direction, -1)
                    attract_coords.append(coord1)
                    coord2 = self.get_coord(coord, direction, -3)
                    coord3 = self.get_coord(coord, direction, 2)
                    rel_coords.append(coord1)
                    rel_coords.append(coord2)
                    rel_coords.append(coord3)
                    back_coords = self.get_coord_pack(coord, direction, (-2, ))

                obj.attract_coords = attract_coords[:]  
                obj.rel_coords = rel_coords[:]
                obj.back_coords = back_coords[:]
            elif ret_str[2:8] == 'HYYZYZ' or ret_str[0:6] == 'ZYZYYH' \
                    or ret_str[2:8] == 'ZYYZYH' or ret_str[0:6] == 'HYZYYZ' \
                    or ret_str[3:8] == 'YYZZY' or ret_str[0:5] == 'YZZYY':
                attr = 'G'
                if ret_str[2:8] == 'HYYZYZ':
                    coord1 = self.get_coord(coord, direction, 2)
                    coord2 = self.get_coord(coord, direction, 4)
                    back_coords = self.get_coord_pack(coord, direction, (-1, 3))
                    obj.back_coords = back_coords[:]
                elif ret_str[0:6] == 'ZYZYYH':
                    coord1 = self.get_coord(coord, direction, -3)
                    coord2 = self.get_coord(coord, direction, -1)
                    back_coords = self.get_coord_pack(coord, direction, (2, -2))
                    obj.back_coords = back_coords[:]
                elif ret_str[2:8] == 'ZYYZYH':
                    coord1 = self.get_coord(coord, direction, -1)
                    coord2 = self.get_coord(coord, direction, 2)
                    back_coords = self.get_coord_pack(coord, direction, (4, 3))
                    obj.back_coords = back_coords[:]
                elif ret_str[0:6] == 'HYZYYZ':
                    coord1 = self.get_coord(coord, direction, -1)
                    coord2 = self.get_coord(coord, direction, 2)
                    back_coords = self.get_coord_pack(coord, direction, (-3, -2))
                    obj.back_coords = back_coords[:]
                elif ret_str[3:8] == 'YYZZY':
                    coord1 = self.get_coord(coord, direction, 2)
                    coord2 = self.get_coord(coord, direction, 3)
                    back_coords = self.get_coord_pack(coord, direction, (4, ))
                    obj.back_coords = back_coords[:]
                elif ret_str[0:5] == 'YZZYY':
                    coord1 = self.get_coord(coord, direction, -2)
                    coord2 = self.get_coord(coord, direction, -1)
                    back_coords = self.get_coord_pack(coord, direction, (-3, ))
                    obj.back_coords = back_coords[:]

                attract_coords.append(coord1)
                attract_coords.append(coord2)
                rel_coords.append(coord1)
                rel_coords.append(coord2)
                obj.attract_coords = attract_coords[:] 
                obj.rel_coords = rel_coords[:]
            elif ret_str[0:8] == 'ZZZYYZZZ':
                attr = 'A+X'
                coord1 = self.get_coord(coord, direction, -2)
                coord2 = self.get_coord(coord, direction, -1)
                coord3 = self.get_coord(coord, direction, 2)
                coord4 = self.get_coord(coord, direction, 3)
                attract_coords.append(coord1)
                attract_coords.append(coord2)
                attract_coords.append(coord3)
                attract_coords.append(coord4)

                special_coords.append(coord2)
                special_coords.append(coord3)

                rel_coords.append(coord1)
                rel_coords.append(coord2)
                rel_coords.append(coord3)
                rel_coords.append(coord4)
                coord5 = self.get_coord(coord, direction, -3)
                coord6 = self.get_coord(coord, direction, 4)
                rel_coords.append(coord5)
                rel_coords.append(coord6)
                obj.attract_coords = attract_coords[:] 
                obj.rel_coords = rel_coords[:]

                obj.special_coords = special_coords[:] 
            elif ret_str[0:8] == 'ZZZYYZZH' or ret_str[0:8] == 'HZZYYZZZ':
                attr = 'A+X'
                if ret_str[0:8] == 'ZZZYYZZH':
                    coord1 = self.get_coord(coord, direction, -2)
                    coord2 = self.get_coord(coord, direction, -1)
                    coord3 = self.get_coord(coord, direction, 2)
                    #
                    coord4 = self.get_coord(coord, direction, -3)
                    coord5 = self.get_coord(coord, direction, 3)
                    back_coords = self.get_coord_pack(coord, direction, (4, ))
                else:
                    coord1 = self.get_coord(coord, direction, -1)
                    coord2 = self.get_coord(coord, direction, 2)
                    coord3 = self.get_coord(coord, direction, 3)
                    #
                    coord4 = self.get_coord(coord, direction, -2)
                    coord5 = self.get_coord(coord, direction, 4)
                    back_coords = self.get_coord_pack(coord, direction, (-3, ))
                attract_coords.append(coord1)
                attract_coords.append(coord2)
                attract_coords.append(coord3)
                rel_coords.append(coord1)
                rel_coords.append(coord2)
                rel_coords.append(coord3)
                rel_coords.append(coord4)
                rel_coords.append(coord5)
                obj.attract_coords = attract_coords[:] 
                obj.rel_coords = rel_coords[:]
                obj.back_coords = back_coords[:]
            elif ret_str[1:8] == 'HZYYZZZ' or ret_str[0:7] == 'ZZZYYZH' or ret_str[0:8] == 'HZZYYZZH':
                attr = 'A+X'
                if ret_str[1:8] == 'HZYYZZZ':
                    coord1 = self.get_coord(coord, direction, 2)
                    coord2 = self.get_coord(coord, direction, 3)
                    #
                    coord3 = self.get_coord(coord, direction, -1)
                    coord4 = self.get_coord(coord, direction, 4)
                    back_coords = self.get_coord_pack(coord, direction, (-2, ))
                elif ret_str[0:7] == 'ZZZYYZH':
                    coord1 = self.get_coord(coord, direction, -2)
                    coord2 = self.get_coord(coord, direction, -1)
                    #
                    coord3 = self.get_coord(coord, direction, -3)
                    coord4 = self.get_coord(coord, direction, 2)
                    back_coords = self.get_coord_pack(coord, direction, (3, ))
                elif ret_str[0:8] == 'HZZYYZZH':
                    coord1 = self.get_coord(coord, direction, -1)
                    coord2 = self.get_coord(coord, direction, 2)
                    #
                    coord3 = self.get_coord(coord, direction, -2)
                    coord4 = self.get_coord(coord, direction, 3)
                    back_coords = self.get_coord_pack(coord, direction, (-3, 4))
                attract_coords.append(coord1)
                attract_coords.append(coord2)
                rel_coords.append(coord1)
                rel_coords.append(coord2)
                rel_coords.append(coord3)
                rel_coords.append(coord4)
                obj.attract_coords = attract_coords[:] 
                obj.rel_coords = rel_coords[:]
                obj.back_coords = back_coords[:]
            elif ret_str[2:8] == 'HYYZZZ' or ret_str[0:6] == 'ZZZYYH' or ret_str[1:8] == 'HZYYZZH' or ret_str[0:7] == 'HZZYYZH':
                attr = 'O'      #优先级比较低
                if ret_str[2:8] == 'HYYZZZ':
                    coord1 = self.get_coord(coord, direction, 2)
                    coord2 = self.get_coord(coord, direction, 3)
                    coord3 = self.get_coord(coord, direction, 4)
                    back_coords = self.get_coord_pack(coord, direction, (-1, ))
                elif ret_str[0:6] == 'ZZZYYH':
                    coord1 = self.get_coord(coord, direction, -3)
                    coord2 = self.get_coord(coord, direction, -2)
                    coord3 = self.get_coord(coord, direction, -1)
                    back_coords = self.get_coord_pack(coord, direction, (2, ))
                elif ret_str[1:8] == 'HZYYZZH':
                    coord1 = self.get_coord(coord, direction, -1)
                    coord2 = self.get_coord(coord, direction, 2)
                    coord3 = self.get_coord(coord, direction, 3)
                    back_coords = self.get_coord_pack(coord, direction, (-2, 4))
                elif ret_str[0:7] == 'HZZYYZH':
                    coord1 = self.get_coord(coord, direction, -2)
                    coord2 = self.get_coord(coord, direction, -1)
                    coord3 = self.get_coord(coord, direction, 2)
                    back_coords = self.get_coord_pack(coord, direction, (-3, 3))
                else:
                    None
                attract_coords.append(coord1)
                attract_coords.append(coord2)
                attract_coords.append(coord3)
                obj.attract_coords = attract_coords[:]
                rel_coords.append(coord1)
                rel_coords.append(coord2)
                rel_coords.append(coord3)
                obj.rel_coords = rel_coords[:]
                obj.back_coords = back_coords[:]
            else:
                if class_name == "My2":
                    print "Something error(My2): " + ret_str
                else:
                    print "Something error(Peer2): " + ret_str
                print "coords: " + str(coord) + " direction: " + direction
                
                # self.pretty_chessboard()
                # self.print_MP_class('M', 2)
                # self.print_MP_class('M', 3)
                # self.print_MP_class('M', 4)
                # self.print_MP_class('P', 2)
                # self.print_MP_class('P', 3)
                # self.print_MP_class('P', 4)

            obj.attr = attr
        else:
            None
            
    def settle_back(self, coord):
        if self.matrix[coord[1]][coord[0]] == 0:
            return None

        before_val = self.matrix[coord[1]][coord[0]]

        self.matrix[coord[1]][coord[0]] = 0
        self.history_track['crd_list'].pop()

        self.dict_point.pop(coord)           #删除元素
        self.withdraw_dict_pointS(coord)     #更新周围节点
        self.update_cross_back(coord)        #更新其他相关类

        if before_val == self.My_point:
            # 
            remove_list = []
            for mp in self.M_index[2]:
                for cd in mp.coords:
                    if cd == coord:
                        remove_list.append(mp)
            if len(remove_list) != 0:
                for remove_class in remove_list:
                    self.M_Attr[remove_class.attr].remove(remove_class)
                    self.M_index[2].remove(remove_class)
            # 
            remove_list = []
            for mp in self.M_index[3]:
                coord_list = []
                if mp.coords[0] == coord:
                    remove_list.append(mp)
                    coord_list = [mp.coords[1], mp.coords[2]]
                    coord_tuple = tuple(coord_list)
                    my2 = self.My2(coord_tuple, mp.direction, None, None)
                    self.M_index[2].append(my2)
                    self.update_MP(my2)
                    self.M_Attr[my2.attr].append(my2)
                elif mp.coords[1] == coord:     #在中间断开，则不用生成My2类型
                    remove_list.append(mp)
                elif mp.coords[2] == coord:
                    remove_list.append(mp)
                    coord_list = [mp.coords[0], mp.coords[1]]
                    coord_tuple = tuple(coord_list)
                    my2 = self.My2(coord_tuple, mp.direction, None, None)
                    self.M_index[2].append(my2)
                    self.update_MP(my2)
                    self.M_Attr[my2.attr].append(my2)
                else:
                    None
            if len(remove_list) != 0:
                for remove_class in remove_list:
                    self.M_Attr[remove_class.attr].remove(remove_class)
                    self.M_index[3].remove(remove_class)
            # 
            remove_list = []
            for mp in self.M_index[4]:
                coord_list = []
                if mp.coords[0] == coord:
                    remove_list.append(mp)
                    coord_list = [mp.coords[1], mp.coords[2],  mp.coords[3]]
                    coord_tuple = tuple(coord_list)
                    my3 = self.My3(coord_tuple, mp.direction, None, None)
                    self.M_index[3].append(my3)
                    self.update_MP(my3)
                    self.M_Attr[my3.attr].append(my3)
                elif mp.coords[1] == coord:     
                    remove_list.append(mp)
                    coord_list = [mp.coords[2],  mp.coords[3]]
                    coord_tuple = tuple(coord_list)
                    my2 = self.My2(coord_tuple, mp.direction, None, None)
                    self.M_index[2].append(my2)
                    self.update_MP(my2)
                    self.M_Attr[my2.attr].append(my2)
                elif mp.coords[2] == coord:
                    remove_list.append(mp)
                    coord_list = [mp.coords[0],  mp.coords[1]]
                    coord_tuple = tuple(coord_list)
                    my2 = self.My2(coord_tuple, mp.direction, None, None)
                    self.M_index[2].append(my2)
                    self.update_MP(my2)
                    self.M_Attr[my2.attr].append(my2)
                elif mp.coords[3] == coord:
                    remove_list.append(mp)
                    coord_list = [mp.coords[0], mp.coords[1], mp.coords[2]]
                    coord_tuple = tuple(coord_list)
                    my3 = self.My3(coord_tuple, mp.direction, None, None)
                    self.M_index[3].append(my3)
                    self.update_MP(my3)
                    self.M_Attr[my3.attr].append(my3)
                else:
                    None
            if len(remove_list) != 0:
                for remove_class in remove_list:
                    self.M_Attr[remove_class.attr].remove(remove_class)
                    self.M_index[4].remove(remove_class)

        #---^_^---
        if before_val == self.Peer_point:
            # 
            remove_list = []
            for mp in self.P_index[2]:
                for cd in mp.coords:
                    if cd == coord:
                        remove_list.append(mp)
            if len(remove_list) != 0:
                for remove_class in remove_list:
                    self.P_Attr[remove_class.attr].remove(remove_class)
                    self.P_index[2].remove(remove_class)

            # 
            remove_list = []
            for mp in self.P_index[3]:
                coord_list = []
                if mp.coords[0] == coord:
                    remove_list.append(mp)
                    coord_list = [mp.coords[1], mp.coords[2]]
                    coord_tuple = tuple(coord_list)
                    my2 = self.Peer2(coord_tuple, mp.direction, None, None)
                    self.P_index[2].append(my2)
                    self.update_MP(my2)
                    self.P_Attr[my2.attr].append(my2)
                elif mp.coords[1] == coord:     #在中间断开，则不用生成Peer2类型
                    remove_list.append(mp)
                elif mp.coords[2] == coord:
                    remove_list.append(mp)
                    coord_list = [mp.coords[0], mp.coords[1]]
                    coord_tuple = tuple(coord_list)
                    my2 = self.Peer2(coord_tuple, mp.direction, None, None)
                    self.P_index[2].append(my2)
                    self.update_MP(my2)
                    self.P_Attr[my2.attr].append(my2)
                else:
                    None
            if len(remove_list) != 0:
                for remove_class in remove_list:
                    self.P_Attr[remove_class.attr].remove(remove_class)
                    self.P_index[3].remove(remove_class)
            # 
            remove_list = []
            for mp in self.P_index[4]:
                coord_list = []
                if mp.coords[0] == coord:
                    remove_list.append(mp)
                    coord_list = [mp.coords[1], mp.coords[2],  mp.coords[3]]
                    coord_tuple = tuple(coord_list)
                    my3 = self.Peer3(coord_tuple, mp.direction, None, None)
                    self.P_index[3].append(my3)
                    self.update_MP(my3)
                    self.P_Attr[my3.attr].append(my3)
                elif mp.coords[1] == coord:     
                    remove_list.append(mp)
                    coord_list = [mp.coords[2], mp.coords[3]]
                    coord_tuple = tuple(coord_list)
                    my2 = self.Peer2(coord_tuple, mp.direction, None, None)
                    self.P_index[2].append(my2)
                    self.update_MP(my2)
                    self.P_Attr[my2.attr].append(my2)
                elif mp.coords[2] == coord:
                    remove_list.append(mp)
                    coord_list = [mp.coords[0], mp.coords[1]]
                    coord_tuple = tuple(coord_list)
                    my2 = self.Peer2(coord_tuple, mp.direction, None, None)
                    self.P_index[2].append(my2)
                    self.update_MP(my2)
                    self.P_Attr[my2.attr].append(my2)
                elif mp.coords[3] == coord:
                    remove_list.append(mp)
                    coord_list = [mp.coords[0], mp.coords[1], mp.coords[2]]
                    coord_tuple = tuple(coord_list)
                    my3 = self.Peer3(coord_tuple, mp.direction, None, None)
                    self.P_index[3].append(my3)
                    self.update_MP(my3)
                    self.P_Attr[my3.attr].append(my3)
                else:
                    None
            if len(remove_list) != 0:
                for remove_class in remove_list:
                    self.P_Attr[remove_class.attr].remove(remove_class)
                    self.P_index[4].remove(remove_class)

            # # 
            # remove_list = []
            # for mp in self.P_index[3]:
            #     coord_list = []
            #     if mp.coords[0] == coord:
            #         remove_list.append(mp)
            #         coord_list = [mp.coords[1], mp.coords[2]]
            #         coord_tuple = tuple(coord_list)
            #         my2 = self.My2(coord_tuple, mp.direction, None, None)
            #         self.P_index[2].append(my2)
            #         self.update_MP(my2)
            #         self.P_Attr[my2.attr].append(my2)
            #     elif mp.coords[1] == coord:     #在中间断开，则不用生成My2类型
            #         remove_list.append(mp)
            #     elif mp.coords[2] == coord:
            #         remove_list.append(mp)
            #         coord_list = [mp.coords[0], mp.coords[1]]
            #         coord_tuple = tuple(coord_list)
            #         my2 = self.My2(coord_tuple, mp.direction, None, None)
            #         self.P_index[2].append(my2)
            #         self.update_MP(my2)
            #         self.P_Attr[my2.attr].append(my2)
            #     else:
            #         None
            # if len(remove_list) != 0:
            #     for remove_class in remove_list:
            #         self.P_Attr[remove_class.attr].remove(remove_class)
            #         self.P_index[3].remove(remove_class)
            # # 
            # remove_list = []
            # for mp in self.P_index[4]:
            #     coord_list = []
            #     if mp.coords[0] == coord:
            #         remove_list.append(mp)
            #         coord_list = [mp.coords[1], mp.coords[2],  mp.coords[3]]
            #         coord_tuple = tuple(coord_list)
            #         my3 = self.My3(coord_tuple, mp.direction, None, None)
            #         self.P_index[3].append(my3)
            #         self.update_MP(my3)
            #         self.P_Attr[my3.attr].append(my3)
            #     elif mp.coords[1] == coord:     
            #         remove_list.append(mp)
            #         coord_list = [mp.coords[2], mp.coords[3]]
            #         coord_tuple = tuple(coord_list)
            #         my2 = self.My2(coord_tuple, mp.direction, None, None)
            #         self.P_index[2].append(my2)
            #         self.update_MP(my2)
            #         self.P_Attr[my2.attr].append(my2)
            #     elif mp.coords[2] == coord:
            #         remove_list.append(mp)
            #         coord_list = [mp.coords[0], mp.coords[1]]
            #         coord_tuple = tuple(coord_list)
            #         my2 = self.My2(coord_tuple, mp.direction, None, None)
            #         self.P_index[2].append(my2)
            #         self.update_MP(my2)
            #         self.P_Attr[my2.attr].append(my2)
            #     elif mp.coords[3] == coord:
            #         remove_list.append(mp)
            #         coord_list = [mp.coords[0], mp.coords[1], mp.coords[2]]
            #         coord_tuple = tuple(coord_list)
            #         my3 = self.My3(coord_tuple, mp.direction, None, None)
            #         self.P_index[3].append(my3)
            #         self.update_MP(my3)
            #         self.P_Attr[my3.attr].append(my3)
            #     else:
            #         None
            # if len(remove_list) != 0:
            #     for remove_class in remove_list:
            #         self.P_Attr[remove_class.attr].remove(remove_class)
            #         self.P_index[4].remove(remove_class)

        return 0


    def get_point_setByAttr(self, attr, val):
        #遍历棋盘上所有的空的坐标
        ret_set = set()

        for x in range(0, self.__SIDELENGTH):
            for y in range(0, self.__SIDELENGTH):
                if self.matrix[y][x] != 0:
                    continue
                ret_dict = self.may_build_new((x,y), val)
                if ret_dict != None and ret_dict.has_key(attr):
                    ret_set.add((x,y))
        return ret_set

    def get_pointNum_byAttr(self, coord, attr, val):
        special_flag = 0
        special_num = 0
        if attr == 'ZW':
            special_flag = 1

        # if attr == 'W' and val == self.My_point:
        if attr == 'W':
            special_flag = 1

        ret_num = 0

        ret_dict = self.may_build_new(coord, val)
        if ret_dict != None and ret_dict.has_key(attr):
            ret_num += ret_dict[attr]
            if special_flag == 1:
                special_num += ret_dict[attr]

        MP_Attr = (val == self.My_point) and self.M_Attr or self.P_Attr
        if attr == 'ZW':
            MP_list = MP_Attr['A+X']
        elif attr == 'G':
            MP_list = MP_Attr['O']
        elif attr == 'W':
            MP_list = MP_Attr['G']  #暂时不考虑ZW的情况
        else:
            return ret_num
            # print "Wait......asdf"
            # sys.exit()

        for mp in MP_list:
            if coord in mp.attract_coords:
                ret_num += 1
            if special_flag == 1:
                if hasattr(mp, "special_coords") and isinstance(mp.special_coords, list) and coord in mp.special_coords:
                    special_num += 1
                
        if special_flag == 1:
            return (ret_num, special_num)

        return ret_num
        

    # def get_point_setByAttr_all_orig(self, attr, val):
    #     #遍历棋盘上所有的空的坐标
    #     ret_set = set()

    #     for x in range(0, self.__SIDELENGTH):
    #         for y in range(0, self.__SIDELENGTH):
    #             if self.matrix[y][x] != 0:
    #                 continue
    #             ret_dict = self.may_build_new((x,y), val)
    #             if ret_dict != None and ret_dict.has_key(attr):
    #                 ret_set.add((x,y))
    #             else:       #查看已有的类, 这里可能把else去掉是不是比较好???
    #                 MP_Attr = (val == self.My_point) and self.M_Attr or self.P_Attr
    #                 if attr == 'ZW':
    #                     MP_list = MP_Attr['A+X']
    #                 elif attr == 'G':
    #                     MP_list = MP_Attr['O']
    #                 else:
    #                     continue
    #                     # print "Wait......"
    #                     # sys.exit()

    #                 for mp in MP_list:
    #                     if (x,y) in mp.attract_coords:
    #                         ret_set.add((x,y))
                    
    #     return ret_set

    def get_point_setByAttr_all_PWW(self):
        #遍历棋盘上所有的空的坐标
        ret_set = set()

        for x in range(0, self.__SIDELENGTH):
            for y in range(0, self.__SIDELENGTH):
                if self.matrix[y][x] != 0:
                    continue
                ret_dict = self.may_build_new((x,y), self.Peer_point)
                if ret_dict != None and ret_dict.has_key('WW'):
                    ret_set.add((x,y))
                
        return ret_set

    def get_point_setByZW(self, val):
        #遍历棋盘上所有的空的坐标
        ret_set = set()

        for x in range(0, self.__SIDELENGTH):
            for y in range(0, self.__SIDELENGTH):
                if self.matrix[y][x] != 0:
                    continue

                ret_block_tuple = self.may_build_ZW((x,y), val)
                if ret_block_tuple != None:
                    ret_set.add(((x,y), ret_block_tuple))

        return ret_set

    def get_point_setByW(self, val):
        #遍历棋盘上所有的空的坐标
        ret_set = set()

        for x in range(0, self.__SIDELENGTH):
            for y in range(0, self.__SIDELENGTH):
                if self.matrix[y][x] != 0:
                    continue

                ret_block_tuple = self.may_build_W((x,y), val)
                if ret_block_tuple != None:
                    ret_set.add(((x,y), ret_block_tuple))

        return ret_set

    '''
    def get_point_setByAttr_all(self, attr, val):
        #遍历棋盘上所有的空的坐标
        ret_set = set()

        for x in range(0, self.__SIDELENGTH):
            for y in range(0, self.__SIDELENGTH):
                if self.matrix[y][x] != 0:
                    continue
                ret_dict = self.may_build_new((x,y), val)
                if ret_dict != None and ret_dict.has_key(attr):
                    ret_set.add((x,y))
                
                MP_Attr = (val == self.My_point) and self.M_Attr or self.P_Attr
                if attr == 'ZW':
                    MP_list = MP_Attr['A+X']
                elif attr == 'G':
                    MP_list = MP_Attr['O']
                else:
                    continue

                for mp in MP_list:
                    if (x,y) in mp.attract_coords:
                        ret_set.add((x,y))
                    
        return ret_set
    '''

    def get_point_setByAttr_all(self, attr, val):
        #遍历棋盘上所有的空的坐标
        ret_set = set()

        for x in range(0, self.__SIDELENGTH):
            for y in range(0, self.__SIDELENGTH):
                if self.matrix[y][x] != 0:
                    continue
                ret_dict = self.may_build_new((x,y), val)
                if ret_dict != None and ret_dict.has_key(attr):
                    ret_set.add((x,y))
                
                MP_Attr = (val == self.My_point) and self.M_Attr or self.P_Attr
                if attr == 'ZW':
                    MP_list = MP_Attr['A+X']
                elif attr == 'G':
                    MP_list = MP_Attr['O']
                elif attr == 'W':
                    MP_list = MP_Attr['G']
                else:
                    continue

                for mp in MP_list:
                    if (x,y) in mp.attract_coords:
                        ret_set.add((x,y))
                    
        return ret_set

    # 包括各种生成G和A+X的方式
    def get_num_G_AX(self, coord, attr, val):
        if attr != "G" and attr != 'A+X':
            return 0

        x = coord[0]
        y = coord[1]
        num = 0

        ret_dict = self.may_build_new((x,y), val)
        if ret_dict != None and ret_dict.has_key(attr):
            num += ret_dict[attr]

        MP_Attr = (val == self.My_point) and self.M_Attr or self.P_Attr
        if attr == 'G':
            MP_list = MP_Attr['O']
            for mp in MP_list:
                if (x,y) in mp.attract_coords:
                    num += 1

        #接下去还得判断类似于HYZYZY构成G的情形，还有类似ZZYZYZ这样构成A+X的情况
        ret_dict = self.may_build_G_AX_special((x,y), val)
        if ret_dict != None and ret_dict.has_key(attr):
            num += ret_dict[attr]

        return num

    def get_num_ByNewAttrAndcoord(self, attr, coord, val):
        x = coord[0]
        y = coord[1]
        num = 0

        ret_dict = self.may_build_new((x,y), val)
        if ret_dict != None and ret_dict.has_key(attr):
            num += ret_dict[attr]

        MP_Attr = (val == self.My_point) and self.M_Attr or self.P_Attr
        if attr == 'ZW':
            MP_list = MP_Attr['A+X']
        elif attr == 'G':
            MP_list = MP_Attr['O']
        else:
            return num

        for mp in MP_list:
            if (x,y) in mp.attract_coords:
                num += 1

        return num

    def may_build_W(self, coord_arg, val):
        self.matrix[coord_arg[1]][coord_arg[0]] = val
        ret_block_tuple = ()

        ret = self.prase_point(coord_arg, val)
        if ret[0] == 'U':       #只考虑U
            list_dirs = list(ret[1])
            N=0; NE=1; E=2; ES=3; S=4; SW=5; W=6; WN=7
            if list_dirs[N] == 'Y' or list_dirs[S] == 'Y':  # 上下方向 |
                # -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
                coord_list = []
                cnt_1 = 0; cnt_2 = 0
                if list_dirs[N] == 'Y':
                    cnt_1 += 1
                    pt = self.check_point(coord_arg, 'N', 2)
                    if pt == 'Y':
                        cnt_1 += 1
                        pt = self.check_point(coord_arg, 'N', 3)
                        if pt == 'Y':
                            cnt_1 += 1
                            pt = self.check_point(coord_arg, 'N', 4)
                            if pt == 'Y':
                                cnt_1 += 1
                                coord = self.get_coord(coord_arg, 'N', 4)
                                coord_list.append(coord)
                            coord = self.get_coord(coord_arg, 'N', 3)
                            coord_list.append(coord)
                        coord = self.get_coord(coord_arg, 'N', 2)
                        coord_list.append(coord)
                    coord = self.get_coord(coord_arg, 'N', 1)
                    coord_list.append(coord)

                coord_list.append(coord_arg)   #别忘了自己
                # ---^_^---
                if list_dirs[S] == 'Y':
                    cnt_2 += 1
                    coord = self.get_coord(coord_arg, 'S', 1)
                    coord_list.append(coord)
                    pt = self.check_point(coord_arg, 'S', 2)
                    if pt == 'Y':
                        cnt_2 += 1
                        coord = self.get_coord(coord_arg, 'S', 2)
                        coord_list.append(coord)
                        pt = self.check_point(coord_arg, 'S', 3)
                        if pt == 'Y':
                            cnt_2 += 1
                            coord = self.get_coord(coord_arg, 'S', 3)
                            coord_list.append(coord)
                            pt = self.check_point(coord_arg, 'S', 4)
                            if pt == 'Y':
                                cnt_2 += 1
                                coord = self.get_coord(coord_arg, 'S', 4)
                                coord_list.append(coord)
                # ---^_^---
                cnt = cnt_1 + cnt_2 + 1
                
                if cnt == 3:
                    if cnt_1 == 1 and cnt_2 == 1:
                        # 生成一个My3类型
                        coord_tuple = tuple(coord_list)
                        obj = self.My3(coord_tuple, 'S', None, None)
                        self.update_MP(obj)
                        if obj.attr == 'W':
                            for crd in obj.attract_coords:
                                ret_block_tuple += (crd, )
                else:       
                    None
            if list_dirs[NE] == 'Y' or list_dirs[SW] == 'Y':    # 方向 /
                # -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
                coord_list = []
                cnt_1 = 0; cnt_2 = 0
                if list_dirs[NE] == 'Y':
                    cnt_1 += 1
                    pt = self.check_point(coord_arg, 'NE', 2)
                    if pt == 'Y':
                        cnt_1 += 1
                        pt = self.check_point(coord_arg, 'NE', 3)
                        if pt == 'Y':
                            cnt_1 += 1
                            pt = self.check_point(coord_arg, 'NE', 4)
                            if pt == 'Y':
                                cnt_1 += 1
                                coord = self.get_coord(coord_arg, 'NE', 4)
                                coord_list.append(coord)
                            coord = self.get_coord(coord_arg, 'NE', 3)
                            coord_list.append(coord)
                        coord = self.get_coord(coord_arg, 'NE', 2)
                        coord_list.append(coord)
                    coord = self.get_coord(coord_arg, 'NE', 1)
                    coord_list.append(coord)

                coord_list.append(coord_arg)   #别忘了自己
                # ---^_^---
                if list_dirs[SW] == 'Y':
                    cnt_2 += 1
                    coord = self.get_coord(coord_arg, 'SW', 1)
                    coord_list.append(coord)
                    pt = self.check_point(coord_arg, 'SW', 2)
                    if pt == 'Y':
                        cnt_2 += 1
                        coord = self.get_coord(coord_arg, 'SW', 2)
                        coord_list.append(coord)
                        pt = self.check_point(coord_arg, 'SW', 3)
                        if pt == 'Y':
                            cnt_2 += 1
                            coord = self.get_coord(coord_arg, 'SW', 3)
                            coord_list.append(coord)
                            pt = self.check_point(coord_arg, 'SW', 4)
                            if pt == 'Y':
                                cnt_2 += 1
                                coord = self.get_coord(coord_arg, 'SW', 4)
                                coord_list.append(coord)
                # ---^_^---
                cnt = cnt_1 + cnt_2 + 1
                
                if cnt == 3:
                    if cnt_1 == 1 and cnt_2 == 1:
                        # 生成一个My3类型
                        coord_tuple = tuple(coord_list)
                        obj = self.My3(coord_tuple, 'SW', None, None)
                        self.update_MP(obj)

                        if obj.attr == 'W':
                            for crd in obj.attract_coords:
                                ret_block_tuple += (crd, )
                else:       
                    None
            if list_dirs[E] == 'Y' or list_dirs[W] == 'Y':    # 左右方向 —
                # -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
                coord_list = []
                cnt_1 = 0; cnt_2 = 0
                if list_dirs[E] == 'Y':
                    cnt_1 += 1
                    pt = self.check_point(coord_arg, 'E', 2)
                    if pt == 'Y':
                        cnt_1 += 1
                        pt = self.check_point(coord_arg, 'E', 3)
                        if pt == 'Y':
                            cnt_1 += 1
                            pt = self.check_point(coord_arg, 'E', 4)
                            if pt == 'Y':
                                cnt_1 += 1
                                coord = self.get_coord(coord_arg, 'E', 4)
                                coord_list.append(coord)
                            coord = self.get_coord(coord_arg, 'E', 3)
                            coord_list.append(coord)
                        coord = self.get_coord(coord_arg, 'E', 2)
                        coord_list.append(coord)
                    coord = self.get_coord(coord_arg, 'E', 1)
                    coord_list.append(coord)

                coord_list.append(coord_arg)   #别忘了自己
                # ---^_^---
                if list_dirs[W] == 'Y':
                    cnt_2 += 1
                    coord = self.get_coord(coord_arg, 'W', 1)
                    coord_list.append(coord)
                    pt = self.check_point(coord_arg, 'W', 2)
                    if pt == 'Y':
                        cnt_2 += 1
                        coord = self.get_coord(coord_arg, 'W', 2)
                        coord_list.append(coord)
                        pt = self.check_point(coord_arg, 'W', 3)
                        if pt == 'Y':
                            cnt_2 += 1
                            coord = self.get_coord(coord_arg, 'W', 3)
                            coord_list.append(coord)
                            pt = self.check_point(coord_arg, 'W', 4)
                            if pt == 'Y':
                                cnt_2 += 1
                                coord = self.get_coord(coord_arg, 'W', 4)
                                coord_list.append(coord)
                # ---^_^---
                cnt = cnt_1 + cnt_2 + 1
                
                if cnt == 3:
                    if cnt_1 == 1 and cnt_2 == 1:
                        # 生成一个My3类型
                        coord_tuple = tuple(coord_list)
                        obj = self.My3(coord_tuple, 'W', None, None)
                        self.update_MP(obj)
                        if obj.attr == 'W':
                            for crd in obj.attract_coords:
                                ret_block_tuple += (crd, )
                else:       
                    None
            if list_dirs[ES] == 'Y' or list_dirs[WN] == 'Y':    # 方向 \
                # -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
                coord_list = []
                cnt_1 = 0; cnt_2 = 0
                if list_dirs[ES] == 'Y':
                    cnt_1 += 1
                    pt = self.check_point(coord_arg, 'ES', 2)
                    if pt == 'Y':
                        cnt_1 += 1
                        pt = self.check_point(coord_arg, 'ES', 3)
                        if pt == 'Y':
                            cnt_1 += 1
                            pt = self.check_point(coord_arg, 'ES', 4)
                            if pt == 'Y':
                                cnt_1 += 1
                                coord = self.get_coord(coord_arg, 'ES', 4)
                                coord_list.append(coord)
                            coord = self.get_coord(coord_arg, 'ES', 3)
                            coord_list.append(coord)
                        coord = self.get_coord(coord_arg, 'ES', 2)
                        coord_list.append(coord)
                    coord = self.get_coord(coord_arg, 'ES', 1)
                    coord_list.append(coord)

                coord_list.append(coord_arg)   #别忘了自己
                # ---^_^---
                if list_dirs[WN] == 'Y':
                    cnt_2 += 1
                    coord = self.get_coord(coord_arg, 'WN', 1)
                    coord_list.append(coord)
                    pt = self.check_point(coord_arg, 'WN', 2)
                    if pt == 'Y':
                        cnt_2 += 1
                        coord = self.get_coord(coord_arg, 'WN', 2)
                        coord_list.append(coord)
                        pt = self.check_point(coord_arg, 'WN', 3)
                        if pt == 'Y':
                            cnt_2 += 1
                            coord = self.get_coord(coord_arg, 'WN', 3)
                            coord_list.append(coord)
                            pt = self.check_point(coord_arg, 'WN', 4)
                            if pt == 'Y':
                                cnt_2 += 1
                                coord = self.get_coord(coord_arg, 'WN', 4)
                                coord_list.append(coord)
                # ---^_^---
                cnt = cnt_1 + cnt_2 + 1
                
                if cnt == 3:
                    if cnt_1 == 1 and cnt_2 == 1:
                        # 生成一个My3类型
                        coord_tuple = tuple(coord_list)
                        obj = self.My3(coord_tuple, 'WN', None, None)
                        self.update_MP(obj)

                        if obj.attr == 'W':
                            for crd in obj.attract_coords:
                                ret_block_tuple += (crd, )
                else:       
                    None


        else:
            None

        self.matrix[coord_arg[1]][coord_arg[0]] = 0         #还原

        if len(ret_block_tuple) == 0:
            return None
        else:
            return ret_block_tuple

    def may_build_ZW(self, coord_arg, val):
        self.matrix[coord_arg[1]][coord_arg[0]] = val
        ret_block_tuple = ()

        ret = self.prase_point(coord_arg, val)
        if ret[0] == 'U':       #只考虑U
            list_dirs = list(ret[1])
            N=0; NE=1; E=2; ES=3; S=4; SW=5; W=6; WN=7
            if list_dirs[N] == 'Y' or list_dirs[S] == 'Y':  # 上下方向 |
                # -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
                coord_list = []
                cnt_1 = 0; cnt_2 = 0
                if list_dirs[N] == 'Y':
                    cnt_1 += 1
                    pt = self.check_point(coord_arg, 'N', 2)
                    if pt == 'Y':
                        cnt_1 += 1
                        pt = self.check_point(coord_arg, 'N', 3)
                        if pt == 'Y':
                            cnt_1 += 1
                            pt = self.check_point(coord_arg, 'N', 4)
                            if pt == 'Y':
                                cnt_1 += 1
                                coord = self.get_coord(coord_arg, 'N', 4)
                                coord_list.append(coord)
                            coord = self.get_coord(coord_arg, 'N', 3)
                            coord_list.append(coord)
                        coord = self.get_coord(coord_arg, 'N', 2)
                        coord_list.append(coord)
                    coord = self.get_coord(coord_arg, 'N', 1)
                    coord_list.append(coord)

                coord_list.append(coord_arg)   #别忘了自己
                # ---^_^---
                if list_dirs[S] == 'Y':
                    cnt_2 += 1
                    coord = self.get_coord(coord_arg, 'S', 1)
                    coord_list.append(coord)
                    pt = self.check_point(coord_arg, 'S', 2)
                    if pt == 'Y':
                        cnt_2 += 1
                        coord = self.get_coord(coord_arg, 'S', 2)
                        coord_list.append(coord)
                        pt = self.check_point(coord_arg, 'S', 3)
                        if pt == 'Y':
                            cnt_2 += 1
                            coord = self.get_coord(coord_arg, 'S', 3)
                            coord_list.append(coord)
                            pt = self.check_point(coord_arg, 'S', 4)
                            if pt == 'Y':
                                cnt_2 += 1
                                coord = self.get_coord(coord_arg, 'S', 4)
                                coord_list.append(coord)
                # ---^_^---
                cnt = cnt_1 + cnt_2 + 1
                
                if cnt == 3:
                    if cnt_1 == 1 and cnt_2 == 1:
                        # 生成一个My3类型
                        coord_tuple = tuple(coord_list)
                        obj = self.My3(coord_tuple, 'S', None, None)
                        self.update_MP(obj)
                        if obj.attr == 'ZW':
                            # for crd in obj.attract_coords:
                            for crd in obj.rel_coords:          #这里是要封堵，所以用rel_coords,2020.3.11
                                ret_block_tuple += (crd, )
                elif cnt == 2:  
                    #生成一个My2类型
                    coord_tuple = tuple(coord_list)
                    obj = self.My2(coord_tuple, 'S', None, None)
                    self.update_MP(obj)
                    if obj.attr == 'ZW':
                        for crd in obj.rel_coords:
                            ret_block_tuple += (crd, )
                else:       
                    # 只考虑cnt为2和3的情况, 忽略其他
                    None
            if list_dirs[NE] == 'Y' or list_dirs[SW] == 'Y':    # 方向 /
                # -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
                coord_list = []
                cnt_1 = 0; cnt_2 = 0
                if list_dirs[NE] == 'Y':
                    cnt_1 += 1
                    pt = self.check_point(coord_arg, 'NE', 2)
                    if pt == 'Y':
                        cnt_1 += 1
                        pt = self.check_point(coord_arg, 'NE', 3)
                        if pt == 'Y':
                            cnt_1 += 1
                            pt = self.check_point(coord_arg, 'NE', 4)
                            if pt == 'Y':
                                cnt_1 += 1
                                coord = self.get_coord(coord_arg, 'NE', 4)
                                coord_list.append(coord)
                            coord = self.get_coord(coord_arg, 'NE', 3)
                            coord_list.append(coord)
                        coord = self.get_coord(coord_arg, 'NE', 2)
                        coord_list.append(coord)
                    coord = self.get_coord(coord_arg, 'NE', 1)
                    coord_list.append(coord)

                coord_list.append(coord_arg)   #别忘了自己
                # ---^_^---
                if list_dirs[SW] == 'Y':
                    cnt_2 += 1
                    coord = self.get_coord(coord_arg, 'SW', 1)
                    coord_list.append(coord)
                    pt = self.check_point(coord_arg, 'SW', 2)
                    if pt == 'Y':
                        cnt_2 += 1
                        coord = self.get_coord(coord_arg, 'SW', 2)
                        coord_list.append(coord)
                        pt = self.check_point(coord_arg, 'SW', 3)
                        if pt == 'Y':
                            cnt_2 += 1
                            coord = self.get_coord(coord_arg, 'SW', 3)
                            coord_list.append(coord)
                            pt = self.check_point(coord_arg, 'SW', 4)
                            if pt == 'Y':
                                cnt_2 += 1
                                coord = self.get_coord(coord_arg, 'SW', 4)
                                coord_list.append(coord)
                # ---^_^---
                cnt = cnt_1 + cnt_2 + 1
                
                if cnt == 3:
                    if cnt_1 == 1 and cnt_2 == 1:
                        # 生成一个My3类型
                        coord_tuple = tuple(coord_list)
                        obj = self.My3(coord_tuple, 'SW', None, None)
                        self.update_MP(obj)

                        if obj.attr == 'ZW':
                            for crd in obj.rel_coords:
                                ret_block_tuple += (crd, )
                elif cnt == 2:  
                    #生成一个My2类型
                    coord_tuple = tuple(coord_list)
                    obj = self.My2(coord_tuple, 'SW', None, None)
                    self.update_MP(obj)

                    if obj.attr == 'ZW':
                        for crd in obj.rel_coords:
                            ret_block_tuple += (crd, )
                else:       
                    # 只考虑cnt为2和3的情况, 忽略其他
                    None
            if list_dirs[E] == 'Y' or list_dirs[W] == 'Y':    # 左右方向 —
                # -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
                coord_list = []
                cnt_1 = 0; cnt_2 = 0
                if list_dirs[E] == 'Y':
                    cnt_1 += 1
                    pt = self.check_point(coord_arg, 'E', 2)
                    if pt == 'Y':
                        cnt_1 += 1
                        pt = self.check_point(coord_arg, 'E', 3)
                        if pt == 'Y':
                            cnt_1 += 1
                            pt = self.check_point(coord_arg, 'E', 4)
                            if pt == 'Y':
                                cnt_1 += 1
                                coord = self.get_coord(coord_arg, 'E', 4)
                                coord_list.append(coord)
                            coord = self.get_coord(coord_arg, 'E', 3)
                            coord_list.append(coord)
                        coord = self.get_coord(coord_arg, 'E', 2)
                        coord_list.append(coord)
                    coord = self.get_coord(coord_arg, 'E', 1)
                    coord_list.append(coord)

                coord_list.append(coord_arg)   #别忘了自己
                # ---^_^---
                if list_dirs[W] == 'Y':
                    cnt_2 += 1
                    coord = self.get_coord(coord_arg, 'W', 1)
                    coord_list.append(coord)
                    pt = self.check_point(coord_arg, 'W', 2)
                    if pt == 'Y':
                        cnt_2 += 1
                        coord = self.get_coord(coord_arg, 'W', 2)
                        coord_list.append(coord)
                        pt = self.check_point(coord_arg, 'W', 3)
                        if pt == 'Y':
                            cnt_2 += 1
                            coord = self.get_coord(coord_arg, 'W', 3)
                            coord_list.append(coord)
                            pt = self.check_point(coord_arg, 'W', 4)
                            if pt == 'Y':
                                cnt_2 += 1
                                coord = self.get_coord(coord_arg, 'W', 4)
                                coord_list.append(coord)
                # ---^_^---
                cnt = cnt_1 + cnt_2 + 1
                
                if cnt == 3:
                    if cnt_1 == 1 and cnt_2 == 1:
                        # 生成一个My3类型
                        coord_tuple = tuple(coord_list)
                        obj = self.My3(coord_tuple, 'W', None, None)
                        self.update_MP(obj)
                        if obj.attr == 'ZW':
                            for crd in obj.rel_coords:
                                ret_block_tuple += (crd, )

                elif cnt == 2:  
                    #生成一个My2类型
                    coord_tuple = tuple(coord_list)
                    obj = self.My2(coord_tuple, 'W', None, None)
                    self.update_MP(obj)
                    if obj.attr == 'ZW':
                        for crd in obj.rel_coords:
                            ret_block_tuple += (crd, )
                else:       
                    # 只考虑cnt为2和3的情况, 忽略其他
                    None
            if list_dirs[ES] == 'Y' or list_dirs[WN] == 'Y':    # 方向 \
                # -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
                coord_list = []
                cnt_1 = 0; cnt_2 = 0
                if list_dirs[ES] == 'Y':
                    cnt_1 += 1
                    pt = self.check_point(coord_arg, 'ES', 2)
                    if pt == 'Y':
                        cnt_1 += 1
                        pt = self.check_point(coord_arg, 'ES', 3)
                        if pt == 'Y':
                            cnt_1 += 1
                            pt = self.check_point(coord_arg, 'ES', 4)
                            if pt == 'Y':
                                cnt_1 += 1
                                coord = self.get_coord(coord_arg, 'ES', 4)
                                coord_list.append(coord)
                            coord = self.get_coord(coord_arg, 'ES', 3)
                            coord_list.append(coord)
                        coord = self.get_coord(coord_arg, 'ES', 2)
                        coord_list.append(coord)
                    coord = self.get_coord(coord_arg, 'ES', 1)
                    coord_list.append(coord)

                coord_list.append(coord_arg)   #别忘了自己
                # ---^_^---
                if list_dirs[WN] == 'Y':
                    cnt_2 += 1
                    coord = self.get_coord(coord_arg, 'WN', 1)
                    coord_list.append(coord)
                    pt = self.check_point(coord_arg, 'WN', 2)
                    if pt == 'Y':
                        cnt_2 += 1
                        coord = self.get_coord(coord_arg, 'WN', 2)
                        coord_list.append(coord)
                        pt = self.check_point(coord_arg, 'WN', 3)
                        if pt == 'Y':
                            cnt_2 += 1
                            coord = self.get_coord(coord_arg, 'WN', 3)
                            coord_list.append(coord)
                            pt = self.check_point(coord_arg, 'WN', 4)
                            if pt == 'Y':
                                cnt_2 += 1
                                coord = self.get_coord(coord_arg, 'WN', 4)
                                coord_list.append(coord)
                # ---^_^---
                cnt = cnt_1 + cnt_2 + 1
                
                if cnt == 3:
                    if cnt_1 == 1 and cnt_2 == 1:
                        # 生成一个My3类型
                        coord_tuple = tuple(coord_list)
                        obj = self.My3(coord_tuple, 'WN', None, None)
                        self.update_MP(obj)

                        if obj.attr == 'ZW':
                            for crd in obj.rel_coords:
                                ret_block_tuple += (crd, )
                elif cnt == 2:  
                    #生成一个My2类型
                    coord_tuple = tuple(coord_list)
                    obj = self.My2(coord_tuple, 'WN', None, None)
                    self.update_MP(obj)
                    if obj.attr == 'ZW':
                        for crd in obj.rel_coords:
                            ret_block_tuple += (crd, )
                else:       
                    None


        else:
            None

        self.matrix[coord_arg[1]][coord_arg[0]] = 0         #还原

        if len(ret_block_tuple) == 0:
            return None
        else:
            return ret_block_tuple
        
    def special_fifth_maylose(self, coord):
        ret = self.prase_point(coord, self.My_point)
        cnt = 0
        list_dirs = list(ret[1])
        N=0; E=2; S=4; W=6
        if list_dirs[N] == 'N':
            cnt += 1
        if list_dirs[E] == 'N':
            cnt += 1
        if list_dirs[S] == 'N':
            cnt += 1
        if list_dirs[W] == 'N':
            cnt += 1

        if cnt >= 3:
            return True
        else:
            return None

    def may_build_G_AX_special(self, coord_arg, val):
        self.matrix[coord_arg[1]][coord_arg[0]] = val
        ret_dict = {}

        N=0; NE=1; E=2; ES=3; #S=4; SW=5; W=6; WN=7

        ret_str = self.get_point_seq(coord_arg, N, 1, 5)
        if ret_str[0:6] == 'HYZYZY' or ret_str[5:11] == 'YZYZYH'\
            or ret_str[2:8] == 'HYZYZY' or ret_str[3:9] == 'YZYZYH'\
            or ret_str[4:10] == 'HYZYZY' or ret_str[1:7] == 'YZYZYH':
            if ret_dict.has_key('G'):
                ret_dict['G'] += 1
            else:
                ret_dict['G'] = 1
        if ret_str[4:10] == 'ZYZYZZ' or ret_str[2:8] == 'ZYZYZZ'\
            or ret_str[3:9] == 'ZZYZYZ' or ret_str[1:7] == 'ZZYZYZ'\
            or ret_str[4:10] == 'ZYZZYZ' or ret_str[2:8] == 'ZYZZYZ':
            if ret_dict.has_key('A+X'):
                ret_dict['A+X'] += 1
            else:
                ret_dict['A+X'] = 1
        # ---
        ret_str = self.get_point_seq(coord_arg, NE, 1, 5)
        if ret_str[0:6] == 'HYZYZY' or ret_str[5:11] == 'YZYZYH'\
            or ret_str[2:8] == 'HYZYZY' or ret_str[3:9] == 'YZYZYH'\
            or ret_str[4:10] == 'HYZYZY' or ret_str[1:7] == 'YZYZYH':
            if ret_dict.has_key('G'):
                ret_dict['G'] += 1
            else:
                ret_dict['G'] = 1
        if ret_str[4:10] == 'ZYZYZZ' or ret_str[2:8] == 'ZYZYZZ'\
            or ret_str[3:9] == 'ZZYZYZ' or ret_str[1:7] == 'ZZYZYZ'\
            or ret_str[4:10] == 'ZYZZYZ' or ret_str[2:8] == 'ZYZZYZ':
            if ret_dict.has_key('A+X'):
                ret_dict['A+X'] += 1
            else:
                ret_dict['A+X'] = 1
        # ---
        ret_str = self.get_point_seq(coord_arg, E, 1, 5)
        if ret_str[0:6] == 'HYZYZY' or ret_str[5:11] == 'YZYZYH'\
            or ret_str[2:8] == 'HYZYZY' or ret_str[3:9] == 'YZYZYH'\
            or ret_str[4:10] == 'HYZYZY' or ret_str[1:7] == 'YZYZYH':
            if ret_dict.has_key('G'):
                ret_dict['G'] += 1
            else:
                ret_dict['G'] = 1
        if ret_str[4:10] == 'ZYZYZZ' or ret_str[2:8] == 'ZYZYZZ'\
            or ret_str[3:9] == 'ZZYZYZ' or ret_str[1:7] == 'ZZYZYZ'\
            or ret_str[4:10] == 'ZYZZYZ' or ret_str[2:8] == 'ZYZZYZ':
            if ret_dict.has_key('A+X'):
                ret_dict['A+X'] += 1
            else:
                ret_dict['A+X'] = 1
        # ---
        ret_str = self.get_point_seq(coord_arg, ES, 1, 5)
        if ret_str[0:6] == 'HYZYZY' or ret_str[5:11] == 'YZYZYH'\
            or ret_str[2:8] == 'HYZYZY' or ret_str[3:9] == 'YZYZYH'\
            or ret_str[4:10] == 'HYZYZY' or ret_str[1:7] == 'YZYZYH':
            if ret_dict.has_key('G'):
                ret_dict['G'] += 1
            else:
                ret_dict['G'] = 1
        if ret_str[4:10] == 'ZYZYZZ' or ret_str[2:8] == 'ZYZYZZ'\
            or ret_str[3:9] == 'ZZYZYZ' or ret_str[1:7] == 'ZZYZYZ'\
            or ret_str[4:10] == 'ZYZZYZ' or ret_str[2:8] == 'ZYZZYZ':
            if ret_dict.has_key('A+X'):
                ret_dict['A+X'] += 1
            else:
                ret_dict['A+X'] = 1
        
        self.matrix[coord_arg[1]][coord_arg[0]] = 0         #还原

        if len(ret_dict) == 0:
            return None
        else:
            return ret_dict
        
    #试探函数，返回字典
    def may_build_new(self, coord_arg, val):     
        self.matrix[coord_arg[1]][coord_arg[0]] = val
        ret_dict = {}

        ret = self.prase_point(coord_arg, val)
        if ret[0] == 'U':       #只考虑U
            list_dirs = list(ret[1])
            N=0; NE=1; E=2; ES=3; S=4; SW=5; W=6; WN=7
            if list_dirs[N] == 'Y' or list_dirs[S] == 'Y':  # 上下方向 |
                # -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
                coord_list = []
                cnt_1 = 0; cnt_2 = 0
                if list_dirs[N] == 'Y':
                    cnt_1 += 1
                    pt = self.check_point(coord_arg, 'N', 2)
                    if pt == 'Y':
                        cnt_1 += 1
                        pt = self.check_point(coord_arg, 'N', 3)
                        if pt == 'Y':
                            cnt_1 += 1
                            pt = self.check_point(coord_arg, 'N', 4)
                            if pt == 'Y':
                                cnt_1 += 1
                                coord = self.get_coord(coord_arg, 'N', 4)
                                coord_list.append(coord)
                            coord = self.get_coord(coord_arg, 'N', 3)
                            coord_list.append(coord)
                        coord = self.get_coord(coord_arg, 'N', 2)
                        coord_list.append(coord)
                    coord = self.get_coord(coord_arg, 'N', 1)
                    coord_list.append(coord)

                coord_list.append(coord_arg)   #别忘了自己
                # ---^_^---
                if list_dirs[S] == 'Y':
                    cnt_2 += 1
                    coord = self.get_coord(coord_arg, 'S', 1)
                    coord_list.append(coord)
                    pt = self.check_point(coord_arg, 'S', 2)
                    if pt == 'Y':
                        cnt_2 += 1
                        coord = self.get_coord(coord_arg, 'S', 2)
                        coord_list.append(coord)
                        pt = self.check_point(coord_arg, 'S', 3)
                        if pt == 'Y':
                            cnt_2 += 1
                            coord = self.get_coord(coord_arg, 'S', 3)
                            coord_list.append(coord)
                            pt = self.check_point(coord_arg, 'S', 4)
                            if pt == 'Y':
                                cnt_2 += 1
                                coord = self.get_coord(coord_arg, 'S', 4)
                                coord_list.append(coord)
                # ---^_^---
                cnt = cnt_1 + cnt_2 + 1
                
                if cnt == 3:
                    if cnt_1 == 1 and cnt_2 == 1:
                        # 生成一个My3类型
                        coord_tuple = tuple(coord_list)
                        obj = self.My3(coord_tuple, 'S', None, None)
                        self.update_MP(obj)
                        if obj.attr == 'W' and obj.other == 'WW':
                            ret_dict['WW'] = 1      #特殊处理

                        if ret_dict.has_key(obj.attr):
                            ret_dict[obj.attr] += 1
                        else:
                            ret_dict[obj.attr] = 1
                elif cnt == 2:  
                    #生成一个My2类型
                    coord_tuple = tuple(coord_list)
                    obj = self.My2(coord_tuple, 'S', None, None)
                    self.update_MP(obj)
                    if obj.attr == 'W' and obj.other == 'WW':
                        ret_dict['WW'] = 1      #特殊处理

                    if ret_dict.has_key(obj.attr):
                        ret_dict[obj.attr] += 1
                    else:
                        ret_dict[obj.attr] = 1
                else:       
                    # 只考虑cnt为2和3的情况, 忽略其他
                    None
            if list_dirs[NE] == 'Y' or list_dirs[SW] == 'Y':    # 方向 /
                # -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
                coord_list = []
                cnt_1 = 0; cnt_2 = 0
                if list_dirs[NE] == 'Y':
                    cnt_1 += 1
                    pt = self.check_point(coord_arg, 'NE', 2)
                    if pt == 'Y':
                        cnt_1 += 1
                        pt = self.check_point(coord_arg, 'NE', 3)
                        if pt == 'Y':
                            cnt_1 += 1
                            pt = self.check_point(coord_arg, 'NE', 4)
                            if pt == 'Y':
                                cnt_1 += 1
                                coord = self.get_coord(coord_arg, 'NE', 4)
                                coord_list.append(coord)
                            coord = self.get_coord(coord_arg, 'NE', 3)
                            coord_list.append(coord)
                        coord = self.get_coord(coord_arg, 'NE', 2)
                        coord_list.append(coord)
                    coord = self.get_coord(coord_arg, 'NE', 1)
                    coord_list.append(coord)

                coord_list.append(coord_arg)   #别忘了自己
                # ---^_^---
                if list_dirs[SW] == 'Y':
                    cnt_2 += 1
                    coord = self.get_coord(coord_arg, 'SW', 1)
                    coord_list.append(coord)
                    pt = self.check_point(coord_arg, 'SW', 2)
                    if pt == 'Y':
                        cnt_2 += 1
                        coord = self.get_coord(coord_arg, 'SW', 2)
                        coord_list.append(coord)
                        pt = self.check_point(coord_arg, 'SW', 3)
                        if pt == 'Y':
                            cnt_2 += 1
                            coord = self.get_coord(coord_arg, 'SW', 3)
                            coord_list.append(coord)
                            pt = self.check_point(coord_arg, 'SW', 4)
                            if pt == 'Y':
                                cnt_2 += 1
                                coord = self.get_coord(coord_arg, 'SW', 4)
                                coord_list.append(coord)
                # ---^_^---
                cnt = cnt_1 + cnt_2 + 1
                
                if cnt == 3:
                    if cnt_1 == 1 and cnt_2 == 1:
                        # 生成一个My3类型
                        coord_tuple = tuple(coord_list)
                        obj = self.My3(coord_tuple, 'SW', None, None)
                        self.update_MP(obj)

                        if obj.attr == 'W' and obj.other == 'WW':
                            ret_dict['WW'] = 1      #特殊处理

                        if ret_dict.has_key(obj.attr):
                            ret_dict[obj.attr] += 1
                        else:
                            ret_dict[obj.attr] = 1
                elif cnt == 2:  
                    #生成一个My2类型
                    coord_tuple = tuple(coord_list)
                    obj = self.My2(coord_tuple, 'SW', None, None)
                    self.update_MP(obj)

                    if obj.attr == 'W' and obj.other == 'WW':
                        ret_dict['WW'] = 1      #特殊处理

                    if ret_dict.has_key(obj.attr):
                        ret_dict[obj.attr] += 1
                    else:
                        ret_dict[obj.attr] = 1
                else:       
                    # 只考虑cnt为2和3的情况, 忽略其他
                    None
            if list_dirs[E] == 'Y' or list_dirs[W] == 'Y':    # 左右方向 —
                # -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
                coord_list = []
                cnt_1 = 0; cnt_2 = 0
                if list_dirs[E] == 'Y':
                    cnt_1 += 1
                    pt = self.check_point(coord_arg, 'E', 2)
                    if pt == 'Y':
                        cnt_1 += 1
                        pt = self.check_point(coord_arg, 'E', 3)
                        if pt == 'Y':
                            cnt_1 += 1
                            pt = self.check_point(coord_arg, 'E', 4)
                            if pt == 'Y':
                                cnt_1 += 1
                                coord = self.get_coord(coord_arg, 'E', 4)
                                coord_list.append(coord)
                            coord = self.get_coord(coord_arg, 'E', 3)
                            coord_list.append(coord)
                        coord = self.get_coord(coord_arg, 'E', 2)
                        coord_list.append(coord)
                    coord = self.get_coord(coord_arg, 'E', 1)
                    coord_list.append(coord)

                coord_list.append(coord_arg)   #别忘了自己
                # ---^_^---
                if list_dirs[W] == 'Y':
                    cnt_2 += 1
                    coord = self.get_coord(coord_arg, 'W', 1)
                    coord_list.append(coord)
                    pt = self.check_point(coord_arg, 'W', 2)
                    if pt == 'Y':
                        cnt_2 += 1
                        coord = self.get_coord(coord_arg, 'W', 2)
                        coord_list.append(coord)
                        pt = self.check_point(coord_arg, 'W', 3)
                        if pt == 'Y':
                            cnt_2 += 1
                            coord = self.get_coord(coord_arg, 'W', 3)
                            coord_list.append(coord)
                            pt = self.check_point(coord_arg, 'W', 4)
                            if pt == 'Y':
                                cnt_2 += 1
                                coord = self.get_coord(coord_arg, 'W', 4)
                                coord_list.append(coord)
                # ---^_^---
                cnt = cnt_1 + cnt_2 + 1
                
                if cnt == 3:
                    if cnt_1 == 1 and cnt_2 == 1:
                        # 生成一个My3类型
                        coord_tuple = tuple(coord_list)
                        obj = self.My3(coord_tuple, 'W', None, None)
                        self.update_MP(obj)
                        if obj.attr == 'W' and obj.other == 'WW':
                            ret_dict['WW'] = 1      #特殊处理

                        if ret_dict.has_key(obj.attr):
                            ret_dict[obj.attr] += 1
                        else:
                            ret_dict[obj.attr] = 1
                elif cnt == 2:  
                    #生成一个My2类型
                    coord_tuple = tuple(coord_list)
                    obj = self.My2(coord_tuple, 'W', None, None)
                    self.update_MP(obj)
                    if obj.attr == 'W' and obj.other == 'WW':
                        ret_dict['WW'] = 1      #特殊处理

                    if ret_dict.has_key(obj.attr):
                        ret_dict[obj.attr] += 1
                    else:
                        ret_dict[obj.attr] = 1
                else:       
                    # 只考虑cnt为2和3的情况, 忽略其他
                    None
            if list_dirs[ES] == 'Y' or list_dirs[WN] == 'Y':    # 方向 \
                # -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
                coord_list = []
                cnt_1 = 0; cnt_2 = 0
                if list_dirs[ES] == 'Y':
                    cnt_1 += 1
                    pt = self.check_point(coord_arg, 'ES', 2)
                    if pt == 'Y':
                        cnt_1 += 1
                        pt = self.check_point(coord_arg, 'ES', 3)
                        if pt == 'Y':
                            cnt_1 += 1
                            pt = self.check_point(coord_arg, 'ES', 4)
                            if pt == 'Y':
                                cnt_1 += 1
                                coord = self.get_coord(coord_arg, 'ES', 4)
                                coord_list.append(coord)
                            coord = self.get_coord(coord_arg, 'ES', 3)
                            coord_list.append(coord)
                        coord = self.get_coord(coord_arg, 'ES', 2)
                        coord_list.append(coord)
                    coord = self.get_coord(coord_arg, 'ES', 1)
                    coord_list.append(coord)

                coord_list.append(coord_arg)   #别忘了自己
                # ---^_^---
                if list_dirs[WN] == 'Y':
                    cnt_2 += 1
                    coord = self.get_coord(coord_arg, 'WN', 1)
                    coord_list.append(coord)
                    pt = self.check_point(coord_arg, 'WN', 2)
                    if pt == 'Y':
                        cnt_2 += 1
                        coord = self.get_coord(coord_arg, 'WN', 2)
                        coord_list.append(coord)
                        pt = self.check_point(coord_arg, 'WN', 3)
                        if pt == 'Y':
                            cnt_2 += 1
                            coord = self.get_coord(coord_arg, 'WN', 3)
                            coord_list.append(coord)
                            pt = self.check_point(coord_arg, 'WN', 4)
                            if pt == 'Y':
                                cnt_2 += 1
                                coord = self.get_coord(coord_arg, 'WN', 4)
                                coord_list.append(coord)
                # ---^_^---
                cnt = cnt_1 + cnt_2 + 1
                
                if cnt == 3:
                    if cnt_1 == 1 and cnt_2 == 1:
                        # 生成一个My3类型
                        coord_tuple = tuple(coord_list)
                        obj = self.My3(coord_tuple, 'WN', None, None)
                        self.update_MP(obj)

                        if obj.attr == 'W' and obj.other == 'WW':
                            ret_dict['WW'] = 1      #特殊处理

                        if ret_dict.has_key(obj.attr):
                            ret_dict[obj.attr] += 1
                        else:
                            ret_dict[obj.attr] = 1
                elif cnt == 2:  
                    #生成一个My2类型
                    coord_tuple = tuple(coord_list)
                    obj = self.My2(coord_tuple, 'WN', None, None)
                    self.update_MP(obj)
                    if obj.attr == 'W' and obj.other == 'WW':
                        ret_dict['WW'] = 1      #特殊处理

                    if ret_dict.has_key(obj.attr):
                        ret_dict[obj.attr] += 1
                    else:
                        ret_dict[obj.attr] = 1
                else:       
                    # 只考虑cnt为2和3的情况, 忽略其他
                    None


        else:
            None

        self.matrix[coord_arg[1]][coord_arg[0]] = 0         #还原

        if len(ret_dict) == 0:
            return None
        else:
            return ret_dict
        
    def settle(self, My_update=True, Peer_update=True):
        '''
        self.last_peer_coord 一定存在
        '''
        if self.last_my_coord == None:
            # 敌方的第一枚棋子，也是全盘的第一枚
            ret = self.prase_point(self.last_peer_coord, self.Peer_point)
            list_dirs = list(ret[1])
            self.dict_point[self.last_peer_coord] = ['F', self.Peer_point, list_dirs]
        else:
            if My_update == True:
                # 先分析我方
                ret = self.prase_point(self.last_my_coord, self.My_point)
                list_dirs = list(ret[1])

                # print "prase_point, my: " + ret[0] 
                if ret[0] == 'F':   #自由之身，说明周边至少有一个空格
                    self.dict_point[self.last_my_coord] = ['F', self.My_point, list_dirs]
                elif ret[0] == 'D': #死棋子
                    self.dict_point[self.last_my_coord] = ['D', self.My_point, list_dirs]
                elif ret[0] == 'U':     #联合队友
                    self.dict_point[self.last_my_coord] = ['U', self.My_point, list_dirs]

                    # coord_list = []
                    N=0; NE=1; E=2; ES=3; S=4; SW=5; W=6; WN=7

                    if list_dirs[N] == 'Y' or list_dirs[S] == 'Y':  # 上下方向 |
                        coord_list = []
                        cnt_1 = 0; cnt_2 = 0
                        if list_dirs[N] == 'Y':
                            cnt_1 += 1
                            pt = self.check_point(self.last_my_coord, 'N', 2)
                            if pt == 'Y':
                                cnt_1 += 1
                                pt = self.check_point(self.last_my_coord, 'N', 3)
                                if pt == 'Y':
                                    cnt_1 += 1
                                    pt = self.check_point(self.last_my_coord, 'N', 4)
                                    if pt == 'Y':
                                        cnt_1 += 1
                                        coord = self.get_coord(self.last_my_coord, 'N', 4)
                                        coord_list.append(coord)
                                    coord = self.get_coord(self.last_my_coord, 'N', 3)
                                    coord_list.append(coord)
                                coord = self.get_coord(self.last_my_coord, 'N', 2)
                                coord_list.append(coord)
                            coord = self.get_coord(self.last_my_coord, 'N', 1)
                            coord_list.append(coord)
                        # ---^_^---
                        coord_list.append(self.last_my_coord)   #别忘了自己
                        # ---^_^---
                        if list_dirs[S] == 'Y':
                            cnt_2 += 1
                            coord = self.get_coord(self.last_my_coord, 'S', 1)
                            coord_list.append(coord)
                            pt = self.check_point(self.last_my_coord, 'S', 2)
                            if pt == 'Y':
                                cnt_2 += 1
                                coord = self.get_coord(self.last_my_coord, 'S', 2)
                                coord_list.append(coord)
                                pt = self.check_point(self.last_my_coord, 'S', 3)
                                if pt == 'Y':
                                    cnt_2 += 1
                                    coord = self.get_coord(self.last_my_coord, 'S', 3)
                                    coord_list.append(coord)
                                    pt = self.check_point(self.last_my_coord, 'S', 4)
                                    if pt == 'Y':
                                        cnt_2 += 1
                                        coord = self.get_coord(self.last_my_coord, 'S', 4)
                                        coord_list.append(coord)
                        # ---^_^---
                        cnt = cnt_1 + cnt_2 + 1
                        if cnt == 4:
                            # 生成一个My4类型
                            coord_tuple = tuple(coord_list)
                            my4 = self.My4(coord_tuple, 'S')
                            self.M_index[4].append(my4)
                            self.update_MP(my4)
                            self.M_Attr[my4.attr].append(my4) 
                            # print "Create new My4: S|"

                            if cnt_1 == 0 or cnt_2 == 0: #说明肯定有一个my3类型, 删除它
                                if coord_tuple[0] != self.last_my_coord:
                                    coord = coord_tuple[0]
                                else:
                                    coord = coord_tuple[1]

                                my3 = self.search_MyX(3, coord, 'S')
                                if my3:
                                    # print "Delete My3: " + str(coord) + "-->" + 'S'
                                    self.M_Attr[my3.attr].remove(my3)
                                    self.M_index[3].remove(my3)
                            else:   # 1+2/2+1组合
                                if cnt_1 == 1:
                                    coord = coord_tuple[2]
                                else:
                                    coord = coord_tuple[0]

                                my2 = self.search_MyX(2, coord, 'S')
                                if my2:
                                    # print "Delete My2: " + str(coord) + "-->" + 'S'
                                    self.M_Attr[my2.attr].remove(my2)
                                    self.M_index[2].remove(my2)
                        elif cnt == 3:
                            # 生成一个My3类型
                            coord_tuple = tuple(coord_list)
                            my3 = self.My3(coord_tuple, 'S', None, None)
                            self.M_index[3].append(my3)
                            self.update_MP(my3)
                            self.M_Attr[my3.attr].append(my3) 

                            if cnt_1 == 0 or cnt_2 == 0:    #说明肯定有一个my2类型, 删除它
                                if coord_tuple[0] != self.last_my_coord:
                                    coord = coord_tuple[0]
                                else:
                                    coord = coord_tuple[1]

                                my2 = self.search_MyX(2, coord, 'S')
                                if my2:
                                    # print "Delete My2: " + str(coord) + "-->" + 'S'
                                    self.M_Attr[my2.attr].remove(my2)
                                    self.M_index[2].remove(my2)
                        elif cnt == 2:
                            #生成一个My2类型
                            coord_tuple = tuple(coord_list)
                            my2 = self.My2(coord_tuple, 'S', None, None)
                            self.M_index[2].append(my2)
                            self.update_MP(my2)
                            self.M_Attr[my2.attr].append(my2)
                        else:
                            print "Something error, cnt: " + str(cnt)
                            None    #不应该发生
                        
                    if list_dirs[NE] == 'Y' or list_dirs[SW] == 'Y':    # 方向 /
                        # -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
                        coord_list = []
                        cnt_1 = 0; cnt_2 = 0
                        if list_dirs[NE] == 'Y':
                            cnt_1 += 1
                            pt = self.check_point(self.last_my_coord, 'NE', 2)
                            if pt == 'Y':
                                cnt_1 += 1
                                pt = self.check_point(self.last_my_coord, 'NE', 3)
                                if pt == 'Y':
                                    cnt_1 += 1
                                    pt = self.check_point(self.last_my_coord, 'NE', 4)
                                    if pt == 'Y':
                                        cnt_1 += 1
                                        coord = self.get_coord(self.last_my_coord, 'NE', 4)
                                        coord_list.append(coord)
                                    coord = self.get_coord(self.last_my_coord, 'NE', 3)
                                    coord_list.append(coord)
                                coord = self.get_coord(self.last_my_coord, 'NE', 2)
                                coord_list.append(coord)
                            coord = self.get_coord(self.last_my_coord, 'NE', 1)
                            coord_list.append(coord)

                        coord_list.append(self.last_my_coord)   #别忘了自己
                        # ---^_^---
                        if list_dirs[SW] == 'Y':
                            cnt_2 += 1
                            coord = self.get_coord(self.last_my_coord, 'SW', 1)
                            coord_list.append(coord)
                            pt = self.check_point(self.last_my_coord, 'SW', 2)
                            if pt == 'Y':
                                cnt_2 += 1
                                coord = self.get_coord(self.last_my_coord, 'SW', 2)
                                coord_list.append(coord)
                                pt = self.check_point(self.last_my_coord, 'SW', 3)
                                if pt == 'Y':
                                    cnt_2 += 1
                                    coord = self.get_coord(self.last_my_coord, 'SW', 3)
                                    coord_list.append(coord)
                                    pt = self.check_point(self.last_my_coord, 'SW', 4)
                                    if pt == 'Y':
                                        cnt_2 += 1
                                        coord = self.get_coord(self.last_my_coord, 'SW', 4)
                                        coord_list.append(coord)
                        # ---^_^---
                        cnt = cnt_1 + cnt_2 + 1
                        if cnt == 4:
                            # 生成一个My4类型
                            coord_tuple = tuple(coord_list)
                            my4 = self.My4(coord_tuple, 'SW')
                            self.M_index[4].append(my4)
                            self.update_MP(my4)
                            self.M_Attr[my4.attr].append(my4)

                            if cnt_1 == 0 or cnt_2 == 0: #说明肯定有一个my3类型, 删除它
                                if coord_tuple[0] != self.last_my_coord:
                                    coord = coord_tuple[0]
                                else:
                                    coord = coord_tuple[1]

                                my3 = self.search_MyX(3, coord, 'SW')
                                if my3:
                                    # print "Delete My3: " + str(coord) + "-->" + 'SW'
                                    self.M_Attr[my3.attr].remove(my3)
                                    self.M_index[3].remove(my3)
                            else:   # 1+2/2+1组合
                                if cnt_1 == 1:
                                    coord = coord_tuple[2]
                                else:
                                    coord = coord_tuple[0]

                                my2 = self.search_MyX(2, coord, 'SW')
                                if my2:
                                    # print "Delete My2: " + str(coord) + "-->" + 'SW'
                                    self.M_Attr[my2.attr].remove(my2)
                                    self.M_index[2].remove(my2)
                        elif cnt == 3:
                            # 生成一个My3类型
                            coord_tuple = tuple(coord_list)
                            my3 = self.My3(coord_tuple, 'SW', None, None)
                            self.M_index[3].append(my3)
                            self.update_MP(my3)
                            self.M_Attr[my3.attr].append(my3)

                            if cnt_1 == 0 or cnt_2 == 0:    #说明肯定有一个my2类型, 删除它
                                if coord_tuple[0] != self.last_my_coord:
                                    coord = coord_tuple[0]
                                else:
                                    coord = coord_tuple[1]

                                my2 = self.search_MyX(2, coord, 'SW')
                                if my2:
                                    # print "Delete My2: " + str(coord) + "-->" + 'SW'
                                    self.M_Attr[my2.attr].remove(my2)
                                    self.M_index[2].remove(my2)
                            
                        elif cnt == 2:  
                            #生成一个My2类型
                            coord_tuple = tuple(coord_list)
                            my2 = self.My2(coord_tuple, 'SW', None, None)
                            self.M_index[2].append(my2)
                            self.update_MP(my2)
                            self.M_Attr[my2.attr].append(my2) 
                        else:       
                            None    #不应该发生
                        # -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
                    if list_dirs[E] == 'Y' or list_dirs[W] == 'Y':    # 左右方向 —
                        # -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
                        coord_list = []
                        cnt_1 = 0; cnt_2 = 0
                        if list_dirs[E] == 'Y':
                            cnt_1 += 1
                            pt = self.check_point(self.last_my_coord, 'E', 2)
                            if pt == 'Y':
                                cnt_1 += 1
                                pt = self.check_point(self.last_my_coord, 'E', 3)
                                if pt == 'Y':
                                    cnt_1 += 1
                                    pt = self.check_point(self.last_my_coord, 'E', 4)
                                    if pt == 'Y':
                                        cnt_1 += 1
                                        coord = self.get_coord(self.last_my_coord, 'E', 4)
                                        coord_list.append(coord)
                                    coord = self.get_coord(self.last_my_coord, 'E', 3)
                                    coord_list.append(coord)
                                coord = self.get_coord(self.last_my_coord, 'E', 2)
                                coord_list.append(coord)
                            coord = self.get_coord(self.last_my_coord, 'E', 1)
                            coord_list.append(coord)

                        coord_list.append(self.last_my_coord)   #别忘了自己
                        # ---^_^---
                        if list_dirs[W] == 'Y':
                            cnt_2 += 1
                            coord = self.get_coord(self.last_my_coord, 'W', 1)
                            coord_list.append(coord)
                            pt = self.check_point(self.last_my_coord, 'W', 2)
                            if pt == 'Y':
                                cnt_2 += 1
                                coord = self.get_coord(self.last_my_coord, 'W', 2)
                                coord_list.append(coord)
                                pt = self.check_point(self.last_my_coord, 'W', 3)
                                if pt == 'Y':
                                    cnt_2 += 1
                                    coord = self.get_coord(self.last_my_coord, 'W', 3)
                                    coord_list.append(coord)
                                    pt = self.check_point(self.last_my_coord, 'W', 4)
                                    if pt == 'Y':
                                        cnt_2 += 1
                                        coord = self.get_coord(self.last_my_coord, 'W', 4)
                                        coord_list.append(coord)
                        # ---^_^---
                        cnt = cnt_1 + cnt_2 + 1
                        if cnt == 4:
                            # 生成一个My4类型
                            coord_tuple = tuple(coord_list)
                            my4 = self.My4(coord_tuple, 'W')
                            self.M_index[4].append(my4)
                            self.update_MP(my4)
                            self.M_Attr[my4.attr].append(my4) 
                            # print "Create new My4 W--"

                            if cnt_1 == 0 or cnt_2 == 0: #说明肯定有一个my3类型, 删除它
                                if coord_tuple[0] != self.last_my_coord:
                                    coord = coord_tuple[0]
                                else:
                                    coord = coord_tuple[1]

                                my3 = self.search_MyX(3, coord, 'W')
                                if my3:
                                    # print "Delete My3: " + str(coord) + "-->" + 'W'
                                    self.M_Attr[my3.attr].remove(my3)
                                    self.M_index[3].remove(my3)
                            else:   # 1+2/2+1组合
                                if cnt_1 == 1:
                                    coord = coord_tuple[2]
                                else:
                                    coord = coord_tuple[0]

                                my2 = self.search_MyX(2, coord, 'W')
                                if my2:
                                    # print "Delete My2: " + str(coord) + "-->" + 'W'
                                    self.M_Attr[my2.attr].remove(my2)
                                    self.M_index[2].remove(my2)
                        elif cnt == 3:
                            # 生成一个My3类型
                            coord_tuple = tuple(coord_list)
                            my3 = self.My3(coord_tuple, 'W', None, None)
                            self.M_index[3].append(my3)
                            self.update_MP(my3)
                            self.M_Attr[my3.attr].append(my3) 

                            if cnt_1 == 0 or cnt_2 == 0:    #说明肯定有一个my2类型, 删除它
                                if coord_tuple[0] != self.last_my_coord:
                                    coord = coord_tuple[0]
                                else:
                                    coord = coord_tuple[1]

                                my2 = self.search_MyX(2, coord, 'W')
                                if my2:
                                    # print "Delete My2: " + str(coord) + "-->" + 'W'
                                    self.M_Attr[my2.attr].remove(my2)
                                    self.M_index[2].remove(my2)
                            
                        elif cnt == 2:  
                            #生成一个My2类型
                            coord_tuple = tuple(coord_list)
                            my2 = self.My2(coord_tuple, 'W', None, None)
                            self.M_index[2].append(my2)
                            self.update_MP(my2)
                            self.M_Attr[my2.attr].append(my2)
                        else:       
                            print "Something error, cnt: " + str(cnt)
                            None    #不应该发生
                        # -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
                    if list_dirs[ES] == 'Y' or list_dirs[WN] == 'Y':    # 方向 \
                        # -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
                        coord_list = []
                        cnt_1 = 0; cnt_2 = 0
                        if list_dirs[ES] == 'Y':
                            cnt_1 += 1
                            pt = self.check_point(self.last_my_coord, 'ES', 2)
                            if pt == 'Y':
                                cnt_1 += 1
                                pt = self.check_point(self.last_my_coord, 'ES', 3)
                                if pt == 'Y':
                                    cnt_1 += 1
                                    pt = self.check_point(self.last_my_coord, 'ES', 4)
                                    if pt == 'Y':
                                        cnt_1 += 1
                                        coord = self.get_coord(self.last_my_coord, 'ES', 4)
                                        coord_list.append(coord)
                                    coord = self.get_coord(self.last_my_coord, 'ES', 3)
                                    coord_list.append(coord)
                                coord = self.get_coord(self.last_my_coord, 'ES', 2)
                                coord_list.append(coord)
                            coord = self.get_coord(self.last_my_coord, 'ES', 1)
                            coord_list.append(coord)
                        # ---^_^---
                        coord_list.append(self.last_my_coord)   #别忘了自己
                        # ---^_^---
                        if list_dirs[WN] == 'Y':
                            cnt_2 += 1
                            coord = self.get_coord(self.last_my_coord, 'WN', 1)
                            coord_list.append(coord)
                            pt = self.check_point(self.last_my_coord, 'WN', 2)
                            if pt == 'Y':
                                cnt_2 += 1
                                coord = self.get_coord(self.last_my_coord, 'WN', 2)
                                coord_list.append(coord)
                                pt = self.check_point(self.last_my_coord, 'WN', 3)
                                if pt == 'Y':
                                    cnt_2 += 1
                                    coord = self.get_coord(self.last_my_coord, 'WN', 3)
                                    coord_list.append(coord)
                                    pt = self.check_point(self.last_my_coord, 'WN', 4)
                                    if pt == 'Y':
                                        cnt_2 += 1
                                        coord = self.get_coord(self.last_my_coord, 'WN', 4)
                                        coord_list.append(coord)
                        # ---^_^---
                        cnt = cnt_1 + cnt_2 + 1
                        if cnt == 4:
                            # 生成一个My4类型
                            coord_tuple = tuple(coord_list)
                            my4 = self.My4(coord_tuple, 'WN')
                            self.M_index[4].append(my4)
                            self.update_MP(my4)
                            #M_Attr[xx]需要放在update_MP处理之后再添加
                            self.M_Attr[my4.attr].append(my4) 

                            if cnt_1 == 0 or cnt_2 == 0: #说明肯定有一个my3类型, 删除它
                                if coord_tuple[0] != self.last_my_coord:
                                    coord = coord_tuple[0]
                                else:
                                    coord = coord_tuple[1]

                                my3 = self.search_MyX(3, coord, 'WN')
                                if my3:
                                    # print "Delete My3: " + str(coord) + "-->" + 'WN'
                                    self.M_Attr[my3.attr].remove(my3)
                                    self.M_index[3].remove(my3)
                            else:   # 1+2/2+1组合
                                if cnt_1 == 1:
                                    coord = coord_tuple[2]
                                else:
                                    coord = coord_tuple[0]

                                my2 = self.search_MyX(2, coord, 'WN')
                                if my2:
                                    # print "Delete My2: " + str(coord) + "-->" + 'WN'
                                    self.M_Attr[my2.attr].remove(my2)
                                    self.M_index[2].remove(my2)
                        elif cnt == 3:
                            # 生成一个My3类型
                            coord_tuple = tuple(coord_list)
                            my3 = self.My3(coord_tuple, 'WN', None, None)
                            self.M_index[3].append(my3)
                            self.update_MP(my3)
                            self.M_Attr[my3.attr].append(my3) 

                            if cnt_1 == 0 or cnt_2 == 0:    #说明肯定有一个my2类型, 删除它
                                if coord_tuple[0] != self.last_my_coord:
                                    coord = coord_tuple[0]
                                else:
                                    coord = coord_tuple[1]

                                my2 = self.search_MyX(2, coord, 'WN')
                                if my2:
                                    # print "Delete My2: " + str(coord) + "-->" + 'WN'
                                    self.M_Attr[my2.attr].remove(my2)
                                    self.M_index[2].remove(my2)
                        elif cnt == 2:  
                            #生成一个My2类型
                            coord_tuple = tuple(coord_list)
                            my2 = self.My2(coord_tuple, 'WN', None, None)
                            self.M_index[2].append(my2)
                            self.update_MP(my2)
                            self.M_Attr[my2.attr].append(my2) 
                        else:       
                            None    #不应该发生
                        # -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
                        
                else:   #not F/D/U
                    None

            if Peer_update == True:
                # 再分析敌方
                ret = self.prase_point(self.last_peer_coord, self.Peer_point)
                list_dirs = list(ret[1])
                # print "prase_point, peer: " + ret[0] 
                if ret[0] == 'F':   #自由之身
                    self.dict_point[self.last_peer_coord] = ['F', self.Peer_point, list_dirs]
                elif ret[0] == 'D':     #死棋子
                    self.dict_point[self.last_peer_coord] = ['D', self.Peer_point, list_dirs]
                elif ret[0] == 'U':     #联合队友
                    self.dict_point[self.last_peer_coord] = ['U', self.Peer_point, list_dirs]

                    rnd = ret[1]
                    # coord_list = []

                    if rnd[0] == 'Y' or rnd[4] == 'Y':  # 上下方向 |
                        # -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
                        coord_list = []
                        cnt_1 = 0; cnt_2 = 0
                        if rnd[0] == 'Y':
                            cnt_1 += 1
                            pt = self.check_point(self.last_peer_coord, 'N', 2)
                            if pt == 'Y':
                                cnt_1 += 1
                                pt = self.check_point(self.last_peer_coord, 'N', 3)
                                if pt == 'Y':
                                    cnt_1 += 1
                                    pt = self.check_point(self.last_peer_coord, 'N', 4)
                                    if pt == 'Y':
                                        cnt_1 += 1
                                        coord = self.get_coord(self.last_peer_coord, 'N', 4)
                                        coord_list.append(coord)
                                    coord = self.get_coord(self.last_peer_coord, 'N', 3)
                                    coord_list.append(coord)
                                coord = self.get_coord(self.last_peer_coord, 'N', 2)
                                coord_list.append(coord)
                            coord = self.get_coord(self.last_peer_coord, 'N', 1)
                            coord_list.append(coord)

                        coord_list.append(self.last_peer_coord)   #别忘了自己
                        # ---^_^---
                        if rnd[4] == 'Y':
                            cnt_2 += 1
                            coord = self.get_coord(self.last_peer_coord, 'S', 1)
                            coord_list.append(coord)
                            pt = self.check_point(self.last_peer_coord, 'S', 2)
                            if pt == 'Y':
                                cnt_2 += 1
                                coord = self.get_coord(self.last_peer_coord, 'S', 2)
                                coord_list.append(coord)
                                pt = self.check_point(self.last_peer_coord, 'S', 3)
                                if pt == 'Y':
                                    cnt_2 += 1
                                    coord = self.get_coord(self.last_peer_coord, 'S', 3)
                                    coord_list.append(coord)
                                    pt = self.check_point(self.last_peer_coord, 'S', 4)
                                    if pt == 'Y':
                                        cnt_2 += 1
                                        coord = self.get_coord(self.last_peer_coord, 'S', 4)
                                        coord_list.append(coord)
                        # ---^_^---
                        cnt = cnt_1 + cnt_2 + 1
                        if cnt >= 5:        
                            #游戏结束
                            print "======Game Over!======"
                            return "GAME_OVER"
                        elif cnt == 4:
                            # 生成一个Peer4类型
                            coord_tuple = tuple(coord_list)
                            peer = self.Peer4(coord_tuple, 'S', None, None)
                            self.P_index[4].append(peer)
                            self.update_MP(peer)
                            self.P_Attr[peer.attr].append(peer)

                            if cnt_1 == 0 or cnt_2 == 0: #说明肯定有一个my3类型, 删除它
                                if coord_tuple[0] != self.last_peer_coord:
                                    coord = coord_tuple[0]
                                else:
                                    coord = coord_tuple[1]

                                peer = self.search_PeerX(3, coord, 'S')
                                if peer:
                                    # print "Delete Peer3: " + str(coord) + "-->" + 'S'
                                    self.P_Attr[peer.attr].remove(peer)
                                    self.P_index[3].remove(peer)
                            else:   # 1+2/2+1组合
                                if cnt_1 == 1:
                                    coord = coord_tuple[2]
                                else:
                                    coord = coord_tuple[0]

                                peer = self.search_PeerX(2, coord, 'S')
                                if peer:
                                    # print "Delete Peer2: " + str(coord) + "-->" + 'S'
                                    self.P_Attr[peer.attr].remove(peer)
                                    self.P_index[2].remove(peer)
                        elif cnt == 3:
                            # 生成一个Peer3类型
                            coord_tuple = tuple(coord_list)
                            peer = self.Peer3(coord_tuple, 'S', None, None)
                            self.P_index[3].append(peer)
                            self.update_MP(peer)
                            # print "peer.attr         " + peer.attr
                            self.P_Attr[peer.attr].append(peer)

                            if cnt_1 == 0 or cnt_2 == 0:    #说明肯定有一个my2类型, 删除它
                                if coord_tuple[0] != self.last_peer_coord:
                                    coord = coord_tuple[0]
                                else:
                                    coord = coord_tuple[1]

                                peer = self.search_PeerX(2, coord, 'S')
                                if peer:
                                    # print "Delete Peer2: " + str(coord) + "-->" + 'S'
                                    self.P_Attr[peer.attr].remove(peer)
                                    self.P_index[2].remove(peer)
                        elif cnt == 2:  
                            #生成一个Peer2类型
                            coord_tuple = tuple(coord_list)
                            peer = self.Peer2(coord_tuple, 'S', None, None)
                            self.P_index[2].append(peer)
                            self.update_MP(peer)
                            self.P_Attr[peer.attr].append(peer)
                        else:       
                            None    #不应该发生
                        # -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
                    if rnd[1] == 'Y' or rnd[5] == 'Y':    # 方向 /
                        # -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
                        coord_list = []
                        cnt_1 = 0; cnt_2 = 0
                        if rnd[1] == 'Y':
                            cnt_1 += 1
                            pt = self.check_point(self.last_peer_coord, 'NE', 2)
                            if pt == 'Y':
                                cnt_1 += 1
                                pt = self.check_point(self.last_peer_coord, 'NE', 3)
                                if pt == 'Y':
                                    cnt_1 += 1
                                    pt = self.check_point(self.last_peer_coord, 'NE', 4)
                                    if pt == 'Y':
                                        cnt_1 += 1
                                        coord = self.get_coord(self.last_peer_coord, 'NE', 4)
                                        coord_list.append(coord)
                                    coord = self.get_coord(self.last_peer_coord, 'NE', 3)
                                    coord_list.append(coord)
                                coord = self.get_coord(self.last_peer_coord, 'NE', 2)
                                coord_list.append(coord)
                            coord = self.get_coord(self.last_peer_coord, 'NE', 1)
                            coord_list.append(coord)

                        coord_list.append(self.last_peer_coord)   #别忘了自己
                        # ---^_^---
                        if rnd[5] == 'Y':
                            cnt_2 += 1
                            coord = self.get_coord(self.last_peer_coord, 'SW', 1)
                            coord_list.append(coord)
                            pt = self.check_point(self.last_peer_coord, 'SW', 2)
                            if pt == 'Y':
                                cnt_2 += 1
                                coord = self.get_coord(self.last_peer_coord, 'SW', 2)
                                coord_list.append(coord)
                                pt = self.check_point(self.last_peer_coord, 'SW', 3)
                                if pt == 'Y':
                                    cnt_2 += 1
                                    coord = self.get_coord(self.last_peer_coord, 'SW', 3)
                                    coord_list.append(coord)
                                    pt = self.check_point(self.last_peer_coord, 'SW', 4)
                                    if pt == 'Y':
                                        cnt_2 += 1
                                        coord = self.get_coord(self.last_peer_coord, 'SW', 4)
                                        coord_list.append(coord)
                        # ---^_^---
                        cnt = cnt_1 + cnt_2 + 1
                        if cnt >= 5:        
                            #游戏结束
                            print "======Game Over!======"
                            return "GAME_OVER"
                        elif cnt == 4:
                            # 生成一个Peer4类型
                            coord_tuple = tuple(coord_list)
                            peer = self.Peer4(coord_tuple, 'SW', None, None)
                            self.P_index[4].append(peer)
                            self.update_MP(peer)
                            self.P_Attr[peer.attr].append(peer)

                            if cnt_1 == 0 or cnt_2 == 0: #说明肯定有一个my3类型, 删除它
                                if coord_tuple[0] != self.last_peer_coord:
                                    coord = coord_tuple[0]
                                else:
                                    coord = coord_tuple[1]

                                peer = self.search_PeerX(3, coord, 'SW')
                                if peer:
                                    # print "Delete Peer3: " + str(coord) + "-->" + 'SW'
                                    self.P_Attr[peer.attr].remove(peer)
                                    self.P_index[3].remove(peer)
                            else:   # 1+2/2+1组合
                                if cnt_1 == 1:
                                    coord = coord_tuple[2]
                                else:
                                    coord = coord_tuple[0]

                                peer = self.search_PeerX(2, coord, 'SW')
                                if peer:
                                    # print "Delete Peer2: " + str(coord) + "-->" + 'SW'
                                    self.P_Attr[peer.attr].remove(peer)
                                    self.P_index[2].remove(peer)
                        elif cnt == 3:
                            # 生成一个Peer3类型
                            coord_tuple = tuple(coord_list)
                            peer = self.Peer3(coord_tuple, 'SW', None, None)
                            self.P_index[3].append(peer)
                            self.update_MP(peer)
                            self.P_Attr[peer.attr].append(peer)

                            if cnt_1 == 0 or cnt_2 == 0:    #说明肯定有一个peer2类型, 删除它
                                if coord_tuple[0] != self.last_peer_coord:
                                    coord = coord_tuple[0]
                                else:
                                    coord = coord_tuple[1]

                                peer = self.search_PeerX(2, coord, 'SW')
                                if peer:
                                    # print "Delete Peer2: " + str(coord) + "-->" + 'SW'
                                    self.P_Attr[peer.attr].remove(peer)
                                    self.P_index[2].remove(peer)
                        elif cnt == 2:  
                            #生成一个Peer2类型
                            coord_tuple = tuple(coord_list)
                            peer = self.Peer2(coord_tuple, 'SW', None, None)
                            self.P_index[2].append(peer)
                            self.update_MP(peer)
                            self.P_Attr[peer.attr].append(peer)
                        else:       
                            None    #不应该发生
                        # -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
                    if rnd[2] == 'Y' or rnd[6] == 'Y':    # 左右方向 —
                        # -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
                        coord_list = []
                        cnt_1 = 0; cnt_2 = 0
                        if rnd[2] == 'Y':
                            cnt_1 += 1
                            pt = self.check_point(self.last_peer_coord, 'E', 2)
                            if pt == 'Y':
                                cnt_1 += 1
                                pt = self.check_point(self.last_peer_coord, 'E', 3)
                                if pt == 'Y':
                                    cnt_1 += 1
                                    pt = self.check_point(self.last_peer_coord, 'E', 4)
                                    if pt == 'Y':
                                        cnt_1 += 1
                                        coord = self.get_coord(self.last_peer_coord, 'E', 4)
                                        coord_list.append(coord)
                                    coord = self.get_coord(self.last_peer_coord, 'E', 3)
                                    coord_list.append(coord)
                                coord = self.get_coord(self.last_peer_coord, 'E', 2)
                                coord_list.append(coord)
                            coord = self.get_coord(self.last_peer_coord, 'E', 1)
                            coord_list.append(coord)

                        coord_list.append(self.last_peer_coord)   #别忘了自己
                        # ---^_^---
                        if rnd[6] == 'Y':
                            cnt_2 += 1
                            coord = self.get_coord(self.last_peer_coord, 'W', 1)
                            coord_list.append(coord)
                            pt = self.check_point(self.last_peer_coord, 'W', 2)
                            if pt == 'Y':
                                cnt_2 += 1
                                coord = self.get_coord(self.last_peer_coord, 'W', 2)
                                coord_list.append(coord)
                                pt = self.check_point(self.last_peer_coord, 'W', 3)
                                if pt == 'Y':
                                    cnt_2 += 1
                                    coord = self.get_coord(self.last_peer_coord, 'W', 3)
                                    coord_list.append(coord)
                                    pt = self.check_point(self.last_peer_coord, 'W', 4)
                                    if pt == 'Y':
                                        cnt_2 += 1
                                        coord = self.get_coord(self.last_peer_coord, 'W', 4)
                                        coord_list.append(coord)
                        # ---^_^---
                        cnt = cnt_1 + cnt_2 + 1
                        # print "U...E&W: " + str(cnt) 
                        if cnt >= 5:        
                            #游戏结束
                            print "======Game Over!======"
                            return "GAME_OVER"
                        elif cnt == 4:
                            # 生成一个Peer4类型
                            coord_tuple = tuple(coord_list)
                            peer = self.Peer4(coord_tuple, 'W', None, None)
                            self.P_index[4].append(peer)
                            self.update_MP(peer)
                            self.P_Attr[peer.attr].append(peer)

                            if cnt_1 == 0 or cnt_2 == 0: #说明肯定有一个peer3类型, 删除它
                                if coord_tuple[0] != self.last_peer_coord:
                                    coord = coord_tuple[0]
                                else:
                                    coord = coord_tuple[1]

                                peer = self.search_PeerX(3, coord, 'W')
                                if peer:
                                    # print "Delete Peer3: " + str(coord) + "-->" + 'W'
                                    self.P_Attr[peer.attr].remove(peer)
                                    self.P_index[3].remove(peer)
                            else:   # 1+2/2+1组合
                                if cnt_1 == 1:
                                    coord = coord_tuple[2]
                                else:
                                    coord = coord_tuple[0]

                                peer = self.search_PeerX(2, coord, 'W')
                                if peer:
                                    # print "Delete Peer2: " + str(coord) + "-->" + 'W'
                                    self.P_Attr[peer.attr].remove(peer)
                                    self.P_index[2].remove(peer)
                        elif cnt == 3:
                            # 生成一个Peer3类型
                            coord_tuple = tuple(coord_list)
                            peer = self.Peer3(coord_tuple, 'W', None, None)
                            self.P_index[3].append(peer)
                            self.update_MP(peer)
                            self.P_Attr[peer.attr].append(peer)

                            if cnt_1 == 0 or cnt_2 == 0:    #说明肯定有一个peer2类型, 删除它
                                if coord_tuple[0] != self.last_peer_coord:
                                    coord = coord_tuple[0]
                                else:
                                    coord = coord_tuple[1]

                                peer = self.search_PeerX(2, coord, 'W')
                                if peer:
                                    # print "Delete Peer2: " + str(coord) + "-->" + 'W'
                                    self.P_Attr[peer.attr].remove(peer)
                                    self.P_index[2].remove(peer)
                            
                        elif cnt == 2:  
                            #生成一个Peer2类型
                            coord_tuple = tuple(coord_list)
                            peer = self.Peer2(coord_tuple, 'W', None, None)
                            self.P_index[2].append(peer)
                            self.update_MP(peer)
                            self.P_Attr[peer.attr].append(peer)
                        else:       
                            None    #不应该发生
                        # -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
                    if rnd[3] == 'Y' or rnd[7] == 'Y':    # 方向 \
                        # -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
                        coord_list = []
                        cnt_1 = 0; cnt_2 = 0
                        if rnd[3] == 'Y':
                            cnt_1 += 1
                            pt = self.check_point(self.last_peer_coord, 'ES', 2)
                            if pt == 'Y':
                                cnt_1 += 1
                                pt = self.check_point(self.last_peer_coord, 'ES', 3)
                                if pt == 'Y':
                                    cnt_1 += 1
                                    pt = self.check_point(self.last_peer_coord, 'ES', 4)
                                    if pt == 'Y':
                                        cnt_1 += 1
                                        coord = self.get_coord(self.last_peer_coord, 'ES', 4)
                                        coord_list.append(coord)
                                    coord = self.get_coord(self.last_peer_coord, 'ES', 3)
                                    coord_list.append(coord)
                                coord = self.get_coord(self.last_peer_coord, 'ES', 2)
                                coord_list.append(coord)
                            coord = self.get_coord(self.last_peer_coord, 'ES', 1)
                            coord_list.append(coord)

                        coord_list.append(self.last_peer_coord)   #别忘了自己
                        # ---^_^---
                        if rnd[7] == 'Y':
                            cnt_2 += 1
                            coord = self.get_coord(self.last_peer_coord, 'WN', 1)
                            coord_list.append(coord)
                            pt = self.check_point(self.last_peer_coord, 'WN', 2)
                            if pt == 'Y':
                                cnt_2 += 1
                                coord = self.get_coord(self.last_peer_coord, 'WN', 2)
                                coord_list.append(coord)
                                pt = self.check_point(self.last_peer_coord, 'WN', 3)
                                if pt == 'Y':
                                    cnt_2 += 1
                                    coord = self.get_coord(self.last_peer_coord, 'WN', 3)
                                    coord_list.append(coord)
                                    pt = self.check_point(self.last_peer_coord, 'WN', 4)
                                    if pt == 'Y':
                                        cnt_2 += 1
                                        coord = self.get_coord(self.last_peer_coord, 'WN', 4)
                                        coord_list.append(coord)
                        # ---^_^---
                        cnt = cnt_1 + cnt_2 + 1
                        if cnt >= 5:        
                            #游戏结束
                            print "======Game Over!======"
                            return "GAME_OVER"
                        elif cnt == 4:
                            # 生成一个Peer4类型
                            coord_tuple = tuple(coord_list)
                            peer = self.Peer4(coord_tuple, 'WN', None, None)
                            self.P_index[4].append(peer)
                            self.update_MP(peer)
                            self.P_Attr[peer.attr].append(peer)
                            
                            if cnt_1 == 0 or cnt_2 == 0: #说明肯定有一个peer3类型, 删除它
                                if coord_tuple[0] != self.last_peer_coord:
                                    coord = coord_tuple[0]
                                else:
                                    coord = coord_tuple[1]

                                peer = self.search_PeerX(3, coord, 'WN')
                                if peer:
                                    # print "Delete Peer3: " + str(coord) + "-->" + 'WN'
                                    self.P_Attr[peer.attr].remove(peer)
                                    self.P_index[3].remove(peer)
                            else:   # 1+2/2+1组合
                                if cnt_1 == 1:
                                    coord = coord_tuple[2]
                                else:
                                    coord = coord_tuple[0]

                                peer = self.search_PeerX(2, coord, 'WN')
                                if peer:
                                    # print "Delete Peer2: " + str(coord) + "-->" + 'WN'
                                    self.P_Attr[peer.attr].remove(peer)
                                    self.P_index[2].remove(peer)
                        elif cnt == 3:
                            # 生成一个Peer3类型
                            coord_tuple = tuple(coord_list)
                            peer = self.Peer3(coord_tuple, 'WN', None, None)
                            self.P_index[3].append(peer)
                            self.update_MP(peer)
                            self.P_Attr[peer.attr].append(peer)

                            if cnt_1 == 0 or cnt_2 == 0:    #说明肯定有一个peer2类型, 删除它
                                if coord_tuple[0] != self.last_peer_coord:
                                    coord = coord_tuple[0]
                                else:
                                    coord = coord_tuple[1]

                                peer = self.search_PeerX(2, coord, 'WN')
                                if peer:
                                    # print "Delete Peer2: " + str(coord) + "-->" + 'WN'
                                    self.P_Attr[peer.attr].remove(peer)
                                    self.P_index[2].remove(peer)
                        elif cnt == 2:  
                            #生成一个Peer2类型，另外要判断队友是否为Peer1类型，若是将其从相关列表中删除
                            coord_tuple = tuple(coord_list)
                            peer = self.Peer2(coord_tuple, 'WN', None, None)
                            self.P_index[2].append(peer)
                            self.update_MP(peer)
                            self.P_Attr[peer.attr].append(peer)
                        else:       
                            None    #不应该发生
                        # -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
                else:
                    None

            # 更新单坐标点字典
            if My_update == True:
                self.update_dict_pointS(self.last_my_coord)
            if Peer_update == True:
                self.update_dict_pointS(self.last_peer_coord)
            if My_update == True:
                self.update_cross(self.last_my_coord)
            if Peer_update == True:
                self.update_cross(self.last_peer_coord)

    # 判断新增的坐标是否影响了原来的类数据
    def update_cross(self, coord):
        for pos in range(2,5):
            for mp in self.M_index[pos]:
                if mp.rel_coords != None:
                    # for rel_coord in mp.rel_coords:   #这个注释保留着，跟下面的对比，显然下面的更简洁
                    #     if coord == rel_coord:
                    if coord in mp.rel_coords:
                        self.M_Attr[mp.attr].remove(mp)
                        self.update_MP(mp)
                        self.M_Attr[mp.attr].append(mp)

        for pos in range(2,5):
            for mp in self.P_index[pos]:
                if mp.rel_coords != None:
                    if coord in mp.rel_coords:
                        self.P_Attr[mp.attr].remove(mp)
                        self.update_MP(mp)
                        self.P_Attr[mp.attr].append(mp)

    def update_cross_back(self, coord):
        for pos in range(2,5):
            for mp in self.M_index[pos]:
                if mp.back_coords != None:
                    if coord in mp.back_coords:
                        self.M_Attr[mp.attr].remove(mp)
                        self.update_MP(mp)
                        self.M_Attr[mp.attr].append(mp)

        for pos in range(2,5):
            for mp in self.P_index[pos]:
                if mp.back_coords != None:
                    if coord in mp.back_coords:
                        self.P_Attr[mp.attr].remove(mp)
                        self.update_MP(mp)
                        self.P_Attr[mp.attr].append(mp)

    def thinking_maybe_MyWin(self):
        for mp in self.M_Attr['W']:
            return mp.attract_coords[0]
        
        return None

    def thinking_prevent_PeerWin(self):
        for mp in self.P_Attr['W']:
            #可能有多个位置，只能选择一个
            return mp.attract_coords[0] 
        return None

    def thinking_maybe_MyWin_Ready(self):
        for mp in self.M_Attr['ZW']:
            return mp.attract_coords[0]
        return None

    def Peer_LX_Check_MyWin(self, try_bool, crd_try):
        w_cnt = 0
        crd_block = 0

        for mp in self.M_Attr['W']:
            if mp.other == 'WW':
                w_cnt = 2
                break
            else:
                w_cnt += 1
                if crd_block == 0:
                    crd_block = mp.attract_coords[0]
                else:
                    if cmp(crd_block, mp.attract_coords[0]) == 0:
                        w_cnt -= 1

        # print "-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-"
        # print "w_cnt: " + str(w_cnt) + ", crd_block: " + str(crd_block) + ", crd_try: " + str(crd_try)
        # print "-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-"

        if w_cnt > 1:
            return "lose"
        elif w_cnt == 0:
            return "cont"
        else:
            if try_bool == True:
                if cmp(crd_block, crd_try) == 0:
                    return "cont"        
                else:
                    return "unknown"
        
        # 执行到这里说明我方有一个W，接下去看看对方有没有可以封堵的点且可以掌握主动权
        for mp in self.P_Attr['G']:
            if cmp(crd_block, mp.attract_coords[0]) == 0 or cmp(crd_block, mp.attract_coords[1]) == 0:
                return "cont"

        if len(self.M_Attr['ZW']) == 0:
            for mp in self.P_Attr['A+X']:
                for crd in mp.attract_coords:
                    if cmp(crd_block, crd) == 0:
                        return "cont"

            ret_dict = self.may_build_new(crd_block, self.Peer_point) 
            if ret_dict != None and ret_dict.has_key('ZW'):
                return "cont"
                
        return "unknown"

    def thinking_G_AX_Peer_associate(self, tier_max):
        #在对方W存在的情况下不应该进行G联想
        if len(self.P_Attr['W']) > 0:
            print "Something error @thinking_G_AX_Peer__associate for W"
            self.wrong_cnt += 20
            return True

        ret_str = self.Peer_LX_Check_MyWin(False, False)
        if ret_str == "lose":
            return None
        elif ret_str == "cont":
            None
        elif ret_str == "unknown":     #结果未知，代表不能直接赢
            return None

        self.Peer_LX_crd_tier_first = 2
        self.LX_Active = "Peer"

        ret = self.thinking_G_AX_Peer_Nest(2, tier_max)
        if self.associate_cnt != 0:
            self.LX_cnt_Total += self.associate_cnt
            print "======>@thinking__G_AX_Peer_Nest, LX_cnt: " + str(self.associate_cnt) + " LX_cnt_Total: " + str(self.LX_cnt_Total)
        self.associate_cnt = 0

        self.thinking_withdraw(2)

        return ret

    def Peer_May_have_2_GAX_cross(self, tier):
        for x in range(0, self.__SIDELENGTH):
            for y in range(0, self.__SIDELENGTH):
                if self.matrix[y][x] != 0:
                    continue
                flag = 0
                for mp in self.P_Attr['G']:
                    if cmp((x, y), mp.attract_coords[0]) == 0 or cmp((x, y), mp.attract_coords[1]) == 0:
                        flag = 1
                        break
                if flag == 0:
                    for mp in self.P_Attr['A+X']:
                        if flag == 1:
                            break
                        for crd in mp.attract_coords:
                            if cmp((x, y), crd) == 0:
                                flag = 1
                                break
                if flag == 0:
                    ret_dict = self.may_build_new((x, y), self.Peer_point)
                    if ret_dict != None:
                        if ret_dict.has_key('G') or ret_dict.has_key('A+X'):
                            flag = 1

                if flag == 0:       #还得判断单独一个点构成G和A+X的情况，例如1+Z+1
                    ret_dict = self.may_build_G_AX_special((x, y), self.Peer_point)
                    if ret_dict != None:
                        if ret_dict.has_key('G') or ret_dict.has_key('A+X'):
                            flag = 1
                
                # ---^_^---
                if flag == 1:
                    self.Peer_LX_Set((x, y), tier)
                    has_num = self.Peer_have_G_AX_cross()
                    if has_num > 1:
                        self.thinking_withdraw(tier)
                        print "===>Find crd_repeat_set: " + str(has_num) + "@Peer_May_have_2_GAX_cross, x:" + str(x) + ", y:" + str(y)
                        return ((x, y))
                    
                    self.thinking_withdraw(tier)

        return None

    def My_have_G_AX_cross(self):
        crd_tmp_set = set()
        crd_repeat_set = set()      #其长度即为交叉点个数
        # 1. 
        for mp in self.M_Attr['G']:
            coord = mp.attract_coords[0]
            if coord not in crd_tmp_set:
                crd_tmp_set.add(coord)
            else:       #发现交叉点
                crd_repeat_set.add(coord)
            coord = mp.attract_coords[1]
            if coord not in crd_tmp_set:
                crd_tmp_set.add(coord)
            else:       #发现交叉点
                crd_repeat_set.add(coord)
        # 2.
        ret_tmp = self.get_point_setByW(self.My_point)
        if len(ret_tmp) != 0:
            for crd_and_block in ret_tmp:
                coord = crd_and_block[0]
                if coord not in crd_tmp_set:
                    crd_tmp_set.add(coord)
                else:
                    crd_repeat_set.add(coord)
        # 3.
        for mp in self.M_Attr['A+X']:
            for coord in mp.attract_coords:
                if coord not in crd_tmp_set:
                    crd_tmp_set.add(coord)
                else:
                    crd_repeat_set.add(coord)
        # 4.
        ret_tmp = self.get_point_setByZW(self.My_point)
        if len(ret_tmp) != 0:
            for crd_and_block in ret_tmp:
                coord = crd_and_block[0]
                if coord not in crd_tmp_set:
                    crd_tmp_set.add(coord)
                else:
                    crd_repeat_set.add(coord)

        ret_num = len(crd_repeat_set)

        if ret_num > 1:
            print "===>Find My crd_repeat_set: " + str(ret_num)

        return ret_num

    def Peer_have_G_AX_cross(self):
        #判断对方G、A+X有几个交叉点， 0/1/2/3...
        crd_tmp_set = set()
        crd_repeat_set = set()      #其长度即为交叉点个数
        # 1. 
        for mp in self.P_Attr['G']:
            coord_peer = mp.attract_coords[0]
            if coord_peer not in crd_tmp_set:
                crd_tmp_set.add(coord_peer)
            else:       #发现交叉点
                crd_repeat_set.add(coord_peer)
            coord_peer = mp.attract_coords[1]
            if coord_peer not in crd_tmp_set:
                crd_tmp_set.add(coord_peer)
            else:       #发现交叉点
                crd_repeat_set.add(coord_peer)
        # 2.
        ret_tmp = self.get_point_setByW(self.Peer_point)
        if len(ret_tmp) != 0:
            for crd_and_block in ret_tmp:
                coord_peer = crd_and_block[0]
                if coord_peer not in crd_tmp_set:
                    crd_tmp_set.add(coord_peer)
                else:
                    crd_repeat_set.add(coord_peer)
        # 3.
        for mp in self.P_Attr['A+X']:
            for coord_peer in mp.attract_coords:
                if coord_peer not in crd_tmp_set:
                    crd_tmp_set.add(coord_peer)
                else:
                    crd_repeat_set.add(coord_peer)
        # 4.
        ret_tmp = self.get_point_setByZW(self.Peer_point)
        if len(ret_tmp) != 0:
            for crd_and_block in ret_tmp:
                coord_peer = crd_and_block[0]
                if coord_peer not in crd_tmp_set:
                    crd_tmp_set.add(coord_peer)
                else:
                    crd_repeat_set.add(coord_peer)

        ret_num = len(crd_repeat_set)

        if ret_num > 1:
            print "===>Find crd_repeat_set: " + str(ret_num)

        return ret_num

    def Peer_has_G_AX_cross(self):
        #找到对方G、A+X有交叉的情况
        crd_tmp_set = set()
        repeat_cnt = 0
        repeat_type = 0
        all_list = []
        think_list = []   #交叉点为第一个元素
        
        for mp in self.P_Attr['G']:
            coord_peer = mp.attract_coords[0]
            coord_block = mp.attract_coords[1]
            coord_block_tuple = (coord_block, )
            if coord_peer not in crd_tmp_set:
                # print "===>1  Add: " + str(coord_peer) + "-->" + str(coord_block_tuple)
                # all_list[(coord_peer, coord_block_tuple)] = True
                all_list.append((coord_peer, coord_block_tuple))
                crd_tmp_set.add(coord_peer)
            else:
                for tmp in all_list:
                    if cmp(coord_peer, tmp[0]) == 0:
                        if cmp(coord_block, tmp[1][0]) == 0:
                            #相同的两个点，当做一个点
                            break
                        else:       #找到交叉点
                            think_list.append(coord_peer)
                            think_list.append(coord_block)
                            think_list.append(tmp[1][0])
                            # print "repeat_type = 1 "
                            repeat_cnt = 1
                            repeat_type = 1
                            break
            
            # --^_^--
            if repeat_cnt == 1:
                break

            # --^_^--
            coord_peer = mp.attract_coords[1]
            coord_block = mp.attract_coords[0]
            coord_block_tuple = (coord_block, )
            if coord_peer not in crd_tmp_set:
                # all_list[(coord_peer, coord_block_tuple)] = True
                # print "===>2  Add: " + str(coord_peer) + "-->" + str(coord_block_tuple)
                all_list.append((coord_peer, coord_block_tuple))
                crd_tmp_set.add(coord_peer)
            else:
                for tmp in all_list:
                    if cmp(coord_peer, tmp[0]) == 0:
                        if cmp(coord_block, tmp[1][0]) == 0:
                            #相同的两个点，当做一个点
                            break
                        else:       #找到交叉点
                            think_list.append(coord_peer)
                            think_list.append(coord_block)
                            think_list.append(tmp[1][0])
                            # print "repeat_type = 1 "
                            repeat_cnt = 1
                            repeat_type = 1
                            break
            # --^_^--
            if repeat_cnt == 1:
                break

        if repeat_cnt == 0:
            ret_tmp = self.get_point_setByW(self.Peer_point)
            if len(ret_tmp) != 0:
                for crd_and_block in ret_tmp:
                    coord_peer = crd_and_block[0]
                    if coord_peer not in crd_tmp_set:
                        # all_list[(coord_peer, crd_and_block[1])] = True
                        # print "===>3  Add: " + str(coord_peer) + "-->" + str(crd_and_block[1])
                        all_list.append((coord_peer, crd_and_block[1]))
                        crd_tmp_set.add(coord_peer)
                    else:
                        for tmp in all_list:
                            if cmp(coord_peer, tmp[0]) == 0:
                                coord_block = crd_and_block[1][0]
                                if cmp(coord_block, tmp[1][0]) == 0:
                                    #相同的两个点，当做一个点
                                    break
                                else:   #找到交叉点
                                    think_list.append(coord_peer)
                                    think_list.append(coord_block)
                                    think_list.append(tmp[1][0])

                                    repeat_cnt = 1
                                    repeat_type = 2
                                    # print "repeat_type = 2 "
                                    break
                    if repeat_cnt == 1:
                        break
        
        if repeat_cnt == 0:
            # print "===>len of ...: " + str(len(self.P_Attr['A+X']))
            mistery_list = []
            for mp in self.P_Attr['A+X']:
                # print "mp...coords...(A+X): " + str(mp.coords)
                # print "mp...attract_coords...(A+X): " + str(mp.attract_coords)
                mistery_list.append(mp)
            
            # for mp in self.P_Attr['A+X']:     #★★★ 这里用这个结果有点奇怪，可能是下面的Peer_AX_To_ZW_Block函数更改了A+X相关的东西
            for mp in mistery_list:
                # print "mp(A+X): " + str(mp.coords)
                # print "mp(A+X): " + str(mp.attract_coords)
                # print "total(a+x): " + str(len(self.P_Attr['A+X']))
                for coord_peer in mp.attract_coords:
                    ret_tmp = self.Peer_AX_To_ZW_Block(coord_peer, 2)
                    if ret_tmp[0] == "OK":
                        if coord_peer not in crd_tmp_set:
                            # all_list[(coord_peer, ret_tmp[1])] = True
                            # print "===>4  Add: " + str(coord_peer) + "-->" + str(ret_tmp[1])
                            all_list.append((coord_peer, ret_tmp[1]))
                            crd_tmp_set.add(coord_peer)
                        else:
                            repeat_cnt = 1      #因为ZW的封堵点较多，所以....

                            repeat_type = 3
                            # print "repeat_type = 3 "
                            for tmp in all_list:
                                if cmp(coord_peer, tmp[0]) == 0:
                                    think_list.append(coord_peer)
                                    # print "===>think_list.append: " + str(coord_peer)
                                    for crd_tmp in ret_tmp[1]:
                                        think_list.append(crd_tmp)
                                        # print "===>think_list.append: " + str(crd_tmp)
                                    for crd_tmp in tmp[1]:
                                        think_list.append(crd_tmp)
                                        # print "===>think_list.append: " + str(crd_tmp)
                                    break
                            break
                    else:
                        print "Something error@Peer_has_G_AX_cross"
                if repeat_cnt == 1:
                    break

        if repeat_cnt == 0:
            ret_tmp = self.get_point_setByZW(self.Peer_point)
            if len(ret_tmp) != 0:
                for crd_and_block in ret_tmp:
                    coord_peer = crd_and_block[0]
                    if coord_peer not in crd_tmp_set:
                        # all_list[(coord_peer, crd_and_block[1])] = True
                        # print "===>5  Add: " + str(coord_peer) + "-->" + str(crd_and_block[1])
                        all_list.append((coord_peer, crd_and_block[1]))
                        crd_tmp_set.add(coord_peer)
                    else:
                        repeat_cnt = 1      #因为ZW的封堵点较多，所以....
                        repeat_type = 4
                        for tmp in all_list:
                            if cmp(coord_peer, tmp[0]) == 0:
                                think_list.append(coord_peer)
                                for crd_tmp in crd_and_block[1]:
                                    think_list.append(crd_tmp)
                                for crd_tmp in tmp[1]:
                                    think_list.append(crd_tmp)
                                break
                        break

        if repeat_cnt == 1:
            print "===>Peer_has_G_AX_cross, find repeat, type: " + str(repeat_type)
            # print "===>think_list: " + str(think_list)

        return (repeat_cnt, think_list)

    # step 6 of thinking
    def thinking_prevent_G_AX(self):
        ret_tmp = self.Peer_has_G_AX_cross()
        has = ret_tmp[0]
        if has == 1:
            think_list = ret_tmp[1]
            print "===>Step 6 will score_and_try: " + str(think_list)
            ret_tuple = self.score_and_try(think_list, "Step 6, thinking_prevent_G_AX")
            ret_crd = ret_tuple[1]
            #后续还可以看看是否能通过G联想，起死回生.....
            return ret_crd
        else:       #没有交叉点
            return None
    '''
    def thinking_prevent_G_AX(self):
        ret_tmp = self.Peer_has_G_AX_cross()
        has = ret_tmp[0]
        if has == 1:
            think_list = ret_tmp[1]


            total_cnt = len(think_list)
            try_cnt = 0

            # 需要对think_list进行高低分排序asdf
            pww_will_set = self.get_point_setByAttr_all_PWW()
            all_list = []   #成员也为list，list[0] 为分数, list[1]为coord, list[2]为二级分数
            for crd in think_list:
                pt = 0  #分数
                pt_2 = 0

                if crd in pww_will_set:
                    pt += 100

                num_tuple = self.get_pointNum_byAttr(crd, 'ZW', self.My_point)
                num = num_tuple[0]
                if num != 0:
                    pt += num*5
                    num_2 = num_tuple[1]
                    if num_2 != 0:
                        pt_2 += num_2

                num_tuple = self.get_pointNum_byAttr(crd, 'W', self.My_point)
                num = num_tuple[0]
                if num != 0:
                    pt += num*4
                    num_2 = num_tuple[1]
                    if num_2 != 0:
                        pt_2 += num_2

                num = self.get_pointNum_byAttr(crd, 'W', self.Peer_point)
                if num != 0:
                    pt += num*3

                num_tuple = self.get_pointNum_byAttr(crd, 'ZW', self.Peer_point)
                num = num_tuple[0]
                if num != 0:
                    pt += num*4
                    num_2 = num_tuple[1]
                    if num_2 != 0:
                        pt_2 += num_2

                g_will_num = self.get_num_ByNewAttrAndcoord('G', crd, self.My_point)
                if g_will_num != 0:
                    pt += g_will_num*2

                ax_will_num = self.get_num_ByNewAttrAndcoord('A+X', crd, self.My_point)
                if ax_will_num != 0:
                    pt += ax_will_num*2

                po_num = self.get_num_ByNewAttrAndcoord('G', crd, self.Peer_point)
                if po_num != 0:
                    pt += po_num*1

                all_list.append([pt, crd, pt_2])

            score_max_crd = {}

            while True:
                try_cnt += 1
                max_pt = 0
                max_pt_2 = 0
                ret_crd = None

                for crd_pt in all_list:
                    if try_cnt == 1:
                        print str(crd_pt[0]) + "." + str(crd_pt[2])  + " : " + str(crd_pt[1]) + "@Step 6: thinking_prevent_G_AX"
                    if crd_pt[0] > max_pt:
                        max_pt = crd_pt[0]
                        ret_crd = crd_pt[1]
                        max_pt_2 = crd_pt[2]
                        if try_cnt == 1:
                            score_max_crd = ret_crd
                    elif crd_pt[0] == max_pt:
                        if crd_pt[2] >= max_pt_2:       #这里用>=，因为零分也视为有效
                            max_pt = crd_pt[0]
                            ret_crd = crd_pt[1]
                            max_pt_2 = crd_pt[2]
                            if try_cnt == 1:
                                score_max_crd = ret_crd
                
                if ret_crd == None:
                    break
                # if cmp(ret_crd, (10, 11)) == 0:
                #     self.something_print = 1
                # else:
                #     self.something_print = 0
                self.My_LX_Set(ret_crd, 1)
                print "===>Try: " + str(ret_crd) + " @Step 6: thinking_prevent_G_AX"
                print "===>thinking__G_AX_Peer_associate@ thinking_prevent_G_AX"
                if self.thinking_G_AX_Peer_associate(6) != None:
                    self.thinking_withdraw(1)
                    all_list.remove([max_pt, ret_crd, max_pt_2])  #删除最高分
                    # self.something_print = 0
                    continue
                else:
                    self.thinking_withdraw(1)
                    # self.something_print = 0
                    print "===>thinking_prevent_G_AX, ret: " + str(ret_crd) + ", try:" + str(try_cnt) + "/" + str(total_cnt)
                    return ret_crd
            
            self.thinking_withdraw(1)
            print "====> I will lose...@thinking_prevent_G_AX, try_total: " + str(total_cnt)
            self.willdie_cnt += 1
            #执行到这里说明封堵对方的点联想之后，我方都会输，但是不封堵的话也输，只好封堵交叉点
            return think_list[0]    
            #后续还可以看看是否能通过G联想，起死回生.....
            
        else:       #没有交叉点
            return None
        '''

    
    def thinking_G_AX_PG_PAX_orig(self):
        '''
        cross_dict = {}

        #封堵对方G/G有交叉或G/A+X有交叉的情况
        for peer in self.P_Attr['G']:
            for crd in peer.attract_coords:
                if cross_dict.has_key(crd):
                    cross_dict[crd].append('G')
                else:
                    cross_dict[crd] = []
                    cross_dict[crd].append('G')

        if len(self.P_Attr['G']) > 0:
            for peer in self.P_Attr['A+X']:
                for crd in peer.attract_coords:
                    if cross_dict.has_key(crd):
                        cross_dict[crd].append('A+X')
                    else:
                        cross_dict[crd] = []
                        cross_dict[crd].append('A+X')
            
            for crd in cross_dict:
                if len(cross_dict[crd]) >= 2 and ('G' in cross_dict[crd]):
                    # 暂时只封堵交叉点，以后再考虑封堵哪个点合适
                    print "Peer G/A+X.........." + str(crd)
                    return crd      #封堵对方G/G有交叉或G/A+X有交叉的情况
                elif len(cross_dict[crd]) == 1 and cross_dict[crd][0] == 'G':
                    #还有一种情况需要考虑是G和1+Z+1/1+Z+Z+1的Z重叠的情况，这就需要进行模拟下子了
                    ret_dict = self.may_build_new(crd, self.Peer_point)
                    if ret_dict != None:
                        # if ret_dict.has_key('W'): 
                        #     print "WolfWolf..222..W..." + str(crd)
                        #     return crd 


                        if ret_dict.has_key('ZW'):
                            print "WolfWolf..222..ZW..." + str(crd)
                            return crd 
        #---^_^---
        print "thinking_G_AX_PG_PAX: step 1"
        '''
        '''
        cross_dict = {}
        #我方A+X和A+X有交叉的情况，这样我方就能构建两个ZW
        #可是我方下子后，对方有没有可能通过G直接赢？？？？？？？
        for mp in self.M_Attr['A+X']:
            for crd in mp.attract_coords:
                if cross_dict.has_key(crd):
                    cross_dict[crd].append(mp)
                else:
                    cross_dict[crd] = []
                    cross_dict[crd].append(mp) 
        for crd in cross_dict:
            if len(cross_dict[crd]) >= 2:
                print "WolfWolf...555...." + str(crd)
                return crd      
            elif len(cross_dict[crd]) == 1:
                ret_dict = self.may_build_new(crd, self.My_point)
                if ret_dict != None:
                    if ret_dict.has_key('W') or ret_dict.has_key('ZW'):
                        print "WolfWolf..666....." + str(crd)
                        return crd 
        print "thinking_G_AX_PG_PAX: step 2"
        '''
        #---^_^---
        '''
        cross_dict = {}
        #考虑我方A+X和O(即能构成G)的交叉点,交集
        zw_will_set = self.get_point_setByAttr_all('ZW', self.My_point)
        g_will_set = self.get_point_setByAttr_all('G', self.My_point)
        zw_g_will_set = zw_will_set & g_will_set    #交集

        for zw_g_crd in zw_g_will_set:   #能构成ZW+G组合的坐标
            self.thinking_withdraw(1)
            #我方模拟试探下子
            self.My_LX_Set(zw_g_crd, 1)

            #先看对方能否通过G直接赢， 如果可以就不要这么下
            print "===>thinking__G_AX_Peer_associate....@zw_g_will_set ..Total: " + str(len(zw_g_will_set))
            if self.thinking_G_AX_Peer_associate(6) != None:    #说明这么下对方会赢，所以不要这么下
                self.thinking_withdraw(1)
                continue

            #先记录对方可能的封堵点,然后对所有情况，我方都能通过G直接赢，那就这么下
            block_coord_list = []
            for mp in self.M_Attr['ZW']:
                class_name = mp.__class__.__name__
                if class_name == 'My2':
                    block_coord_list.append(mp.rel_coords[0])
                    block_coord_list.append(mp.rel_coords[1])
                    block_coord_list.append(mp.rel_coords[2])
                elif class_name == 'My3':
                    # block_coord_list.append(mp.attract_coords[0])
                    # block_coord_list.append(mp.attract_coords[1])
                    for attract_crd in mp.attract_coords:
                        block_coord_list.append(attract_crd)
                else:
                    None
                break   #有一个ZW就可以了，如果对方不封堵，那就输咯
            if len(block_coord_list) == 0:
                print "Something error @thinking_G_AX_PG_PAX 123"
                sys.exit()

            tmp_flag = 0
            for crd in block_coord_list:
                self.thinking_withdraw(2)
                #对方模拟下子
                self.Peer_LX_Set(crd, 2)
                # self.associate_crd_tier[2] = crd
                #看我方能否直接赢
                self.My_LX_crd_tier_first = 3
                self.LX_Active = "My"
                ret = self.thinking_G_AX_My_Nest(3, 5)
                self.thinking_withdraw(3)
                if ret != None:         #我方可以赢，继续下一个情况(猜测对方下子)分析
                    self.thinking_withdraw(2)
                    continue
                else:           #我方不能直接赢，继续下一个情况(我方假设下子)分析
                    self.thinking_withdraw(2)
                    tmp_flag = 1
                    break
            if tmp_flag == 0:   #说明我方下子后准赢
                self.thinking_withdraw(1)
                return zw_g_crd

        #---^_^---

        self.thinking_withdraw(1)       #2020.2.22添加，要注意是否有副作用
        '''
        #对方有两个A+X的情况
        '''
        print "thinking_G_AX_PG_PAX: step 3"
        cross_dict = {}
        for mp in self.P_Attr['A+X']:
            for crd in mp.attract_coords:
                if cross_dict.has_key(crd):
                    cross_dict[crd].append(mp)
                else:
                    cross_dict[crd] = []
                    cross_dict[crd].append(mp) 
        for crd in cross_dict:
            if len(cross_dict[crd]) >= 2:
                print "Peer...A+X/A+X...." + str(crd)
                return crd      
            elif len(cross_dict[crd]) == 1:
                ret_dict = self.may_build_new(crd, self.Peer_point)
                if ret_dict != None:
                    if ret_dict.has_key('W') or ret_dict.has_key('ZW'):
                        print "WolfWolf..qqq....." + str(crd)
                        return crd 
        '''
        
        #对方有A+X和O的交叉点，将会变成ZW+G的组合，我方不提前封堵就可能会输喔, 真的这样吗？

        #接下去进行打分操作吧！！！
        '''
        print "thinking_G_AX_PG_PAX: step 4"
        zw_will_set = self.get_point_setByAttr_all('ZW', self.My_point)
        # w_will_set = set()
        # for mp in self.M_Attr['G']:
        #     w_will_set.add(mp.attract_coords[0])
        #     w_will_set.add(mp.attract_coords[1])
        w_will_set = self.get_point_setByAttr_all('W', self.My_point)
        # pg_set = set()
        # for mp in self.P_Attr['G']:
        #     pg_set.add(mp.attract_coords[0])
        #     pg_set.add(mp.attract_coords[1])
        pg_set = self.get_point_setByAttr_all('W', self.Peer_point)
        pax_set = self.get_point_setByAttr_all('ZW', self.Peer_point)

        pww_will_set = self.get_point_setByAttr_all_PWW()

        local_print_debug = 0
        all_set = zw_will_set | w_will_set | pg_set | pax_set | pww_will_set  #取并集
        all_list = []   #成员也为list，list[0] 为分数, list[1]为coord
        for crd in all_set:
            pt = 0  #分数
            pt_2 = 0

            if crd in pww_will_set:
                pt += 100       #不封堵的话应该会输

            if crd in zw_will_set:
                num_tuple = self.get_pointNum_byAttr(crd, 'ZW', self.My_point)
                num = num_tuple[0]
                if num == 0:
                    print "num == 0!!!!!!!!! Error! 1"
                    sys.exit()
                if local_print_debug == 1:
                    print "crd:" + str(crd) + ", zw_will_set: +5*" + str(num)
                pt += num*5

                num_2 = num_tuple[1]
                if num_2 != 0:
                    if local_print_debug == 1:
                        print "crd:" + str(crd) + ", ! zw_will_set: +1*" + str(num_2)
                    pt_2 += num_2

            if crd in w_will_set:
                num_tuple = self.get_pointNum_byAttr(crd, 'W', self.My_point)
                num = num_tuple[0]
                if num == 0:
                    print "num == 0!!!!!!!!! Error! 2"
                    sys.exit()
                if local_print_debug == 1:
                    print "crd:" + str(crd) + ", w_will_set: +4*" + str(num)
                pt += num*4

                num_2 = num_tuple[1]
                if num_2 != 0:
                    if local_print_debug == 1:
                        print "crd:" + str(crd) + ", ! w_will_set: +1*" + str(num_2)
                    pt_2 += num_2

            if crd in pg_set:
                num = self.get_pointNum_byAttr(crd, 'W', self.Peer_point)
                if num == 0:
                    print "num == 0!!!!!!!!! Error! 3"
                    sys.exit()
                if local_print_debug == 1:
                    print "crd:" + str(crd) + ", pg_set: +3*" + str(num)
                pt += num*3
                
            if crd in pax_set:
                num_tuple = self.get_pointNum_byAttr(crd, 'ZW', self.Peer_point)
                num = num_tuple[0]
                if num == 0:
                    print "num == 0!!!!!!!!! Error! 4"
                    sys.exit()
                if local_print_debug == 1:
                    print "crd:" + str(crd) + ", pax_set: +4*" + str(num)
                pt += num*4
                
                num_2 = num_tuple[1]
                if num_2 != 0:
                    if local_print_debug == 1:
                        print "crd:" + str(crd) + ", ! pax_set_special: +1*" + str(num_2)
                    pt_2 += num_2

            g_will_num = self.get_num_ByNewAttrAndcoord('G', crd, self.My_point)
            if g_will_num != 0:
                if local_print_debug == 1:
                    print "crd:" + str(crd) + ", g_will: +2*" + str(g_will_num)
                pt += g_will_num*2

            ax_will_num = self.get_num_ByNewAttrAndcoord('A+X', crd, self.My_point)
            if ax_will_num != 0:
                if local_print_debug == 1:
                    print "crd:" + str(crd) + ", ax_will: +2*" + str(ax_will_num)
                pt += ax_will_num*2

            po_num = self.get_num_ByNewAttrAndcoord('G', crd, self.Peer_point)
            if po_num != 0:
                if local_print_debug == 1:
                    print "crd:" + str(crd) + ", po: +1*" + str(po_num)
                pt += po_num*1

            all_list.append([pt, crd, pt_2])

        #不考虑我方能直接赢的情况，但要考虑我方下子后对方能直接赢的情况

        # 为了让出牌速度快一点，这里可能需要加一个机制，若all_list长度太长的话，只判断前N个即可
        while_cnt = 0
        while_max = 10
        score_max_crd = {}

        self.dbg_list = []

        while True:
            max_pt = 0
            max_pt_2 = 0
            ret_crd = None

            while_cnt += 1

            # if while_cnt > while_max:       #试了N次也没用，从花费时间角度考虑就不继续了，返回一个最高分即可
            #     print "=====>I am 6, have no idea, but not 7..."
            #     self.thinking_withdraw(1)
            #     # return score_max_crd
            #     return None

            for crd_pt in all_list:
                
                # 开局特殊处理，我方后下情况
                if len(self.history_track['crd_list']) == 5 and self.history_track['start'] == 'Peer':
                    # 如果上下左右有三颗对方棋子，则不要填这里，相当于填坑
                    # print "-=-=-=-=-=-=-=-=-=-=-"
                    if self.special_fifth_maylose(crd_pt[1]) == True:
                        print "===>Discard special fifth, crd: " + str(crd_pt[1]) + ", score: " + str(crd_pt[0]) + "." + str(crd_pt[2]) 
                        continue

                print str(crd_pt[0]) + "." + str(crd_pt[2])  + " : " + str(crd_pt[1]) + "@thinking_G_AX_PG_PAX"
                if crd_pt[0] > max_pt:
                    max_pt = crd_pt[0]
                    ret_crd = crd_pt[1]
                    max_pt_2 = crd_pt[2]
                    if while_cnt == 1:
                        score_max_crd = ret_crd
                elif crd_pt[0] == max_pt:
                    if self.random_flag == 1:
                        random_num = random.randint(1,3)
                        if random_num == 1:
                            if crd_pt[2] > max_pt_2:
                                max_pt = crd_pt[0]
                                ret_crd = crd_pt[1]
                                max_pt_2 = crd_pt[2]
                                if while_cnt == 1:
                                    score_max_crd = ret_crd
                        else:
                            if crd_pt[2] >= max_pt_2:
                                max_pt = crd_pt[0]
                                ret_crd = crd_pt[1]
                                max_pt_2 = crd_pt[2]
                                if while_cnt == 1:
                                    score_max_crd = ret_crd
                    else:
                        if crd_pt[2] > max_pt_2:
                            max_pt = crd_pt[0]
                            ret_crd = crd_pt[1]
                            max_pt_2 = crd_pt[2]
                            if while_cnt == 1:
                                score_max_crd = ret_crd
            if ret_crd == None:
                break

            print "   "
            #我方模拟试探下子
            self.My_LX_Set(ret_crd, 1)

            print "===>thinking__G_AX_Peer_associate...@step4...True..., Total: " + str(len(all_list))
            if self.thinking_G_AX_Peer_associate(6) != None:
                #说明这么下对方会赢，所以不要这么下,去看看下一个分数最高的
                self.thinking_withdraw(1)
                all_list.remove([max_pt, ret_crd, max_pt_2])  #删除最高分
                print "Select next pt which is max. discard: " + str(ret_crd)
                if ret_crd not in self.dbg_list:
                    self.dbg_list.append(ret_crd)
                else:
                    self.dbg_cnt += 100

                continue
            else:
                self.thinking_withdraw(1)
                break
            
        if ret_crd != None:
            return ret_crd

        print "thinking_G_AX_PG_PAX: step 5(Nothing...)"
        '''
        return None

    # step 7 of thinking
    def thinking_others(self):
        all_list = []   #成员也为list，list[0] 为分数, list[1]为coord
        think_set = set()
        for x in range(0, self.__SIDELENGTH):
            for y in range(0, self.__SIDELENGTH):
                if self.matrix[y][x] != 0:
                    continue
                crd = (x, y)
                think_set.add(crd)  # 考虑所有空着的点
        if len(think_set) == 0:
            print "============ Game Over ======== Peace and Love !!"
            sys.exit()
        
        ret_tuple = self.score_and_try(think_set, "step 7, thinking_others")
        ret_crd = ret_tuple[1]

        return ret_crd
        

    def thinking_AX_G_PAX_PG(self):
        #接下去进行打分操作吧！！！
        local_print_debug = 0

        zw_will_set = self.get_point_setByAttr_all('ZW', self.My_point)
        w_will_set = self.get_point_setByAttr_all('W', self.My_point)
        pg_set = self.get_point_setByAttr_all('W', self.Peer_point)
        pax_set = self.get_point_setByAttr_all('ZW', self.Peer_point)
        pww_will_set = self.get_point_setByAttr_all_PWW()
        all_set = zw_will_set | w_will_set | pg_set | pax_set | pww_will_set  #取并集
        all_list = []   #成员也为list，list[0] 为分数, list[1]为coord
        for crd in all_set:
            pt = 0  #分数
            pt_2 = 0

            if crd in pww_will_set:
                pt += 100       #不封堵的话应该会输

            if crd in zw_will_set:
                num_tuple = self.get_pointNum_byAttr(crd, 'ZW', self.My_point)
                num = num_tuple[0]
                if num == 0:
                    print "num == 0!!!!!!!!! Error! 1"
                    sys.exit()
                if local_print_debug == 1:
                    print "crd:" + str(crd) + ", zw_will_set: +5*" + str(num)
                pt += num*5

                num_2 = num_tuple[1]
                if num_2 != 0:
                    if local_print_debug == 1:
                        print "crd:" + str(crd) + ", ! zw_will_set: +1*" + str(num_2)
                    pt_2 += num_2

            if crd in w_will_set:
                num_tuple = self.get_pointNum_byAttr(crd, 'W', self.My_point)
                num = num_tuple[0]
                if num == 0:
                    print "num == 0!!!!!!!!! Error! 2"
                    sys.exit()
                if local_print_debug == 1:
                    print "crd:" + str(crd) + ", w_will_set: +4*" + str(num)
                pt += num*4

                num_2 = num_tuple[1]
                if num_2 != 0:
                    if local_print_debug == 1:
                        print "crd:" + str(crd) + ", ! w_will_set: +1*" + str(num_2)
                    pt_2 += num_2

            if crd in pg_set:
                num = self.get_pointNum_byAttr(crd, 'W', self.Peer_point)
                if num == 0:
                    print "num == 0!!!!!!!!! Error! 3"
                    sys.exit()
                if local_print_debug == 1:
                    print "crd:" + str(crd) + ", pg_set: +3*" + str(num)
                pt += num*3
                
            if crd in pax_set:
                num_tuple = self.get_pointNum_byAttr(crd, 'ZW', self.Peer_point)
                num = num_tuple[0]
                if num == 0:
                    print "num == 0!!!!!!!!! Error! 4"
                    sys.exit()
                if local_print_debug == 1:
                    print "crd:" + str(crd) + ", pax_set: +4*" + str(num)
                pt += num*4
                
                num_2 = num_tuple[1]
                if num_2 != 0:
                    if local_print_debug == 1:
                        print "crd:" + str(crd) + ", ! pax_set_special: +1*" + str(num_2)
                    pt_2 += num_2

            # ------^_^------
            g_will_num = self.get_num_ByNewAttrAndcoord('G', crd, self.My_point)
            if g_will_num != 0:
                if local_print_debug == 1:
                    print "crd:" + str(crd) + ", g_will: +2*" + str(g_will_num)
                pt += g_will_num*2

            ax_will_num = self.get_num_ByNewAttrAndcoord('A+X', crd, self.My_point)
            if ax_will_num != 0:
                if local_print_debug == 1:
                    print "crd:" + str(crd) + ", ax_will: +2*" + str(ax_will_num)
                pt += ax_will_num*2

            po_num = self.get_num_ByNewAttrAndcoord('G', crd, self.Peer_point)
            if po_num != 0:
                if local_print_debug == 1:
                    print "crd:" + str(crd) + ", po: +1*" + str(po_num)
                pt += po_num*1

            all_list.append([pt, crd, pt_2])

        self.dbg_list = []
        total_cnt = len(all_list)
        try_cnt = 0
        try_max = 5
        score_max_crd = {}

        while True:
            try_cnt += 1

            # if try_cnt > try_max:     #最多尝试N次
            #     break

            max_pt = 0
            max_pt_2 = 0
            ret_crd = None

            for crd_pt in all_list:
                # 开局特殊处理，我方后下情况
                if len(self.history_track['crd_list']) == 5 and self.history_track['start'] == 'Peer':
                    # 如果上下左右有三颗对方棋子，则不要填这里，相当于填坑
                    if self.special_fifth_maylose(crd_pt[1]) == True:
                        continue

                if try_cnt == 1:
                    print str(crd_pt[0]) + "." + str(crd_pt[2])  + " : " + str(crd_pt[1]) + "@Step 7, thinking_AX_G_PAX_PG"
                if crd_pt[0] > max_pt:
                    max_pt = crd_pt[0]
                    ret_crd = crd_pt[1]
                    max_pt_2 = crd_pt[2]
                    if try_cnt == 1:
                        score_max_crd = ret_crd
                elif crd_pt[0] == max_pt:
                    if self.random_flag == 1:
                        random_num = random.randint(1,3)
                        if random_num == 1:
                            if crd_pt[2] > max_pt_2:
                                max_pt = crd_pt[0]
                                ret_crd = crd_pt[1]
                                max_pt_2 = crd_pt[2]
                                if try_cnt == 1:
                                    score_max_crd = ret_crd
                        else:
                            if crd_pt[2] >= max_pt_2:
                                max_pt = crd_pt[0]
                                ret_crd = crd_pt[1]
                                max_pt_2 = crd_pt[2]
                                if try_cnt == 1:
                                    score_max_crd = ret_crd
                    else:
                        if crd_pt[2] > max_pt_2:
                            max_pt = crd_pt[0]
                            ret_crd = crd_pt[1]
                            max_pt_2 = crd_pt[2]
                            if try_cnt == 1:
                                score_max_crd = ret_crd
            if ret_crd == None:
                break
            
            #我方模拟试探下子
            self.My_LX_Set(ret_crd, 1)
            print "===>Try: " + str(ret_crd) + " @Step 7: thinking_AX_G_PAX_PG"
            print "===>thinking__G_AX_Peer_associate@thinking_AX_G_PAX_PG..., Total: " + str(len(all_list))
            if self.thinking_G_AX_Peer_associate(6) != None:
                #说明这么下对方会赢，所以不要这么下,去看看下一个分数最高的
                self.thinking_withdraw(1)
                all_list.remove([max_pt, ret_crd, max_pt_2])  #删除最高分
                if ret_crd not in self.dbg_list:
                    self.dbg_list.append(ret_crd)
                else:
                    self.dbg_cnt += 1
                    print "=====Something warning@thinking_AX_G_PAX_PG..."
                continue
            else:
                self.thinking_withdraw(1)
                break
        
        if ret_crd != None:
            print "======>thinking_AX_G_PAX_PG: " + str(try_cnt) + "/" + str(total_cnt)
            return ret_crd
        else:
            return None

    def thinking_O_ZAX_PO_PZAX(self):
        g_will_set = self.get_point_setByAttr_all('G', self.My_point)    
        ax_will_set = self.get_point_setByAttr_all('A+X', self.My_point)
        po_set = self.get_point_setByAttr_all('G', self.Peer_point)
        pzax_set = self.get_point_setByAttr_all('A+X', self.Peer_point)

        all_set = g_will_set | ax_will_set | po_set |  pzax_set
        all_list = []
        for crd in all_set:
            pt = 0
            if crd in g_will_set:
                num = self.get_pointNum_byAttr(crd, 'G', self.My_point)
                pt += num*2
            if crd in ax_will_set:
                num = self.get_pointNum_byAttr(crd, 'A+X', self.My_point)
                pt += num*2
            if crd in po_set:
                num = self.get_pointNum_byAttr(crd, 'G', self.Peer_point)
                pt += num*1
            if crd in pzax_set:
                num = self.get_pointNum_byAttr(crd, 'A+X', self.Peer_point)
                pt += num*1
            all_list.append([pt, crd])

        # 为了让出牌速度快一点，这里可能需要加一个机制，若all_list长度太长的话，只判断前N个即可
        total_cnt = len(all_list)
        try_cnt = 0
        try_max = 10
        score_max_crd = {}

        while True:
            try_cnt += 1

            # if try_cnt > try_max:
            #     ret_crd = score_max_crd
            #     break

            max_pt = 0
            ret_crd = None
            for crd_pt in all_list:
                if try_cnt == 1:
                    print str(crd_pt[0]) + ": " + str(crd_pt[1]) + "@Step 8: thinking_O_ZAX_PO_PZAX"
                if crd_pt[0] > max_pt:
                    max_pt = crd_pt[0]
                    ret_crd = crd_pt[1]
                    if try_cnt == 1:            #记住最高分，无奈之下才用
                        score_max_crd = ret_crd
                    
            if ret_crd == None:
                break
            #我方模拟试探下子
            self.My_LX_Set(ret_crd, 1)
            print "===>Try: " + str(ret_crd) + " @Step 8: thinking_O_ZAX_PO_PZAX"
            print "===>thinking__G_AX_Peer_associate...@thinking_O_ZAX_PO_PZAX..., len: " + str(len(all_list))
            if self.thinking_G_AX_Peer_associate(6) != None:
                #说明这么下对方会赢，所以不要这么下,去看看下一个分数最高的
                self.thinking_withdraw(1)
                all_list.remove([max_pt, ret_crd])  #删除最高分
                if ret_crd not in self.dbg_list:
                    self.dbg_list.append(ret_crd)
                else:
                    self.dbg_cnt += 1
                    print "=====Something warning@thinking_O_ZAX_PO_PZAX..."
                continue
            else:
                self.thinking_withdraw(1)
                break
            
        if ret_crd != None:
            print "======>thinking_O_ZAX_PO_PZAX: " + str(try_cnt) + "/" + str(total_cnt)
            return ret_crd
        else:
            return None
        

    def My_LX_Check_PeerWin(self, crd_try):
        w_cnt = 0
        crd_block = 0
        
        for mp in self.P_Attr['W']:
            if mp.other == 'WW':    
                w_cnt = 2
                break
            else:
                w_cnt += 1
                if crd_block == 0:
                    crd_block = mp.attract_coords[0]
                else:
                    if cmp(crd_block, mp.attract_coords[0]) == 0:
                        w_cnt -= 1  #当对方两个W的封堵点是同一个时，视为一个W

        if w_cnt > 1:       #说明这么下会输
            return "lose"
        elif w_cnt == 0:
            return "cont"            #对方没有W的情况，继续往下走
        else:       # == 1 的情况
            if cmp(crd_block, crd_try) == 0:
                return "cont"        #封堵对方的点正是我方G/A+X内，就继续往下走
            else:
                return "unknown"

    # 我方联想下子
    def My_LX_Set(self, coord, tier, lx_active=0):  #lx_active, 1表示主动，2表示被动，0表示不关心
        if lx_active == 1:
            if len(self.associate_point) > 0:
                last_handle = self.associate_point[-1]
                tier_last = last_handle[1]
                if (tier_last+1) == tier:
                    None
                else:
                    self.warning += 100
                    print "==============>Something error 1 @My_LX_Set"
        elif lx_active == 2:
            if len(self.associate_point) > 0:
                last_handle = self.associate_point[-1]
                tier_last = last_handle[1]
                active_last = last_handle[2]
                if tier_last == tier and active_last == 1:
                    None
                else:
                    self.warning += 100
                    print "==============>Something error 2 @My_LX_Set"
            else:
                self.warning += 100
                print "==============>Something error 3 @My_LX_Set"
    
        self.set_my_point(coord, 1)        #我方下
        self.associate_point.append((coord, tier, lx_active))
        self.settle(True, False)
        if lx_active == 1:
            self.My_LX_crd_tier[tier] = coord
        
                

    def Peer_LX_Set(self, coord_peer, tier, lx_active=0):
        if lx_active == 1:
            if len(self.associate_point) > 0:
                last_handle = self.associate_point[-1]
                tier_last = last_handle[1]
                if (tier_last+1) == tier:
                    None
                else:
                    self.warning += 100
                    print "==============>Something error 1 @Peer_LX_Set"
        elif lx_active == 2:
            if len(self.associate_point) > 0:
                last_handle = self.associate_point[-1]
                tier_last = last_handle[1]
                active_last = last_handle[2]
                if tier_last == tier and active_last == 1:
                    None
                else:
                    self.warning += 100
                    print "==============>Something error 2 @Peer_LX_Set"
            else:
                self.warning += 100
                print "==============>Something error 3 @Peer_LX_Set"
                
        self.set_peer_point(coord_peer, 1)            #对方下
        self.associate_point.append((coord_peer, tier, lx_active))
        self.settle(False, True)                #整理
        if lx_active == 1:
            self.Peer_LX_crd_tier[tier] = coord_peer
                

    '''
    def My_AX_To_ZW_Block(self, coord, tier):
        self.My_LX_Set(coord, tier)             #我方下

        zw_cnt = 0
        crd_block_tuple = ()
        for mp in self.M_Attr['ZW']:
            if coord in mp.coords:
                zw_cnt += 1
                for crd_block in mp.attract_coords:
                    if crd_block not in crd_block_tuple:    #防止重复
                        crd_block_tuple += (crd_block, )
                continue

            if hasattr(mp, "back_coords") and isinstance(mp.back_coords, list) and coord in mp.back_coords:
                zw_cnt += 1
                class_name = mp.__class__.__name__
                if class_name == 'My3':
                    for crd_block in mp.attract_coords:
                        if crd_block not in crd_block_tuple:    #防止重复
                            crd_block_tuple += (crd_block, )
                else:
                    for crd_block in mp.rel_coords:
                        if crd_block not in crd_block_tuple:    #防止重复
                            crd_block_tuple += (crd_block, )

                continue

        self.thinking_withdraw(tier)        #还原

        ret1 = ""
        ret2 = None
        if zw_cnt >= 1:
            ret1 = "OK"
            ret2 = crd_block_tuple
        else:
            ret1 = "Error"

        return (ret1, ret2)
    '''

    # 2020.3.11 修改
    def My_AX_To_ZW_Block(self, coord, tier):
        self.My_LX_Set(coord, tier)             #我方下

        zw_cnt = 0
        crd_block_tuple = ()
        for mp in self.M_Attr['ZW']:        
            if coord in mp.coords:          
                zw_cnt += 1
                class_name = mp.__class__.__name__
                if class_name == 'My3' and mp.other == 1:
                    for crd_block in mp.attract_coords:
                        if crd_block not in crd_block_tuple:    #防止重复
                            crd_block_tuple += (crd_block, )
                    
                else:
                    for crd_block in mp.rel_coords:
                        if crd_block not in crd_block_tuple:    #防止重复
                            crd_block_tuple += (crd_block, )

                continue

            if hasattr(mp, "back_coords") and isinstance(mp.back_coords, list) and coord in mp.back_coords:
                zw_cnt += 1
                for crd_block in mp.rel_coords:
                    if crd_block not in crd_block_tuple:    #防止重复
                        crd_block_tuple += (crd_block, )

                continue

        self.thinking_withdraw(tier)        #还原

        ret1 = ""
        ret2 = None
        if zw_cnt >= 1:
            ret1 = "OK"
            ret2 = crd_block_tuple
        else:
            ret1 = "Error"

        return (ret1, ret2)

    #对方可以由A+X变为ZW，找到形成ZW之后的封堵点 # 2020.3.11 修改
    def Peer_AX_To_ZW_Block(self, coord_peer, tier):
        self.Peer_LX_Set(coord_peer, tier)      #对方下

        #这时应该生成新的ZW，且包含coord_peer
        zw_cnt = 0
        crd_block_tuple = ()
        for mp in self.P_Attr['ZW']:
            if coord_peer in mp.coords:
                zw_cnt += 1
                class_name = mp.__class__.__name__
                if class_name == 'Peer3' and mp.other == 1:
                    for crd_block in mp.attract_coords:
                        if crd_block not in crd_block_tuple:    #防止重复
                            crd_block_tuple += (crd_block, )
                else:
                    for crd_block in mp.rel_coords:
                        if crd_block not in crd_block_tuple:    #防止重复
                            crd_block_tuple += (crd_block, )
                continue
            
            if hasattr(mp, "back_coords") and isinstance(mp.back_coords, list) and coord_peer in mp.back_coords:
                zw_cnt += 1
                for crd_block in mp.rel_coords:
                    if crd_block not in crd_block_tuple:    #防止重复
                        crd_block_tuple += (crd_block, )

                continue

        self.thinking_withdraw(tier)        #还原

        ret1 = ""
        ret2 = None
        if zw_cnt >= 1:
            ret1 = "OK"
            ret2 = crd_block_tuple
        else:
            ret1 = "Error"

        return (ret1, ret2)

    # 返回None表示对方没有可以通过G方式直接赢的
    # 后来发现不只是G，若对方有ZW，则也能掌握主动权
    def thinking_G_AX_Peer_Nest(self, tier, tier_max, tier_offset=0):
        local_print_debug = 0

        #这里可能也要考虑tier太大的情况，即嵌套太多，花费时间太多
        #或许当tier超过N级的时候认为对方不一定能完全有把握
        # if self.history_track['start'] == "My":
        #     #我方先下，进攻为主
        #     if tier > (6 + tier_offset):
        #         return None
        # else:
        #     #我方后下，防守为主
        #     if tier > (7 + tier_offset):
        #         return None
        if tier > (tier_max + tier_offset):
            return None

        # Step 1: 先进行掌握主动权的坐标点的收集
        nest = {}
        nest_cont = 0
        crd_tmp_set = set()

        for mp in self.P_Attr['G']:
            coord_peer = mp.attract_coords[0]
            coord_block = mp.attract_coords[1]
            coord_block_tuple = (coord_block, )
            if coord_peer not in crd_tmp_set:
                nest[(coord_peer, coord_block_tuple)] = True
                crd_tmp_set.add(coord_peer)

            coord_peer = mp.attract_coords[1]
            coord_block = mp.attract_coords[0]
            coord_block_tuple = (coord_block, )
            if coord_peer not in crd_tmp_set:
                nest[(coord_peer, coord_block_tuple)] = True
                crd_tmp_set.add(coord_peer)


        # if len(self.M_Attr['ZW']) == 0:
        # if len(self.M_Attr['ZW']) == 0 and len(self.M_Attr['G']) == 0:
        if len(self.M_Attr['ZW']) == 0:
            w_will_set = self.get_point_setByAttr_all('W', self.My_point)
            if len(w_will_set) == 0:
                for mp in self.P_Attr['A+X']:
                    for coord_peer in mp.attract_coords:
                        ret_tmp = self.Peer_AX_To_ZW_Block(coord_peer, tier+1)
                        if ret_tmp[0] == "OK":
                            if coord_peer not in crd_tmp_set:
                                nest[(coord_peer, ret_tmp[1])] = True
                                crd_tmp_set.add(coord_peer)
                        else:
                            print "Something error@thinking__G_AX_Peer_Nest, 123, crd: " + str(crd)

                # 还得考虑1+1+1新生成ZW的情况, 但貌似消耗计算机资源太多
                ret_tmp = self.get_point_setByZW(self.Peer_point)
                if len(ret_tmp) != 0:
                    for crd_and_block in ret_tmp:
                        coord_peer = crd_and_block[0]
                        if coord_peer not in crd_tmp_set:
                            nest[(coord_peer, crd_and_block[1])] = True
                            crd_tmp_set.add(coord_peer)

        if self.something_print == 1:
            if tier == 2:
                print "===>something_print: " + str(nest)


        if len(nest) != 0:
            # if tier <= (self.Peer_LX_crd_tier_first + 1):
            #     print "===> Peer G/A+X nest...tier: " + str(tier) + ", len_nest: " + str(len(nest))

            out_for_cnt = 0

            for pair in nest:
                coord_peer = pair[0]
                must_cnt = len(pair[1])     #必须全部封堵点满足才行
                can_cnt = 0                 #满足一次 +1

                if tier > self.Peer_LX_crd_tier_first:
                    crd_last = self.Peer_LX_crd_tier[tier-1]
                    if self.check_distance_long(coord_peer, crd_last) == True:
                        continue            #太远了，略过

                if self.something_print == 1:
                    if tier == 2 and cmp(coord_peer, (11, 8)) == 0:
                        print "===>something_print 123, must_cnt: " + str(must_cnt)

                out_for_cnt += 1

                if out_for_cnt > 1:
                    self.thinking_withdraw(tier)

                # ^_^
                ret_str = self.Peer_LX_Check_MyWin(True, coord_peer)
                
                if ret_str == "lose":
                    return None
                elif ret_str == "cont":
                    None
                elif ret_str == "unknown":
                    continue

                if self.something_print == 1:
                    if tier == 2 and cmp(coord_peer, (11, 8)) == 0:
                        print "===>something_print 234, pair[1]: " + str(pair[1])

                for coord_block in pair[1]:
                    nest_cont = 0
                    # 先进行上一次循环的悔棋操作
                    self.thinking_withdraw(tier)

                    # ret_str = self.Peer_LX_Check_MyWin(True, coord_peer)
                    # if ret_str == "lose":
                    #     return None
                    # elif ret_str == "cont":
                    #     None
                    # elif ret_str == "unknown":
                    #     break

                    if self.something_print == 1:
                        if tier == 2 and cmp(coord_peer, (11, 8)) == 0:
                            print "===>something_print 345, coord_block: " + str(coord_block)
                    self.Peer_LX_Set(coord_peer, tier, 1)          #对方下
                    self.My_LX_Set(coord_block, tier, 2)         #我方下
                    self.associate_cnt += 1

                    
                    #查看对方有没有W，若有直接返回
                    # if len(self.P_Attr['W']) > 0:
                    if len(self.P_Attr['W']) > 0 or ( len(self.P_Attr['ZW']) > 0 and len(self.M_Attr['W']) == 0):
                        can_cnt += 1
                        if can_cnt >= must_cnt:
                            self.thinking_withdraw(tier)
                            if must_cnt > 1:
                                if self.LX_Active == "Peer":        #避免反复嵌套联想
                                    self.Peer_LX_Set(coord_peer, tier)          #对方下
                                    self.My_LX_crd_tier_first = tier + 1
                                    ret = self.thinking_G_AX_My_Nest(tier+1, 5, tier)
                                    self.thinking_withdraw(tier+1)
                                    self.thinking_withdraw(tier)

                                    if ret != None:     #对方可能赢，但是下了后却是我方翻盘的好戏
                                        break
                                    else:           #对方能赢且我方不能赢的情况
                                        return coord_peer
                                else:
                                    print "========>Something error, LX_Active: " + self.LX_Active
                                    self.wrong_cnt += 10000
                                    return coord_peer
                            else:
                                return coord_peer
                        else:               # 成了一个，但革命尚未完全成功，同志仍需努力
                            continue

                        
                    #查看对方还有没有G的，若有再次进行嵌套
                    # print "===>Peer_Nest, tier: " + str(tier) + "===" + str(self.associate_point) 
                    if self.something_print == 1:
                        if tier == 2 and cmp(coord_peer, (11, 8)) == 0:
                            self.something_print2 = 1
                        else:
                            self.something_print2 = 0
                    else:
                        self.something_print2 = 0
                    ret = self.thinking_G_AX_Peer_Nest(tier+1, tier_max, tier_offset)
                    self.something_print2 = 0
                    self.thinking_withdraw(tier+1)  #联想撤回
                    if ret != None:
                        can_cnt += 1
                        if self.something_print == 1:
                            if tier == 2 and cmp(coord_peer, (11, 8)) == 0:
                                print "===>something_print, tier(2), can_cnt: " + str(can_cnt) + ", coord_block: " + str(coord_block)
                        if can_cnt >= must_cnt:
                            self.thinking_withdraw(tier)
                            if tier == 2 and cmp(coord_peer, (11, 8)) == 0:
                                print "===>something_print, tier(2), can_cnt>=mus_cnt: " + str(must_cnt)
                            if must_cnt > 1:
                                if self.LX_Active == "Peer":        #避免反复嵌套联想
                                    self.Peer_LX_Set(coord_peer, tier)          #对方下
                                    self.My_LX_crd_tier_first = tier + 1
                                    ret = self.thinking_G_AX_My_Nest(tier+1, 5, tier)
                                    self.thinking_withdraw(tier+1)
                                    self.thinking_withdraw(tier)

                                    if ret != None:     #对方可能赢，但是下了后却是我方翻盘的好戏
                                        if tier == 2 and cmp(coord_peer, (11, 8)) == 0:
                                            print "===>something_print, Something error! 555"
                                        break
                                    else:           #对方能赢且我方不能赢的情况
                                        return coord_peer
                                else:
                                    print "========>Something error, LX_Active: " + self.LX_Active
                                    self.wrong_cnt += 10000
                                    return coord_peer
                            else:
                                return coord_peer
                        else:
                            # 成了一个，但革命尚未完全成功，同志仍需努力
                            continue
                    else:
                        
                        break
        else:
            return None

        self.thinking_withdraw(tier)    #存疑
        
        return None

    # step 5 of thinking
    def thinking_prevent_PZW_associate(self):
        pzw_cnt = len(self.P_Attr['ZW'])

        if pzw_cnt > 1:     #对方有两个ZW，期待奇迹吧
            #一线生机，只能寄希望于G的再次联想功能，能让对方2个ZW变为1个ZW的
            self.My_LX_crd_tier_first = 1
            ret = self.thinking_G_My_prevent_2PZW_Nest(1)
            if self.associate_cnt != 0:
                self.LX_cnt_Total += self.associate_cnt
                print "===>@thinking_G_AX_My_associate, LX_cnt: " + str(self.associate_cnt) + " LX_cnt_Total: " + str(self.LX_cnt_Total)
                self.associate_cnt = 0
            self.thinking_withdraw(1)
            if ret != None:
                print "========== Magic !!! Peer 2ZW--may-->ZW ============"
                self.magicsmile_cnt += 1
                return ret
            else:
                self.willdie_cnt += 1
                print "==========Game will over, I lose! because Peer 2ZW, @thinking_prevent_PZW_associate...============"
                for crd in self.P_Attr['ZW'][0].attract_coords:
                    return crd      #一般来说，必死无疑，要死的有尊严，堵他
        elif pzw_cnt == 0:      #对方没有准赢的情况，也就不需要封堵
            return None
        else:
            None
        
        # --- ^_^: 收集封堵点
        point_dict = {}         #用字典，防止重复

        mp = self.P_Attr['ZW'][0]
        class_name = mp.__class__.__name__
        if class_name == 'Peer2':
            #注意这里用rel_coords而不是attract_coords, 封堵的点多一些
            for rel in mp.rel_coords:
                point_dict[rel] = True            
        else:   #Peer3
            for attract_coord in mp.attract_coords:
                point_dict[attract_coord] = True       

        print "===>Step 5 will score_and_try: " + str(point_dict)
        ret_tuple = self.score_and_try(point_dict, "Step 5, thinking_prevent_PZW_associate")
        ret_crd = ret_tuple[1]
        return ret_crd
        
            
    def score_and_try(self, crd_dict, dbg_info=""):
        # --- ^_^: 打分
        pww_will_set = self.get_point_setByAttr_all_PWW()
        all_list = []   #成员也为list，list[0] 为分数, list[1]为coord, list[2]为二级分数
        for crd in crd_dict:
            pt = 0  #分数
            pt_2 = 0

            # 不封堵我方就会输的那种， 如1+Z+1+Z+1+Z+1
            if crd in pww_will_set:
                pt += 100

            # 我方能构建ZW
            num_tuple = self.get_pointNum_byAttr(crd, 'ZW', self.My_point)
            num = num_tuple[0]
            if num != 0:
                pt += num*5
                num_2 = num_tuple[1]
                if num_2 != 0:
                    pt_2 += num_2

            # 我方能构建W
            num_tuple = self.get_pointNum_byAttr(crd, 'W', self.My_point)
            num = num_tuple[0]
            if num != 0:
                pt += num*4
                num_2 = num_tuple[1]
                if num_2 != 0:
                    pt_2 += num_2

            # 对方能构建W
            num_tuple = self.get_pointNum_byAttr(crd, 'W', self.Peer_point)
            num = num_tuple[0]
            if num != 0:
                pt += num*3
                num_2 = num_tuple[1]
                if num_2 != 0:
                    pt_2 += num_2

            # 对方能构建ZW
            num_tuple = self.get_pointNum_byAttr(crd, 'ZW', self.Peer_point)
            num = num_tuple[0]
            if num != 0:
                pt += num*4
                num_2 = num_tuple[1]
                if num_2 != 0:
                    pt_2 += num_2

            # 我方能构建G
            num = self.get_num_G_AX(crd, 'G', self.My_point)
            if num != 0:
                pt += num*2

            # 我方能构建A+X
            num = self.get_num_G_AX(crd, 'A+X', self.My_point)
            if num != 0:
                pt += num*2

                self.My_LX_Set(crd, 1)
                if self.My_have_G_AX_cross() > 1:
                    pt += 30
                    print "===>Try: " + str(crd) + " and My_have_G_AX_cross." 
                    self.willwin_cnt += 1
                self.thinking_withdraw(1)


            # 对方能构建G
            num = self.get_num_G_AX(crd, 'G', self.Peer_point)
            if num != 0:
                pt += num

            all_list.append([pt, crd, pt_2])
        # ---
        score_max_crd = {}
        total_cnt = len(all_list)
        try_cnt = 0

        while True:
            try_cnt += 1
            max_pt = 0
            max_pt_2 = 0
            ret_crd = None

            for crd_pt in all_list:
                if try_cnt == 1:
                    if crd_pt[0] != 0:
                        print str(crd_pt[0]) + "." + str(crd_pt[2])  + " : " + str(crd_pt[1]) + " @" + dbg_info
                if crd_pt[0] > max_pt:
                    max_pt = crd_pt[0]
                    ret_crd = crd_pt[1]
                    max_pt_2 = crd_pt[2]
                elif crd_pt[0] == max_pt:
                    if crd_pt[2] >= max_pt_2:       #这里用>=，因为零分也视为有效
                        max_pt = crd_pt[0]
                        ret_crd = crd_pt[1]
                        max_pt_2 = crd_pt[2]

            if ret_crd == None:
                break

            if try_cnt == 1:
                score_max_crd = ret_crd

            self.My_LX_Set(ret_crd, 1)

            # 我方不能形成两个G/AX交叉点，但对方能形成，则属于对方将赢的情况 --- 不知道是否严谨
            if self.My_have_G_AX_cross() <= 1 and self.Peer_May_have_2_GAX_cross(2) != None:
                print "===>Try : " + str(ret_crd) + ", but Peer_May_have_2_GAX_cross.."
                self.thinking_withdraw(1)
                all_list.remove([max_pt, ret_crd, max_pt_2])  #删除最高分
                continue

            print "===>Try : " + str(ret_crd) + " Then, thinking_G_AX_Peer_associate"
            if self.thinking_G_AX_Peer_associate(6) != None:
                self.thinking_withdraw(1)
                all_list.remove([max_pt, ret_crd, max_pt_2])  #删除最高分
                continue
            else:
                self.thinking_withdraw(1)
                print "===>score_and_try, ret: " + str(ret_crd) + ", try:" + str(try_cnt) + "/" + str(total_cnt)
                return ((True, ret_crd))

        self.willdie_cnt += 1
        print "====> I will lose...@score_and_try, try_total: " + str(total_cnt)
        return ((False, score_max_crd))         #无奈之举，返回最高分
    
    '''
    def thinking_prevent_PZW_associate(self):
        point_dict = {}         #用字典，防止重复
        pzw_cnt = 0
        cont = 0

        for mp in self.P_Attr['ZW']:
            pzw_cnt += 1
            class_name = mp.__class__.__name__
            if class_name == 'Peer2':
                #注意这里用rel_coords而不是attract_coords, 封堵的点多一些
                for rel in mp.rel_coords:
                    point_dict[rel] = 0            #给每个点初始分数
            else:   #Peer3
                for attract_coord in mp.attract_coords:
                    point_dict[attract_coord] = 0

        if len(point_dict) == 0:    #没有准赢的情况，也就不需要封堵
            return None

        print "===>PZW, block_len: " + str(len(point_dict)) +",  Point: " + str(point_dict)

        #接下去要给每一个封堵点进行打分，选取分数最高的那个
            #封堵后我方有1个W和1个ZW的，直接返回.....但是貌似不应该发生
        #封堵后对方至少还有1个ZW的，清分，且只有零分，放弃该点
        #封堵后我方有2个ZW的，直接返回
        #封堵后我方有一个ZW的计3分，有W的计2分,有一个G的计2分，有两个子(非D类型)的计1分
        #封堵后对方多个一个D的计2分，降级的计1分
        score_max_crd = {}
        score_max = 0

        for coord in point_dict:
            self.thinking_withdraw(1)
            #--- 联想下子之前
            #将影响我方的情况
            for mp in self.M_Attr['A+X']:
                if coord in mp.attract_coords:
                    point_dict[coord] += 5 #3
                    continue

                if coord in mp.rel_coords:
                    point_dict[coord] += 2
                
            for mp in self.M_Attr['O']:
                if coord in mp.rel_coords:      #能构成G的那种，范围相对狭窄
                    point_dict[coord] += 1

            #将影响对方的情况
            for peer in self.P_Attr['W']:      
                #执行到这里，不应该有对方W的情况
                print "Something error @thinking_prevent_PZW_associate:2"
                sys.exit()

            for peer in self.P_Attr['ZW']:          #至少得进一次
                if coord in peer.rel_coords:
                    point_dict[coord] += 5

            for peer in self.P_Attr['G']:
                if coord in peer.attract_coords:
                    point_dict[coord] += 2      #也不错
            
            for peer in self.P_Attr['A+X']:
                if coord in peer.attract_coords:    #能构成ZW的, 破坏它
                    point_dict[coord] += 3
                    continue
                if coord in peer.rel_coords:        #多少能搞点破坏
                    point_dict[coord] += 1

            for peer in self.P_Attr['O']:
                if coord in peer.rel_coords:
                    point_dict[coord] += 1

            point_dict[coord] -= 5      #把堵对方ZW的那个分数减掉
            point_dict[coord] += 1      #至少给1分，区别于0分的那种

            #--- 模拟联想下子
            self.My_LX_Set(coord, 1)

            print "===>thinking__G_AX_Peer_associate...Total: " + str(len(point_dict))
            if self.thinking_G_AX_Peer_associate(6) != None:    #说明这么下对方会赢，所以不要这么下
                print str(coord) + " is discard(score:"+ str(point_dict[coord]) + "), Peer can win...@prevent_PZW...."
                print " "
                if point_dict[coord] > score_max:
                    score_max = point_dict[coord]
                    score_max_crd = coord
                point_dict[coord] = 0
                continue

            # #--- 联想下子之后
            # # 查看对方是否还有ZW，若有我方就输咯，所以不能这么下
            # for peer in self.P_Attr['ZW']:
            #     cont = 1
            #     print str(coord) + " is discard, because peer ZW again."
            #     point_dict[coord] = 0   #堵不住所有的ZW，清分，放弃
            #     break

            # if cont == 1:
            #     continue

            #---^_^---
            # # 查看我方是否有两个W/ZW，若有，我方可能就赢咯，所以应该这么下
            # wzw_cnt = 0
            # for mp in self.M_Attr['W']:
            #     wzw_cnt += 1
            # for mp in self.M_Attr['ZW']:
            #     wzw_cnt += 1

            # if wzw_cnt >= 2:
            #     # 这里直接返回吧
            #     self.thinking_withdraw(1)
            #     return coord

            w_cnt = 0
            crd_block = 0

            for mp in self.M_Attr['W']:
                if mp.other == 'WW':
                    w_cnt = 2
                    break
                else:
                    w_cnt += 1
                    if crd_block == 0:
                        crd_block = mp.attract_coords[0]
                    else:
                        if cmp(crd_block, mp.attract_coords[0]) == 0:
                            w_cnt -= 1
            
            if w_cnt > 1:
                self.thinking_withdraw(1)
                return coord 
            


            #---最后一步，查看我方新生成的My2类型
            for my in self.M_index[2]:
                if my.attr != 'D' and my.attr != 'W':
                    for crd in my.coords:
                        if crd == coord:            #这样就表示是新生成的My2
                            if my.attr == 'ZW':
                                point_dict[coord] += 5
                            elif my.attr == 'G':
                                point_dict[coord] += 2
                            elif my.attr == 'A+X':
                                point_dict[coord] += 2
                            elif my.attr == 'O':
                                point_dict[coord] += 1
                            else:
                                None
                            break

        self.thinking_withdraw(1)

        ret_coord = None
        max_point = 0
        for coord in point_dict:    
            print "prevent_PZW_associate-->point_dict: " + str(coord) + "--> " +   str(point_dict[coord])     
            if self.random_flag == 1:
                random_num = random.randint(1,3)
                if random_num == 1:
                    if point_dict[coord] > max_point:
                        ret_coord = coord
                        max_point = point_dict[coord]
                else:
                    if point_dict[coord] >= max_point:
                        ret_coord = coord
                        max_point = point_dict[coord]
            else:
                if point_dict[coord] > max_point:
                    ret_coord = coord
                    max_point = point_dict[coord]

        if ret_coord != None:
            return ret_coord        #返回最高分
        else:       
            #执行到这里说明对方肯定有两个ZW，且我方不能直接封堵
            dbg_cnt = 0
            dbg_cnt = len(self.P_Attr['ZW']) 
            if dbg_cnt < 2:     #不应该发生
                print "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! May be lose, have no idea!"
                self.willdie_cnt += 1
                print "==========Game will over, I lose...============"
                #这时可以考虑选一个嵌套层数最多的点，或分数最高的点?  这样也许对方会出现失误，我方还有翻盘的可能
                return score_max_crd
                # for coord in point_dict:
                #     return coord
                return None

            # print "==========Game will over, I lose..ZZZ....============"
            # return score_max_crd

            #一线生机，只能寄希望于G的再次联想功能，能让对方2个ZW变为1个ZW的
            self.My_LX_crd_tier_first = 1
            ret = self.thinking_G_My_prevent_2PZW_Nest(1)
            if self.associate_cnt != 0:
                self.LX_cnt_Total += self.associate_cnt
                print "===>@thinking_G_AX_My_associate, LX_cnt: " + str(self.associate_cnt) + " LX_cnt_Total: " + str(self.LX_cnt_Total)
            self.associate_cnt = 0

            self.thinking_withdraw(1)
            if ret != None:
                print "========== Magic !!! ============"
                self.magicsmile_cnt += 1
                return ret
            else:       #执行到这里，一般来说我方要输了，要死的有尊严
                self.willdie_cnt += 1
                print "==========Game will over, I lose..@thinking_prevent_PZW_associate...============"
                return score_max_crd
                # for coord in point_dict:
                #     return coord
                return None
            
        return None
    '''

    #这个函数里不需要判断我方能赢的情况，只要判断能将对方只剩一个ZW的情况, 垂死挣扎，不知是否可行
    def thinking_G_My_prevent_2PZW_Nest(self, tier):
        nest = {}
        nest_cont = 0

        if tier > 5:
            return None

        for mp in self.M_Attr['G']:
            coord = mp.attract_coords[0]
            coord_block = mp.attract_coords[1]
            nest[(coord, coord_block)] = True
            coord = mp.attract_coords[1]
            coord_block = mp.attract_coords[0]
            nest[(coord, coord_block)] = True
        
        if len(nest) != 0:
            out_for_cnt = 0

            for pair in nest:
                coord = pair[0]
                coord_block = pair[1]
                nest_cont = 0
                break_flag = 0

                if tier > self.My_LX_crd_tier_first:
                    crd_last = self.My_LX_crd_tier[tier-1]
                    if self.check_distance_long(coord, crd_last) == True:
                        continue            #太远了，略过
                
                out_for_cnt += 1

                if out_for_cnt > 1:
                    self.thinking_withdraw(tier)

                ret_str = self.My_LX_Check_PeerWin(coord)
                if ret_str == "lose":
                    return None
                elif ret_str == "cont":
                    None
                elif ret_str == "unknown":
                    continue
                #---
                self.My_LX_Set(coord, tier, 1)
                self.Peer_LX_Set(coord_block, tier, 2)
                self.associate_cnt += 1

                #统计对方ZW数量，若<=1，则说明封堵成功
                zw_cnt = len(self.P_Attr['ZW'])
                if zw_cnt <= 1:     
                    #达到目的了，返回  
                    self.thinking_withdraw(tier)
                    return coord

                #查看我方还有没有G的，若有再次进行嵌套
                ret = self.thinking_G_My_prevent_2PZW_Nest(tier+1)
                self.thinking_withdraw(tier+1)  #联想撤回
                if ret != None:
                    self.thinking_withdraw(tier)
                    return coord    #注意这里的返回值不是ret
                else:
                    continue
        else:       #不存在G的情况
            return None

        self.thinking_withdraw(tier)            #存疑

        return None

    #只要我方有G就进行嵌套联想，直到找到能生成W或ZW的
    # 因为加入了AX->ZW的联想, 这和对方有G的情况是冲突的，所以本函数返回值能否用还得再商榷
    def thinking_G_AX_My_associate(self):
        self.My_LX_crd_tier_first = 1
        self.LX_Active = "My"
        ret = self.thinking_G_AX_My_Nest(1, 5, 0)
        if self.associate_cnt != 0:
            self.LX_cnt_Total += self.associate_cnt
            print "===>@thinking_G_AX_My_associate, LX_cnt: " + str(self.associate_cnt) + " LX_cnt_Total: " + str(self.LX_cnt_Total)
        self.associate_cnt = 0

        self.thinking_withdraw(1)

        return ret

    
    def thinking_G_AX_My_Nest(self, tier, tier_max, tier_offset=0):     #tier为嵌套的层次，最小为1
        local_print_debug = 0
        
        #嵌套层次太多，计算机可能受不了
        # if self.history_track['start'] == "My":
        #     #我方先下，进攻为主
        #     if tier > (6 + tier_offset):        
        #         return None
        # else:
        #     #我方后下，防守为主
        #     if tier > (5 + tier_offset):
        #         return None
        if tier > (tier_max + tier_offset):
            return None

        # 如何进行联想优化？两个下子的位置相差太大，是否可以略过？哈哈，我真是个人才

        # Step 1: 先进行掌握主动权的坐标点的收集
        nest_cont = 0
        nest = {}
        crd_tmp_set = set()

        for mp in self.M_Attr['G']:
            coord = mp.attract_coords[0]
            coord_block = mp.attract_coords[1]
            coord_block_tuple = (coord_block, )
            if coord not in crd_tmp_set: 
                nest[(coord, coord_block_tuple)] = True
                crd_tmp_set.add(coord)
            coord = mp.attract_coords[1]
            coord_block = mp.attract_coords[0]
            coord_block_tuple = (coord_block, )
            if coord not in crd_tmp_set: 
                nest[(coord, coord_block_tuple)] = True
                crd_tmp_set.add(coord)

        #对方没有ZW，才能用A+X联想, 但是对方若有G，我方似乎联想也有难度啊
        # if len(self.P_Attr['ZW']) == 0:
        # if len(self.P_Attr['ZW']) == 0 and len(self.P_Attr['G']) == 0:
        if len(self.P_Attr['ZW']) == 0:
            peer_w_will_set = self.get_point_setByAttr_all('W', self.Peer_point)
            if len(peer_w_will_set) == 0:
                #如果不考虑计算机算力的话，理论上应该把我方可以形成ZW的情况加进去(包括A+X形成ZW，和新生成ZW的情况)
                for mp in self.M_Attr['A+X']:
                    for coord in mp.attract_coords:
                        ret_tmp = self.My_AX_To_ZW_Block(coord, tier+1)
                        if ret_tmp[0] == "OK":
                            if coord not in crd_tmp_set:            #避免重复添加
                                nest[(coord, ret_tmp[1])] = True
                                crd_tmp_set.add(coord)
                        else:
                            print "Something error@thinking__G_AX_My_Nest, 123, crd: " + str(crd)

                ret_tmp = self.get_point_setByZW(self.My_point)
                if len(ret_tmp) != 0:
                    for crd_and_block in ret_tmp:
                        coord = crd_and_block[0]
                        if coord not in crd_tmp_set:            #避免重复添加
                            nest[(coord, crd_and_block[1])] = True
                            crd_tmp_set.add(coord)

        # Step 2: 上面收集封堵点，下面开始联想，要注意一级中联想的次数，G为1次，ZW为多次,ZW需要满足全部, 且要考虑对方G的情况

        if len(nest) != 0:
            # if tier <= (self.My_LX_crd_tier_first + 1):
            #     print "===> My G/A+X LX...tier: " + str(tier) + ", len_nest: " + str(len(nest))

            out_for_cnt = 0
                
            for pair in nest:
                coord = pair[0]
                must_cnt = len(pair[1])     #必须全部封堵点满足才行
                can_cnt = 0                 #满足一次 +1

                if tier > self.My_LX_crd_tier_first:
                    crd_last = self.My_LX_crd_tier[tier-1]
                    if self.check_distance_long(coord, crd_last) == True:
                        continue            #太远了，略过

                if tier == 1 and cmp(coord, (8, 5)) == 0:
                    self.something_print = 1

                out_for_cnt += 1

                if out_for_cnt > 1:
                    self.thinking_withdraw(tier)
                
                # ^_^
                ret_str = self.My_LX_Check_PeerWin(coord)
                if ret_str == "lose":
                    return None
                elif ret_str == "cont":
                    None
                elif ret_str == "unknown":
                    continue

                for coord_block in pair[1]:
                    # 先进行上一次循环的悔棋操作
                    self.thinking_withdraw(tier)

                    # ^_^
                    # ret_str = self.My_LX_Check_PeerWin(coord)
                    # if ret_str == "lose":
                    #     return None
                    # elif ret_str == "cont":
                    #     None
                    # elif ret_str == "unknown":
                    #     break

                    # if len(self.P_Attr['W']) > 0:
                    #     self.dbg_cnt += 100
                    #     print "=====error=====4317"
                        
                    #---
                    self.My_LX_Set(coord, tier, 1)         #我方下
                    #因为我方加入了ZW的联想，或许也得加入对方G的强行插入联想...但貌似复杂了...2020.3.10
                    self.Peer_LX_Set(coord_block, tier, 2) #对方下
                    self.associate_cnt += 1

                    #查看我方有没有W, 若有直接返回
                    # if len(self.M_Attr['W']) > 0:
                    if len(self.M_Attr['W']) > 0 or (len(self.M_Attr['ZW']) > 0 and len(self.P_Attr['W']) == 0):
                        can_cnt += 1
                        if can_cnt >= must_cnt:
                            if self.something_print == 1:
                                print "=== === === ==="
                                print "===>" + str(self.associate_point)


                            self.thinking_withdraw(tier)
                            if must_cnt > 1:        #我方ZW联想能赢得情况，不保险
                                if self.LX_Active == "My":          #避免反复嵌套联想
                                    self.My_LX_Set(coord, tier)         #我方下
                                    self.Peer_LX_crd_tier_first = tier + 1
                                    ret = self.thinking_G_AX_Peer_Nest(tier+1, 5, tier)
                                    self.thinking_withdraw(tier+1)
                                    self.thinking_withdraw(tier)
                                    if ret != None:     #我方可能赢，但是下了后却是对方翻盘的好戏
                                        break
                                    else:           #我方能赢且对方不能赢的情况
                                        return coord
                                else:
                                    print "========>Something error, LX_Active: " + self.LX_Active
                                    self.wrong_cnt += 1000
                                    return coord
                            else:
                                return coord
                        else:       # 成了一个，但革命尚未完全成功，同志仍需努力
                            continue

                    #查看我方还有没有G的，若有再次进行嵌套
                    ret = self.thinking_G_AX_My_Nest(tier+1, tier_max, tier_offset)
                    self.thinking_withdraw(tier+1)  #联想撤回
                    if ret != None:
                        can_cnt += 1
                        if can_cnt >= must_cnt:
                            self.thinking_withdraw(tier)
                            if must_cnt > 1:        #我方ZW联想能赢得情况，不保险
                                if self.LX_Active == "My":          #避免反复嵌套联想
                                    self.My_LX_Set(coord, tier)         #我方下
                                    self.Peer_LX_crd_tier_first = tier + 1
                                    ret = self.thinking_G_AX_Peer_Nest(tier+1, 5, tier)
                                    self.thinking_withdraw(tier+1)
                                    self.thinking_withdraw(tier)
                                    if ret != None:     #我方可能赢，但是下了后却是对方翻盘的好戏
                                        break
                                    else:           #我方能赢且对方不能赢的情况
                                        return coord
                                else:
                                    print "========>Something error, LX_Active: " + self.LX_Active
                                    return coord
                            else:
                                return coord    #注意这里的返回值不是ret
                        else:
                            # 成了一个，但革命尚未完全成功，同志仍需努力
                            continue
                    else:       # 退出内循环
                        break
        else:
            return None

        self.thinking_withdraw(tier)        #存疑？？？

        return None

    def thinking_withdraw(self, tier):
        while len(self.associate_point) != 0:
            last_handle = self.associate_point[-1]
            if last_handle[1] == tier:
                # print "---> nest...back..." + str(tier)
                self.settle_back(last_handle[0])
                self.associate_point.pop()
            elif last_handle[1] > tier:
                # 说明上层调用逻辑有误
                self.warning += 1
                break
            else:
                break

    # 返回(True/False, direction/None)
    # 这个函数很牛逼，有联想功能喔
    def can_build_ZW(self, val, coord, coord_block=None):
        val_block = (val == 1) and 2 or 1
        x = coord[0]; y = coord[1]
        self.matrix[y][x] = val
        if coord_block != None:
            x_b = coord_block[0]; y_b = coord_block[1]
            self.matrix[y_b][x_b] = val_block
        
        #ZZYYYZ, ZYYYZZ, ZYYZYZ, ZYZYYZ
        ret_tuple = None

        length = 1
        distance = 4
        for direct in ['S', 'SW', 'W', 'WE']:
            ret_str = self.get_point_seq(coord, direct, length, distance)
            if ret_str[2:8] == 'ZZYYYZ' or ret_str[1:7] == 'ZZYYYZ' or ret_str[0:6] == 'ZZYYYZ':
                ret_tuple =  (True, direct)
            elif ret_str[3:9] == 'ZYYYZZ' or ret_str[2:8] == 'ZYYYZZ' or ret_str[1:7] == 'ZYYYZZ':
                ret_tuple =  (True, direct)
            elif ret_str[3:9] == 'ZYYZYZ' or ret_str[2:8] == 'ZYYZYZ' or ret_str[0:6] == 'ZYYZYZ':
                ret_tuple =  (True, direct)
            elif ret_str[3:9] == 'ZYZYYZ' or ret_str[1:7] == 'ZYZYYZ' or ret_str[0:6] == 'ZYZYYZ':
                ret_tuple =  (True, direct)

        #还原
        self.matrix[y][x] = 0
        if coord_block != None:
            self.matrix[y_b][x_b] = 0

        if ret_tuple != None:
            return ret_tuple
        else:
            return (False, None)

    def thinking(self):
        # W > ZW > G > ZZW

        # self.print_MP_class('M', 2)
        # self.print_MP_class('M', 3)
        # self.print_MP_class('M', 4)
        # print "-------------------------------------"
        # self.print_MP_class('P', 2)
        # self.print_MP_class('P', 3)
        # self.print_MP_class('P', 4)

        self.LX_cnt_Total = 0

        # 1. 先判断我方是否能直接赢
        print "===========>thingking: 1 W.............................................."
        ret = self.thinking_maybe_MyWin()               #1-W
        if ret != None:
            return ('W', ret)

        # 2. 封堵对方会直接赢的那种
        print "===========>thingking: 2 PW.............................................."
        ret = self.thinking_prevent_PeerWin()           #2-PW
        if ret != None:
            return ('2: PW', ret)

        # 3. 寻找我方能准赢的那种
        print "===========>thingking: 3 ZW.............................................."
        ret = self.thinking_maybe_MyWin_Ready()         #3-ZW
        if ret != None:
            return ('3: ZW', ret)

        # 4.X G+X, 有一个G就可以进行联想了...
        # - 我方下子，对方封堵后——我方生成W，能赢
        # - 我方下子，对方封堵后——对方生成W，会输，所以不能这么下
        # - 我方下子，对方封堵后——我方能生成ZW

        # - 我方下子，对方封堵后——我方生成G...再次联想
        # - 我方下子，对方封堵后——对方生成两个ZW的，不能这么下

        # 4. 我方有一个或多个G的联想
        print "===========>thingking: 4 G+W/ZW.............................................."
        ret = self.thinking_G_AX_My_associate()
        if ret != None:
            return ('4: G+W/ZW', ret)


        # 5. 寻找那种不封堵，对方就会赢的
        print "===========>thingking: 5 PZW.............................................."
        ret = self.thinking_prevent_PZW_associate() 
        if ret != None:
            return ('5: PZW', ret)

        #我方能构成2个ZW类型的
        if len(self.associate_point) != 0:
            print "associate_point:"
            print self.associate_point

        # 6. 封堵对方G/G，G/A+X，A+X/A+X有交叉的点
        print "===========>thingking: 6: PG/AX.............................................."
        ret = self.thinking_prevent_G_AX()
        if ret != None:
            return ('6: PG/AX', ret)

        # # 6. 我方G 或 我方构建ZW 或封堵对方G 或阻止对方构建ZW
        # # 6.1 封堵对方G/G有交叉或G/A+X有交叉的情况
        # # -- 我方G和G/A+X有交叉的情况这里不考虑，因为在thinking_G_AX_My_associate中已经考虑过了
        # # 6.3 我方A+X和A+X有交叉的情况，这样我方就能构建两个ZW
        # # 6.4 其他的用打分机制,封堵对方两个A+X有交叉的优先级比PG要高
        # print "===========>thingking: 6: G/AX/PG/PAX.............................................."
        # ret = self.thinking_G_AX_PG_PAX()
        # if ret != None:
        #     return ('6: G/AX/PG/PAX', ret)

        print "=============>thinking: 7 Others..............................................."
        ret = self.thinking_others()
        if ret != None:
            return ('7: Others', ret)

        # print "===========>thingking: 7: AX/G/PAX/PG.............................................."
        # ret = self.thinking_AX_G_PAX_PG()
        # if ret != None:
        #     return ('7: AX/G/PAX/PG', ret)

        # print "===========>thingking: 8: AO/ZAX/PAO/PZAX.............................................."
        # ret = self.thinking_O_ZAX_PO_PZAX()
        # if ret != None:
        #     return ('8: AO/ZAX/PAO/PZAX', ret)

        print "==>Sorry! I have no idea.............................................."
        self.noidea_cnt += 1

        for mp in self.M_Attr['A+X']:
            return ('NO IDEA', mp.attract_coords[0])

        for mp in self.P_Attr['A+X']:
            return ('NO IDEA', mp.attract_coords[0])

        print "===>Sorry! I am crazy......"
        # 执行到这里，为了机器的尊严，也得返回一个空子的地方...........

        return ('D', (14,14))

    def get_coord_pack(self, coord, direction, offset_pack):
        ret_list = []
        for offset in offset_pack:
            ret = self.get_coord(coord, direction, offset)
            ret_list.append(ret)

        return ret_list

    #返回元组形式的坐标，若无效，返回None
    def get_coord(self, coord, direction, offset):
        x = coord[0]
        y = coord[1]

        limit = self.__SIDELENGTH - 1
        x_new = x
        y_new = y
        
        if direction == 'N':
            y_new += offset
        elif direction == 'NE':
            x_new += offset; y_new += offset
        elif direction == 'E':
            x_new += offset
        elif direction == 'ES':
            x_new += offset; y_new -= offset
        elif direction == 'S':
            y_new -= offset
        elif direction == 'SW':
            x_new -= offset; y_new -= offset
        elif direction == 'W':
            x_new -= offset
        elif direction == 'WN':
             x_new -= offset; y_new += offset
        else:
            return None
            
        if x_new < 0 or x_new > limit or y_new < 0 or y_new > limit:
            return None
        else:
            return (x_new, y_new)

    def get_point_seq(self, coord, direction, length, distance):
        '''
        参数: coord: 初始坐标点
              direction: 方向
              length: 挨着的队友总数(包括coord本身)
              distance: 需要查看的远方是敌是友的个数
        返回: 类似于HZYYYZYH, Y表示队友, Z表示空的, H表示敌人或城墙
        '''
        ret_str = ""
        for i in range(0, distance):
            offset = i-distance
            ret = self.check_point(coord, direction, offset)
            if ret == 'Y':
                ret_str += 'Y'
            elif ret == 'Q' or ret == 'N':
                ret_str += 'H'
            elif ret == 'Z':
                ret_str += 'Z'
            else:
                None
        ret_str += 'Y'*length
        for i in range(0, distance):
            offset = i+length
            ret = self.check_point(coord, direction, offset)
            if ret == 'Y':
                ret_str += 'Y'
            elif ret == 'Q' or ret == 'N':
                ret_str += 'H'
            elif ret == 'Z':
                ret_str += 'Z'
            else:
                None

        return ret_str

    def check_point(self, coord, direction, offset):
        '''
        参数: coord位置必须有棋子; direction 8个方向之一; offset偏移量
        返回: 指定偏移坐标的类型 Q/Z/Y/N
        '''
        x = coord[0]
        y = coord[1]
        orig = self.matrix[y][x]
        if orig == 0:
            return None

        coord_new = self.get_coord(coord, direction, offset)
            
        if coord_new == None:
            return 'Q'
        else:
            x_new = coord_new[0]
            y_new = coord_new[1]
            if self.matrix[y_new][x_new] == 0:
                return 'Z'
            elif self.matrix[y_new][x_new] == orig:
                return 'Y'
            else:
                return 'N'

    def withdraw_dict_pointS(self, coord):      #coord坐标的值应该为0
        coord_new = self.get_coord(coord, 'N', 1)
        if coord_new != None and self.matrix[coord_new[1]][coord_new[0]] != 0:
            #确保存在对应的字典键
            dir_pos = 4  #S
            self.dict_point[coord_new][2][dir_pos] = 'Z'
            if self.dict_point[coord_new][0] == 'D':
                self.dict_point[coord_new][0] = 'F'     #复活
            elif self.dict_point[coord_new][0] == 'U':  #F不用考虑
                attr = 'F'
                for direction in self.dict_point[coord_new][2]:
                    if direction == 'Y':
                        attr = 'U'
                        break
                if attr == 'F':
                    self.dict_point[coord_new][0] = 'F'  #U-->F
        coord_new = self.get_coord(coord, 'NE', 1)
        if coord_new != None and self.matrix[coord_new[1]][coord_new[0]] != 0:
            #确保存在对应的字典键
            dir_pos = 5  #SW
            self.dict_point[coord_new][2][dir_pos] = 'Z'
            if self.dict_point[coord_new][0] == 'D':
                self.dict_point[coord_new][0] = 'F'     #复活
            elif self.dict_point[coord_new][0] == 'U':  #F不用考虑
                attr = 'F'
                for direction in self.dict_point[coord_new][2]:
                    if direction == 'Y':
                        attr = 'U'
                        break
                if attr == 'F':
                    self.dict_point[coord_new][0] = 'F'  #U-->F
        coord_new = self.get_coord(coord, 'E', 1)
        if coord_new != None and self.matrix[coord_new[1]][coord_new[0]] != 0:
            #确保存在对应的字典键
            dir_pos = 6  #W
            self.dict_point[coord_new][2][dir_pos] = 'Z'
            if self.dict_point[coord_new][0] == 'D':
                self.dict_point[coord_new][0] = 'F'     #复活
            elif self.dict_point[coord_new][0] == 'U':  #F不用考虑
                attr = 'F'
                for direction in self.dict_point[coord_new][2]:
                    if direction == 'Y':
                        attr = 'U'
                        break
                if attr == 'F':
                    self.dict_point[coord_new][0] = 'F'  #U-->F
        coord_new = self.get_coord(coord, 'ES', 1)
        if coord_new != None and self.matrix[coord_new[1]][coord_new[0]] != 0:
            #确保存在对应的字典键
            dir_pos = 7  #WN
            self.dict_point[coord_new][2][dir_pos] = 'Z'
            if self.dict_point[coord_new][0] == 'D':
                self.dict_point[coord_new][0] = 'F'     #复活
            elif self.dict_point[coord_new][0] == 'U':  #F不用考虑
                attr = 'F'
                for direction in self.dict_point[coord_new][2]:
                    if direction == 'Y':
                        attr = 'U'
                        break
                if attr == 'F':
                    self.dict_point[coord_new][0] = 'F'  #U-->F
        coord_new = self.get_coord(coord, 'S', 1)
        if coord_new != None and self.matrix[coord_new[1]][coord_new[0]] != 0:
            #确保存在对应的字典键
            dir_pos = 0  #N
            self.dict_point[coord_new][2][dir_pos] = 'Z'
            if self.dict_point[coord_new][0] == 'D':
                self.dict_point[coord_new][0] = 'F'     #复活
            elif self.dict_point[coord_new][0] == 'U':  #F不用考虑
                attr = 'F'
                for direction in self.dict_point[coord_new][2]:
                    if direction == 'Y':
                        attr = 'U'
                        break
                if attr == 'F':
                    self.dict_point[coord_new][0] = 'F'  #U-->F
        coord_new = self.get_coord(coord, 'SW', 1)
        if coord_new != None and self.matrix[coord_new[1]][coord_new[0]] != 0:
            #确保存在对应的字典键
            dir_pos = 1  #NE
            self.dict_point[coord_new][2][dir_pos] = 'Z'
            if self.dict_point[coord_new][0] == 'D':
                self.dict_point[coord_new][0] = 'F'     #复活
            elif self.dict_point[coord_new][0] == 'U':  #F不用考虑
                attr = 'F'
                for direction in self.dict_point[coord_new][2]:
                    if direction == 'Y':
                        attr = 'U'
                        break
                if attr == 'F':
                    self.dict_point[coord_new][0] = 'F'  #U-->F
        coord_new = self.get_coord(coord, 'W', 1)
        if coord_new != None and self.matrix[coord_new[1]][coord_new[0]] != 0:
            #确保存在对应的字典键
            dir_pos = 2  #E
            self.dict_point[coord_new][2][dir_pos] = 'Z'
            if self.dict_point[coord_new][0] == 'D':
                self.dict_point[coord_new][0] = 'F'     #复活
            elif self.dict_point[coord_new][0] == 'U':  #F不用考虑
                attr = 'F'
                for direction in self.dict_point[coord_new][2]:
                    if direction == 'Y':
                        attr = 'U'
                        break
                if attr == 'F':
                    self.dict_point[coord_new][0] = 'F'  #U-->F
        coord_new = self.get_coord(coord, 'WN', 1)
        if coord_new != None and self.matrix[coord_new[1]][coord_new[0]] != 0:
            #确保存在对应的字典键
            dir_pos = 3  #ES
            self.dict_point[coord_new][2][dir_pos] = 'Z'
            if self.dict_point[coord_new][0] == 'D':
                self.dict_point[coord_new][0] = 'F'     #复活
            elif self.dict_point[coord_new][0] == 'U':  #F不用考虑
                attr = 'F'
                for direction in self.dict_point[coord_new][2]:
                    if direction == 'Y':
                        attr = 'U'
                        break
                if attr == 'F':
                    self.dict_point[coord_new][0] = 'F'  #U-->F

    def update_dict_pointS(self, coord):
        val = self.matrix[coord[1]][coord[0]]

        coord_new = self.get_coord(coord, 'N', 1)
        if coord_new != None and self.matrix[coord_new[1]][coord_new[0]] != 0:  
            #确保存在对应的字典键
            dir_pos = 4  #S
            if self.dict_point[coord_new][1] == val:
                dir_val = 'Y'
                self.dict_point[coord_new][2][dir_pos] = dir_val
                attr = 'U'
                self.dict_point[coord_new][0] = attr
            else:   #相反
                dir_val = 'N'
                self.dict_point[coord_new][2][dir_pos] = dir_val
                if self.dict_point[coord_new][0] == 'F':   #U不用考虑，而且不可能是D  
                    cnt = 0 
                    for direction in self.dict_point[coord_new][2]:
                        if direction == 'Q' or direction == 'N':
                            cnt += 1
                    if cnt == 8:
                        attr = 'D'  #死棋子
                        self.dict_point[coord_new][0] = attr
                    
        coord_new = self.get_coord(coord, 'NE', 1)
        if coord_new != None and self.matrix[coord_new[1]][coord_new[0]] != 0:  
            dir_pos = 5  #SW
            if self.dict_point[coord_new][1] == val:
                dir_val = 'Y'
                self.dict_point[coord_new][2][dir_pos] = dir_val
                attr = 'U'
                self.dict_point[coord_new][0] = attr
            else:   #相反
                dir_val = 'N'
                self.dict_point[coord_new][2][dir_pos] = dir_val
                if self.dict_point[coord_new][0] == 'F':   #U不用考虑，而且不可能是D  
                    cnt = 0 
                    for direction in self.dict_point[coord_new][2]:
                        if direction == 'Q' or direction == 'N':
                            cnt += 1
                    if cnt == 8:
                        attr = 'D'  #死棋子
                        self.dict_point[coord_new][0] = attr
                    
        coord_new = self.get_coord(coord, 'E', 1)
        if coord_new != None and self.matrix[coord_new[1]][coord_new[0]] != 0:  
            dir_pos = 6  #W
            if self.dict_point[coord_new][1] == val:
                dir_val = 'Y'
                self.dict_point[coord_new][2][dir_pos] = dir_val
                attr = 'U'
                self.dict_point[coord_new][0] = attr
            else:   #相反
                dir_val = 'N'
                self.dict_point[coord_new][2][dir_pos] = dir_val
                if self.dict_point[coord_new][0] == 'F':   #U不用考虑，而且不可能是D  
                    cnt = 0 
                    for direction in self.dict_point[coord_new][2]:
                        if direction == 'Q' or direction == 'N':
                            cnt += 1
                    if cnt == 8:
                        attr = 'D'  #死棋子
                        self.dict_point[coord_new][0] = attr
                    
        coord_new = self.get_coord(coord, 'ES', 1)
        if coord_new != None and self.matrix[coord_new[1]][coord_new[0]] != 0:  
            dir_pos = 7  #WN
            if self.dict_point[coord_new][1] == val:
                dir_val = 'Y'
                self.dict_point[coord_new][2][dir_pos] = dir_val
                attr = 'U'
                self.dict_point[coord_new][0] = attr
            else:   #相反
                dir_val = 'N'
                self.dict_point[coord_new][2][dir_pos] = dir_val
                if self.dict_point[coord_new][0] == 'F':   #U不用考虑，而且不可能是D  
                    cnt = 0 
                    for direction in self.dict_point[coord_new][2]:
                        if direction == 'Q' or direction == 'N':
                            cnt += 1
                    if cnt == 8:
                        attr = 'D'  #死棋子
                        self.dict_point[coord_new][0] = attr
                    
        coord_new = self.get_coord(coord, 'S', 1)
        if coord_new != None and self.matrix[coord_new[1]][coord_new[0]] != 0:  
            dir_pos = 0  #N
            if self.dict_point[coord_new][1] == val:
                dir_val = 'Y'
                self.dict_point[coord_new][2][dir_pos] = dir_val
                attr = 'U'
                self.dict_point[coord_new][0] = attr
            else:   #相反
                dir_val = 'N'
                self.dict_point[coord_new][2][dir_pos] = dir_val
                if self.dict_point[coord_new][0] == 'F':   #U不用考虑，而且不可能是D  
                    cnt = 0 
                    for direction in self.dict_point[coord_new][2]:
                        if direction == 'Q' or direction == 'N':
                            cnt += 1
                    if cnt == 8:
                        attr = 'D'  #死棋子
                        self.dict_point[coord_new][0] = attr
                    
        coord_new = self.get_coord(coord, 'SW', 1)
        if coord_new != None and self.matrix[coord_new[1]][coord_new[0]] != 0:  
            dir_pos = 1  #NE
            if self.dict_point[coord_new][1] == val:
                dir_val = 'Y'
                self.dict_point[coord_new][2][dir_pos] = dir_val
                attr = 'U'
                self.dict_point[coord_new][0] = attr
            else:   #相反
                dir_val = 'N'
                self.dict_point[coord_new][2][dir_pos] = dir_val
                if self.dict_point[coord_new][0] == 'F':   #U不用考虑，而且不可能是D  
                    cnt = 0 
                    for direction in self.dict_point[coord_new][2]:
                        if direction == 'Q' or direction == 'N':
                            cnt += 1
                    if cnt == 8:
                        attr = 'D'  #死棋子
                        self.dict_point[coord_new][0] = attr
                    
        coord_new = self.get_coord(coord, 'W', 1)
        if coord_new != None and self.matrix[coord_new[1]][coord_new[0]] != 0:  
            dir_pos = 2  #E
            if self.dict_point[coord_new][1] == val:
                dir_val = 'Y'
                self.dict_point[coord_new][2][dir_pos] = dir_val
                attr = 'U'
                self.dict_point[coord_new][0] = attr
            else:   #相反
                dir_val = 'N'
                self.dict_point[coord_new][2][dir_pos] = dir_val
                if self.dict_point[coord_new][0] == 'F':   #U不用考虑，而且不可能是D  
                    cnt = 0 
                    for direction in self.dict_point[coord_new][2]:
                        if direction == 'Q' or direction == 'N':
                            cnt += 1
                    if cnt == 8:
                        attr = 'D'  #死棋子
                        self.dict_point[coord_new][0] = attr
                    
            
        coord_new = self.get_coord(coord, 'WN', 1)
        if coord_new != None and self.matrix[coord_new[1]][coord_new[0]] != 0: 
            dir_pos = 3  #ES
            if self.dict_point[coord_new][1] == val:
                dir_val = 'Y'
                self.dict_point[coord_new][2][dir_pos] = dir_val
                attr = 'U'
                self.dict_point[coord_new][0] = attr
            else:   #相反
                dir_val = 'N'
                self.dict_point[coord_new][2][dir_pos] = dir_val
                if self.dict_point[coord_new][0] == 'F':   #U不用考虑，而且不可能是D  
                    cnt = 0 
                    for direction in self.dict_point[coord_new][2]:
                        if direction == 'Q' or direction == 'N':
                            cnt += 1
                    if cnt == 8:
                        attr = 'D'  #死棋子
                        self.dict_point[coord_new][0] = attr
                    

    #该函数返回坐标点周围的情况，从正北方向开始，顺时针方向，0~7，8个元素的元组代表8个方向的情况
    #Y代表同子, N代表异子, Z代表空的, Q代表界外
    def prase_point(self, coord, val):
        limit = self.__SIDELENGTH - 1
        x = coord[0]
        y = coord[1]

        N = None; NE = None; E = None; ES = None 
        S = None; SW = None; W = None; WN = None
        QN_cnt = 0; Y_cnt = 0; Z_cnt = 0

        if (y+1) > limit:
            N = 'Q'; QN_cnt += 1
        else:
            if self.matrix[y+1][x] == 0:
                N = 'Z'; Z_cnt += 1
            elif self.matrix[y+1][x] == val:
                N = 'Y'; Y_cnt += 1
            else:
                N = 'N'; QN_cnt += 1
        
        if (y+1) > limit or (x+1) > limit:
            NE = 'Q'; QN_cnt += 1
        else:
            if self.matrix[y+1][x+1] == 0:
                NE = 'Z'; Z_cnt += 1
            elif self.matrix[y+1][x+1] == val:
                NE = 'Y'; Y_cnt += 1
            else:
                NE = 'N'; QN_cnt += 1
        
        if (x+1) > limit:
            E = 'Q'; QN_cnt += 1
        else:
            if self.matrix[y][x+1] == 0:
                E = 'Z'; Z_cnt += 1
            elif self.matrix[y][x+1] == val:
                E = 'Y'; Y_cnt += 1
            else:
                E = 'N'; QN_cnt += 1

        if (x+1) > limit or (y-1) < 0:
            ES = 'Q'; QN_cnt += 1
        else:
            if self.matrix[y-1][x+1] == 0:
                ES = 'Z'; Z_cnt += 1
            elif self.matrix[y-1][x+1] == val:
                ES = 'Y'; Y_cnt += 1
            else:
                ES = 'N'; QN_cnt += 1

        if (y-1) < 0:
            S = 'Q'; QN_cnt += 1
        else:
            if self.matrix[y-1][x] == 0:
                S = 'Z'; Z_cnt += 1
            elif self.matrix[y-1][x] == val:
                S = 'Y'; Y_cnt += 1
            else:
                S = 'N'; QN_cnt += 1

        if (x-1) < 0 or (y-1) < 0:
            SW = 'Q'; QN_cnt += 1
        else:
            if self.matrix[y-1][x-1] == 0:
                SW = 'Z'; Z_cnt += 1
            elif self.matrix[y-1][x-1] == val:
                SW = 'Y'; Y_cnt += 1
            else:
                SW = 'N'; QN_cnt += 1

        if (x-1) < 0:
            W = 'Q'; QN_cnt += 1
        else:
            if self.matrix[y][x-1] == 0:
                W = 'Z'; Z_cnt += 1
            elif self.matrix[y][x-1] == val:
                W = 'Y'; Y_cnt += 1
            else:
                W = 'N'; QN_cnt += 1

        if (x-1) < 0 or (y+1) > limit:
            WN = 'Q'; QN_cnt += 1
        else:
            if self.matrix[y+1][x-1] == 0:
                WN = 'Z'; Z_cnt += 1
            elif self.matrix[y+1][x-1] == val:
                WN = 'Y'; Y_cnt += 1
            else:
                WN = 'N'; QN_cnt += 1

        if QN_cnt == 8:
            attr = 'D'  # 'D': die 对自己而言是死棋子
        elif Z_cnt > 0 and Y_cnt == 0:
            attr = 'F'  # 'F': free 自由的一颗棋子，有发展空间
        elif Y_cnt > 0:
            attr = 'U'  # 'U': union 联合其他棋子
        else:       #应该没有其他情况了
            attr = None
        
        point_round = (N, NE, E, ES, S, SW, W, WN)

        return (attr, point_round)

    #悔棋
    def withdraw_point(self):
        if self.__last_coord == None:
            return -1   #无需悔棋 或者 不能连续悔棋
        self.set_point(self.__last_coord, 0)

        return 0


    #搜索指定坐标是否为MyX类型
    def search_MyX(self, index, coord, direction=None):
        if len(self.M_index[index]) == 0:
            None

        if index == 1:
            for my1 in self.M_index[index]:
                if my1.coord == coord:
                    return my1
        elif index == 2:
            for my2 in self.M_index[index]:
                if my2.coords[0] == coord and my2.direction == direction:
                    return my2
        elif index == 3:
            for my3 in self.M_index[index]:
                if my3.coords[0] == coord and my3.direction == direction:
                    return my3
        elif index == 4:
            None

        return None

    def search_PeerX(self, index, coord, direction=None):
        if len(self.P_index[index]) == 0:
            None

        if index == 1:
            for peer in self.P_index[index]:
                if peer.coord == coord:
                    return peer
        elif index == 2:
            for peer in self.P_index[index]:
                if peer.coords[0] == coord and peer.direction == direction:
                    return peer
        elif index == 3:
            for peer in self.P_index[index]:
                if peer.coords[0] == coord and peer.direction == direction:
                    return peer
        elif index == 4:
            None

        return None

    '''
    智能下棋，核心关键策略函数
    '''
    def smart_point(self):
        limit = self.__SIDELENGTH - 1

        youlose = 0
        status = "INIT"
        
        if self.last_peer_coord == None:    #由我方下第一个子
            random_num = random.randint(1,8)
            # random_num = 4

            if random_num == 1:
                coord = (7, 7)      #正中间
            elif random_num == 2:
                coord = (5, 5)
            elif random_num == 3:
                coord = (5, 9)
            elif random_num == 4:
                coord = (9, 5)
            elif random_num == 5:
                coord = (9, 9)
            else:
                coord = (7, 7)      #正中间
        elif self.last_my_coord == None:    #由敌方下第一个子，我方下第二个
            x = self.last_peer_coord[0]
            y = self.last_peer_coord[1]
            if x == 0 or x == limit or y == 0 or y == limit:
                coord = (7, 7)      #对方在不正经得下棋，不予理会
            elif x == 7 and y == 7:
                random_num = random.randint(1,13)
                random_num = 11

                if random_num == 1:     #平
                    coord = (6, 6)
                elif random_num == 2:   #输
                    coord = (6, 7)
                elif random_num == 3:   #输
                    coord = (6, 8)
                elif random_num == 4:
                    coord = (7, 8)
                elif random_num == 5:
                    coord = (8, 8)
                elif random_num == 6:
                    coord = (8, 7)
                elif random_num == 7:
                    coord = (8, 6)
                elif random_num == 8:
                    coord = (7, 6)
                elif random_num == 9:
                    coord = (7, 5)
                elif random_num == 10:
                    coord = (7, 9)
                elif random_num == 11:
                    coord = (5, 7)
                elif random_num == 12:
                    coord = (9, 7)
                else:
                    coord = (6, 6)

                # coord = (8, 7)

                # coord = (7, 6)

            else:               #封堵对方的第一子，尽量下在棋盘中间
                if x < 7:
                    my_x = x+1
                else:
                    my_x = x-1

                if y < 7:
                    my_y = y+1
                else:
                    my_y = y-1

                coord = (my_x, my_y)
        else:
            ret = self.thinking()
            status = ret[0]
            coord = ret[1]
            print "  "
            print "☆☆☆☆☆☆ Smart type: " + status + " --------->coord: " + str(coord)
            print "☆☆☆ Point Cnt: " + str(len(self.history_track['crd_list']))
            print "  "

            if status == 'W':
                youlose = 1
                print "------------------------------> My Win!!"
            elif status == 'D':
                print "------------------------------>God bless me!"

            if self.wrong_cnt > 0:
                print "------------->wrong_cnt: " + str(self.wrong_cnt)
                self.print_MP_Attr('P')
                    
        self.set_my_point(coord)

        return (youlose, coord, status)



# Create your views here.

def start(request):
    turn = request.POST.get('turn', '')
    user_name = request.session.get('username', None)

    Redis_Pool = redis.ConnectionPool(host='127.0.0.1', port=6379, db=0)
    rds = redis.Redis(connection_pool=Redis_Pool)

    print "====================================================="
    print "=======================Game Start: " + turn + " ===================="
    print "====================================================="


    if turn == 'user_first':
        match = Match(2)

        # with open("pickle-fp", "w") as f:
        #     pickle.dump(match, f)

        # 需要把match存储起来喔
        match_string = pickle.dumps(match)
        rds.set("Match_"+user_name, match_string)
        
        ret = {
            'stat': 'success'
        }
    elif turn == 'user_second':
        match = Match(1)

        tmp = match.smart_point()
        pos_smart_x = tmp[1][0]
        pos_smart_y = tmp[1][1]
        status = tmp[2]

        match.settle(True, False)

        if False:
            match.set_peer_point((10, 4))
            match.settle(False, True)

            match.set_my_point((10, 5))
            match.settle(True, False)


            match.set_peer_point((11, 5))
            match.settle(False, True)

            match.set_my_point((9, 3))
            match.settle(True, False)

            match.set_peer_point((9, 4))
            match.settle(False, True)

            match.set_my_point((8, 4))
            match.settle(True, False)

            match.set_peer_point((10, 6))
            match.settle(False, True)

            match.set_my_point((7, 5))
            match.settle(True, False)

            match.set_peer_point((6, 6))
            match.settle(False, True)

            match.set_my_point((6, 5))
            match.settle(True, False)

            match.set_peer_point((8, 5))
            match.settle(False, True)

            match.set_my_point((7, 6))
            match.settle(True, False)

            match.set_peer_point((12, 4))
            match.settle(False, True)

            match.set_my_point((13, 3))
            match.settle(True, False)

            match.set_peer_point((11, 4))
            match.settle(False, True)

            match.set_my_point((13, 4))
            match.settle(True, False)

            match.set_peer_point((11, 3))
            match.settle(False, True)

            match.set_my_point((11, 6))
            match.settle(True, False)

            match.set_peer_point((9, 1))
            match.settle(False, True)

            match.set_my_point((10, 2))
            match.settle(True, False)

            if True:
                print "========================================  before   11, 1"
                match.print_MP_class('M', 3)
                match.print_MP_class('M', 4)
            

            match.set_peer_point((11, 1))
            match.settle(False, True)

            if True:
                print "========================================  after  11, 1"
                match.print_MP_class('M', 3)
                match.print_MP_class('M', 4)

            match.settle_back((11, 1))

            if True:
                print "========================================  back 11, 1"
                match.print_MP_class('M', 3)
                match.print_MP_class('M', 4)



        # 需要把match存储起来喔
        match_string = pickle.dumps(match)
        rds.set("Match_"+user_name, match_string)
        
        # with open("pickle-fp", "w") as f:
        #     pickle.dump(match, f)

        ret = {
            'stat': 'success',
            'x': pos_smart_x,
            'y': pos_smart_y,
            'status_type': status
        }
    else:
        ret = {
            'stat': 'error'
        }

    return HttpResponse(json.dumps(ret))

def regret(request):
    with open("pickle-fp", "r") as f:
        match = pickle.load(f)

    ret_tmp = None
    reason = "Not need or forbid!"

    if match.regret_flag == 0:
        if match.last_my_coord != None:
            match.settle(True, False)
            ret_tmp = match.settle_back(match.last_my_coord)

        if ret_tmp != None and match.last_peer_coord != None:
            ret_tmp = match.settle_back(match.last_peer_coord)

    
    if ret_tmp == None:
        ret = {
            'stat': 'error',
            'reason': reason
        }
    else:
        ret = {
            'stat': 'success'
        }
        match.regret_flag = 1

    with open("pickle-fp", "w") as f:
        pickle.dump(match, f)
        
    return HttpResponse(json.dumps(ret))

def history_print(request):
    # with open("pickle-fp", "r") as f:
    #     match = pickle.load(f)

    user_name = request.session.get('username', None)

    Redis_Pool = redis.ConnectionPool(host='127.0.0.1', port=6379, db=0)
    rds = redis.Redis(connection_pool=Redis_Pool)

    match_string = rds.get("Match_"+user_name)
    match = pickle.loads(match_string)

    print "**************************<<< H i s t o r y >>> ****************************************"
    
    print match.history_track['start'] + " First"

    for cell in  match.history_track['crd_list']:
        if cell[0] == 'my':
            print cell[1]
        else:
            print "      " + str(cell[1])

    print "****************************************************************************************"

    ret = {
        'stat': 'success',
    }

    return HttpResponse(json.dumps(ret))

def debug_print(request):
    # with open("pickle-fp", "r") as f:
    #     match = pickle.load(f)

    user_name = request.session.get('username', None)

    Redis_Pool = redis.ConnectionPool(host='127.0.0.1', port=6379, db=0)
    rds = redis.Redis(connection_pool=Redis_Pool)

    match_string = rds.get("Match_"+user_name)
    match = pickle.loads(match_string)

    print "******************************* debug_print Start *********************************************************"
    # match.print_MP_class('M', 2)
    # match.print_MP_class('M', 3)
    # match.print_MP_class('M', 4)
    # match.print_MP_Attr('M')
    print "  "
    # print "\-----------------------M***P-----------------------/"
    print "  "
    # match.print_MP_Attr('P')
    # match.print_MP_class('P', 2)
    # match.print_MP_class('P', 3)
    # match.print_MP_class('P', 4)
    # print "******************************** debug_print End ********************************************************"
    print "===>No idea: " + str(match.noidea_cnt)
    print "===>Wrong: " + str(match.wrong_cnt)
    print "===>Wrong_2: " + str(match.wrong2_cnt)
    print "===>magicsmile_cnt: " + str(match.magicsmile_cnt)
    print "===>willdie_cnt: " + str(match.willdie_cnt)
    print "===>willwin_cnt: " + str(match.willwin_cnt)
    print "===>dbg_cnt: " + str(match.dbg_cnt)
    print "===>warning: " + str(match.warning)
    print "===>LX_cnt_Total: " + str(match.LX_cnt_Total)

    print "****************************************************************************************"
    if len(match.associate_point) > 0:
        print match.associate_point
    
    ret = {
        'stat': 'success',
    }

    return HttpResponse(json.dumps(ret))
    

def userstep(request):
    user_name = request.session.get('username', None)

    pos_x = request.POST.get('x', '')
    pos_y = request.POST.get('y', '')

    Redis_Pool = redis.ConnectionPool(host='127.0.0.1', port=6379, db=0)
    rds = redis.Redis(connection_pool=Redis_Pool)

    match_string = rds.get("Match_"+user_name)
    match = pickle.loads(match_string)

    # with open("pickle-fp", "r") as f:
    #     match = pickle.load(f)

    match.set_peer_point((int(pos_x), int(pos_y)))
    # tmp = match.settle()
    tmp = match.settle(False, True)
    if tmp == "GAME_OVER":
        # time.sleep(1)
        print "**************************<<< H i s t o r y >>>(Game over! You Win!!) ****************************************"
    
        print match.history_track['start'] + " First"

        for cell in  match.history_track['crd_list']:
            if cell[0] == 'my':
                print cell[1]
            else:
                print "      " + str(cell[1])

        print "****************************************************************************************"

        ret = {
            'stat': 'success',
            'youwin': 1
        }

        # rds.delete("Match_6")
        
    else:
        # match.print_MP_Attr('M')
        # match.print_MP_Attr('P')

        tmp = match.smart_point()
        
        pos_smart_x = tmp[1][0]
        pos_smart_y = tmp[1][1]
        youlose = tmp[0]
        status = tmp[2]

        if youlose == 0:
            match.settle(True, False)

        # print "pos_smart_x: " +  str(pos_smart_x)
        # print "pos_smart_y: " +  str(pos_smart_y)
        # 需要把match存储起来喔
        match_string = pickle.dumps(match)
        rds.set("Match_"+user_name, match_string)

        match.regret_flag = 0
        
        # with open("pickle-fp", "w") as f:
        #     pickle.dump(match, f)
            

        # time.sleep(1)
        ret = {
            'stat': 'success',
            'x': pos_smart_x,
            'y': pos_smart_y,
            'youlose': youlose,
            'status_type': status
        }

        # if youlose == 1:
        #     # rds.delete("Match_6")
            

    return HttpResponse(json.dumps(ret))
