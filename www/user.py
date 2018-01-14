# -*- coding:utf-8 -*-
'user info'
__autor__ = 'ZAM';

from utils import next_id;
from orm import Model, StringField, IntegerField, BooleanField, FloatField;
import time;

class User(Model):
    __table__ = 'users';

    id = StringField(primary_key=True, default = next_id, ddl='varchar(50)');
    email = StringField(ddl = 'varchar(50)');
    passwd = StringField(ddl = 'varchar(50)');
    admin = BooleanField();
    name = StringField(ddl = 'varchar(50)');
    image = StringField(ddl = 'varchar(500)');
    create_at = FloatField(default=time.time);
