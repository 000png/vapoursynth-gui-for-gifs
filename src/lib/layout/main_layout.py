#!./bin/python.exe
"""
Main base layout for application
"""
import sys
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QDir, Qt, QUrl
from PyQt5.QtWidgets import QMainWindow, QWidget, QGridLayout, QAction, QFileDialog

from lib.layout.video_layout import DualVideoLayout

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

        layout.addLayout(self._videoLayout, 0, 0)

        wid.setLayout(layout)

    def _generateActions(self):
        """
        Generate actions
        """
        # Create new action
        self._openAction = QAction(QIcon('open.png'), '&Open', self)        
        self._openAction.setShortcut('Ctrl+O')
        self._openAction.setStatusTip('Open movie')
        self._openAction.triggered.connect(self._openFile)

        # create exit action
        self._exitAction = QAction(QIcon('exit.png'), '&Exit', self)        
        self._exitAction.setShortcut('Ctrl+Q')
        self._exitAction.setStatusTip('Exit application')
        self._exitAction.triggered.connect(self._exitCall)

    def _generateWindow(self):
        """
        Generate window
        """
        # make menu bar and add actions
        menuBar = self.menuBar()
        fileMenu = menuBar.addMenu('&File')
        fileMenu.addAction(self._openAction)
        fileMenu.addAction(self._exitAction)

    def _openFile(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Open Video", QDir.homePath())

        if filename:
            self._videoLayout.loadVideoFile(filename)

    def _exitCall(self):
        sys.exit()
