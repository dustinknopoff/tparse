# Natural Language Things Parser in Python

## NOTE: JSON Data is currently not functional

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

## A More Technical Overview

The original used a combination of *Moment.js*, *Chrono.js*, and *Drafts 5* specific wrappers for the *Things 3* URL scheme and callback urls. This repository also includes a Python wrapper for these as well.

This is not a direct porting of [@pdavidsonreiler](https://github.com/pdavisonreiber/Public-Drafts-Scripts/tree/master/Things%20Parser)'s parser. This is in particular due to the nuances of JavaScript that are not possible in Python. For this reason, the code is organized as such:

1. Most importantly, all parsing functionality lives within the `Parser` class. It takes care of splitting text into parts and then delegating to `Block` or `Line` types. 
2. `Block` and `Line` types inherit common functionality from the `ParsedItem` class. This is particularly helpful in the case of `Block`s due to the *parent* line being separated from it's children architecturally rather than by call.
3. The conversion to Things elements is separated into it's own class for increased encapsulation and clarity.
