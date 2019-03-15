# -*- coding: utf-8 -*-
"""
工具函数
"""
from __future__ import unicode_literals


def read_binary(orig, pos):     # pos从0开始
    if (orig & (1 << pos)) > 0:
        return 1
    else:
        return 0

def write_binary(orig, pos, val):
    if val == 1:
        ret = orig | (1 << pos)
    else:
        ret = orig & ~(1 << pos)

    return ret

# print read_binary(5, 0)

# print read_binary(5, 1)

# print write_binary(5, 1, 1)

# print write_binary(5, 0, 0)
