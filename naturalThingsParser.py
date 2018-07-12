import re
from datetime import datetime
from typing import Dict

import parsedatetime

from thingsJSONCoder import *
from CallbackURL import *

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


# Represents common values of Blocks and Lines
class ParserItem:
    def __init__(self, string):
        self.params = {}
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


class Line(ParserItem):
    def __init__(self):
        super(ParserItem, self).__init__()

    def __str__(self):
        return str(self.params)


class Parser:
    def __init__(self, delims):
        self.delimiter: Dict[str, str] = delims
        self.delimiter.pop('block')
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
        string = parsed.pop('title-date')
        # Parse date
        cal = parsedatetime.Calendar()
        time_struct, parse_status = cal.parse(string)
        temp = datetime(*time_struct[:6])
        # Convert to ISO8601 format for Things compatibility
        date = datetime.isoformat(temp)
        # If no date is found return None
        if 'today' in string:
            date = ''
        title = string.split('on')[0]
        # Add to self.parsed
        parsed['title'] = title.strip()
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
            cal = parsedatetime.Calendar()
            time_struct, parse_status = cal.parse(parsed['deadline'])
            temp = datetime(*time_struct[:6])
            parsed['deadline'] = datetime.isoformat(temp)
        return parsed

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
                    block.override_non_none(self.parse_line(sentences[i]), i)
                for line in block.lines:
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


teststring = "Task name on Wednesday at 6pm #Project Name ==Heading @Tag 1 @Tag 2 //Additional Note !Friday " \
             "*first thing *second thing *third thing"
test2 = """
``
today at 1 #Portfolio @Now
make bread
toast
oranges !Friday
``
"""
parser = Parser(delimiters)
parser.parse(test2)
parser.send_to_things()
