#!./bin/python.exe
"""
Main base layout for application
"""
import sys
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QDir, Qt, QUrl
from PyQt5.QtWidgets import QMainWindow, QWidget, QGridLayout, QAction, \
    QFileDialog, QMessageBox

import lib.utils.pyqt_utils as utils
from lib.layouts.video_layout import DualVideoLayout
from lib.layouts.script_layout import ScriptLayout
from lib.layouts.vs_panel_layout import VSPanelLayout

class MainLayout(QMainWindow):
    """
    Main base layout for application
    """
    def __init__(self):
        super().__init__()
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

        self._videoLayout = DualVideoLayout(parent=self)
        self._scriptLayout = ScriptLayout(parent=self)
        self._vsPanelLayout = VSPanelLayout(scriptEditor=self._scriptLayout.scriptEditor, parent=self)

        layout.addLayout(self._videoLayout, 0, 0)
        layout.addLayout(self._scriptLayout, 1, 0)
        layout.addLayout(self._vsPanelLayout, 0, 1, 0, 1)

        wid.setLayout(layout)

    def _generateActions(self):
        """
        Generate actions
        """
        # open action
        self._openAction = QAction(QIcon('open.png'), '&Open', self)        
        self._openAction.setShortcut('Ctrl+O')
        self._openAction.setStatusTip('Open movie')
        self._openAction.triggered.connect(self._openFile)

        # exit action
        self._exitAction = QAction(QIcon('exit.png'), '&Exit', self)        
        self._exitAction.setShortcut('Ctrl+Q')
        self._exitAction.setStatusTip('Exit application')
        self._exitAction.triggered.connect(self._exitCall)

        # crop/trim/resize action
        self._resizeAction = QAction(QIcon('open.png'), '&Resize/crop/trim', self) 
        self._resizeAction.setShortcut('Ctrl+R')
        self._resizeAction.setStatusTip('Resize, crop, and/or trim video')
        self._resizeAction.triggered.connect(self._resizeVideo)

    def _generateWindow(self):
        """ Generate window """
        # make menu bar and add actions
        menuBar = self.menuBar()
        fileMenu = menuBar.addMenu('&File')
        fileMenu.addAction(self._openAction)
        fileMenu.addAction(self._exitAction)

        editMenu = menuBar.addMenu('&Edit')
        editMenu.addAction(self._resizeAction)

    def _openFile(self):
        """ Open a file and populate the video layout """
        filename, _ = QFileDialog.getOpenFileName(self, "Open Video", QDir.homePath())

        if filename:
            self._videoLayout.loadVideoFile(filename)
            self._vsPanelLayout.setVideo(filename, 100)

    def _exitCall(self):
        """ Exit the application """
        sys.exit()

    def _resizeVideo(self):
        """ Open up resize window """
        msgBox = utils.generateMessageBox()
