# Google Home for Home Assistant

## Manual Installation

First, install the required dependencies, so you will have fewer problems when installing into Home Assistant. In my
case, the command is as follows, but may vary for your installation:

```shell
python3.8 -m pip install requests==2.23.0 glocaltokens==0.1.4
```

Then, you can clone this repo in any dir you want, `~`, for example, with:

```shell
git clone https://github.com/ArnyminerZ/HomeAssistant-GoogleHome.git
```

After that, copy the `googlehome` dir inside the cloned repo to the `custom_components`
directory of your Home Assistant config path (usually `~/.homeassistant`). Do:

```shell
cp -r HomeAssistant-GoogleHome/custom_components/googlehome ~/.homeassistant/custom_components
```

Then, add the following tag to your Home Assistant's `configuration.yaml` file:

```yaml
googlehome:
```

# Credits

This is a kind of compilation of different scripts in order to make the usage process easier. The used repositories are
as follows:

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

## GLocalTokens

Repository: https://github.com/leikoilja/glocaltokens