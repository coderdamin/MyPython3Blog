# -*- coding:utf-8 -*-
'Utils'
__autor__ = 'ZAM';

import time, uuid;
import hashlib;
import logging;
from config import configs;
_COOKIE_KEY = configs.session.Secret;

def next_id():
    return '%015d%s000'%(int(time.time() * 1000), uuid.uuid4().hex);

async def cookie2user(cookie_str):
    '''
    Parse cookie and load user if cookie is valid.
    '''
    if not cookie_str:
        return None;
    try:
        L = cookie_str.split('-');
        if len(L) != 3:
            return None;
        uid, expires, sha1 = L;
        if int(expires) < time.time():
            return None;
        from user import User;
        user = await User.find(uid);
        if user is None:
            return None;
        s = '%s-%s-%s-%s'%(uid, user.passwd, expires, _COOKIE_KEY);
        if sha1 != hashlib.sha1(s.encode('utf-8')).hexdigest():
            logging.info('invalid sha1');
            return None;
        user.passwd = '******';
        return user;
    except Exception as e:
        logging.exception(e);
        return None;

def check_admin(user):
    if (user is None) or (not user.admin):
        from apis import APIPermissionError;
        raise APIPermissionError();

def text2html(text):
    # lines = map(lambda s: '<p>%s</p>'%(s.replact('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;'), filter(lambda s: s.strip() != '', text.split('\n'))));
    lines = map(lambda s: '<p>%s</p>' % s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;'), filter(lambda s: s.strip() != '', text.split('\n')))
    return ''.join(lines);

def get_page_index(page_str):
    p = 1;
    try:
        p = int(page_str);
    except ValueError as e:
        pass
    if p < 1:
        p = 1;
    return p;
