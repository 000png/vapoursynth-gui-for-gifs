#!./bin/python.exe
"""
Base class for options widgets
"""
import copy
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QPlainTextEdit, QHBoxLayout, QLabel, QComboBox, \
    QMessageBox

from lib.utils.pyqt_utils import generateMessageBox, generateTextEntry

ARG_MAX_WIDTH = 40
ARG_MAX_HEIGHT = 25
DROPDOWN_ARG_MIN_WIDTH = 50

class OptionsBase(QWidget):
    """ Options base class """
    def __init__(self, sourceConfig, optionName, parent=None):
        super().__init__(parent)
        self.args = copy.deepcopy(sourceConfig)
        self._optionName = optionName
        self._argPlainTextWidgets = {}

        self._generateWidgets()
        self._generateLayout()

    def _generateDropDownArg(self, fields, minWidth=DROPDOWN_ARG_MIN_WIDTH):
        """ Generate drop down args """
        dropDown = QComboBox()
        for item in fields:
            dropDown.addItem(item)
        dropDown.setMinimumWidth(minWidth)
        return dropDown

    def _generateWidgets(self, fields=None, maxWidth=ARG_MAX_WIDTH, maxHeight=ARG_MAX_HEIGHT):
        """ Generate subwidgets """
        if not fields:
            return

        for item in fields:
            self._argPlainTextWidgets[item] = generateTextEntry(str(self.args[item]))
            if maxWidth is not None:
                self._argPlainTextWidgets[item].setMaximumWidth(maxWidth)
            if maxHeight is not None:
                self._argPlainTextWidgets[item].setMaximumHeight(maxHeight)

    def _generateHBoxLayout(self, addStretch=False, abbreviate=False):
        """ Generate generate plain text args layout """
        layout = QHBoxLayout()
        for key, value in self._argPlainTextWidgets.items():
            if abbreviate:
                key = key[0]
            layout.addWidget(QLabel(key))
            layout.addWidget(value)

        if addStretch:
            layout.addStretch(0)
            layout.setSpacing(5)
        return layout

    def _generateLayout(self, addStretch=False):
        """ Generate layout """
        self.setLayout(self._generateHBoxLayout(addStretch))

    def save(self, ignoreErrors=False, intArgs=None, floatArgs=None):
        """ Set and validate text args """
        if intArgs is None:
            intArgs = []

        if floatArgs is None:
            floatArgs = []

        for key, value in self._argPlainTextWidgets.items():
            result = value.toPlainText()
            try:
                if key in intArgs:
                    result = int(result)
                elif key in floatArgs:
                    result = float(result)
            except ValueError:
                if not ignoreErrors:
                    requiredType = 'an integer' if key in intArgs else 'a float'
                    msgBox = generateMessageBox(f"{self._optionName} {key} arg must be {requiredType}", icon=QMessageBox.Critical,
                                                windowTitle="Invalid argument", buttons=QMessageBox.Ok)
                    msgBox.exec()
                    return False

            if not ignoreErrors and (key in intArgs or key in floatArgs) and result < 0:
                msgBox = generateMessageBox(f"{self._optionName} {key} arg cannot be negative", icon=QMessageBox.Critical,
                                            windowTitle="Invalid argument", buttons=QMessageBox.Ok)
                msgBox.exec()
                return False

            self.args[key] = result

        return True
