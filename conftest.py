from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import inspect
import os
import pytest
import unittest

import matplotlib
matplotlib.use('agg')

from matplotlib import default_test_modules
from matplotlib.testing.decorators import ImageComparisonTest


IGNORED_TESTS = {
    'matplotlib': [
        'test_sankey',
        'test_skew',
        'test_ttconv',
        'test_usetex',
    ],
}


def blacklist_check(path):
    head, tests_dir = os.path.split(path.dirname)
    if tests_dir != 'tests':
        return True
    head, top_module = os.path.split(head)
    return path.purebasename in IGNORED_TESTS.get(top_module, [])


def whitelist_check(path):
    head, tests_dir = os.path.split(path.dirname)
    head, top_module = os.path.split(head)
    test_name = '.'.join([top_module, tests_dir, path.purebasename])
    return test_name not in default_test_modules


COLLECT_FILTERS = {
    'none': lambda _: False,
    'blacklist': blacklist_check,
    'whitelist': whitelist_check,
}


def is_nose_class(cls):
    return any(name in ['setUp', 'tearDown']
               for name, _ in inspect.getmembers(cls))


def pytest_addoption(parser):
    parser.addoption('--collect-filter', action='store',
                     choices=COLLECT_FILTERS, default='whitelist',
                     help='filter tests during collection phase')


def pytest_configure(config):
    matplotlib._called_from_pytest = True


def pytest_unconfigure(config):
    matplotlib._called_from_pytest = False


def pytest_ignore_collect(path, config):
    if path.ext == '.py':
        collect_filter = config.getoption('--collect-filter')
        return COLLECT_FILTERS[collect_filter](path)


def pytest_pycollect_makeitem(collector, name, obj):
    if inspect.isclass(obj):
        if issubclass(obj, ImageComparisonTest):
            # Workaround `image_compare` decorator as it returns class
            # instead of function and this confuses pytest because it crawls
            # original names and sees 'test_*', but not 'Test*' in that case
            return pytest.Class(name, parent=collector)

        if is_nose_class(obj) and not issubclass(obj, unittest.TestCase):
            # Workaround unittest-like setup/teardown names in pure classes
            setup = getattr(obj, 'setUp', None)
            if setup is not None:
                obj.setup_method = lambda self, _: obj.setUp(self)
            tearDown = getattr(obj, 'tearDown', None)
            if tearDown is not None:
                obj.teardown_method = lambda self, _: obj.tearDown(self)
            setUpClass = getattr(obj, 'setUpClass', None)
            if setUpClass is not None:
                obj.setup_class = obj.setUpClass
            tearDownClass = getattr(obj, 'tearDownClass', None)
            if tearDownClass is not None:
                obj.teardown_class = obj.tearDownClass

            return pytest.Class(name, parent=collector)
