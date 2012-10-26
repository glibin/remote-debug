#!/usr/bin/python
# -*- coding: utf-8 -*-

import tornado.ioloop
import tornado.web
import tornado.httpserver
import tornado.gen
import tornadoredis
from tornado.options import define, options
from tornado.escape import json_encode, json_decode

import config

import os
import time
import logging
import hashlib
import shutil

from datetime import datetime

class BaseHandler(tornado.web.RequestHandler):
    @property
    def aredis(self):
        return self.application.aredis

    @property
    def log(self):
        return self.application.log

    def compute_etag(self):
        return None

class StatusHandler(BaseHandler):
    def get(self):
        self.finish({'status' : 'ok'})

class LogHandler(BaseHandler):
    def get(self):
        type = self.get_argument('type', 'raw')
        data = self.get_argument('msg', '')
        key = self.get_argument('key')
        timestamp = datetime.fromtimestamp(int(self.get_argument('t', (time.time() * 1000))) / 1000)

        if type == 'json':
            data = json_decode(data)

        self.log.info("[{time}, {key}] {msg}".format(time = timestamp, key = key, msg = data))

        callback = self.get_argument('callback', None)
        if callback is not None:
            self.set_header('Content-Type', 'text/javascript')
            self.finish('{callback}(true)'.format(callback = callback))
        else:
            self.finish({})

class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/", StatusHandler),
            (r"/log", LogHandler),
            ]

        settings = dict(
            debug = True
        )
        tornado.web.Application.__init__(self, handlers, **settings)

        self.log = logging

        self.aredis = tornadoredis.Client(port = int(options.redis_port), selected_db = options.redis_db)
        self.aredis.connect()

if __name__ == "__main__":

    tornado.options.parse_command_line()

    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(int(options.port), '127.0.0.1')

    tornado.ioloop.IOLoop.instance().start()