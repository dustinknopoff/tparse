import pytest
from tparse.thingsJSONCoder import *


def check_exception():
    with pytest.raises(InvalidParams):
        check = TJSHeader(james='blue', operation=Operation.CREATE)


def make_checklist():
    kwargs = {
        'title': 'Go to mall',
        'completed': '9-7-16',
        'canceled': 'false',
        'creation-date': '5-3-17',
        'completion-date': ''
    }
    check = TJSChecklistItem(operation=Operation.CREATE, **kwargs)
    for key, value in check.attributes.items():
        assert value is kwargs[key]


def make_checklist_missing_args():
    kwargs = {
        'title': 'Go to mall',
        'completed': '9-7-16',
        'canceled': 'false',
        'creation-date': '5-3-17',
    }
    check = TJSChecklistItem(operation=Operation.CREATE, **kwargs)
    for key, value in check.attributes.items():
        assert value is kwargs[key]