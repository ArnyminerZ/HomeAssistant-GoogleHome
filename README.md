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