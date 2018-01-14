# -*- coding:utf-8 -*-

import asyncio;
import orm;
from sqlHelper import create_pool;
import user, blog, comment;

loop = asyncio.get_event_loop()
def Test():
    print("#####################2")
    yield from create_pool(loop, user='www-blog-zam', password = 'www-blog-1990', db = 'zamblog');
    # yield from create_pool(loop, user='www-blog-zam', password = 'www-blog-1990', db = 'zamblog');
    # yield from create_pool(loop, user='root', password = 'zhouaimin1990', db = 'zamblog');
    u = user.User(name = "Test", email='test@example.com', passwd='123456', image='about:blank');
    print("#####################3")
    yield from u.save();

loop.run_until_complete(Test())
loop.run_forever()

# loop = asyncio.get_event_loop()

# SQL 连接调试
# import aiomysql;
# @asyncio.coroutine
# def test_example():
#     conn = yield from aiomysql.connect(host='127.0.0.1', port=3306,
#                                        user='www-blog-zam', password='www-blog-1990', db='awesome',
#                                        loop=loop)

#     cur = yield from conn.cursor()
#     yield from cur.execute("SELECT Host,User FROM user")
#     print(cur.description)
#     r = yield from cur.fetchall()
#     print(r)
#     yield from cur.close()
#     conn.close()

# loop.run_until_complete(test_example())