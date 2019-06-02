#!/usr/bin/env python2


class ReturnValueException(Exception):

    def __init__(self, value):
        self.value = value


class BreakException(Exception):
    pass


class ContinueException(Exception):
    pass
