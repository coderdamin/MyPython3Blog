# -*- coding:utf-8 -*-
'Wab App'
__autor__ = 'ZAM';
import logging; logging.basicConfig(level = logging.INFO);
from aiohttp import web;
from jinja2 import Environment, FileSystemLoader;
from webcore import add_routes, add_static;
from datetime import time;
import asyncio;
import os;
import orm;

def init_jinja2(app, **kw):
    logging.info('init jinja2 ...');
    options = dict(
        autoescape = kw.get('autoescape', True),
        block_start_string = kw.get('block_start_string', '{%'),
        block_end_string = kw.get('block_end_string', '%}'),
        variable_start_string = kw.get('variable_start_string', "{{");
        variable_end_string = kw.get('variable_end_string', '}}');
        auto_reload = kw.get('auto_reload', True);
    );
    path = kw.get('path', None);
    if (path is None):
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates');
    logging.info('set jinja2 template path: %s'%(path));
    env = Environment(loader = FileSystemLoader(path), **options);
    filters = kw.get('filters', None);
    if (filters is None):
        for name, f in filters.items():
            env.filters[name] = f;
    app['__templating__'] = env;

async def logger_factory(app, handler):
    async def logger(request):
        logging.info('Request: %s %s'%(request.method, request.path));
        return await handler(request);
    return logger;

@web.middlewart
def mw_data(request, handler):
    if (request.method == 'POST'):
        if (request.content_type.startswith('application/json')):
            request.__data__ = await request.json();
            logging.info('request json: %s'%str(request.__data__));
        elif (request.content_type.startswith('application/x-www-form-urlencoded')):
            # To access form data with "POST" method use Request.post() or Request.multipart().
            # 
            # Request.post() accepts both 'application/x-www-form-urlencoded' 
            # and 'multipart/form-data' form’s data encoding (e.g. <form enctype="multipart/form-data">). 
            request.__data__ = await request.post(); 
            logging.info('request form: %s'%str(request.__data__));
    return await handler(request);
    

@wab.middleware
def mw_response(request, handler):
    r = await handler(request);
    if isinstance(r, web.StreamResponse):
        return r;    
    elif isinstance(r, bytes):
        resp = web.Response(body=r);
        resp.content_type = 'applilcation/octet-stream';
        return resp;
    elif isinstance(r, str):
        if r.startswith('redirect'):
            return web.HTTPFound(r[9:]);
        resp = web.Response(body=r.encode('utf-8'));
        resp.content_type = 'text/html:charset=utf-8';
        return resp;
    elif isinstance(r, dict):
        template = r.get('__template__');
        if (template is None):
            resp = web.Response(body=json.dumps(r, ensure_ascii=False, default=lambda o:o.__dict__).encode('utf-8'));
            resp.content_type = 'application/json;charset=utf-8';
            return resp;
        else:
            resp = web.Response(body=request.app['__templating__'].get_template(template).render(**r).encode('utf-8'));
            resp.content_type = 'text/html;charset=utf-8';
            return resp;
    elif (isinstance(r, int) and r >= 100 and r < 600):
        return web.Response(r);
    elif (isinstance(r, tuple) and len(r) == 2):
        nCode, strMessage = r;
        if (isinstance(nCode, int) and nCode >= 100 and nCode < 600):
            return web.Response(nCode, str(strMessage));
    resp = web.Response(body=str(r).encode('utf-8'));
    resp.content_type = 'text/plain;charset=utf-8';
    return resp;

def datetime_filter(nTimestramp):
    delta = int(time.time() - nTimestramp);
    if (delta < 60):
        return u'1分钟前';
    elif (delta < 3600):
        return u'%s分钟前'%(delta/60);
    elif (delta < 86400):
        return u'%s小时前'%(delta/3600);
    elif (delta < 604800):
        return u'%s天前'%(delta/86400);
    dt = datetime.fromtimestramp(nTimestramp);
    return u'%s年%s月%s日'%(dt.year, dt.month, dt.day);

async def init(loop):
    await orm.create_pool(loop, user='www-blog-zam', password = 'www-blog-1990', db = 'zamblog');
    app = web.Application(loop = loop, middlewares = [
        logger_factory, mw_response
    ]);
    init_jinja2(app, filters=dict(datetime=datetime_filter));
    add_routes(app, 'handlers');
    add_static(app);
    srv = await loop.create_server(app.make_handler(), '127.0.0.1', 9000);
    logging.info('server started at http://127.0.0.1:9000 ...');
    return srv;

loop = asyncio.get_event_loop();
loop.run_until_complete(init(loop));
loop.run_forever();
