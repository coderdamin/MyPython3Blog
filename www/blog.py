# -*- coding:utf-8 -*-
'Blog Instance'
__autor__ = 'ZAM';
from utils import next_id;
from orm import Model, StringField, IntegerField, TextField, FloatField;
import time;

class Blog(Model):
    __table__ = 'Blogs';

    id = StringField(primary_key = True, default=next_id, ddl='varchar(50)');
    user_id = StringField(ddl='varchar(50)');
    user_name = StringField(ddl = 'varchar(50)');
    user_image = StringField(ddl = 'varchar(500)');
    name = StringField(ddl='varchar(50)');
    summary = StringField(ddl='varchar(200)');
    content = TextField();
    create_at = FloatField(default=time.time);
