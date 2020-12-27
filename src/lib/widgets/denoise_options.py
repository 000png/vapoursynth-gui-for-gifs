#!./bin/python.exe
"""
Denoise options.
"""
import copy
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QPlainTextEdit, QHBoxLayout, QLabel, QComboBox, \
    QMessageBox

from lib.utils.vs_constants import DENOISE_CONFIG
from lib.utils.pyqt_utils import generateMessageBox


class DenoiseOptionKNLM(QWidget):
    """ Denoise options for KNLM """
    def __init__(self, parent=None):
        """ Initiailzer """
        super().__init__(parent)
        # mirrors DENOISE_CONFIG['KNLM']
        self.args = copy.deepcopy(DENOISE_CONFIG['KNLM'])
        self._argPlainTextWidgets = {}

        self._generateWidgets()
        self._generateLayout()

    def _generateWidgets(self):
        """ Generate subwidgets """
        for item in ['d', 'a', 's', 'h']:
            self._argPlainTextWidgets[item] = QPlainTextEdit(str(self.args[item]))

        for key, value in self._argPlainTextWidgets.items():
            value.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            value.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            value.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
            value.setMaximumWidth(30)

        self._channelsArg = QComboBox()
        for item in ["YUV", "Y", "UV", "RGB", "auto"]:
            self._channelsArg.addItem(item)
        self._channelsArg.activated[str].connect(self._setChannelArg)
        self._channelsArg.setMinimumWidth(50)

    def _generateLayout(self):
        """ Generate layout """
        layout = QHBoxLayout()
        for key, value in self._argPlainTextWidgets.items():
            layout.addWidget(QLabel(key))
            layout.addWidget(value)

        layout.addWidget(QLabel("CH"))
        layout.addWidget(self._channelsArg)
        self.setLayout(layout)

    def _setChannelArg(self, text):
        """ Set channel argument """
        self.args['channels'] = text

    def save(self, ignoreErrors=False):
        """ Set and validate text args """
        for key, value in self._argPlainTextWidgets.items():
            result = value.toPlainText()
            try:
                result = int(result) if key != 'h' else float(result)
                self.args[key] = result
            except ValueError:
                if not ignoreErrors:
                    requiredType = 'an integer' if key != 'h' else 'a float'
                    msgBox = generateMessageBox(f"KNLM {key} arg must be {requiredType}", icon=QMessageBox.Critical, windowTitle="Invalid argument",
                                                buttons=QMessageBox.Ok)
                    msgBox.exec()
                    return False
            return True


class DenoiseOptionBM3D(QWidget):
    """ Denoise options for BM3D """
    def __init__(self, parent=None):
        """ Initiailzer """
        super().__init__(parent)
        # mirrors DENOISE_CONFIG['KNLM']
        self.args = copy.deepcopy(DENOISE_CONFIG['BM3D'])
        self._argPlainTextWidgets = {}

        self._generateWidgets()
        self._generateLayout()

    def _generateWidgets(self):
        """ Generate subwidgets """
        for item in ['sigma', 'radius1', 'matrix']:
            self._argPlainTextWidgets[item] = QPlainTextEdit(str(self.args[item]))

        self._profileArg = QComboBox()
        for item in ["fast", "lc", "np", "high", "very high"]:
            self._profileArg.addItem(item)
        self._profileArg.activated[str].connect(self._setProfileArg)
        self._profileArg.setMinimumWidth(60)

        for key, value in self._argPlainTextWidgets.items():
            value.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            value.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            value.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)

    def _generateLayout(self):
        """ Generate layout """
        layout = QHBoxLayout()
        for key, value in self._argPlainTextWidgets.items():
            layout.addWidget(QLabel(key[0]))
            layout.addWidget(value)

        layout.addWidget(QLabel("p"))
        layout.addWidget(self._profileArg)
        self.setLayout(layout)

    def _setProfileArg(self, text):
        """ Set profile1 argument """
        self.args['profile1'] = text

    def save(self, ignoreErrors=False):
        """ Set and validate text args """
        for key, value in self._argPlainTextWidgets.items():
            result = value.toPlainText()

            if key in ['sigma', 'radius1']:
                try:
                    result = int(result) if key == 'radius1' else float(result)
                except ValueError:
                    if not ignoreErrors:
                        requiredType = 'an integer' if key == 'radius1' else 'a float'
                        msgBox = generateMessageBox(f"BM3D {key} arg must be {requiredType}", icon=QMessageBox.Critical, windowTitle="Invalid argument",
                                                    buttons=QMessageBox.Ok)
                        msgBox.exec()
                        return False

                if result < 0 and not ignoreErrors:
                    msgBox = generateMessageBox(f"BM3D {key} arg must be greater than 0", icon=QMessageBox.Critical, windowTitle="Invalid argument",
                                                buttons=QMessageBox.Ok)
                    msgBox.exec()
                    return False

            self.args[key] = result
        return True
