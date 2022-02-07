#!/usr/bin/env python3

import logging

def getLogger(cl, name=None, short=True):
    if short:
        fullname = type(cl).__name__
    else:
        fullname = ".".join([type(cl).__module__, type(cl).__name__])
    if name:
        fullname += f".{name}"
    return logging.getLogger(fullname)

def getNodeLogger(node):
    return logging.getLogger(node.name)
