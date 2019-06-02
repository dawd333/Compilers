#!/usr/bin/env python2

import inspect

__all__ = ['on', 'when']

def on(param_name):
  def f(fn):
    dispatcher = Dispatcher(param_name, fn)
    return dispatcher
  return f


def when(param_type):

  # f - actual decorator
  # fn - decorated method, i.e. visit
  # ff - fn gets replaced by ff in the effect of applying @when decorator
  # dispatcher is an function object
  def f(fn):
    frame = inspect.currentframe().f_back
    dispatcher = frame.f_locals[fn.__name__]
    if not isinstance(dispatcher, Dispatcher):
      dispatcher = dispatcher.dispatcher
    dispatcher.add_target(param_type, fn)
    def ff(*args, **kw):
      return dispatcher(*args, **kw)
    ff.dispatcher = dispatcher
    return ff
  return f


class Dispatcher(object):
    def __init__(self, param_name, fn):
        self.param_index = inspect.getargspec(fn).args.index(param_name)
        self.param_name = param_name
        self.targets = {}

    def __call__(self, *args, **kw):
        """
        If there is a visit function defined explicitely
        for the class of `typ`, result of the `visit` function is returned.
        If the visit function is defined for superclasse(s)
        of `typ`, a list of `visit` results for all `typ`
        superclasses is returned.
        """

        typ = args[self.param_index].__class__
        d = self.targets.get(typ)
        if d is not None:
            return d(*args, **kw)
        else:
            class_to_visitorfun = self.targets
            classes = class_to_visitorfun.iterkeys()
            results = [class_to_visitorfun[c](*args, **kw) for c in classes if issubclass(typ, c)]
            if results == []:
                print("No visitor found for class {}".format(typ))
            return results

    def add_target(self, typ, target):
        self.targets[typ] = target