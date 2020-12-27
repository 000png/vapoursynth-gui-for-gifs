#!./bin/python.exe
"""
Denoise and sharpen options.
"""
from PyQt5.QtWidgets import QLabel

from lib.utils.vs_constants import DENOISE_CONFIG, SHARPEN_CONFIG
from lib.widgets.options_base import OptionsBase


class DenoiseOptionKNLM(OptionsBase):
    """ Denoise options for KNLM """
    def __init__(self, parent=None):
        """ Initiailzer """
        super().__init__(DENOISE_CONFIG['KNLM'], 'KNLM', parent)

    def _generateWidgets(self):
        """ Generate subwidgets """
        super()._generateWidgets(fields=['d', 'a', 's', 'h'], maxWidth=30)
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

    def save(self, ignoreErrors=False):
        """ Set and validate text args """
        return super().save(ignoreErrors=ignoreErrors, intArgs=['d', 'a', 's'], floatArgs=['h'])


class DenoiseOptionBM3D(OptionsBase):
    """ Denoise options for BM3D """
    def __init__(self, parent=None):
        """ Initiailzer """
        super().__init__(DENOISE_CONFIG['BM3D'], 'BM3D', parent)

    def _generateWidgets(self):
        """ Generate subwidgets """
        super()._generateWidgets(fields=['sigma', 'radius1', 'matrix'], maxWidth=None)
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

    def save(self, ignoreErrors=False):
        """ Set and validate text args """
        return super().save(ignoreErrors=ignoreErrors, intArgs=['radius1'], floatArgs=['sigma'])


class FineSharpOptions(OptionsBase):
    """ FineSharp option """
    def __init__(self, parent=None):
        """ Initiailzer """
        super().__init__(SHARPEN_CONFIG['FineSharp'], 'FineSharp', parent)

    def _generateWidgets(self):
        """ Generate subwidgets """
        return super()._generateWidgets(fields=['sstr'])

    def _generateLayout(self):
        """ Generate layout """
        return super()._generateLayout(addStretch=True)

    def save(self, ignoreErrors=False):
        """ Set and validate text args """
        return super().save(ignoreErrors=ignoreErrors, floatArgs=['sstr'])
