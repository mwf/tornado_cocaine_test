#!/usr/bin/env python
# -*- coding: utf-8 -*-
# author: I. Korolev
from __future__ import unicode_literals
from __future__ import print_function
from __future__ import absolute_import

from cocaine.worker import Worker
from time import sleep
import msgpack

from cocaine.logging import Logger

log = Logger()


def sleepy_echo(request, response):
    msg = yield request.read()
    msg = msgpack.loads(msg)
    log.debug("Sleeping...")
    sleep(10)
    log.debug("Returning msg back!")
    response.write(msg)
    response.close()


W = Worker()
W.run({
    "sleepy_echo": sleepy_echo
})
