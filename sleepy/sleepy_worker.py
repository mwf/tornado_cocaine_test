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
    """Sleep for requested number of seconds"""

    msg = yield request.read()
    t = msgpack.loads(msg)
    log.debug("Sleeping for {0}...".format(t))
    sleep(t)
    log.debug("Awaken!")
    response.write("Awaken!")
    response.close()


W = Worker()
W.run({
    "sleepy_echo": sleepy_echo
})
