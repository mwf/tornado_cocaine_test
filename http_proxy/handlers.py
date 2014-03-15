# -*- coding: utf-8 -*-
# author: I. Korolev
from __future__ import unicode_literals
from __future__ import print_function
from __future__ import absolute_import

from tornado.web import RequestHandler

import msgpack
import logging

from cocaine.services import Service
from cocaine.asio.engine import asynchronous

request_cnt = 0


class BaseCocaineProxy(RequestHandler):
    def prepare(self):
        """Count incoming requests for better debug"""
        global request_cnt
        request_cnt += 1
        self.request_num = request_cnt

    def log(self, data):
        logging.info("{0} - {1}".format(self.request_num, data))

    def process_synchronous(self, cocaine_service_name, cocaine_method, data):
        """Synchronous Cocaine worker handling."""
        self.log("In process_synchronous()")
        service = Service(cocaine_service_name)
        response = service.enqueue(cocaine_method, msgpack.dumps(data)).get()

        service.disconnect()
        self.log("process_synchronous() finished")
        return response

    @asynchronous
    def process_asynchronous(self, cocaine_service_name, cocaine_method, data):
        """Run selected service and get all chunks as generator."""
        self.log("In process_asynchronous()")
        service = Service(cocaine_service_name)

        chunks_g = service.enqueue(cocaine_method, msgpack.dumps(data))

        for chunk in chunks_g:
            yield umsgpack.loads(chunk)

        service.disconnect()
        self.log("process_asynchronous() finished")


class SleepSynchronous(BaseCocaineProxy):
    def get(self):
        """Sleep for requested number of seconds"""
        time = float(self.get_argument("time", 10.0))
        self.log("In get()")
        res = self.process_synchronous("sleepy", "sleepy_echo", time)
        self.write(res)
