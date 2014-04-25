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
    """Sleep for requested number of seconds

    Request is a msgpacked dict:
    {
        "time": float,   # time in seconds to sleep for
        "verbose": bool  # if True - send back passed seconds every second
    }

    """
    msg = yield request.read()
    params = msgpack.loads(msg)

    t = params["time"]
    log.debug("Sleeping for {0} seconds".format(t))
    if params.get("verbose", False):
        for i in range(1, int(t)+1):
            sleep(1)
            response.write(i)

        # sleep for the rest of time, < 1 second
        sleep(t - int(t))
    else:
        sleep(t)
    log.debug("Awaken!")
    response.write("Awaken!")
    response.close()


W = Worker()
W.run({
    "sleepy_echo": sleepy_echo
})
