#!/usr/bin/env python3
import logging

def getLogger(cl, name=None):
    fullname = ".".join([type(cl).__module__, type(cl).__name__])
    if name:
        fullname += f".{name}"
    return logging.getLogger(fullname)
