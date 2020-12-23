#!./bin/python.exe
"""
Layout containing original video cut
"""
from PyQt5.QtWidgets import QWidget, QGridLayout, QPushButton

class PreviewVideoLayout(QGridLayout):
    """
    Main base layout for application
    """
    def __init__(self):
        super().__init__()
        
        self.addWidget(QPushButton("PreviewVideoLayout"), 0, 0)

