# Natural Language Things Parser in Python

## NOTE:

<details>
<summary>
	The following are issues with this release:
</summary>

1. Cannot recognize `Wednesday at 6` as PM or AM but returns 6 as this the day of the output.
2. Block sublines are overrides by the last element.
3. The JSON package is not accepted by *Things 3* as valid.

### Plan:

- [ ] fix issues
- [ ] make an Automator Service for applying to a file
- [ ] make an Automator Application for dragging files on to to run.
</details>
<br />

This is a port of [@pdavidsonreiler](https://github.com/pdavisonreiber/Public-Drafts-Scripts/tree/master/Things%20Parser)'s *Drafts 5* parser to Python.

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

## A More Technical Overview

The original used a combination of *Moment.js*, *Chrono.js*, and *Drafts 5* specific wrappers for the *Things 3* URL scheme and callback urls. This repository also includes a Python wrapper for *Things 3* and callback urls.

This is not a direct porting of [@pdavidsonreiler](https://github.com/pdavisonreiber/Public-Drafts-Scripts/tree/master/Things%20Parser)'s parser. This is in particular due to the nuances of JavaScript that are not possible in Python. For this reason, the code is organized as such:

1. Most importantly, all parsing functionality lives within the `Parser` class. It takes care of splitting text into parts and then delegating to `Block` or `Line` types. 
2. `Block` and `Line` types inherit common functionality from the `ParsedItem` class. This is particularly helpful in the case of `Block`s due to the *parent* line being separated from it's children architecturally rather than by call.
3. The conversion to Things elements is separated into it's own class for increased encapsulation and clarity.
