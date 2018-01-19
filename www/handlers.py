# -*- coding:utf-8 -*-
'Router List'
__autor__ = 'ZAM';

from webcore import get, post;
from user import User;
import logging;

# @get("/blog/{id}")
# def get_blog(id):
#     pass;
#     # return {
#     #     '__template__': 'blogs.html',
#     #     'id': id
#     # }

# @get('/api/comments')
# def api_comments(*, page='1'):
#     pass;

@get('/')
async def index(request):
    logging.info('<handler get> index(%s)'%str(request));
    users = await User.findAll();
    return {
        '__template__' : 'test.html',
        'users' : users
    };