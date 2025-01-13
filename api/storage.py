#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
vue-pywebview-pyinstaller:
    Author: 潘高
'''

from api.db.orm import ORM


class Storage:
    '''存储类'''

    orm = ORM()    # 操作数据库类

    def storage_get(self, key):
        '''获取关键词的值'''
        return self.orm.getStorageVar(key)

    def storage_set(self, key, val):
        '''设置关键词的值'''
        self.orm.setStorageVar(key, val)
