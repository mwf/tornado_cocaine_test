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

valid_users = ["vasya", "petya", "kolya"]


def login(request, response):
    """Simple username check with 2 seconds delay"""
    msg = yield request.read()
    username = msgpack.loads(msg)
    log.debug("Username: {0}".format(username))
    # log.debug("Sleeping for 2 seconds...")
    # sleep(2)
    if username in valid_users:
        response.write("ok")
    else:
        response.write("error: user '{0}' not valid!")
    response.close()


W = Worker()
W.run({
    "login": login
})
