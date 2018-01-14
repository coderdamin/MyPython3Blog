# -*- coding:utf-8 -*-
"ORM for My SQL"
__autor__ = "ZAM";

import logging;
import asyncio;
from sqlHelper import *;

def create_args_string(num):
    L = [];
    for n in range(num):
        L.append('?');
    return ','.join(L);

class Field(object):
    def __init__(self, name, column_type, primary_key, default):
        self.name = name;
        self.column_type = column_type;
        self.primary_key = primary_key;
        self.default = default;

    def __str__(self):
        return "<%s, %s:%s>"%(self.__class__.__name__, self.column_type, self.name);

class StringField(Field):
    def __init__(self, name = None, primary_key = False, default = None, ddl='varchar(100)'):
        super(StringField, self).__init__(name, ddl, primary_key, default);

class IntegerField(Field):
    def __init__(self, name = None, primary_key = False, default = 0):
        super().__init__(name, "bigint", primary_key, default);

class BooleanField(Field):
    def __init__(self, name = None, default = False):
        super().__init__(name, 'boolean', False, default);

class FloatField(Field):
    def __init__(self, name = None, primary_key = False, default = 0.0):
        super().__init__(name, 'real', primary_key, default);

class TextField(Field):
    def __init__(self, name = None, default = None):
        super().__init__(name, 'text', False, default);

class ModelMetaclass(type):
    def __new__(cls, name, bases, attrs):
        if (name == 'Model'):
            return type.__new__(cls, name, bases, attrs);

        tableName = attrs.get('__table__', None) or name;
        logging.info('found model:%s (table:%s)'%(name, tableName));
        mappings = dict();
        fields = [];
        primaryKey = None;
        for k, v in attrs.items():
            if isinstance(v, Field):
                logging.info('found mapping:%s ==> %s'%(k, v));
                mappings[k] = v;
                if v.primary_key:
                    if primaryKey:
                        raise RuntimeError("Duplicate primary key for field: %s"%k);
                    primaryKey = k;
                else:
                    fields.append(k);
        if not primaryKey:
            raise RuntimeError("Primary Key not Found");
        for k in mappings.keys():
            attrs.pop(k);

        escaped_fields = list(map(lambda f:'`%s`'%f, fields));
        attrs['__mappings__'] = mappings;
        attrs['__table__'] = tableName;
        attrs['__primary_key__'] = primaryKey;
        attrs['__fields__'] = fields;
        attrs['__select__'] = 'select `%s`, %s from `%s`'%(primaryKey, ','.join(escaped_fields), tableName);
        attrs['__insert__'] = 'insert into `%s` (%s, `%s`) values (%s)'%(tableName, ','.join(escaped_fields), primaryKey, create_args_string(len(escaped_fields) + 1));
        attrs['__update__'] = 'update `%s` set %s where `%s`=?'%(tableName, ','.join(map(lambda f:'`%s`=?'%(mappings.get(f).name or f), fields)), primaryKey);
        attrs['__delete__'] = 'delete from `%s` where `%s`=?'%(tableName, primaryKey);
        
        return type.__new__(cls, name, bases, attrs);

class Model(dict, metaclass=ModelMetaclass):
    def __init__(self, **kw):
        super(Model, self).__init__(**kw);
    
    def __getattr__(self, key):
        try:
            return self[key];
        except KeyError:
            raise AttributeError(r"'Model' object has no attribute '%s'"%key);
    
    def __setattr__(self, key, value):
        self[key] = value;
    
    def getValue(self, key):
        return getattr(self, key, None);

    def getValueOrDefault(self, key):
        value = getattr(self, key, None);
        if value is None:
            field = self.__mappings__[key];
            if field.default is not None:
                value = field.default() if callable(field.default) else field.default;
                logging.debug('using default value forr %s : %s'%(key, str(value)));
                # 此处有坑，可能只是某一次需要用default
                setattr(self, key, value);
        return value;

    @classmethod
    async def find(self, pk):
        'find object by primary key.'
        rs = await select('%s where `%s`=?'%(self.__select__, cls.__primary_key__), [pk], 1);
        if (len(rs) == 0):
            return None;
        return self(**rs[0]);
    
    @classmethod
    async def findAll(self, where = None, args = None, **kw):
        'find all objects by where clause.'
        sql = [self.__select__];
        if where:
            sql.append('where ');
            sql.append(where);
        if args is None:
            args = [];
        orderBy = kw.get('orderBy', None);
        if orderBy:
            sql.append('order by ');
            sql.append(orderBy);
        limit = kw.get('limit', None);
        if limit is not None:
            sql.append('limit ');
            if isinstance(limit, int):
                sql.append('?');
                args.append(limit);
            elif isinstance(limit, tuple) and (len(limit) == 2):
                sql.append('?,?');
                args.extend(limit);
            else:
                raise ValueError('Invalid limit value: %s'%str(limit));
        rs = await select(''.join(sql), args);
        return [self(**r) for r in rs];

    @classmethod
    async def findNumber(self, where = None, args = None):
        'find number by where clause.'
        sql = [self.__select__];
        if where:
            sql.append('where ');
            sql.append(where);
        if args is None:
            args = [];
        rs = await select(''.join(sql), args);

    @classmethod
    async def update(self):
        args = list(map(self.getValue, self.__fields__));
        args.append(self.getValue(self.__primary_key__));
        rows = await execute(self.__update__, args);
        if (rows != 1):
            logging.warn('failed to update by primary key: affected rows: %s'%rows);

    @classmethod
    async def remove(self):
        args = [self.getValue(self.__primary_key__)];
        rows = await execute(self.__delete__, args);
        if (rows != 1):
            logging.warn('failed to remove by primary key: affected rows: %s'%rows);

    @asyncio.coroutine
    def save(self):
        args = list(map(self.getValueOrDefault, self.__fields__));
        args.append(self.getValueOrDefault(self.__primary_key__));
        rows = yield from execute(self.__insert__, args);
        if (rows != 1):
            logging.warn('Failed to Insert record: affected rows: %s'%rows);

