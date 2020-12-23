#!./bin/python.exe
"""
Layout containing original video cut
"""
from PyQt5.QtWidgets import QWidget, QGridLayout, QPushButton

class ScriptLayout(QGridLayout):
    """
    Main base layout for application
    """
    def __init__(self):
        super().__init__()
        
        self.addWidget(QPushButton("ScriptLayout"), 0, 0)

