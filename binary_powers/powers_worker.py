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


def binary_powers(request, response):
    """Simple username check with 2 seconds delay"""
    msg = yield request.read()
    max_power = msgpack.loads(msg)

    res = 1
    for i in range(0, max_power):
        res *= 2
        response.write(res)

    response.close()


W = Worker()
W.run({
    "binary_powers": binary_powers
})
