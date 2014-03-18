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
from cocaine.exceptions import ChokeEvent

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

    def process_asynchronous(self, cocaine_service_name, cocaine_method, data):
        """Run selected service and get all chunks as generator."""
        self.log("In process_asynchronous()")
        service = Service(cocaine_service_name)

        chunks_g = service.enqueue(cocaine_method, msgpack.dumps(data))

        yield chunks_g
        service.disconnect()
        self.log("process_asynchronous() finished")

    def write_chunk(self, data):
        """Implements chunked data write.

        Transfer-Encoding set to "chunked" automatically

        """
        self.write(data)
        self.flush()


class SleepSynchronous(BaseCocaineProxy):
    def get(self):
        """Sleep for requested number of seconds"""
        self.log("In get()")
        time = float(self.get_argument("time", 10.0))
        res = self.process_synchronous("sleepy", "sleepy_echo", time)
        self.write(res)
        self.finish()


class PowersWithLogin(BaseCocaineProxy):
    @tornado.web.asynchronous
    def get(self):
        """Test 2 workers consequent work"""
        self.log("In get()")
        login = self.get_argument("login")
        power = int(self.get_argument("power", 10))
        self.log("Login: '{0}', power: '{1}'".format(login, power))

        self.start_async(login, power)

    @asynchronous
    def start_async(self, login, power):
        self.log("In start_async()")
        service = Service("login")

        login_response = yield service.enqueue("login", msgpack.dumps(login))

        service.disconnect()
        self.log("got login!")

        if "error" in login_response:
            self.log("Login '{0}' is invalid!".format(login))
            self.write(login_response)
            self.finish()
        else:
            self.log("Login '{0}' ok!".format(login))
            self.process_powers("powers", "binary_powers", power)

        self.log("Finished start_async()")

    @asynchronous
    def process_powers(self, cocaine_service_name, cocaine_method, data):
        self.log("In process_powers()")
        service = Service(cocaine_service_name)

        chunk = yield service.enqueue(cocaine_method, msgpack.dumps(data))

        if chunk:
            try:
                while True:
                    ch = yield
                    self.log(ch)
                    self.write_chunk("{0} ".format(ch))

            except ChokeEvent as err:
                pass
        else:
            self.write_chunk("no data!")

        service.disconnect()
        self.log("process_powers() finished")
        self.finish()


class DoublePowers(BaseCocaineProxy):
    @tornado.web.asynchronous
    def get(self):
        """Test 2 workers consequent work"""
        self.log("In get()")

        # When cocaine will be based on Futures it'd be easy:
        # yield self.powers_4()
        # yield self.powers_8()

        # What should I do now??

    @asynchronous
    def start_async(self):
        self.log("In start_async()")

        self.powers_4().then(self.powers_8)

        self.log("Foo")

        self.write_chunk(self.powers_4_res)
        self.write_chunk("\n")
        self.write_chunk(self.powers_8_res)
        self.finish()

    @asynchronous
    def powers_4(self):
        self.log("In powers_4()")
        service = Service("powers")

        chunk = yield service.enqueue("binary_powers", msgpack.dumps(4))

        chunks = [chunk]
        try:
            while True:
                ch = yield
                chunk.append(ch)

        except ChokeEvent as err:
            pass

        self.powers_4_res = chunks
        service.disconnect()
        self.log("powers_4() finished")

    @asynchronous
    def powers_8(self):
        self.log("In powers_8()")
        service = Service("powers")

        chunk = yield service.enqueue("binary_powers", msgpack.dumps(8))

        chunks = [chunk]
        try:
            while True:
                ch = yield
                chunk.append(ch)

        except ChokeEvent as err:
            pass

        self.powers_8_res = chunks
        service.disconnect()
        self.log("powers_8() finished")
