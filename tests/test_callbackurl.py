from things_parser.CallbackURL import CallbackURL
import pytest


def test_add_param():
    cbu = CallbackURL()
    cbu.add_parameter('change', '3')
    assert cbu.parameters.pop('change') is '3'
