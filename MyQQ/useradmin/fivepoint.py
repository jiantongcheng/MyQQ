# -*- coding: utf-8 -*-
"""
投票相关
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

    magicsmile_cnt = 0
    willdie_cnt = 0
    willwin_cnt = 0

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

    def set_my_point(self, coord):
        ret = self.set_point(coord, self.My_point)
        if ret == 0:
            self.history_track['crd_list'].append(("my", coord))
        else:
            print "set_my_point fail:" + str(ret) + " coord: " + str(coord)
            self.wrong2_cnt += 1
        return ret

    def set_peer_point(self, coord):
        ret = self.set_point(coord, self.Peer_point)
        if ret == 0:
            self.history_track['crd_list'].append(("PEER", coord))
        else:
            print "set_peer_point fail:" + str(ret) + " coord: " + str(coord)
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
                if ret_str[0:5] == 'ZYYYY':
                    coord1 = self.get_coord(coord, direction, -1)
                elif ret_str[1:6] == 'YYYYZ':
                    coord1 = self.get_coord(coord, direction, 4)
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
                obj.attract_coords = attract_coords[:] 
                obj.rel_coords = rel_coords[:]
            elif ret_str[0:6] == "ZZYYYH" or ret_str[1:7] == 'HYYYZZ' or ret_str[0:7] == 'HZYYYZH':
                attr = 'G' #Guide
                if ret_str[0:6] == "ZZYYYH":
                    coord1 = self.get_coord(coord, direction, -2)
                    coord2 = self.get_coord(coord, direction, -1)
                    back_coords = self.get_coord_pack(coord, direction, (3, ))
                elif ret_str[1:7] == 'HYYYZZ':
                    coord1 = self.get_coord(coord, direction, 3)
                    coord2 = self.get_coord(coord, direction, 4)
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
                    my2 = self.My2(coord_tuple, mp.direction, None, None)
                    self.P_index[2].append(my2)
                    self.update_MP(my2)
                    self.P_Attr[my2.attr].append(my2)
                elif mp.coords[1] == coord:     #在中间断开，则不用生成My2类型
                    remove_list.append(mp)
                elif mp.coords[2] == coord:
                    remove_list.append(mp)
                    coord_list = [mp.coords[0], mp.coords[1]]
                    coord_tuple = tuple(coord_list)
                    my2 = self.My2(coord_tuple, mp.direction, None, None)
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
                    my3 = self.My3(coord_tuple, mp.direction, None, None)
                    self.P_index[3].append(my3)
                    self.update_MP(my3)
                    self.P_Attr[my3.attr].append(my3)
                elif mp.coords[1] == coord:     
                    remove_list.append(mp)
                    coord_list = [mp.coords[2], mp.coords[3]]
                    coord_tuple = tuple(coord_list)
                    my2 = self.My2(coord_tuple, mp.direction, None, None)
                    self.P_index[2].append(my2)
                    self.update_MP(my2)
                    self.P_Attr[my2.attr].append(my2)
                elif mp.coords[2] == coord:
                    remove_list.append(mp)
                    coord_list = [mp.coords[0], mp.coords[1]]
                    coord_tuple = tuple(coord_list)
                    my2 = self.My2(coord_tuple, mp.direction, None, None)
                    self.P_index[2].append(my2)
                    self.update_MP(my2)
                    self.P_Attr[my2.attr].append(my2)
                elif mp.coords[3] == coord:
                    remove_list.append(mp)
                    coord_list = [mp.coords[0], mp.coords[1], mp.coords[2]]
                    coord_tuple = tuple(coord_list)
                    my3 = self.My3(coord_tuple, mp.direction, None, None)
                    self.P_index[3].append(my3)
                    self.update_MP(my3)
                    self.P_Attr[my3.attr].append(my3)
                else:
                    None
            if len(remove_list) != 0:
                for remove_class in remove_list:
                    self.P_Attr[remove_class.attr].remove(remove_class)
                    self.P_index[4].remove(remove_class)

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
                        if ret_dict.has_key(obj.attr):
                            ret_dict[obj.attr] += 1
                        else:
                            ret_dict[obj.attr] = 1
                elif cnt == 2:  
                    #生成一个My2类型
                    coord_tuple = tuple(coord_list)
                    obj = self.My2(coord_tuple, 'S', None, None)
                    self.update_MP(obj)
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
                        if ret_dict.has_key(obj.attr):
                            ret_dict[obj.attr] += 1
                        else:
                            ret_dict[obj.attr] = 1
                elif cnt == 2:  
                    #生成一个My2类型
                    coord_tuple = tuple(coord_list)
                    obj = self.My2(coord_tuple, 'SW', None, None)
                    self.update_MP(obj)
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
                        if ret_dict.has_key(obj.attr):
                            ret_dict[obj.attr] += 1
                        else:
                            ret_dict[obj.attr] = 1
                elif cnt == 2:  
                    #生成一个My2类型
                    coord_tuple = tuple(coord_list)
                    obj = self.My2(coord_tuple, 'W', None, None)
                    self.update_MP(obj)
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
                        if ret_dict.has_key(obj.attr):
                            ret_dict[obj.attr] += 1
                        else:
                            ret_dict[obj.attr] = 1
                elif cnt == 2:  
                    #生成一个My2类型
                    coord_tuple = tuple(coord_list)
                    obj = self.My2(coord_tuple, 'WN', None, None)
                    self.update_MP(obj)
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

    def thinking_G_Peer_associate(self):
        ret = self.thinking_G_Peer_Nest(2)
        self.thinking_withdraw(2)
        return ret

    def thinking_G_AX_PG_PAX(self):
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
                    print "WolfWolf......." + str(crd)
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
        #---^_^---
        cross_dict = {}
        #考虑我方A+X和O(即能构成G)的交叉点,交集
        zw_will_set = self.get_point_setByAttr_all('ZW', self.My_point)
        g_will_set = self.get_point_setByAttr_all('G', self.My_point)
        zw_g_will_set = zw_will_set & g_will_set    #交集

        for zw_g_crd in zw_g_will_set:   #能构成ZW+G组合的坐标
            self.thinking_withdraw(1)
            #我方模拟试探下子
            self.set_my_point(zw_g_crd)
            self.associate_point.append((zw_g_crd, 1)) 
            self.settle(True, False)

            #先看对方能否通过G直接赢， 如果可以就不要这么下
            if self.thinking_G_Peer_associate() != None:    #说明这么下对方会赢，所以不要这么下
                print "thinking_G_Peer_associate is not None!!"
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
                self.set_peer_point(crd)
                self.associate_point.append((crd, 2)) 
                self.settle(False, True)
                #看我方能否直接赢
                ret = self.thinking_G_My_Nest(3)
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
        #考虑我方构成ZW的情况，对方封堵后，我方能通过G直接赢的，这个再议...........

        self.thinking_withdraw(1)       #2020.2.22添加，要注意是否有副作用

        #对方有两个A+X的情况
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
                print "WolfWolf...asdf...." + str(crd)
                return crd      
            elif len(cross_dict[crd]) == 1:
                ret_dict = self.may_build_new(crd, self.Peer_point)
                if ret_dict != None:
                    if ret_dict.has_key('W') or ret_dict.has_key('ZW'):
                        print "WolfWolf..qqq....." + str(crd)
                        return crd 
        
        #对方有A+X和O的交叉点，将会变成ZW+G的组合，我方不提前封堵就可能会输喔

        #接下去进行打分操作吧！！！
        print "thinking_G_AX_PG_PAX: step 4"
        zw_will_set = self.get_point_setByAttr_all('ZW', self.My_point)
        w_will_set = set()
        for mp in self.M_Attr['G']:
            w_will_set.add(mp.attract_coords[0])
            w_will_set.add(mp.attract_coords[1])
        pg_set = set()
        for mp in self.P_Attr['G']:
            pg_set.add(mp.attract_coords[0])
            pg_set.add(mp.attract_coords[1])
        pax_set = self.get_point_setByAttr_all('ZW', self.Peer_point)

        local_print_debug = 1
        all_set = zw_will_set | w_will_set | pg_set | pax_set   #取并集
        all_list = []   #成员也为list，list[0] 为分数, list[1]为coord
        for crd in all_set:
            pt = 0  #分数
            pt_2 = 0
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
                num = self.get_pointNum_byAttr(crd, 'W', self.My_point)
                if num == 0:
                    print "num == 0!!!!!!!!! Error! 2"
                    sys.exit()
                if local_print_debug == 1:
                    print "crd:" + str(crd) + ", w_will_set: +4*" + str(num)
                pt += num*4
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

            # pzax_num = self.get_num_ByNewAttrAndcoord('A+X', crd, self.Peer_point)
            # if pzax_num != 0:
            #     pt += pzax_num*1
            
            all_list.append([pt, crd, pt_2])

        #不考虑我方能直接赢的情况，但要考虑我方下子后对方能直接赢的情况
        while True:
            max_pt = 0
            max_pt_2 = 0
            ret_crd = None
            for crd_pt in all_list:
                print str(crd_pt[0]) + "." + str(crd_pt[2])  + " : " + str(crd_pt[1]) + "@thinking_G_AX_PG_PAX"
                if crd_pt[0] > max_pt:
                    max_pt = crd_pt[0]
                    ret_crd = crd_pt[1]
                    max_pt_2 = crd_pt[2]
                elif crd_pt[0] == max_pt:
                    if crd_pt[2] > max_pt_2:
                        max_pt = crd_pt[0]
                        ret_crd = crd_pt[1]
                        max_pt_2 = crd_pt[2]
            if ret_crd == None:
                break
            #我方模拟试探下子
            self.set_my_point(ret_crd)
            self.associate_point.append((ret_crd, 1)) 
            self.settle(True, False)

            if self.thinking_G_Peer_associate() != None:
                #说明这么下对方会赢，所以不要这么下,去看看下一个分数最高的
                self.thinking_withdraw(1)
                all_list.remove([max_pt, ret_crd, max_pt_2])  #删除最高分
                print "Select next pt which is max. discard: " + str(ret_crd)
                continue
            else:
                self.thinking_withdraw(1)
                break
            
        if ret_crd != None:
            return ret_crd

        print "thinking_G_AX_PG_PAX: step 5(None)"
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

        while True:
            max_pt = 0
            ret_crd = None
            for crd_pt in all_list:
                print str(crd_pt[0]) + ": " + str(crd_pt[1]) + "@thinking_O_ZAX_PO_PZAX"
                if crd_pt[0] > max_pt:
                    max_pt = crd_pt[0]
                    ret_crd = crd_pt[1]
            if ret_crd == None:
                break
            #我方模拟试探下子
            self.set_my_point(ret_crd)
            self.associate_point.append((ret_crd, 1)) 
            self.settle(True, False)

            if self.thinking_G_Peer_associate() != None:
                #说明这么下对方会赢，所以不要这么下,去看看下一个分数最高的
                self.thinking_withdraw(1)
                all_list.remove([max_pt, ret_crd])  #删除最高分
                print "Select next pt which is max........discard: " + str(ret_crd)
                continue
            else:
                self.thinking_withdraw(1)
                break
            
        if ret_crd != None:
            return ret_crd

        return None
        

    # 返回None表示对方没有可以通过G方式直接赢的
    def thinking_G_Peer_Nest(self, tier):
        nest = {}
        nest_cont = 0

        #这里可能也要考虑tier太大的情况，即嵌套太多，花费时间太多

        for mp in self.P_Attr['G']:
            coord_peer = mp.attract_coords[0]
            coord_block = mp.attract_coords[1]
            nest[(coord_peer, coord_block)] = True
            coord_peer = mp.attract_coords[1]
            coord_block = mp.attract_coords[0]
            nest[(coord_peer, coord_block)] = True

        if len(nest) != 0:
            # print "===> Peer nest..." + str(tier)
            for pair in nest:
                coord_peer = pair[0]
                coord_block = pair[1]
                nest_cont = 0
                # print "===> Peer...for..." + str(tier)
                # 先进行上一次循环的悔棋操作
                self.thinking_withdraw(tier)
                #---
                self.set_peer_point(coord_peer)          #对方下
                self.associate_point.append((coord_peer, tier))
                self.settle(False, True)        #整理
                #查看我方有没有W，若有,则对方需要continue一颗棋子来封堵且在对方G内的
                for mp in self.M_Attr['W']:
                    nest_cont = 1
                    # print "Find My Win...continue"
                    break
                if nest_cont == 1:
                    continue
                
                self.set_my_point(coord_block)           #我方下
                self.associate_point.append((coord_block, tier))
                self.settle(True, False)        #整理
                #查看对方有没有W，若有直接返回
                for mp in self.P_Attr['W']:
                    print "*** Find Peer Win...tier: " + str(tier) + ", coord: " + str(coord_peer)
                    print self.associate_point
                    print self.P_Attr['W'][0].coords
                    return coord_peer
                #查看我方有没有W，若有则对方可以尝试封堵,且封堵的点在对方的G内
                nest_cont = 0
                break_flag = 0
                for mp in self.M_Attr['W']:
                    if mp.other == 'WW':
                        # print "Find My Win...continue"
                        nest_cont = 1
                        break
                    else:
                        # print "--->Debug: 11"
                        crd = mp.attract_coords[0]
                        break_flag = 0
                        for my_a in self.P_Attr['G']:
                            if my_a.attract_coords[0] == crd or my_a.attract_coords[1] == crd:
                                if my_a.attract_coords[0] == crd:
                                    crd_block = my_a.attract_coords[1]
                                else:
                                    crd_block = my_a.attract_coords[0]
                                self.set_peer_point(crd)            #对方下
                                self.associate_point.append((crd, tier))
                                self.settle(False, True)                #整理
                                #查看我方有没有W，若有,则对方需要continue一颗棋子
                                for mp_b in self.M_Attr['W']:
                                    # print "Find My Win...continue"
                                    nest_cont = 1
                                    break

                                if nest_cont == 0:
                                    self.set_my_point(crd_block)                    #我方下
                                    self.associate_point.append((crd_block, tier))     
                                    self.settle(True, False)                #整理
                                
                                break_flag = 1
                                break


                        if break_flag == 0:
                            # print "Find My Win.2..continue"
                            nest_cont = 1
                            break
                        else:
                            break
                
                if nest_cont == 1:
                    continue
                #查看对方有没有ZW，若有直接返回
                for mp in self.P_Attr['ZW']:
                    print "*** Find Peer Z Win......tier: " + str(tier) + ", coord: " + str(coord_peer)
                    print self.associate_point
                    print self.P_Attr['ZW'][0].coords
                    return coord_peer
                #查看对方还有没有G的，若有再次进行嵌套
                ret = self.thinking_G_Peer_Nest(tier+1)
                self.thinking_withdraw(tier+1)  #联想撤回
                if ret != None:
                    return coord_peer    #注意这里的返回值不是ret
                else:
                    continue
        else:
            return None
        
        return None

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

        if len(point_dict) == 0:
            return None

        #接下去要给每一个封堵点进行打分，选取分数最高的那个
            #封堵后我方有1个W和1个ZW的，直接返回.....但是貌似不应该发生
        #封堵后对方至少还有1个ZW的，清分，且只有零分，放弃该点
        #封堵后我方有2个ZW的，直接返回
        #封堵后我方有一个ZW的计3分，有W的计2分,有一个G的计2分，有两个子(非D类型)的计1分
        #封堵后对方多个一个D的计2分，降级的计1分
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
            self.set_my_point(coord)
            self.associate_point.append((coord, 1)) 
            self.settle(True, False)

            if self.thinking_G_Peer_associate() != None:    #说明这么下对方会赢，所以不要这么下
                print "thinking_G_Peer_associate is not None!!"
                point_dict[coord] = 0
                continue

            #--- 联想下子之后
            # 查看对方是否还有ZW，若有我方就输咯，所以不能这么下
            for peer in self.P_Attr['ZW']:
                cont = 1
                print str(coord) + " is discard, because peer ZW again."
                point_dict[coord] = 0   #堵不住所有的ZW，清分，放弃
                break

            if cont == 1:
                continue
            # 查看我方是否有两个W/ZW，若有，我方可能就赢咯，所以应该这么下
            wzw_cnt = 0
            for mp in self.M_Attr['W']:
                wzw_cnt += 1
            for mp in self.M_Attr['ZW']:
                wzw_cnt += 1

            if wzw_cnt >= 2:
                # 这里直接返回吧
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
            print "-->point_dict: " + str(coord) + "--> " +   str(point_dict[coord])     
            if point_dict[coord] > max_point:
                ret_coord = coord
                max_point = point_dict[coord]

        if ret_coord != None:
            return ret_coord
        else:       
            #执行到这里说明对方肯定有两个ZW，且我方不能直接封堵
            dbg_cnt = 0
            dbg_cnt = len(self.P_Attr['ZW']) 
            if dbg_cnt < 2:     #不应该发生
                print "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!  Wrong!!, May be lose"
                self.wrong_cnt += 1

                return None

            #一线生机，只能寄希望于G的再次联想功能，能让对方2个ZW变为1个ZW的
            ret = self.thinking_G_My_prevent_2PZW_Nest(1)
            self.thinking_withdraw(1)
            if ret != None:
                self.magicsmile_cnt += 1
                return ret
            else:       #执行到这里，一般来说我方要输了，要死的有尊严
                self.willdie_cnt += 1
                print "==========Game will over, I lose...============"
                for coord in point_dict:
                    return coord
                
                print "!!!!!!!!!!!!!!!!!!!!!!!!  Wrong!!, May be lose"
                self.wrong_cnt += 1
                return None
            
        return None

    #这个函数里不需要判断我方能赢的情况，只要判断能将对方只剩一个ZW的情况
    def thinking_G_My_prevent_2PZW_Nest(self, tier):
        nest = {}
        nest_cont = 0

        for mp in self.M_Attr['G']:
            coord = mp.attract_coords[0]
            coord_block = mp.attract_coords[1]
            nest[(coord, coord_block)] = True
            coord = mp.attract_coords[1]
            coord_block = mp.attract_coords[0]
            nest[(coord, coord_block)] = True
        
        if len(nest) != 0:
            for pair in nest:
                coord = pair[0]
                coord_block = pair[1]
                nest_cont = 0
                break_flag = 0
                # 先进行上一次循环的悔棋操作
                self.thinking_withdraw(tier)
                #---
                self.set_my_point(coord)                    #我方下
                self.associate_point.append((coord, tier))     
                self.settle(True, False)                #整理

                self.set_peer_point(coord_block)            #对方下
                self.associate_point.append((coord_block, tier))
                self.settle(False, True)                #整理

                #对方若有W，则能用G封堵的我方进行封堵，不能封堵的或不能用G封堵的，则continue
                #统计对方ZW数量，若<=1，则说明封堵成功
                for mp in self.P_Attr['W']:
                    if mp.other == 'WW':
                        print "Find Peer Win...continue"
                        nest_cont = 1
                    else:
                        crd = mp.attract_coords[0]
                        tmp_flag = 0
                        for my_a in self.M_Attr['G']:
                            if crd in my_a.attract_coords:
                                if my_a.attract_coords[0] == crd:
                                    crd_block = my_a.attract_coords[1]
                                else:
                                    crd_block = my_a.attract_coords[0]
                                self.set_my_point(crd)                    #我方下
                                self.associate_point.append((crd, tier))     
                                self.settle(True, False)                #整理

                                self.set_peer_point(crd_block)            #对方下
                                self.associate_point.append((crd_block, tier))
                                self.settle(False, True)                #整理
                                print "--->Debug: 222"
                                tmp_flag = 1
                                break
                        if tmp_flag == 0:
                            #我方也能用非G的点进行封堵，但主动权又被对方掌握了
                            print "Find Other Win.222..continue"
                            nest_cont = 1
                    break

                if nest_cont == 1:
                    continue

                zw_cnt = len(self.P_Attr['ZW'])
                if zw_cnt <= 1:
                    return coord

                #查看我方还有没有G的，若有再次进行嵌套
                ret = self.thinking_G_My_Nest(tier+1)
                self.thinking_withdraw(tier+1)  #联想撤回
                if ret != None:
                    return coord    #注意这里的返回值不是ret
                else:
                    continue
        else:
            return None

        return None

    #只要我方有G就进行嵌套联想，直到找到能生成W或ZW的
    def thinking_G_My_associate(self):
        ret = self.thinking_G_My_Nest(1)
        self.thinking_withdraw(1)
        return ret

    def thinking_G_My_Nest(self, tier):     #tier为嵌套的层次，最小为1
        local_print_debug = 0
        
        if tier > 4:        #嵌套层次太多，计算机可能受不了
            if local_print_debug == 1:
                print "===thinking_G_My_Nest===, tier > 4, discard..."
            return None

        nest = {}
        nest_cont = 0

        for mp in self.M_Attr['G']:
            coord = mp.attract_coords[0]
            coord_block = mp.attract_coords[1]
            nest[(coord, coord_block)] = True
            coord = mp.attract_coords[1]
            coord_block = mp.attract_coords[0]
            nest[(coord, coord_block)] = True

        if len(nest) != 0:
            if local_print_debug == 1:
                print "===> My G associate...tier: " + str(tier)
            for pair in nest:
                coord = pair[0]
                coord_block = pair[1]
                nest_cont = 0
                break_flag = 0
                # 先进行上一次循环的悔棋操作
                self.thinking_withdraw(tier)

                # ww_flag = 0
                w_cnt = 0
                crd_block = 0

                #^_^
                for mp in self.P_Attr['W']:
                    if mp.other == 'WW':
                        return None     #说明这么下会输————换哪个G也没用，返回上一级联想
                    else:
                        w_cnt += 1
                        if crd_block == 0:
                            crd_block = mp.attract_coords[0]
                        else:
                            if cmp(crd_block, mp.attract_coords[0]) == 0:
                                w_cnt -= 1  #当对方两个W的封堵点是同一个时，视为一个W

                if w_cnt > 1:
                    return None     #说明这么下会输————换哪个G也没用，返回上一级联想
                elif w_cnt == 0:
                    None            #对方没有W的情况，继续往下走
                else:       # == 1 的情况
                    if cmp(crd_block, coord) == 0:
                        None        #封堵对方的点正是我方G内，就继续往下走
                    else:
                        continue     #说明这么下没结果————换一个G进行本级联想
                    
                #---
                if local_print_debug == 1:
                    print "     My G associate(tier: " + str(tier) + "), set_my_point: " + str(coord)
                self.set_my_point(coord)                    #我方下
                self.associate_point.append((coord, tier))     
                self.settle(True, False)                #整理

                if local_print_debug == 1:
                    print "     My G associate(tier: " + str(tier) + "), set_peer_point: " + str(coord_block)
                self.set_peer_point(coord_block)            #对方下
                self.associate_point.append((coord_block, tier))
                self.settle(False, True)                #整理

                #查看我方有没有W, 若有直接返回
                for mp in self.M_Attr['W']:
                    if local_print_debug == 1:
                        print "======> My G associate ** Win...tier: " + str(tier) + ", coord: " + str(coord)
                        print self.M_Attr['W'][0].coords
                    self.willwin_cnt += 1
                    if self.willwin_cnt == 1:
                        print "==========Game will over, I Win !! @thinking_G_My_Nest@W ============"
                        print self.associate_point      #打印联想路径

                    return coord

                #^_^
                w_cnt = 0
                crd_block = 0

                for mp in self.P_Attr['W']:
                    if mp.other == 'WW':
                        w_cnt = 2       #相当于两个W
                        break
                    else:
                        w_cnt += 1
                        if crd_block == 0:
                            crd_block = mp.attract_coords[0]
                        else:
                            if cmp(crd_block, mp.attract_coords[0]) == 0:
                                w_cnt -= 1  #当对方两个W的封堵点是同一个时，视为一个W

                zw_flag = 1

                if w_cnt > 1:
                    continue     #说明这么下会输————换一个G进行本级联想
                elif w_cnt == 0:
                    None            #对方没有W的情况，继续往下走
                else:       # == 1 的情况
                    coincide = 0
                    for mp in self.P_Attr['G']:
                        if cmp(crd_block, mp.attract_coords[0]) == 0 or cmp(crd_block, mp.attract_coords[1]) == 0:
                            coincide = 1
                            break

                    if coincide == 1:
                        zw_flag = 0        #封堵对方的点正是我方G内，就进行下一级联想，而忽略我方可能存在的ZW判断
                    else:           #找不到在我方G内且可以封堵对方的点
                        continue     #说明这么下没结果(否则主动权给了对方)————换一个G进行本级联想


                # #查看对方有没有W!若有，我方可以尝试封堵,且封堵的点在我方G内的
                # for mp in self.P_Attr['W']:
                #     if mp.other == 'WW':     #说明这么下对方稳赢，所以不要这么下，换一个G进行本级联想
                #         if local_print_debug == 1:
                #             print "     My G associate(tier:"+ str(tier) +"), Find Peer Win...continue"
                #         nest_cont = 1
                #     else:
                #         crd = mp.attract_coords[0]      #对方不是WW稳赢的W，应该只有一个封堵点
                #         tmp_flag = 0
                #         for my_a in self.M_Attr['G']:
                #             if crd in my_a.attract_coords:        #封堵对方的点在我方的G的attract_coords内，执行一次或零次
                #                 if my_a.attract_coords[0] == crd:
                #                     crd_block = my_a.attract_coords[1]
                #                 else:
                #                     crd_block = my_a.attract_coords[0]

                #                 if local_print_debug == 1:
                #                     print "     My G associate(tier: " + str(tier) + "), (special:PW) set_my_point: " + str(crd)
                #                 self.set_my_point(crd)                    #我方下
                #                 self.associate_point.append((crd, tier))     
                #                 self.settle(True, False)                #整理

                #                 if local_print_debug == 1:
                #                     print "     My G associate(tier: " + str(tier) + "), (special:PW) set_peer_point: " + str(crd_block)
                #                 self.set_peer_point(crd_block)            #对方下
                #                 self.associate_point.append((crd_block, tier))
                #                 self.settle(False, True)                #整理
                #                 if local_print_debug == 1:
                #                     print "--->Debug: 2 asdf"
                #                 #查看我方有没有W, 若有直接返回
                #                 for mp_b in self.M_Attr['W']:
                #                     if local_print_debug == 1:
                #                         print "======> My G associate **** Win...tier: " + str(tier) + ", (special:PW) coord: " + str(coord)
                #                         print self.associate_point
                #                         print self.M_Attr['W'][0].coords
                #                     print "==========Game will over, I Win !! @thinking_G_My_Nest@PW 1 ============"
                #                     self.willwin_cnt += 1
                #                     return coord

                #                 # #这里可能还得判断我方有ZW，且对方没有W的情况，这估计我方将要赢
                #                 # if len(self.M_Attr['ZW']) > 0 and len(self.P_Attr['W']) == 0:
                #                 #     print "==========Game will over, I Win !! @thinking_G_My_Nest@PW 2 ============"
                #                 #     self.willwin_cnt += 1
                #                 #     return coord


                #                 # 这里可能还得考虑对方有没有W的情况, 头有点大........
                #                 for mp_c in self.P_Attr['W']:
                #                     #若真出现这种情况，再研究吧..........头大
                #                     print "<----******-----Something need consider!-----*****------>"
                #                     self.wrong_cnt += 100
                #                     break

                #                 tmp_flag = 1
                #                 break

                #         if tmp_flag == 0:       #说明封堵对方的点不在我方的G...内，也就没有必要再次嵌套
                #             if local_print_debug == 1:
                #                 print "     My G associate(tier:"+ str(tier) +"), (special:PW) need stop..continue"
                #             nest_cont = 1
                #     break

                # if nest_cont == 1:
                #     continue            #说明这么下没结果，换一个G进行本级联想

                if zw_flag == 1:
                    #查看我方有没有ZW，若有直接返回
                    for mp in self.M_Attr['ZW']:
                        if local_print_debug == 1:
                            print "======> My G associate ***ZW*** Z Win...tier: " + str(tier) + ", coord: " + str(coord)
                            print self.M_Attr['ZW'][0].coords
                            
                        self.willwin_cnt += 1
                        if self.willwin_cnt == 1:
                            print "==========Game will over, I Win !! @thinking_G_My_Nest@ZW============"
                            print self.associate_point      #打印联想路径

                        return coord

                #查看我方还有没有G的，若有再次进行嵌套
                ret = self.thinking_G_My_Nest(tier+1)
                self.thinking_withdraw(tier+1)  #联想撤回
                if ret != None:
                    return coord    #注意这里的返回值不是ret
                else:
                    continue
        else:
            return None

        return None
        

    def thinking_withdraw(self, tier):
        while len(self.associate_point) != 0:
            last_handle = self.associate_point[-1]
            if last_handle[1] == tier:
                # print "---> nest...back..." + str(tier)
                self.settle_back(last_handle[0])
                self.associate_point.pop()
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
        ret = self.thinking_G_My_associate()
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

        # 6. 我方G 或 我方构建ZW 或封堵对方G 或阻止对方构建ZW
        # 6.1 封堵对方G/G有交叉或G/A+X有交叉的情况
        # -- 我方G和G/A+X有交叉的情况这里不考虑，因为在thinking_G_My_associate中已经考虑过了
        # 6.3 我方A+X和A+X有交叉的情况，这样我方就能构建两个ZW
        # 6.4 其他的用打分机制,封堵对方两个A+X有交叉的优先级比PG要高
        print "===========>thingking: 6: G/AX/PG/PAX.............................................."
        ret = self.thinking_G_AX_PG_PAX()
        if ret != None:
            return ('6: G/AX/PG/PAX', ret)

        print "===========>thingking: 7: AO/ZAX/PAO/PZAX.............................................."
        ret = self.thinking_O_ZAX_PO_PZAX()
        if ret != None:
            return ('7: AO/ZAX/PAO/PZAX', ret)

        print "==>Sorry! I have no idea.............................................."
        self.noidea_cnt += 1
        # self.print_MP_class('M', 2)
        # self.print_MP_class('M', 3)
        # self.print_MP_class('M', 4)
        # print "\***-----------M--P-----------***/"
        # self.print_MP_class('P', 2)
        # self.print_MP_class('P', 3)
        # self.print_MP_class('P', 4)

        for mp in self.M_Attr['A+X']:
            return ('NO IDEA', mp.attract_coords[0])

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
            # random_num = random.randint(1,8)
            # if random_num == 1:
            #     coord = (7, 7)      #正中间
            # elif random_num == 2:
            #     coord = (5, 5)
            # elif random_num == 3:
            #     coord = (5, 9)
            # elif random_num == 4:
            #     coord = (9, 5)
            # elif random_num == 5:
            #     coord = (9, 9)
            # else:
                coord = (7, 7)      #正中间
        elif self.last_my_coord == None:    #由敌方下第一个子，我方下第二个
            x = self.last_peer_coord[0]
            y = self.last_peer_coord[1]
            if x == 0 or x == limit or y == 0 or y == limit:
                coord = (7, 7)      #对方在不正经得下棋，不予理会
            # elif x == 7 and y == 7:
            #     coord = (7, 8)
            # elif x == 7 and y == 7:
            #     coord = (7, 8)
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
            print "Smart coord: " + str(coord)
            print "Smart type: " + status

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
    match.print_MP_Attr('M')
    print "  "
    print "\-----------------------M***P-----------------------/"
    print "  "
    match.print_MP_Attr('P')
    # match.print_MP_class('P', 2)
    # match.print_MP_class('P', 3)
    # match.print_MP_class('P', 4)
    print "******************************** debug_print End ********************************************************"
    print "===>No idea: " + str(match.noidea_cnt)
    print "===>Wrong: " + str(match.wrong_cnt)
    print "===>Wrong_2: " + str(match.wrong2_cnt)
    print "===>magicsmile_cnt: " + str(match.magicsmile_cnt)
    print "===>willdie_cnt: " + str(match.willdie_cnt)
    print "===>willwin_cnt: " + str(match.willwin_cnt)

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
        match.print_MP_Attr('M')
        match.print_MP_Attr('P')

        tmp = match.smart_point()
        
        pos_smart_x = tmp[1][0]
        pos_smart_y = tmp[1][1]
        youlose = tmp[0]
        status = tmp[2]

        if youlose == 0:
            match.settle(True, False)

        print "pos_smart_x: " +  str(pos_smart_x)
        print "pos_smart_y: " +  str(pos_smart_y)
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
