# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

# Create your models here.

class userAdmin(models.Model):
    user_name = models.CharField('aa', max_length=32)

    user_nickname = models.CharField('bb', max_length=32)
    user_password = models.CharField('cc', max_length=32)
    user_email = models.EmailField()
    user_sign = models.IntegerField(default=0)
    user_gender = models.IntegerField(default=3)

    def __unicode__(self):
            return self.user_name

