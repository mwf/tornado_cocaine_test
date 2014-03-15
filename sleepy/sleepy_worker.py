#!/usr/bin/env python
# -*- coding: utf-8 -*-
# author: I. Korolev
from __future__ import unicode_literals
from __future__ import print_function
from __future__ import absolute_import

from cocaine.worker import Worker
from time import sleep

from cocaine.logging import Logger

log = Logger()


def tag_entities(request, response):
    msg = yield request.read()
    log.debug("Sleeping...")
    sleep(10)
    log.debug("Returning msg back!")
    response.write(msg)
    response.close()


W = Worker()
W.run({
    "add_object": add_object,
    "add_organism": add_organism,
    "new_attribute": new_attribute,
    "delete_object": delete_object,
    "delete_attribute": delete_attribute,
    "delete_organism": delete_organism,
    "get_attribute": get_attribute,
    "get_attributes": get_attributes,
    "get_object": get_object,
    "get_objects": get_objects,
    "get_organism": get_organism,
    "get_organisms": get_organisms,
    "get_tags": get_tags,
    "get_query": get_query,
    "get_queries": get_queries,
    "update_attribute": update_attribute,
    "update_object": update_object,
    "save_import_mapping": save_import_mapping,
    "update_import_mapping": update_import_mapping,
    "delete_import_mapping": delete_import_mapping,
    "get_import_mapping": get_import_mapping,
    "get_import_mappings": get_import_mappings,
    "untag_entities": untag_entities,
    "tag_entities": tag_entities,
})
