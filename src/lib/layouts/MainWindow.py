#!./bin/python.exe
"""
Main base layout for application
"""
import os
import sys
import posixpath
from PyQt5.QtCore import QDir
from PyQt5.QtWidgets import QMainWindow, QWidget, QGridLayout, QFileDialog

import lib.utils.PyQtUtils as utils
from lib.helpers.ActionsManager import ActionsManager
from lib.layouts.VideoLayout import DualVideoLayout
from lib.layouts.ScriptLayout import ScriptLayout
from lib.layouts.VSPanelLayout import VSPanelLayout
from lib.widgets.WaitingSpinnerOverlay import WaitingSpinnerOverlay


class MainWindow(QMainWindow):
    """
    Main base layout for application
    """
    def __init__(self, version):
        """ Initializer """
        super().__init__()
        self._originalToggled = True
        self._renderToggled = True
        self._useBrowserForResizer = True

        self.setWindowTitle(f"VapourSynth GUI for Gifs v{version}")
        self._generateLayout()
        self._generateWindow()

    def _generateLayout(self):
        """ Generate the main layout """
        wid = QWidget(self)
        self.setCentralWidget(wid)
        layout = QGridLayout()

        self._videoLayout = DualVideoLayout(style=self.style())
        self._scriptLayout = ScriptLayout()
        vsWidget = QWidget()
        self._vsPanelLayout = VSPanelLayout(scriptEditor=self._scriptLayout.scriptEditor, parent=self)
        vsWidget.setLayout(self._vsPanelLayout)
        vsWidget.setMaximumWidth(375)
        self._vsPanelLayout.setContentsMargins(0, 0, 0, 0)

        layout.addLayout(self._videoLayout, 0, 0)
        layout.addLayout(self._scriptLayout, 1, 0)
        layout.addWidget(vsWidget, 0, 1, 0, 1)

        wid.setLayout(layout)

        self._loadingScreen = WaitingSpinnerOverlay(self.centralWidget())
        self._loadingScreen.hide()
        self._vsPanelLayout.setSubprocessManager(self._loadingScreen)

    def _generateWindow(self):
        """ Generate window """
        # make menu bar and add actions
        self._actionsManager = ActionsManager(self)
        menuBar = self.menuBar()

        fileMenu = menuBar.addMenu('&File')
        fileMenu.addAction(self._actionsManager.makeAction('open_video', self._openFile))
        fileMenu.addAction(self._actionsManager.makeAction('load_preset', self._vsPanelLayout.loadPreset))
        fileMenu.addAction(self._actionsManager.makeAction('save_preset', self._vsPanelLayout.savePreset))

        fileMenu.addAction(self._actionsManager.makeAction('save_script', self._saveScript))
        fileMenu.addAction(self._actionsManager.makeAction('exit', self._exitCall))

        editMenu = menuBar.addMenu('&Edit')
        editMenu.addAction(self._actionsManager.makeAction('resizer', self._vsPanelLayout.openResizeCropWindow))

        editMenu = menuBar.addMenu('&View')
        editMenu.addAction(self._actionsManager.makeAction('toggle_original_video',
                           lambda: self._toggleVideo('original')))
        editMenu.addAction(self._actionsManager.makeAction('toggle_render_video',
                           lambda: self._toggleVideo('render')))

        settingsMenu = menuBar.addMenu('&Settings')
        settingsMenu.addAction(self._actionsManager.makeAction('toggle_browser_resizer',
                               self._setBrowserResizer))

    def _setBrowserResizer(self):
        """ Set browser resizer """
        self._useBrowserForResizer = not self._useBrowserForResizer
        self._actionsManager.setToggleIcon('toggle_browser_resizer', self._useBrowserForResizer)

    def _saveScript(self):
        """ Save script """
        self._vsPanelLayout.saveScriptToFile()

    def _openFile(self):
        """ Open a file and populate the video layout """
        filename, _ = QFileDialog.getOpenFileName(self, "Open Video", QDir.homePath())

        if filename:
            self._videoLayout.loadVideoFile(filename)
            self._vsPanelLayout.setVideo(filename)

    def _toggleVideo(self, videoType):
        """ Toggle a video to show/hide """
        if videoType == 'original':
            self._originalToggled = not self._originalToggled
            self._actionsManager.setToggleIcon('toggle_original_video', self._originalToggled)
        elif videoType == 'render':
            self._renderToggled = not self._renderToggled
            self._actionsManager.setToggleIcon('toggle_render_video', self._renderToggled)
        else:
            raise ValueError(f"Unrecognized video type {videoType}")

        self._videoLayout.toggleVideo(videoType=videoType)

    def _exitCall(self):
        """ Exit the application """
        sys.exit()

    def setVideos(self, filename, videoType=None):
        """ Set original video """
        filename = filename.replace(os.sep, posixpath.sep)

        if videoType == 'render':
            _, extension = os.path.splitext(filename)
            if extension == '.png':
                return

        self._videoLayout.loadVideoFile(filename, videoType=videoType, forceLoad=True)

    def resizeEvent(self, event):
        """ Resize event """
        self._loadingScreen.resize(event.size())
        event.accept()

    def closeEvent(self, event):
        """ Save history if save history is toggled """
        self._vsPanelLayout.savePreset(isHistory=True)
        event.accept()
        