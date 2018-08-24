#!/usr/bin/env python
import argparse
import os
from typing import Dict
try:
    from clipboard import get as clipper
except ModuleNotFoundError:
    from pyperclip import paste as clipper

from tparse.naturalThingsParser import Parser

delimiters: Dict[str, str] = {
    'tags': "#",
    'project': "[",
    'new-project': "[[",
    'notes': "::",
    'heading': "==",
    'deadline': ">",
    'checklist-items': "*",
    'due': '>',
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


def main():
    teststring = "+Buy Milk @August 24 ==Test"
    # teststring = "Task name at London on Wednesday at 6pm #Project Name ==Heading @Tag 1 @Tag 2 " \
    #              "//Additional Note !Friday *first thing *second thing *third thing"
    test2 = """
        ``
        today at 1 #Portfolio @Now
        make bread
        toast
        oranges !Friday
        at London do More
        ``
        """
    argsparsed = argparse.ArgumentParser(description='Natural Things Parser:')
    argsparsed.add_argument('-f', '--file', help='Next argument needs to be a valid file path', type=str)
    argsparsed.add_argument('-c', '--clip', help='tparse will extract text from clipboard', action='store_true')
    argsparsed.add_argument('-t', '--test', help='tparse will use some sample test strings.', action='store_true')

    args = argsparsed.parse_args()
    if args.file:
        print(f"Accessing {os.path.basename(args.file)} now.")
        string = open(args.file, 'r').read()
    elif args.clip:
        print("Accessing the clipboard now.")
        string = clipper()
    elif args.test:
        print("Using tests now.")
        string = teststring
    else:
        raise ValueError("Please enter a valid argument.")
    parser = Parser(delimiters, escapes)
    parser.parse(string)
    parser.send_to_things()


if __name__ == '__main__':
    main()
