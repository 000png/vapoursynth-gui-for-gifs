#!./bin/python.exe
"""
Adapted from https://wiki.python.org/moin/PyQt/A%20full%20widget%20waiting%20indicator
"""
import math, sys
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPalette, QPainter, QBrush, QColor, QPen
from PyQt5.QtWidgets import QWidget, QMainWindow, QApplication, QTextEdit, QGridLayout, \
    QPushButton


class WaitingSpinnerOverlay(QWidget):

    def __init__(self, parent=None):
        """ Initializer """
        super().__init__(parent)
        self.timer = QTimer()
        self.timer.timeout.connect(self.showTime)
        palette = QPalette(self.palette())
        palette.setColor(palette.Background, Qt.transparent)
        self.setPalette(palette)
    
    def paintEvent(self, event):
        """ Paint event """
        painter = QPainter()
        painter.begin(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.fillRect(event.rect(), QBrush(QColor(255, 255, 255, 127)))
        painter.setPen(QPen(Qt.NoPen))
        
        for i in range(6):
            if int(self.counter / 2) % 6 == i:
                painter.setBrush(QBrush(QColor(0, 200, 255)))
            else:
                painter.setBrush(QBrush(QColor(127, 127, 127)))
            painter.drawEllipse(
                int(self.width()/2 + 30 * math.cos(2 * math.pi * i / 6.0) - 10),
                int(self.height()/2 + 30 * math.sin(2 * math.pi * i / 6.0)) - 10,
                20, 20)
        
        painter.end()
    
    def showEvent(self, event):
        """ Show event """
        self.timer.start(50)
        self.counter = 0

    def showTime(self):
        self.counter +=1
        self.update()

    def hideEvent(self, event):
        self.timer.stop()
