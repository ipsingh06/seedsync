# Copyright 2017, Inderpreet Singh, All rights reserved.

import inspect


def overrides(interface_class):
    """
    Decorator to check that decorated method is a valid override
    Source: https://stackoverflow.com/a/8313042
    :param interface_class: The super class
    :return:
    """
    assert(inspect.isclass(interface_class)), "Overrides parameter must be a class type"

    def overrider(method):
        assert(method.__name__ in dir(interface_class)), "Method does not override super class"
        return method
    return overrider
