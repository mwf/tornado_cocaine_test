# -*- coding: utf-8 -*-
# author: I. Korolev
from __future__ import unicode_literals
from __future__ import print_function
from __future__ import absolute_import

from tornado.web import RequestHandler

import msgpack
import logging

from cocaine.services import Service

request_cnt = 0


class CocaineProxySync(RequestHandler):
    def process_synchronous(self, cocaine_service_name):
        """Synchronous Cocaine worker handling."""
        service = Service(cocaine_service_name)
        response = service.enqueue(
            "sleepy_echo",
            msgpack.dumps("Hello, sleepy!")).get()

        self.write(response)
        service.disconnect()
        self.finish()

    def log(self, data):
        logging.info("{0} - {1}".format(self.request_num, data))

    def get(self):
        request_cnt += 1
        self.request_num = request_cnt
        self.log("In get()")
        cocaine_service_name = "sleepy"
        self.process_synchronous(cocaine_service_name)
