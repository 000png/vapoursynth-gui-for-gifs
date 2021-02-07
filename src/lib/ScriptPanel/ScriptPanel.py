#!./bin/python.exe
"""
Layout containing generated script
"""
import os
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QGridLayout, QPlainTextEdit, QWidget, QFrame

from .VSOptionsToScript import vsOptionsToScript


class ScriptFrame(QFrame):
    def __init__(self, parent=None):
        """ Initializer """
        super().__init__(parent)
        self._generateLayout()

    def _generateLayout(self):
        """ Generate layout """
        layout = QGridLayout(self)
        self.scriptEditor = ScriptEditor()
        layout.addWidget(self.scriptEditor, 0, 0)

        self.setLayout(layout)
        self.setFrameShape(QFrame.StyledPanel)

    def setText(self, text):
        """ Set text """
        self.scriptEditor.insertPlainText(text)

    def copyText(self):
        """ Copy text """
        self.scriptEditor.copy()


class ScriptEditor(QPlainTextEdit):
    """ Custom QPlainTextEdit for script editor """
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setPlaceholderText('The generated script will appear here')
        self.setFont(QFont("Courier", 10))

    def toScript(self, data):
        """ Generate script """
        # add stuff that will always be there + plugins
        videoData = data['video']
        plugins = '\n'.join(data['plugins'].values())

        # source changes depending on type
        _, extension = os.path.splitext(videoData['filename'])
        if extension == '.mp4':
            sourceInput = f"video = core.ffms2.Source(source=r\"{videoData['filename']}\")"
        else:
            sourceInput = f"video = core.lsmas.LWLibavSource(source=r\"{videoData['filename']}\")"

        script = f"""#!./bin/python.exe
import sys
sys.path.append('../src/bin/scripts64')

import vapoursynth as vs
{plugins}

core = vs.get_core()
#core.max_cache_size = 1000 #Use this command to limit the RAM usage (1000 is equivalent to 1GB of RAM)

{sourceInput}
"""
        # add options
        script += vsOptionsToScript(data)

        # add output information
        script += f"""
video = core.fmtc.bitdepth(video, bits=16)
video.set_output()
"""     
        return script
