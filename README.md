# HomeAssistant-GoogleHome
A python program that loads selected data from a Google Home in the network.

Right now it only loads the data, the final objective is to allow it to be loaded into [Home Assistant](https://home-assistant.io) easily.

# Credits
This is a kind of compilation of different scripts in order to make the usage process easier. The used repositories are as follows:

## Google Home Foyer API
Repository: https://gist.github.com/rithvikvibhu/952f83ea656c6782fbd0f1645059055d/

License:
```
MIT License

Copyright (c) 2020 Rithvik Vibhu

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## GHLocal API
Repository: https://rithvikvibhu.github.io/GHLocalApi/

# Requirements
## Git
For clonning the repository, git is required. Please, follow the instructions at the [official page](https://git-scm.com/).
## Python 3.5+
Other versions may work, but I'd recomment using versions greater or equal than 3.5. It can be installed as well from the [official webpage](https://www.python.org/).\
Pip is also required for installing some dependencies.
## Pip requirements
```bash
pip install gpsoauth
```
```bash
pip install python-dotenv
```