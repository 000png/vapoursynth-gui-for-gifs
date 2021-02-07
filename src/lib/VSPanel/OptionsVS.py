#!./bin/python.exe
"""
Denoise and sharpen options.
"""
from PyQt5.QtWidgets import QLabel, QMessageBox

from lib.utils.PyQtUtils import generateMessageBox
from .VSConstants import DENOISE_CONFIG, SHARPEN_CONFIG, TRIM_CONFIG
from .OptionsBase import OptionsBase

class DenoiseOptionKNLM(OptionsBase):
    """ Denoise options for KNLM """
    def __init__(self, parent=None):
        """ Initiailzer """
        super().__init__(DENOISE_CONFIG['KNLM'], 'KNLM', ['d', 'a', 's', 'h'], parent)

    def _generateWidgets(self):
        """ Generate subwidgets """
        super()._generateWidgets(maxWidth=30)
        self._channelsArg = self._generateDropDownArg(fields=["YUV", "Y", "UV", "RGB", "auto"])
        self._channelsArg.activated[str].connect(self._setChannelArg)

    def _generateLayout(self):
        """ Generate layout """
        layout = self._generateHBoxLayout()

        layout.addWidget(QLabel("CH"))
        layout.addWidget(self._channelsArg)
        self.setLayout(layout)

    def _setChannelArg(self, text):
        """ Set channel argument """
        self.args['channels'] = text

    def loadArgs(self, args):
        """ Load args """
        index = self._channelsArg.findText(args['channels'])
        if index >= 0:
            self._channelsArg.setCurrentIndex(index)

        super().loadArgs(args)

    def save(self, ignoreErrors=False):
        """ Set and validate text args """
        return super().save(ignoreErrors=ignoreErrors, intArgs=['d', 'a', 's'], floatArgs=['h'])


class DenoiseOptionBM3D(OptionsBase):
    """ Denoise options for BM3D """
    def __init__(self, parent=None):
        """ Initiailzer """
        super().__init__(DENOISE_CONFIG['BM3D'], 'BM3D', ['sigma', 'radius1', 'matrix'], parent)

    def _generateWidgets(self):
        """ Generate subwidgets """
        super()._generateWidgets(maxWidth=None)
        self._profileArg = self._generateDropDownArg(fields=["fast", "lc", "np", "high", "very high"],
                                                     minWidth=60)
        self._profileArg.activated[str].connect(self._setProfileArg)

    def _generateLayout(self):
        """ Generate layout """
        layout = self._generateHBoxLayout(abbreviate=True)

        layout.addWidget(QLabel("p"))
        layout.addWidget(self._profileArg)
        self.setLayout(layout)

    def _setProfileArg(self, text):
        """ Set profile1 argument """
        self.args['profile1'] = text

    def loadArgs(self, args):
        """ Load args """
        index = self._profileArg.findText(args['profile1'])
        if index >= 0:
            self._profileArg.setCurrentIndex(index)

        super().loadArgs(args)

    def save(self, ignoreErrors=False):
        """ Set and validate text args """
        return super().save(ignoreErrors=ignoreErrors, intArgs=['radius1'], floatArgs=['sigma'])


class FineSharpOptions(OptionsBase):
    """ FineSharp option """
    def __init__(self, parent=None):
        """ Initializer """
        super().__init__(SHARPEN_CONFIG['FineSharp'], 'FineSharp', ['sstr'], parent)

    def _generateLayout(self):
        """ Generate layout """
        return super()._generateLayout(addStretch=True)

    def save(self, ignoreErrors=False):
        """ Set and validate text args """
        result = super().save(ignoreErrors=ignoreErrors, floatArgs=['sstr'])
        if result and not ignoreErrors:
            if self.args['sstr'] > 255:
                msgBox = generateMessageBox(f"{self._optionName} sstr arg cannot be greater than 255", icon=QMessageBox.Critical,
                                            windowTitle="Invalid argument", buttons=QMessageBox.Ok)
                msgBox.exec()
                return False

        return result

class TrimOptions(OptionsBase):
    """ FineSharp option """
    def __init__(self, parent=None):
        """ Initializer """
        super().__init__(TRIM_CONFIG['Yes'], 'Trimming', ['start frame', 'end frame'], parent)

    def _generateLayout(self):
        """ Generate layout """
        return super()._generateLayout(addStretch=True)

    def save(self, ignoreErrors=False):
        """ Set and validate text args """
        return super().save(ignoreErrors=ignoreErrors, intArgs=['start frame', 'end frame'])
