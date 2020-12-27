#!./bin/python.exe
"""
Layout containing generated script
"""
from PyQt5.QtWidgets import QGridLayout, QPushButton, QPlainTextEdit, QWidget
from PyQt5.QtGui import QFont

OPENING_DEFAULT_SCRIPT = 'The generated script will appear here'

class ScriptLayout(QGridLayout):
    def __init__(self, parent=None):
        """ Initializer """
        super().__init__()
        self._parent = parent

        self._generateWidgets()
        self._generateLayout()

    def _generateWidgets(self):
        """ Generate widgets """
        self.scriptEditor = QPlainTextEdit(OPENING_DEFAULT_SCRIPT)
        self.scriptEditor.setFont(QFont("Courier", 10))
        self.scriptEditor.setMaximumHeight(250)

    def _generateLayout(self):
        """ Generate layout """
        self.addWidget(self.scriptEditor, 0, 0)

    def setText(self, text):
        self.scriptEditor.insertPlainText(text)

    def copyText(self):
        self.scriptEditor.copy()
