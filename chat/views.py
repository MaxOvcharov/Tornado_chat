# -*- coding: utf-8 -*-
import os
import json
from time import time

import aiohttp_jinja2
from aiohttp import web
from aiohttp_session import get_session
from models import users

from aiohttp import web

from settings import BASE_DIR


async def index(request):
    """
    Simple client in web browser
    :param request: request from page
    :return: response app.html file
    """
    with open(os.path.join(BASE_DIR, "chat/chat_widget/index.html")) as f:
        return web.Response(text=f.read(), content_type='text/html')


def redirect(request, router_name):
    url = request.app.router[router_name].url()
    raise web.HTTPFound(url)


def set_session(session, user_id, request):
    session['user'] = str(user_id)
    session['last_visit'] = time()
    redirect(request, 'main')


def convert_json(message):
    return json.dumps({'error': message})


class Login(web.View):

    # @aiohttp_jinja2.template('/auth/login.html')
    async def get(self):
        session = await get_session(self.request)
        if session.get('user'):
            redirect(self.request, 'main')
            return {'conten': 'Please enter email and login with password'}
        return aiohttp_jinja2.render_template('/auth/login.html', self.request,
                                              {'conten': 'Please enter email and login with password'})

    async def post(self):
        print(self.request)
        data = await self.request.post()
        user = User(self.request.db, data)
        result = await user.check_user()
        if isinstance(result, dict):
            session = await get_session(self.request)
            set_session(session, str(result['_id']), self.request)
        else:
            return web.Response(content_type='application/json', text=convert_json(result))


class SignIn(web.View):

    @aiohttp_jinja2.template('auth/sign.html')
    async def get(self, **kw):
        session = await get_session(self.request)
        if session.get('user'):
            redirect(self.request, 'main')
        return {'conten': 'Please enter your data'}

    async def post(self, **kw):
        data = await self.request.post()
        user = User(self.request.db, data)
        result = await user.create_user()
        # if isinstance(result, ObjectId):
        #     session = await get_session(self.request)
        #     set_session(session, str(result), self.request)
        # else:
        #     return web.Response(content_type='application/json', text=convert_json(result))


class SignOut(web.View):

    async def get(self, **kw):
        session = await get_session(self.request)
        if session.get('user'):
            del session['user']
            redirect(self.request, 'login')
        else:
            raise web.HTTPForbidden(body=b'Forbidden')