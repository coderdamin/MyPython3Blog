# -*- coding:utf-8 -*-
'Router List'
__autor__ = 'ZAM';

from webcore import get, post;
from user import User;
from blog import Blog;
from comment import Comment;
from utils import next_id, check_admin, text2html, get_page_index;
from config import configs;
from aiohttp import web;
import logging;
import time;
import hashlib, base64;
import json;
import markdown2;

from apis import Page, APIError, APIValueError, APIPermissionError, APIResourceNotFoundError;
from constant import _RE_EMAIL, _RE_SHA1;

COOKIE_NAME = 'awesession';
_COOKIE_KEY = configs.session.Secret;

def user2cookie(user, max_age):
    '''
    Generate cookie str by user.
    '''
    expires = str(int(time.time() + max_age));
    s = '%s-%s-%s-%s'%(user.id, user.passwd, expires, _COOKIE_KEY);
    L = [user.id, expires, hashlib.sha1(s.encode('utf-8')).hexdigest()];
    return '-'.join(L);

def generateResponseToSetCookie(user):
    r = web.Response();
    r.set_cookie(COOKIE_NAME, user2cookie(user, 86400), max_age=86400, httponly=True);
    return r;

def generateResponseToNotifyAboutCookie(user):
    r = generateResponseToSetCookie(user);
    user.passwd='******';
    r.content_type='application/json';
    r.body=json.dumps(user, ensure_ascii=False).encode('utf-8');
    return r;

# async def index(request):
@get('/')
async def index(*, request, page='1'):
    logging.info('<handler get> index(%s)'%str(request));
    page_index = get_page_index(page);
    num = await Blog.findNumber('count(id)');
    page = Page(num);
    if num == 0:
        blogs = ();
    else:
        blogs = await Blog.findAll(orderBy='create_at desc', limit=(page.offset, page.limit));
    return {
        '__template__' : 'blogs.html',
        'page' : page,
        'blogs' : blogs
    };

@get('/register')
def register(request):
    logging.info('<handler get> register');
    return {
        '__template__' : 'register.html'
    };

@get('/signin')
def signin(request):
    logging.info('<handler get> signin');
    return {
        '__template__' : 'signin.html'
    };

@get('/signout')
def signout(request):
    referer = request.headers.get('Referer');
    r = web.HTTPFound(referer or '/');
    r.set_cookie(COOKIE_NAME, '-deleted-', max_age=0, httponly=True);
    logging.info('user signed out.');
    return r;

@get('/blog/{id}')
async def get_blog(*, id, request):
    logging.info('<handler get> get_blog %s'%id);
    blog = await Blog.find(id);
    comments = await Comment.findAll('blog_id=?', [id], orderBy='create_at desc');
    for c in comments:
        c.html_content = text2html(c.content);
    blog.html_content = markdown2.markdown(blog.content);
    return {
        '__template__' : 'blog.html',
        'blog' : blog,
        'comments' : comments
    };

@get('/manage/blogs/create')
def manage_create_blog(request):
    logging.info('<handler get> manage_create_blog');
    return {
        '__template__' : 'manage_blog_edit.html',
        'id' : '',
        'action' : '/api/blogs'
    };

@get('/manage/blogs')
def manage_blogs(*, page='1'):
    return {
        '__template__' : 'manage_blogs.html',
        'page_index' : get_page_index(page)
    };

@get('/manage/blogs/edit')
def manage_edit_blogs(*, id):
    return {
        '__template__' : 'manage_blog_edit.html',
        'id' : id,
        'action' : '/api/blogs/%s' % id
    };

@get('/manage/comments')
def manage_comments(*, page='1'):
    return {
        '__template__' : 'manage_comments.html',
        'page_index' : get_page_index(page)
    };

@get('/manage/users')
def manage_users(*, page='1'):
    return {
        '__template__' : 'manage_users.html',
        'page_index' : get_page_index(page)
    };

'''
APIS
'''
@get('/api/users')
async def api_get_users(*, page='1'):
    page_index = get_page_index(page);
    num = await User.findNumber('count(id)');
    p = Page(num, page_index);
    if num == 0:
        return dict(page=p, users=());
    users = await User.findAll(orderBy='create_at desc', limit=(p.offset, p.limit));
    return dict(page=p, users=users);

@post('/api/users')
async def api_register_user(*, email, name, passwd):
    if (not name or not name.strip()):
        raise APIValueError('name');
    elif (not email or not _RE_EMAIL.match(email)):
        raise APIValueError('email');
    elif (not passwd or not _RE_SHA1.match(passwd)):
        raise APIValueError('passwd');
    users = await User.findAll('email=?', (email));
    if (len(users) > 0):
        raise APIError('register:failed', 'email', 'Email is already in use.');
    uid = next_id();
    sha1_passwd = '%s:%s'%(uid, passwd);
    user = User(id=uid, name=name.strip(), email=email, passwd=hashlib.sha1(sha1_passwd.encode('utf-8')).hexdigest()
        , image="http://www.gravatar.com/avatar/%s?d=mm&s=120"%hashlib.md5(email.encode('utf-8')).hexdigest());
    await user.save();
    #make session cookie:
    return generateResponseToNotifyAboutCookie(user);

@post('/api/authenticate')
async def authenticate(*, email, passwd):
    if not email:
        raise APIValueError('email', 'Invalid email');
    elif not passwd:
        raise APIValueError('passwd', 'Invalid password');
    users = await User.findAll('email=?', (email));
    if len(users)==0:
        raise APIValueError('email', 'Email not exist.');
    user=users[0];
    #check passwd:
    sha1 = hashlib.sha1();
    sha1.update(user.id.encode('utf-8'));
    sha1.update(b':');
    sha1.update(passwd.encode('utf-8'));
    if sha1.hexdigest() != user.passwd:
        raise APIValueError('passwd', 'Invalid password');
    #authenticate ok, set cookie:
    return generateResponseToNotifyAboutCookie(user);

@get('/api/blogs/{id}')
async def api_get_blog(*, id):
    logging.info('<handler get> api_get_blog id->%s'%id);
    blog = await Blog.find(id);
    return blog;

@post('/api/blogs/{id}')
async def api_modify_blog(id, request, *, name, summary, content):
    check_admin(request.__user__);
    if not name or not name.strip():
        raise APIValueError('name', 'name cannot be empty.');
    if not summary or not summary.strip():
        raise APIValueError('summary', 'summary cannot be empty.');
    if not content or not content.strip():
        raise APIValueError('content', 'content cannot be empty.');
    blog = await Blog.find(id);
    blog.name = name.strip();
    blog.summary = summary.strip();
    blog.content = content.strip();
    await blog.update();
    return blog;

@post('/api/blogs')
async def api_create_blog(request, *, name, summary, content):
    check_admin(request.__user__);
    if not name or not name.strip():
        raise APIValueError('name', 'name cannot be empty.');
    if not summary or not summary.strip():
        raise APIValueError('summary', 'summary cannot be empty.');
    if not content or not content.strip():
        raise APIValueError('content', 'content cannot be empty.');
    blog = Blog(user_id=request.__user__.id, user_name=request.__user__.name, user_image=request.__user__.image
        , name = name, summary = summary, content = content);
    await blog.save();
    return blog;

@get('/api/blogs')
async def api_blogs(*, page='1'):
    page_index = get_page_index(page);
    num = await Blog.findNumber('count(id)');
    p = Page(num, page_index);
    if num == 0:
        return dict(page=p, blogs=());
    blogs = await Blog.findAll(orderBy='create_at desc', limit=(p.offset, p.limit));
    return dict(page=p, blogs=blogs);

@post('/api/blogs/{id}/delete')
async def api_delete_blogs(id, request):
    check_admin(request.__user__);
    blog = await Blog.find(id);
    if blog:
        await blog.remove();
    return dict(id = id);

@get('/api/comments')
async def api_get_comments(*, page='1'):
    page_index = get_page_index(page);
    num = await Comment.findNumber('count(id)');
    p = Page(num, page_index);
    if num == 0:
        return dict(page=p, comments={});
    comments = await Comment.findAll(orderBy='create_at desc', limit=(p.offset, p.limit));
    return dict(page=p, comments=comments);

@post('/api/blogs/{blog_id}/comments')
async def api_add_comments(blog_id, request, *, content):
    user = request.__user__;
    if user is None:
        raise APIPermissionError('Please signin first.');
    if not(content and content.strip()):
        raise APIValueError('content');
    blog = await Blog.find(blog_id);
    if blog is None:
        raise APIResourceNotFoundError('Blog');
    comment = Comment(blog_id=blog.id, user_id=user.id, user_name=user.name, user_image=user.image, content=content.strip());
    await comment.save();
    return comment;

@post('/api/comments/{id}/delete')
async def api_delete_comment(id, request):
    # user = request.__user__;
    # if user is None:
    #     raise APIPermissionError('Please signin first.');
    check_admin(request.__user__);
    comment = await Comment.find(id);
    if comment is None:
        raise APIResourceNotFoundError('comment');
    # if comment.user_id == request.__user__.id:
    #     return None;
    await comment.remove();
    return dict(id=id);

