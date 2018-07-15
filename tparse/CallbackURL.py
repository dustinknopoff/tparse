#!/usr/bin/env python3.6
import webbrowser
from urllib.parse import urlencode, quote_plus


class CallbackURL:
    def __init__(self):
        self.base_url = ''
        self.parameters = {}

    def add_parameter(self, key, value):
        """
        Adds a key and value to be send with the url.
        :param key: A valid key for this url.
        :param value: Any value for this key.
        NOTE: URL specifics on valid key/values is not enforced.
        """
        self.parameters[key] = value

    def open(self):
        """
        URL encodes baseurl and parameters and opens in default webbrowser.
        """
        # print(self.parameters)
        url = self.base_url + urlencode(self.parameters, quote_via=quote_plus, encoding='utf8')
        url = url.replace('%3A', ':').replace('%2C', ',').replace('+', '%20')
        print(url)
        webbrowser.open(url)

    def set_baseurl(self, url):
        self.base_url = url
