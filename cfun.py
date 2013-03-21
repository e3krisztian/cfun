'''
Simple function composition syntactic sugar

Data flow direction between functions is marked
by the << , >> and | (pipe) operator.

Composition is started by the word `cfun` - short for `compose function`

e.g.

cfun >> itemgetter('output') >> attrgetter('processed.count')

is an unnamed equivalent of this function:

def processed_count(data):
    return data['output'].processed.count

'''

from functools import partial

__all__ = ['cfun']


# Implementation notes:
#
# Partial is used instead of monkey pathing on individual functions
# because it is not possible to monkey patch special method names.
# See:
# http://docs.python.org/2/reference/datamodel.html#new-style-special-lookup
# http://docs.python.org/3/reference/datamodel.html#special-lookup
#
# Another (more expensive?) option would be wrapper classes with
# __call__ methods.
#
# Idea of using partial is taken from
# http://stackoverflow.com/questions/2279423/python-function-composition
#
# For pipe-ish implementations with some lazyness
# look here (found by `pip search pipe`):
#
# https://github.com/0101/pipetools
# http://dev-tricks.net/pipe-infix-syntax-for-python
# http://www.trinhhaianh.com/stream.py/
# http://jwilk.net/software/python-grapevine
# https://pypi.python.org/pypi/DAGPype
#
# This module has no support for lazyness.


class _LeftFlowing(partial):
    '''result << data'''

    def __lshift__(self, other):
        def f(*args, **kwargs):
            return self(other(*args, **kwargs))

        return _LeftFlowing(f)


class _RightFlowing(partial):
    '''data >> result'''

    def __rshift__(self, other):
        def f(*args, **kwargs):
            return other(self(*args, **kwargs))

        return _RightFlowing(f)

    __or__ = __rshift__


class _Compositor(object):

    def __lshift__(self, func):
        # <<
        return _LeftFlowing(func)

    def __rshift__(self, func):
        # >>
        return _RightFlowing(func)

    __or__ = __rshift__


cfun = _Compositor()
