"""
Preserve order of keys
"""
import json
from typing import List

import yaml
from collections import OrderedDict
from yaml.resolver import BaseResolver


class StringableOrderedDict(OrderedDict):
    def __str__(self):
        return str(dict(self))

    def __repr__(self):
        return json.dumps(self)


class GitlabReferenceError(Exception):
    def __init__(self, message):
        self.message = message


class GitlabReference:
    def __init__(self, job, element, value):
        self.job = job
        self.element = element
        self.value = value
        self.location = ""

    def __repr__(self):
        if self.value:
            return "!reference [{}, {}, {}]".format(self.job, self.element, self.value)
        return "!reference [{}, {}]".format(self.job, self.element)

    def __str__(self):
        return repr(self) + f" at {self.location}"


class OrderedLoader(yaml.FullLoader):
    def __init__(self, stream, firstpass=None):
        super(OrderedLoader, self).__init__(stream)
        if firstpass is None:
            firstpass = StringableOrderedDict()
        self.first_pass = firstpass


def reference_constructor(loader: OrderedLoader, node):
    address = []
    for item in node.value:
        address.append(item.value)

    jobname = address[0]
    jobelement = address[1]
    elementvalue = None
    if len(address) > 2:
        elementvalue = address[2]

    reference = GitlabReference(jobname, jobelement, elementvalue)
    reference.location = node.start_mark
    return reference


yaml.add_constructor(u"!reference", reference_constructor)


def ordered_load(stream, preloaded=None):

    def construct_mapping(loader, node):
        loader.flatten_mapping(node)
        return StringableOrderedDict(loader.construct_pairs(node))

    OrderedLoader.add_constructor(BaseResolver.DEFAULT_MAPPING_TAG, construct_mapping)

    def context_loader(*kwargs):
        ret = OrderedLoader(*kwargs, preloaded)
        return ret

    return yaml.load(stream, context_loader)


def ordered_dump(data, **kwargs):
    """Dump data with OrderedDict content"""
    def get_dumper(*args, **x):
        dumper = yaml.Dumper(*args, **x)
        dict_repr = dumper.yaml_representers.get(dict)
        dumper.yaml_representers[OrderedDict] = dict_repr
        dumper.yaml_representers[StringableOrderedDict] = dict_repr
        return dumper
    return yaml.dump(data, Dumper=get_dumper, **kwargs, sort_keys=False)
