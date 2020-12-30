#!./bin/python.exe
"""
Layout containing generated script
"""
from PyQt5.QtWidgets import QGridLayout, QPushButton, QPlainTextEdit, QWidget
from PyQt5.QtGui import QFont

from lib.utils.VSEvaluateOptions import evaluateVapourSynthOptions


class ScriptLayout(QGridLayout):
    def __init__(self, parent=None):
        """ Initializer """
        super().__init__(parent)
        self._generateLayout()

    def _generateLayout(self):
        """ Generate layout """
        self.scriptEditor = ScriptEditor()
        self.addWidget(self.scriptEditor, 0, 0)

    def setText(self, text):
        self.scriptEditor.insertPlainText(text)

    def copyText(self):
        self.scriptEditor.copy()


class ScriptEditor(QPlainTextEdit):
    """ Custom QPlainTextEdit for script editor """
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setPlaceholderText('The generated script will appear here')
        self.setFont(QFont("Courier", 10))
        self.setMaximumHeight(250)

    def toScript(self, data):
        """ Generate script """
        # add stuff that will always be there + plugins
        videoData = data['video']
        plugins = '\n'.join(data['plugins'].values())

        script = f"""#!./bin/python.exe
import sys
sys.path.append('../src/bin/scripts64')

import vapoursynth as vs
{plugins}

core = vs.get_core()
#core.max_cache_size = 1000 #Use this command to limit the RAM usage (1000 is equivalent to 1GB of RAM)

video = core.lsmas.LWLibavSource(source=r"{videoData['trimmedFilename']}")
video = core.fmtc.resample(video, css="444")
"""
        # add options
        script += evaluateVapourSynthOptions(data)

        # add output information
        script += f"""
video = core.fmtc.bitdepth(video, bits=16)
video.set_output()
"""     
        return script
