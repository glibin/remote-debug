#!/usr/bin/python
# -*- coding: utf-8 -*-

from tornado.options import define, options
import logging

define("port", default="8333", help="Port to run on")

define("redis_host", default="localhost", help="Redis host")
define("redis_port", default="6379", help="Redis port")
define("redis_db", default=5, help="Redis db")