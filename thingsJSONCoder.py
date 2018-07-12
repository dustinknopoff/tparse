#!/usr/bin/env python3.6
import json
from enum import Enum
from typing import List

from dateutil import parser


# Represents the container holding the array of items to be sent.
class TJSContainer:
    def __init__(self, items):
        self.items: List[TJSModelItem] = items
        self.reveal = False

    def set_reveal(self):
        """
        Flips the boolean of opening Things on action.
        """
        self.reveal = not self.reveal

    def export(self):
        """
        :return: a Things-Callback compatible JSON String.
        """
        result = []
        for item in self.items:
            d = {'type': item.type, 'attributes': item.attributes}
            if item.operation is Operation.UPDATE:
                d['operation'] = item.operation
                d['id'] = item.id
            if self.reveal:
                d['reveal'] = True
            remove = {}
            for key in item.attributes.keys():
                if item.attributes[key] is '' or len(item.attributes[key]) == 0:
                    remove[key] = item.attributes[key]
            item.attributes = {k: v for k, v in item.attributes.items() if k not in remove}
            d['attributes'] = item.attributes
            result.append(d)
        return json.dumps(result)


class Operation(Enum):
    CREATE = 1
    UPDATE = 2


# Represents a Things Model Item
class TJSModelItem:
    def __init__(self, operation):
        self.id = ''
        self.operation = operation
        self.type = ''
        self.attributes = {}

    def add_id(self, id):
        if self.operation is Operation.update:
            self.id = id


# Represents a Things Todo
class TJSTodo(TJSModelItem):
    # Allow any element to be passed in as kwargs but filter only valid params
    def __init__(self, operation, **parameters):
        super(TJSTodo, self).__init__(operation)
        possible_params = ["title", "notes", "prepend-notes", "append-notes", "when", "deadline", "tags", "add-tags",
                           "checklist-items",
                           "prepend-checklist-items", "append-checklist-items", "list-id", "list", "heading",
                           "completed", "canceled",
                           "creation-date", "completion-date"]
        # self.attributes = {}
        self.type = 'to-do'
        for key, value in parameters.items():
            if str(key).lower() in possible_params:
                if str(value).lower() in ['true', 'false']:
                    value = bool(value)
                elif 'date' in str(key).lower():
                    value = parser.parse(value)
                self.attributes[key.lower()] = value
        # If there are no valid parameters raise an error
        if len(self.attributes.items()) == 0:
            raise InvalidParams('Please enter a valid parameter.')


# Represents a Things Project
class TJSProject(TJSModelItem):
    # Allow any element to be passed in as kwargs but filter only valid params
    def __init__(self, operation, **parameters):
        super(TJSProject, self).__init__(operation)
        possible_params = ["title", "notes", "prepend-notes", "append-notes", "when", "deadline", "tags", "add-tags",
                           "area-id", "area", "items", "completed", "canceled", "creation-date", "completion-date"]
        # self.attributes = {}
        self.type = 'project'
        for key, value in parameters.items():
            if str(key).lower() in possible_params:
                self.attributes[key.lower()] = value
        # If there are no valid parameters raise an error
        if len(self.attributes.items()) == 0:
            raise InvalidParams('Please enter a valid parameter.')


# Represents a Things Header
class TJSHeader(TJSModelItem):
    # Allow any element to be passed in as kwargs but filter only valid params
    def __init__(self, operation, **parameters):
        super(TJSHeader, self).__init__(operation)
        possible_params = ["title", "archived", "creation-date", "completion-date"]
        # self.attributes = {}
        self.type = 'heading'
        for key, value in parameters.items():
            if str(key).lower() in possible_params:
                self.attributes[key.lower()] = value
        # If there are no valid parameters raise an error
        if len(self.attributes.items()) == 0:
            raise InvalidParams('Please enter a valid parameter.')


# Represents a Things Checklist Item
class TJSChecklistItem(TJSModelItem):
    # Allow any element to be passed in as kwargs but filter only valid params
    def __init__(self, operation, **parameters):
        super(TJSChecklistItem, self).__init__(operation)
        possible_params = ["title", "completed", "canceled", "creation-date", "completion-date"]
        # self.attributes = {}
        self.type = 'checklist-item'
        for key, value in parameters.items():
            if str(key).lower() in possible_params:
                self.attributes[key.lower()] = value
        # If there are no valid parameters raise an error
        if len(self.attributes.items()) == 0:
            raise InvalidParams('Please enter a valid parameter.')


# Invalid Parameters Exception
class InvalidParams(Exception):
    pass

# kwargs = {'title': 'Fly me Away!', 'checklist-items': ['1']}
# tjs = TJSTodo(Operation.CREATE, **kwargs)
# contain = TJSContainer([tjs])
