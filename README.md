# Natural Language Things Parser in Python

### Plan:

- [ x] fix issues
- [ ] make an Automator Service for applying to a file
- [ ] make an Automator Application for dragging files on to to run.
</details>
<br />

This is a port of [@pdavidsonreiler](https://github.com/pdavisonreiber/Public-Drafts-Scripts/tree/master/Things%20Parser)'s *Things Parser for Drafts 5* to Python.

It currently supports near parity in syntax:

```
#Project Name @Tag Name ==Heading //Task note !Natural Language Deadline String *Checklist Item
```

Additionally, block syntax has a start and end character:

```
``
today at 5pm !Friday #Project ==Heading @Tag 1 @Tag 2 *checklist item 1 *checklist item 2 //note
task 1
task 2
task 3
``

```

[Check out the original for more examples.](https://github.com/pdavisonreiber/Public-Drafts-Scripts/tree/master/Things%20Parser)

## How to Install

Enter into your shell:

```
pip install git+https://github.com/dustinknopoff/py-thingsparser.git
```

Or:

```
git clone https://github.com/dustinknopoff/py-thingsparser
cd py-thingsparser
python install .
```

<details>
<summary>  Not available yet.</summary>
	<h3>For iOS</h3>

1. Make sure you have [Pythonista](https://itunes.apple.com/us/app/pythonista-3/id1085978097?ls=1&mt=8).
2. Install [StaSH](https://github.com/ywangd/stash).

```
import requests as r; exec(r.get('http://bit.ly/get-stash').text)
```

3. Run `launch_stach.py`.
4.  Enter the following into the StaSH console:

```
wget https://github.com/dustinknopoff/py-thingsparser/releases/download/v0.1-beta-2/tparse-0.2.tar.gz
```

5. Enter the following:

```
tar -xzf tparse-0.1.tar.gz
```

6. Go to `things_parser.py`. 
7. Add at the top of the file `import appex`. 
8. Change line 55 to `string = appex.get_text()`.

<br />
<strong>For use as a share sheet extension</strong>

Go to Settings>Share Extension Shortcuts>`+`>find and click `things_parser.py`> add `-f` as arguments> customize title and icon details> tap Done.
</details>

### Usage

```
usage: tparse.py [-h] [-f FILE] [-c] [-t]

Natural Things Parser:

optional arguments:
  -h, --help            show this help message and exit
  -f FILE, --file FILE  Next argument needs to be a valid file path
  -c, --clip            tparse will extract text from clipboard
  -t, --test            tparse will use some sample test strings.

```

## A More Technical Overview

The original used a combination of *Moment.js*, *Chrono.js*, and *Drafts 5* specific wrappers for the *Things 3* URL scheme and callback urls. This repository also includes a Python wrapper for *Things 3* and callback urls.

This is not a direct porting of [@pdavidsonreiler](https://polymaths.blog/2018/04/things-parser-two-point-o-for-drafts-5)'s parser. This is in particular due to the nuances of JavaScript that are not possible in Python. For this reason, the code is organized as such:

1. Most importantly, all parsing functionality lives within the `Parser` class. It takes care of splitting text into parts and then delegating to `Block` or `Line` types. 
2. `Block` and `Line` types inherit common functionality from the `ParsedItem` class. This is particularly helpful in the case of `Block`s due to the *parent* line being separated from it's children architecturally rather than by call.
3. The conversion to Things elements is separated into it's own class for increased encapsulation and clarity.

- [thingsJSONCoder.py](tparse/thingsJSONCoder.py) is the python wrapper for [thingsJSONCoder](https://github.com/culturedcode/ThingsJSONCoder) which is written in Swift.
- [CallbackURL.py](tparse/CallbackURL.py) is the python wrapper for [Callback URL](https://github.com/agiletortoise/drafts-documentation/wiki/CallbackURL) which is Draft's JavaScript wrapper for callback urls in Swift.

## NOTE:

The following are issues with this release:

1. Cannot recognize `Wednesday at 6` as PM or AM but returns 6 as this the day of the output.

~~2. Block sublines are overriden by the last element.~~

~~3. The JSON package is not accepted by *Things 3* as valid.~~