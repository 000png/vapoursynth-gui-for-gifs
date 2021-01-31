#!./bin/python.exe
"""
FFMPEG Settings window
"""
import os
import copy
import json
from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QPushButton, QLabel

from lib.utils.GlobalConstants import WORK_DIR
from lib.utils.PyQtUtils import generateRow, generateTextEntry, clearAndSetText, generateMessageBox

HISTORY_SETTINGS = os.path.join(WORK_DIR, 'ffmpeg_settings.json')

class FfmpegSettingsWindow(QMainWindow):
    """ FFMPEG settings window """
    #DEFAULT_TRIM_FLAGS = "-vcodec libx264 -preset ultrafast -pix_fmt yuv420p"
    DEFAULT_TRIM_FLAGS = "-vcodec libvpx -acodec libvorbis -preset ultrafast"
    DEFAULT_PNG_FLAGS = ""
    DEFAULT_MOV_FLAGS = "-vcodec rawvideo -pix_fmt rgb24 -sws_flags full_chroma_int+accurate_rnd"
    DEFAULT_MP4_FLAGS = "-vcodec libx264 -qp 0"

    DEFAULT_FLAGS = {
        'trim': DEFAULT_TRIM_FLAGS,
        '.png': DEFAULT_PNG_FLAGS,
        '.mov': DEFAULT_MOV_FLAGS,
        '.mp4': DEFAULT_MP4_FLAGS
    }

    def __init__(self, parent=None):
        """ Initializer """
        super(FfmpegSettingsWindow, self).__init__(parent)
        self.resize(800, 200)
        self.setWindowTitle("Ffmpeg Settings")
        
        self.loadSettings()
        self._generateLayout()

    def loadSettings(self, loadFile=HISTORY_SETTINGS):
        """ Load settings """
        # default
        self._settings = copy.deepcopy(self.DEFAULT_FLAGS)
        self._rows = {}

        if os.path.isfile(loadFile):
            with open(loadFile, 'r') as fh:
                self._settings.update(json.load(fh))

    def saveSettings(self, saveFile=HISTORY_SETTINGS):
        """ Save settings """
        for key, tb in self._rows.items():
            self._settings[key] = tb.text()

        with open(saveFile, 'w') as fh:
            json.dump(self._settings, fh, indent=4)

        msgBox = generateMessageBox("Successfully saved FFMPEG settings", windowTitle='Saved Successfully')
        msgBox.exec()

    def resetDefaults(self):
        """ Reset to defaults """
        self._settings = copy.deepcopy(self.DEFAULT_FLAGS)
        for key, tb in self._rows.items():
            clearAndSetText(tb, self._settings[key])

    def _generateLayout(self):
        """ Generate layout; always assumes webmd """
        wid = QWidget(self)
        self.setCentralWidget(wid)

        layout = QVBoxLayout()
        descr = QLabel("The following are the FFMPEG flags used to render the given file formats, or perform "
                        + "specific actions.")
        descr.setMaximumHeight(50)
        layout.addWidget(descr)

        for key, value in self._settings.items():
            tb = generateTextEntry(value, oneLiner=True)
            row = generateRow(key, tb)
            self._rows[key] = tb
            layout.addLayout(row)

        saveButton = QPushButton('Save')
        saveButton.clicked.connect(lambda result: self.saveSettings())
        resetButton = QPushButton('Reset')
        resetButton.clicked.connect(self.resetDefaults)
        layout.addLayout(generateRow(saveButton, resetButton))

        wid.setLayout(layout)

    def getFlags(self, flagType):
        """ Get flag settings """
        if flagType not in self._settings:
            raise ValueError(f"Unrecognized ffmpeg flag type {flagType}")

        return self._settings[flagType]
