# -*- coding:utf-8 -*-
'Comment'
__autor__ = 'ZAM';

from utils import next_id;
from orm import Model, StringField, TextField, FloatField;
import time;

class Comment(Model):
    __table__ = 'comments';

    id = StringField(primary_key = True, default = next_id, ddl = 'varchar(50)');
    blog_id = StringField(ddl = 'varchar(50)');
    user_id = StringField(ddl = 'varchar(50)');
    user_name = StringField(ddl = 'varchar(50)');
    user_image = StringField(ddl = 'varchar(500)');
    content = TextField();
    create_at = FloatField(default = time.time);
