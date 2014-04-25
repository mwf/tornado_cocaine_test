# -*- coding: utf-8 -*-
# author: I. Korolev
from __future__ import unicode_literals
from __future__ import print_function
from __future__ import absolute_import

import tornado.web

import simplejson as json
import msgpack
import logging

from cocaine.services import Service
from cocaine.asio.engine import asynchronous
from cocaine.exceptions import ChokeEvent

from http_proxy.formatted_traceback import formatted_tb

log = logging.getLogger()
request_cnt = 0


def pretty_json(stuff):
    """Get pretty formated json-dumped data."""
    kwargs = dict(ensure_ascii=False, indent=2, encoding="utf8")
    return json.dumps(stuff, **kwargs)


class RunServiceMixin(object):
    @asynchronous
    def run_service(self, cocaine_service_name, cocaine_event, data,
                    attr_name, serializer=msgpack):
        """Run selected service and get all chunks.

        Arguments:
            cocaine_service_name -- service to run,
            cocaine_event -- Cocaine worker's event name for enqueue,
            data -- data, serialized for service,
            serializer -- serializer to use.

        Chunks are saved to self.<attr_name>

        """
        service = Service(cocaine_service_name)
        try:
            chunk = yield service.enqueue(
                cocaine_event,
                serializer.dumps(data))

            chunks = [chunk]
            try:
                while True:
                    ch = yield
                    chunks.append(ch)
            except ChokeEvent as err:
                log.debug("Out of chunks!")

            setattr(self, attr_name, chunks)
        except Exception, e:
            log.error('Unexpected error in run_service()\n{0}'.format(
                formatted_tb()))
            log.info("Cocaine service: '{0}', event: '{1}', data: {2}".format(
                cocaine_service_name, cocaine_event, data))
            log.info("Reraising...")
            raise
        finally:
            service.disconnect()


class BaseHandler(tornado.web.RequestHandler):
    @property
    def mimetype(self):
        header = self.request.headers.get('Content-Type', '')
        content_type = header.split(";")
        return content_type[0]

    def get_json_data(self):
        """Get dict from json-dumped request body."""
        if self.mimetype == 'application/json':
            try:
                return json.loads(self.request.body)
            except json.JSONDecodeError as e:
                log.error("wrong json body format:\n{0}".format(e[0]))
                raise tornado.web.HTTPError(400)
        else:
            log.error("wrong Content-Type header")
            raise tornado.web.HTTPError(400)

    def prepare(self):
        """Count incoming requests for better debug."""
        global request_cnt
        request_cnt += 1
        self.request_num = request_cnt

    def log(self, data):
        logging.info("{0} - {1}".format(self.request_num, data))

    def write_chunk(self, data):
        """Implements chunked data write.

        Transfer-Encoding set to "chunked" automatically

        """
        self.write(data)
        self.flush()


class CocaineJsonProxy(BaseHandler, RunServiceMixin):
    @tornado.web.asynchronous
    def post(self, service_name):
        """Authenticate user by login as a key and run selected service.

        Incoming json should have following structure:

        {
            "key": str,  # login
            "method": str,  # worker's event to enqueue
            "params": <worker params dict>
        }

        """
        self.json_data = self.get_json_data()
        self.log(pretty_json(self.json_data))

        self.start_async(service_name)

    @asynchronous
    def start_async(self, service_name):
        """A trigger method to start Cocaine workers asynchronously."""
        self.log("In start_async()")

        yield self.run_service(cocaine_service_name="login",
                               cocaine_event="login",
                               data=self.json_data["key"],
                               attr_name="login_result")

        if "error" in self.login_result[0]:
            self.log("Login '{0}' is invalid!".format(self.json_data["key"]))
            res = dict(result=self.login_result)
            self.write(pretty_json(res))
            self.finish()
        else:
            self.log("Login '{0}' ok!".format(self.json_data["key"]))
            yield self.process_stream(cocaine_service_name=service_name,
                                      cocaine_event=self.json_data["method"],
                                      data=self.json_data["params"])
        self.log("Finished start_async()")

    @asynchronous
    def process_stream(self, cocaine_service_name, cocaine_event, data,
                       serializer=msgpack):
        """Run selected Cocaine service and stream json response.

        Arguments:
            cocaine_service_name -- service to run,
            cocaine_event -- Cocaine worker's event name for enqueue,
            data -- data, serialized for service,
            serializer -- serializer to use.

        """
        self.log("In process_stream()")
        self.set_header("Content-Type", "application/json; charset=UTF-8")

        service = Service(cocaine_service_name)

        self.write_chunked('{"result":[')
        try:
            chunk = yield service.enqueue(
                cocaine_event,
                serializer.dumps(data))

            self.log("Got first chunk!")
            self.write_chunked(pretty_json(chunk))

            try:
                while True:
                    chunk = yield
                    wr = pretty_json(chunk)
                    self.write_chunked("," + wr)
            except ChokeEvent as err:
                log.debug("Out of chunks!")

            self.write_chunked("]}")
        except Exception as err:
            log.error('Unexpected error in run_service()\n{0}'.format(
                formatted_tb()))
            log.info("Cocaine service: '{0}', event: '{1}', data: {2}".format(
                cocaine_service_name, cocaine_event, data))
            log.info("Reraising...")
            raise
        finally:
            service.disconnect()
            self.log("process_powers() finished")
            self.finish()
        self.log("process_powers() finished")
