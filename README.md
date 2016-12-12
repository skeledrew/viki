# VIKI Speech Recognition

## Purpose of this application

This application uses the Uberi/speech_recognition (https://github.com/Uberi/speech_recognition)
Library for performing speech recognition, with support for several engines and APIs, online and offline.
Speech recognition engine/API support:
- CMU Sphinx (works offline)
- Google Speech Recognition
- Wit.ai
- Houndify API
- IBM

## Requirements
To use all of the functionality of the library, you should have:
- Python 2.6, 2.7, or 3.3+ (required)
- Hy (currently optional)
- PyAudio 0.2.9+ (required only if you need to use microphone input, Microphone)
- PocketSphinx (required only if you need to use the Sphinx recognizer, recognizer_instance.recognize_sphinx)
- Wit.ai key (if you want to use wit.ai for speech recognition)
- Uberi/speech_recognition

### Python
The first software requirement is Python 2.6, 2.7, or Python 3.3+. This is required to use the library.
The application itself requires Python 3.3+

### hy
You need to install hy language. You can Install hy from GitHub with 
```sh
$ pip install git+https://github.com/hylang/hy.git.
```

### PyAudio
PyAudio is required because microphone will be used as input. PyAudio version 0.2.9+ is required, as earlier versions have overflow issues with recording on certain machines.
The installation instructions are quite good as of PyAudio v0.2.9. For convenience, they are summarized below:
- On Windows, install PyAudio using Pip: execute in a terminal.
```sh
$ pip install pyaudio 
```
- On Debian-derived Linux distributions (like Ubuntu and Mint), install PyAudio using APT: execute sudo apt-get install python-pyaudio python3-pyaudio in a terminal. (I am not able to install it on my Ubuntu)

If the version in the repositories is too old, install the latest release using Pip: execute 
```sh
$sudo apt-get install portaudio19-dev python-all-dev python3-all-dev 
$sudo pip install pyaudio (replace pip with pip3 if using Python 3).
```
- On OS X, install PortAudio using Homebrew: brew install portaudio && sudo brew link portaudio. Then, install PyAudio using Pip: pip install pyaudio.
- On other POSIX-based systems, install the portaudio19-dev and python-all-dev (or python3-all-dev if using Python 3) packages (or their closest equivalents) using a package manager of your choice, and then install PyAudio using Pip: pip install pyaudio (replace pip with pip3 if using Python 3).

PyAudio wheel packages for 64-bit Python 2.7, 3.4, and 3.5 on Windows and Linux are included for convenience, under the third-party/ directory in the repository root. To install, simply run pip install wheel followed by pip install ./third-party/WHEEL_FILENAME (replace pip with pip3 if using Python 3) in the repository root directory.

### PocketSphinx-Python (for Sphinx users)
PocketSphinx-Python is required if and only if you want to use the Sphinx recognizer (recognizer_instance.recognize_sphinx).
PocketSphinx-Python wheel packages for 64-bit Python 2.7, 3.4, and 3.5 on Windows are included for convenience, under the third-party/ directory. To install, simply run in the SpeechRecognition folder.
```sh
$pip install wheel 
$pip install ./third-party/WHEEL_FILENAME(replace pip with pip3 if using Python 3) 
```
On Linux and other POSIX systems (such as OS X), follow the instructions under "Building PocketSphinx-Python from source" in Notes on using PocketSphinx for installation instructions.
Note that the versions available in most package repositories are outdated and will not work with the bundled language data. Using the bundled wheel packages or building from source is recommended.
See Notes on using PocketSphinx for information about installing languages, compiling PocketSphinx, and building language packs from online resources. This document is also included under reference/pocketsphinx.rst.

## Wit.ai server and client access token
Wit.ai is an API that makes it easy for developers to build bots, applications and devices that you can talk or text to. You can use it for backend engine for speech recognition. However, you need set up account and use server access token. You can use your Github account to log in Wit.ai. Then you can start with “My First App”. Once you are in “My First App”, you can click Settings on the top right. In API Details, you can find your server access token. It is a 32-character uppercase alphanumeric string. You can also find your client access token below server access token.

## Houndify Client_ID and Client_key
Houndify is a platform that allows anyone to add smart, voice enabled, conversational interfaces to anything with an internet connection. You can try it free. Use your email to create an account and log in. You can find that you have a client already under my clients list. Click the name of client, you will enter client page. Click “Overview & API Keys” on the left side of the screen. Under API Credentials, you can find Client ID and Client Key.  

## Uberi/speech_recognition
Uberi/speech_recognition is required. To install Uberi/speech_recognition, you can use following command:
```sh
$pip install SpeechRecognition. 
```
To quickly try it out, run python -m speech_recognition after installing.

## Quickstart
Now you are ready to use viki.
```sh
~~$ hy viki.hy~~
$ python3 voice.py commands.py
```

## Licence
    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as published
    by the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.

