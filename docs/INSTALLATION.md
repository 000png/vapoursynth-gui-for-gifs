# Installation & Setup

Versions used:

* [Python 3.8.7 (embedded)](https://www.python.org/downloads/release/python-387/) (`Windows embeddable package (64-bit)` version)
* PyQt5 v. 5.15 (this was pip installed and ported)
* [VapourSynth Portable R52](https://github.com/vapoursynth/vapoursynth/releases) (x64 version)
* [VSRepo GUI v. 0.9.5](https://github.com/theChaosCoder/VSRepoGUI/releases)

## 1. Extract Source
If you downloaded this repo correctly, there should be a `src/bin` directory where the only things in it are:

* `vsrepogui.json`

All you need to do is extract `resources/python3.8.7.7z` into this directory. This comes with Python 3.8.7, PyQt5 v. 5.15, VapourSynth R52 (portable), and the VSRepo GUI, which we'll need for the next step.

## 2. Download Plugins
Next, we need to install some VapourSynth plugins. Luckily, the VSRepo GUI makes this easy. Go to the `src/bin` directory and run the `VSRepoGUI` application (has a pusheen icon), navigate to the **Full List** tab, and download the following (download speeds will vary):

* `descale`
* `havsfunc`
* `lsmas`
* `muvsfunc`
* `mvmulti`

Feel free to add any other plugins you want to use; that being said, my GUI only supports/generates code for certain features of the above; you'll have to add the VapourSynth code yourself in order to use other plugins and features.

## 3. Additional Downloads

It is likely you will need to install codecs to get the GUI video player to work. If you ran the application manually you'll probably see an error similar to this in the terminal:

```
DirectShowPlayerService::doRender: Unresolved error code 0x80040266
```

Installing [K-lite codecs] or something similar will solve the issue (you should only need the basic version).

### Notes

You may be familiar with the [VapourSynth Editor](https://forum.doom9.org/showthread.php?p=1688477). While this is a great application, the way its set up unfortunately seems to clash with PyQt5 as I'm using it here (tldr; it seems in the ported version both use Qt but build/reference it differently), so do NOT try to integrate this into the above `src/bin` directory. If you want to use the editor, please download it separately (meaning you might have two copies of VapourSynth).

If anyone can figure out how to get the two to play nice together _please_ let me know; but I already wasted a day on it (granted I barely know anything about any of this) so I'm not going to bother at this point :D
