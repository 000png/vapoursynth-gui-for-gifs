#!./bin/python.exe
"""
Main base layout for application
"""
import os
import sys
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QDir, Qt, QUrl
from PyQt5.QtWidgets import QMainWindow, QWidget, QGridLayout, QAction, \
    QFileDialog, QMessageBox, QStyle

import lib.utils.PyQtUtils as utils
from lib.layouts.VideoLayout import DualVideoLayout
from lib.layouts.ScriptLayout import ScriptLayout
from lib.layouts.VSPanelLayout import VSPanelLayout

class MainLayout(QMainWindow):
    """
    Main base layout for application
    """
    def __init__(self):
        """ Initializer """
        super().__init__()
        self._originalToggled = True
        self._renderToggled = True

        self.setWindowTitle("VapourSynth GUI for Gifs")
        self._generateLayout()
        self._generateActions()
        self._generateWindow()

    def _generateLayout(self):
        """
        Generate the main layout
        """
        wid = QWidget(self)
        self.setCentralWidget(wid)
        layout = QGridLayout()

        self._videoLayout = DualVideoLayout(style=self.style())
        self._scriptLayout = ScriptLayout()
        self._vsPanelLayout = VSPanelLayout(scriptEditor=self._scriptLayout.scriptEditor, parent=self)

        layout.addLayout(self._videoLayout, 0, 0)
        layout.addLayout(self._scriptLayout, 1, 0)
        layout.addLayout(self._vsPanelLayout, 0, 1, 0, 1)

        wid.setLayout(layout)

        # resizer/crop layout is actually in new window

    def _generateActions(self):
        """ Generate actions """
        # open action
        self._openAction = QAction(QIcon(self.style().standardIcon(QStyle.SP_DirIcon)), '&Open', self)        
        self._openAction.setShortcut('Ctrl+O')
        self._openAction.setStatusTip('Open video')
        self._openAction.triggered.connect(self._openFile)

        # exit action
        self._exitAction = QAction(QIcon('exit.png'), '&Exit', self)        
        self._exitAction.setShortcut('Ctrl+Q')
        self._exitAction.setStatusTip('Exit application')
        self._exitAction.triggered.connect(self._exitCall)

        # save script action
        self._saveScriptAction = QAction(QIcon(self.style().standardIcon(QStyle.SP_DialogSaveButton)), '&Save script', self)       
        self._saveScriptAction.setStatusTip('Save script')
        self._saveScriptAction.triggered.connect(self._saveScript)

        # crop/trim/resize action
        self._resizeAction = QAction(QIcon('open.png'), '&Resize and crop', self) 
        self._resizeAction.setShortcut('Ctrl+R')
        self._resizeAction.setStatusTip('Resize and crop video')
        self._resizeAction.triggered.connect(self._resizeVideo)

        # view actions
        self._toggledIcon = QIcon(self.style().standardIcon(QStyle.SP_DialogApplyButton))
        self._notToggledIcon = QIcon(self.style().standardIcon(QStyle.SP_DialogCancelButton))
        self._toggleOriginalVideo = QAction(self._toggledIcon, '&Toggle original video', self)
        self._toggleOriginalVideo.setStatusTip('Toggle showing the original video in the editor')
        self._toggleOriginalVideo.triggered.connect(lambda: self._toggleVideo('original'))
        self._toggleRenderVideo = QAction(self._toggledIcon, '&Toggle render video', self)
        self._toggleRenderVideo.setStatusTip('Toggle showing the render video in the editor')
        self._toggleRenderVideo.triggered.connect(lambda: self._toggleVideo('render'))

    def _generateWindow(self):
        """ Generate window """
        # make menu bar and add actions
        menuBar = self.menuBar()
        fileMenu = menuBar.addMenu('&File')
        fileMenu.addAction(self._openAction)
        fileMenu.addAction(self._saveScriptAction)
        fileMenu.addAction(self._exitAction)

        editMenu = menuBar.addMenu('&Edit')
        editMenu.addAction(self._resizeAction)

        editMenu = menuBar.addMenu('&View')
        editMenu.addAction(self._toggleOriginalVideo)
        editMenu.addAction(self._toggleRenderVideo)

    def _saveScript(self):
        """ Save script """
        self._vsPanelLayout.saveScriptToFile()

    def _openFile(self):
        """ Open a file and populate the video layout """
        filename, _ = QFileDialog.getOpenFileName(self, "Open Video", QDir.homePath())

        if filename:
            self._videoLayout.loadVideoFile(filename)
            #self._videoLayout.clearVideo(videoType='render')
            self._vsPanelLayout.setVideo(filename, 100)

    def _toggleVideo(self, videoType):
        """ Toggle a video to show/hide """
        if videoType == 'original':
            if self._originalToggled:
                self._toggleOriginalVideo.setIcon(self._notToggledIcon)
            else:
                self._toggleOriginalVideo.setIcon(self._toggledIcon)
            self._originalToggled = not self._originalToggled
        elif videoType == 'render':
            if self._renderToggled:
                self._toggleRenderVideo.setIcon(self._notToggledIcon)
            else:
                self._toggleRenderVideo.setIcon(self._toggledIcon)
            self._renderToggled = not self._renderToggled
        else:
            raise ValueError(f"Unrecognized video type {videoType}")

        self._videoLayout.toggleVideo(videoType=videoType)

    def _exitCall(self):
        """ Exit the application """
        sys.exit()

    def _resizeVideo(self):
        """ Open up resize window """
        msgBox = utils.generateMessageBox()

    def setRenderVideo(self, filename):
        """ Set render video """
        _, extension = os.path.splitext(filename)
        if extension != '.png':
            self._videoLayout.loadVideoFile(filename, videoType='render')
