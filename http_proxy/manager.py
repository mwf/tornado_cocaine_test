#!/usr/bin/env python
# -*- coding: utf-8 -*-
# author: I. Korolev
from __future__ import unicode_literals
from __future__ import print_function
from __future__ import absolute_import

from tornado.web import Application
from tornado.ioloop import IOLoop
from tornado.httpserver import HTTPServer
from tornado.options import parse_command_line, options, define

import logging
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from http_proxy.handlers import CocaineJsonProxy

if __name__ == '__main__':
    try:
        define("debug", default=False, help="run Tornado in debug mode")
        define("host", default="0.0.0.0", help="host to listen on")
        define("port", default=8888, help="port to listen on")
        parse_command_line()

        logging.info("Tornado server started on '{0}:{1}'".format(
            options["host"], options["port"]))
        logging.info("debug = {0}".format(options["debug"]))
        logging.info("logging_level = {0}".format(
            options["logging"]))
        application = Application(
            [(r'/(\w*)/?', CocaineJsonProxy)],
            debug=options["debug"],
        )

        http_server = HTTPServer(application)
        http_server.listen(options["port"], options["host"])

        loop = IOLoop.instance()
        logging.info("Starting IOLoop")
        loop.start()
    except KeyboardInterrupt:
        logging.info("Exiting Tornado...")
