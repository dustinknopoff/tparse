#!/usr/bin/env python3.6
import pprint
import re
from datetime import timedelta
from typing import Dict

from dateutil.parser import parse

from CallbackURL import *
from thingsJSONCoder import *

delimiters: Dict[str, str] = {
    'tags': "@",
    'project': "#",
    'new-project': "+",
    'notes': "//",
    'heading': "==",
    'deadline': "!",
    'checklist-items': "*",
    'block': "``"
}

escapes: Dict[str, str] = {
    '@': '-at',
    '#': '-hash',
    '+': '-plus',
    '//': '-slash',
    '==': '-qq',
    '!': '-ex',
    '*': '-star',
    '``': '-bl'
}


# Represents common values of Blocks and Lines
class ParserItem:
    def __init__(self, string):
        self.params: Dict[str, str] = {}
        self.string: str = string


class Block(ParserItem):
    def __init__(self):
        super(ParserItem, self).__init__()
        self.lines: List[Line] = []

    def __str__(self):
        return str(self.lines)

    def fill_array(self, maximum):
        """
        Fill array of lines with params as template.
        :param maximum: Number of elements to add to list.
        """
        # Make a copy of params
        outparams = self.params
        # If there is a new project, copy project name to array as project not newProject
        if 'new-project' in self.params.keys() and self.params['new-project'] is not '':
            outparams['project'] = outparams.pop('new-project')
        for i in range(0, maximum):
            templine = Line()
            templine.params = outparams
            self.lines.append(templine)

    def override_non_none(self, parsed: Dict[str, str], index):
        """
        If subvalues in a block are different from the original, override.
        :param parsed: dict of parsed data.
        :param index: index of array
        """
        # For every key, value in the sub lines, check if they're different from the master and override
        for key, value in parsed.items():
            try:
                # Check to see if the value is empty or not equal to the master
                if value not in ('', []) and parsed[key] is not self.lines[index].params[key]:
                    self.lines[index].params[key] = value
            except KeyError:
                self.lines[index].params[key] = value
        print(f"Current parameters in self.lines at index: {index}")
        pprint.pprint(self.lines[index].params)
        print('=' * 50 + '\n\n')


class Line(ParserItem):
    def __init__(self):
        super(ParserItem, self).__init__()

    def __str__(self):
        return str(self.params)


class Parser:
    def __init__(self, delims, escapechars):
        self.delimiter: Dict[str, str] = delims
        self.delimiter.pop('block')
        self.escapechars: Dict[str, str] = escapechars
        self.items: List[Line] = []

    @staticmethod
    def __split_before(pattern, text) -> List[str]:
        """
        Found on stack overflow: splits text before delimiter is found
        :param pattern: a valid regex pattern
        :param text: text to compare to.
        """
        prev = 0
        for m in re.finditer(pattern, text):
            yield text[prev:m.start()]
            prev = m.start()
        yield text[prev:]

    def __convert_to_names(self, parsed: Dict[str, str]) -> Dict[str, str]:
        """
        Converts parsed dictionary to {name: value} instead of {delimiter: value}
        :param parsed: dict of parsed data.
        :return: updated dict of parsed data.
        """
        for key, value in self.delimiter.items():
            if value in parsed.keys():
                parsed[key] = parsed.pop(value)
        return parsed

    @staticmethod
    def __split_title_date(parsed: Dict[str, str]) -> Dict[str, str]:
        """
        Extract and parse title and date from dict of parsed data.
        :param parsed: dict of parsed data.
        :return: updated dict of parsed data.
        """
        # Temporary variable for title-date
        # print(parsed)
        string = parsed.pop('title-date')
        combned = ''
        if hasattr(string, '__iter__'):
            for i in string:
                combned += i
            string = combned
        # Parse date
        try:
            parsd = parse(string, fuzzy=True, fuzzy_with_tokens=True, default=datetime.now())
            # Make Things compatible format
            date = parsd[0].isoformat()
            if parsd[0] < datetime.now():
                date = parsd[0] + timedelta(days=7)
                date = date.isoformat()
            # Extract title from parsed tokens
            title = parsd[1][0].strip()
            # Add to dictionary
        except ValueError:
            date = ''
            title = string
        parsed['title'] = title
        parsed['when'] = date
        return parsed

    @staticmethod
    def __parse_deadline(parsed: Dict[str, str]) -> Dict[str, str]:
        """
        Convert deadline to Things Compatible date format.
        :param parsed: dict of parsed data.
        :return: updated dict of parsed data.
        """
        if 'deadline' in parsed.keys():
            parsd = parse(parsed['deadline'], fuzzy=True, default=datetime.now())
            if parsd < datetime.now():
                parsd = parsd + timedelta(days=7)
            parsed['deadline'] = parsd.isoformat()
        return parsed

    # TODO: Allow @,#, etc. to be including using escaping
    # def __escape(self, parsed: Dict[str, str]) -> Dict[str, str]:

    def parse(self, string: str):
        """
        Given a blob of text, parse and parse blocks and sentences.
        :param string: a blob of text.
        """
        paragraphs = string.split('\n\n')
        for paragraph in paragraphs:
            # Check for no block delimiter
            if len(re.findall(r'(?<=``)((.|\n)*)(?=``)', paragraph)) == 0:
                sentences = paragraph.split('\n')
                for sentence in sentences:
                    line = Line()
                    # Make a sentence and parse attributes into it's fields
                    line.string = sentence
                    line.params = self.parse_line(line.string)
                    self.items.append(line)
            else:
                paragraph = re.findall(r'(?<=``)((.|\n)*)(?=``)', paragraph)[0][0]
                block = Block()
                block.string = paragraph
                sentences = paragraph.split('\n')
                # Remove the first sentence and parse it
                first = sentences.pop(0)
                block.params = self.parse_line(first)
                # Include block line in items
                add_sentence = Line().params = block.params
                self.items.append(add_sentence)
                # Use it as the template for the rest of the sentences
                block.fill_array(len(sentences))
                for i in range(0, len(sentences)):
                    # Only change values which exist
                    # print(block.lines[i])
                    block.override_non_none(self.parse_line(sentences[i]), i)
                for line in block.lines:
                    # print(line)
                    self.items.append(line)

    def parse_line(self, string: str) -> Dict[str, str]:
        """
        Given a single line of text, extract data based on delimiters
        :param string: a single line of text.
        """
        # Allow multiple tags and checklist items
        result = {'*': [], '@': [], '==': []}
        # Split string by delimiters
        pattern = '|'.join(map(re.escape, tuple(self.delimiter.values())))
        split_list = list(self.__split_before(pattern, string))
        for i in range(0, len(split_list)):
            if i == 0:
                # The first must be title and or date
                result['title-date'] = split_list[i].strip()
            else:
                # Add to result as {delimiter: value}
                if str(split_list[i])[:2] in tuple(self.delimiter.values()):
                    if str(split_list[i])[:2] is '==':
                        result[str(split_list[i])[:2]].append(str(split_list[i])[2:].strip())
                    else:
                        result[str(split_list[i])[:2]] = str(split_list[i])[2:].strip()
                elif str(split_list[i])[:1] in tuple(self.delimiter.values()):
                    # If it can be a list, add to the list instead of overriding
                    if str(split_list[i])[:1] in ('*', '@'):
                        result[str(split_list[i])[:1]].append(str(split_list[i])[1:].strip())
                    else:
                        result[str(split_list[i])[:1]] = str(split_list[i])[1:].strip()
                else:
                    raise Exception("Impossible error.")
        # Flatten lists if there is only one element
        if len(result['*']) == 1:
            result['*'] = result['*'][0]
        if len(result['@']) == 1:
            result['@'] = result['@'][0]
        if len(result['==']) == 1:
            result['=='] = result['=='][0]
        # result = self.__escape(result)
        # Convert to names instead of delimiters as keys
        result = self.__convert_to_names(result)
        # Split the titles and dates
        result = self.__split_title_date(result)
        # Get the date from the deadline
        result = self.__parse_deadline(result)
        return result

    def send_to_things(self):
        adapter = ThingsAdapter(self.items)
        package = adapter.create()
        print("Final JSON:\n" + '=' * 50)
        pprint.pprint(package)
        cb = CallbackURL()
        cb.base_url = "things:///json?"
        cb.add_parameter("data", package)
        cb.open()


class ThingsAdapter:
    def __init__(self, items: List[Line]):
        self.items: List[Line] = items
        self.data: List[TJSModelItem] = []

    def create(self):
        # For every item
        for line in self.items:
            # If there is a new project key, make a new project and add to data
            if type(line) is dict:
                continue
            elif 'new-project' in line.params.keys() and line.params['new-project'] is not '':
                project = TJSProject(Operation.CREATE, title=line.params['new-project'])
                self.data.append(project)
            else:
                # For special types, convert to into Things Type
                if 'checklist-item' in line.params.keys():
                    arr = []
                    for checklist in line.params['checklist-item']:
                        TJSChecklistItem(Operation.CREATE, title=checklist)
                    line.params['checklist-item'] = arr
                if 'heading' in line.params.keys():
                    arr = []
                    for heading in line.params['heading']:
                        TJSHeader(Operation.CREATE, title=heading)
                    line.params['heading'] = arr
                # Convert to a Things compatible element.
                todo = TJSTodo(Operation.CREATE, **line.params)
                self.data.append(todo)
        container = TJSContainer(self.data)
        return container.export()
