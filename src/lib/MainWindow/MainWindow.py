#!./bin/python.exe
"""
Main base layout for application
"""
import os
import sys
import posixpath
from PyQt5.QtCore import QDir, Qt
from PyQt5.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QFileDialog, QSplitter

import lib.utils.PyQtUtils as utils
from .ActionsManager import ActionsManager
from .WaitingSpinnerOverlay import WaitingSpinnerOverlay

from lib.ScriptPanel.ScriptPanel import ScriptFrame
from lib.VideoPanel.VideoPanel import DualVideoFrame
from lib.VSPanel.VSPanel import VSPanelFrame


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
        layout = QHBoxLayout()

        self._videoFrame = DualVideoFrame(style=self.style())
        self._scriptFrame = ScriptFrame()
        self._vsPanelFrame = VSPanelFrame(scriptEditor=self._scriptFrame.scriptEditor, parent=self)

        vsplitter = QSplitter(Qt.Vertical)
        vsplitter.addWidget(self._videoFrame)
        vsplitter.addWidget(self._scriptFrame)

        windowHeight = self.frameGeometry().height()
        windowWidth = self.frameGeometry().width()
        vsplitter.setSizes([int(windowHeight * 0.65), int(windowHeight * 0.35)])

        hsplitter = QSplitter(Qt.Horizontal)
        hsplitter.addWidget(vsplitter)
        hsplitter.addWidget(self._vsPanelFrame)
        hsplitter.setSizes([int(windowWidth * 0.85), int(windowWidth * 0.15)])

        layout.addWidget(hsplitter)
        wid.setLayout(layout)

        self._loadingScreen = WaitingSpinnerOverlay(self.centralWidget())
        self._loadingScreen.hide()
        self._vsPanelFrame.setSubprocessManager(self._loadingScreen)

    def _generateWindow(self):
        """ Generate window """
        # make menu bar and add actions
        self._actionsManager = ActionsManager(self)
        menuBar = self.menuBar()

        fileMenu = menuBar.addMenu('&File')
        fileMenu.addAction(self._actionsManager.makeAction('open_video', self._openFile))
        fileMenu.addAction(self._actionsManager.makeAction('load_preset', self._vsPanelFrame.loadPreset))
        fileMenu.addAction(self._actionsManager.makeAction('save_preset', self._vsPanelFrame.savePreset))

        fileMenu.addAction(self._actionsManager.makeAction('save_script', self._saveScript))
        fileMenu.addAction(self._actionsManager.makeAction('exit', self._exitCall))

        editMenu = menuBar.addMenu('&Edit')
        editMenu.addAction(self._actionsManager.makeAction('resizer', self._vsPanelFrame.openResizer))

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
        self._vsPanelFrame.saveScriptToFile()

    def _openFile(self):
        """ Open a file and populate the video layout """
        filename, _ = QFileDialog.getOpenFileName(self, "Open Video", QDir.homePath())

        if filename:
            self._videoFrame.loadVideoFile(filename)
            self._vsPanelFrame.setVideo(filename)

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

        self._videoFrame.toggleVideo(videoType=videoType)

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

        self._videoFrame.loadVideoFile(filename, videoType=videoType, forceLoad=True)

    def resizeEvent(self, event):
        """ Resize event """
        self._loadingScreen.resize(event.size())
        event.accept()

    def closeEvent(self, event):
        """ Save history if save history is toggled """
        self._vsPanelFrame.savePreset(isHistory=True)
        event.accept()
        