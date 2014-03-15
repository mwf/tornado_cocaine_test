# -*- coding: utf-8 -*-
# author: I. Korolev
from __future__ import unicode_literals
from __future__ import print_function
from __future__ import absolute_import

import tornado.web

import msgpack
import logging

from cocaine.services import Service
from cocaine.asio.engine import asynchronous

request_cnt = 0


class BaseCocaineProxy(tornado.web.RequestHandler):
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
            yield chunk

        service.disconnect()
        self.log("process_asynchronous() finished")


class SleepSynchronous(BaseCocaineProxy):
    def get(self):
        """Sleep for requested number of seconds"""
        self.log("In get()")
        time = float(self.get_argument("time", 10.0))
        res = self.process_synchronous("sleepy", "sleepy_echo", time)
        self.write(res)


class PowersWithLogin(BaseCocaineProxy):
    @tornado.web.asynchronous
    def get(self):
        """Test 2 workers consequent work"""
        self.log("In get()")
        login = self.get_argument("login")
        power = int(self.get_argument("power", 10))
        self.log("Login: '{0}', power: '{1}'".format(login, power))

        login_response_gen = self.process_asynchronous(
            "login", "login", login)
        login_response = login_response_gen.next()
        if "error" in login_response:
            self.log("Login '{0}' is invalid!".format(login))
            self.write(login_response)
        else:
            self.log("Login '{0}' ok!".format(login))

            powers_gen = self.process_asynchronous(
                "powers", "binary_powers", power)

            for chunk in powers_gen:
                self.write("{0} ".format(chunk))
