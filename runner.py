from naturalThingsParser import *
import pyperclip
import argparse
import os

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

if __name__ == '__main__':
    teststring = "Task name at London on Wednesday at 6pm #Project Name ==Heading @Tag 1 @Tag 2 " \
                 "//Additional Note !Friday *first thing *second thing *third thing"
    test2 = """
    ``
    today at 1 #Portfolio @Now
    make bread
    toast
    oranges !Friday
    -at London do More
    ``
    """
    argsparsed = argparse.ArgumentParser(description='Natural Things Parser:')
    argsparsed.add_argument('-f', '--file', help='Next argument needs to be a valid file path', type=str)
    argsparsed.add_argument('-c', '--clip', help='NTP will extract text from clipboard', action='store_true')
    argsparsed.add_argument('-t', '--test', help='NTP will use some sample test strings.', action='store_true')

    args = argsparsed.parse_args()
    if args.file:
        print(f"Accessing {os.path.basename(args.file)} now.")
        string = open(args.file, 'r')
    elif args.clip:
        print("Accessing the clipboard now.")
        string = pyperclip.paste()
    elif args.test:
        print("Using tests now.")
        string = test2
    else:
        raise ValueError("Please enter a valid argument.")
    parser = Parser(delimiters, escapes)
    parser.parse(string)
    parser.send_to_things()
