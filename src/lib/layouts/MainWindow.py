#!./bin/python.exe
"""
Main base layout for application
"""
import os
import sys
import posixpath
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QDir, Qt, QUrl
from PyQt5.QtWidgets import QMainWindow, QWidget, QGridLayout, QAction, \
    QFileDialog, QMessageBox, QStyle

import lib.utils.PyQtUtils as utils
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
        self._generateActions()
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

        # preset actions
        self._savePreset = QAction(QIcon(self.style().standardIcon(QStyle.SP_DialogSaveButton)), '&Save preset', self)
        self._savePreset.setStatusTip('Save current editor state as preset')
        self._savePreset.triggered.connect(lambda: self._vsPanelLayout.savePreset())
        self._loadPreset = QAction(QIcon(self.style().standardIcon(QStyle.SP_DirIcon)), '&Load preset', self)
        self._loadPreset.setStatusTip('Load preset into editor')
        self._loadPreset.triggered.connect(lambda: self._vsPanelLayout.loadPreset())

        # settings actions
        self._useBrowserForResizerAction = QAction(self._toggledIcon, '&Use browser for resizer')
        self._useBrowserForResizerAction.setStatusTip('Open up the resizer in the default browser')
        self._useBrowserForResizerAction.triggered.connect(lambda: self._setBrowserResizer())

    def _setBrowserResizer(self):
        """ Set browser resizer """
        self._useBrowserForResizer = not self._useBrowserForResizer
        if self._useBrowserForResizer:
            self._useBrowserForResizerAction.setIcon(self._toggledIcon)
        else:
            self._useBrowserForResizerAction.setIcon(self._notToggledIcon)

    def _generateWindow(self):
        """ Generate window """
        # make menu bar and add actions
        menuBar = self.menuBar()
        fileMenu = menuBar.addMenu('&File')
        fileMenu.addAction(self._openAction)
        fileMenu.addAction(self._loadPreset)
        fileMenu.addAction(self._savePreset)
        fileMenu.addAction(self._saveScriptAction)
        fileMenu.addAction(self._exitAction)

        editMenu = menuBar.addMenu('&Edit')
        editMenu.addAction(self._resizeAction)

        editMenu = menuBar.addMenu('&View')
        editMenu.addAction(self._toggleOriginalVideo)
        editMenu.addAction(self._toggleRenderVideo)

        settingsMenu = menuBar.addMenu('&Settings')
        settingsMenu.addAction(self._useBrowserForResizerAction)

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
        self._vsPanelLayout.openResizeCropWindow()

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
        