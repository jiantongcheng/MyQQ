# -*- coding: utf-8 -*-

from useradmin.models import user_contacts, user_news, user_chats

''' 这段代码暂时不要删除，是网上找到的动态创建数据表的方法
from django.db import models

def create_model_local(name, fields=None, app_label='', module='', options=None):
    class Meta:
        pass
    if app_label:
        setattr(Meta, 'app_label', app_label)
    if options is not None:
        for key, value in options.items():
            setattr(Meta, key, value)
    attrs = {'__module__':module, 'Meta':Meta}
    
    if fields:
        attrs.update(fields) #创建模型类对象
    return type(name.encode('utf-8','strict'), (models.Model,), attrs)

def create_contacts(username):
    RELATION_CHOICES = (
        (u'F', u'Friend'),
        (u'S', u'Stranger'),
    )
    STATUS_CHOICES = (
        (u'on', u'online'),
        (u'off', u'offline'),
        (u'lve', u'leave'),
    )

    fields = {
        'relation': models.CharField(max_length=3,choices=RELATION_CHOICES, null=True),
        'status': models.CharField(max_length=3,choices=STATUS_CHOICES),

         '__str__': lambda self: '%s %s' % (self.relation, self.status),
    }

    options = { 'ordering': ['relation', 'status'], 'verbose_name': 'contacts list',}

    tbName = "user_" + username
    myModel = create_model_local(tbName, fields, options=options, app_label='useradmin', module='useradmin.models')
    install(myModel)    # 同步到数据库中
'''

def create_user_contacts(user_name):
    class create_contacts(user_contacts):
        class Meta(user_contacts.Meta):
            db_table = 'user_' + user_name
    install(create_contacts)

def get_user_contacts(user_name):
    class get_contacts(user_contacts):
        class Meta(user_contacts.Meta):
            db_table = 'user_' + user_name
    return get_contacts

def create_user_news(user_name):
    class create_news(user_news):
        class Meta(user_news.Meta):
            db_table = 'news_' + user_name
    install(create_news)

def get_user_news(user_name):
    class get_news(user_news):
        class Meta(user_news.Meta):
            db_table = 'news_' + user_name
    return get_news

def create_user_chats(user_name):
    class create_chats(user_chats):
        class Meta(user_chats.Meta):
            db_table = 'chats_' + user_name
    install(create_chats)

def get_user_chats(user_name):
    class get_chats(user_chats):
        class Meta(user_chats.Meta):
            db_table = 'chats_' + user_name
    return get_chats

def install(custom_model):
    from django.db import connection
    from django.db.backends.base.schema import BaseDatabaseSchemaEditor
    editor = BaseDatabaseSchemaEditor(connection)
    try:
        editor.create_model(model=custom_model)
    except AttributeError as aerror:
        print(aerror)