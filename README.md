# Alternative open.mp Launcher
A fork of omp-server-browser which allows you to add favourites, connect to servers while using the omp-launcher, aimed to work on wine.

## But why?

Currently (as far as i am aware), there isn't a launcher that supports open.mp and works on wine, and therefore there isn't a way to comfortably use a gui for samp with open-mp on linux.

[Video Example](https://www.youtube.com/watch?v=gCzvV8IPk10)

Servers are provided from [open.mp/servers](https://www.open.mp/servers)

<kbd><img src="screenshots/Screenshot-1.png" alt="Screenshot-1" border="0"></kbd>

<kbd><img src="screenshots/Screenshot-2.png" alt="Screenshot-2" border="0"></kbd>

### Download
- [Releases](https://github.com/dzmtrzz/alt-omp-launcher/releases)

## Version 1.1.5
- Added a favourites tab
- You can now use a config file launcher-settings.json in your GTA San Andreas User Files folder to specify the path for the game, omp launcher and your username

## Version 1.1.0
- Dark Mode theme


## Development
Build on your machine:
  - Install Python 3.8.2 (old version for program compatibility with Windows 7)
  - Open Command Prompt and cd into the repo directory
  ```bash
    cd alt-omp-launcher
  ```
  - Install dependencies
  ```bash
    python -m pip install -r requirements.txt PyInstaller
  ```
  - Build
  ```bash
    PyInstaller main.spec
  ```

The executable file goes to the `./dist` folder.
