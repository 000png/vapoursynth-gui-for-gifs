#!./bin/python.exe
"""
Layout containing options for Vapoursynth
"""
import os
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QGridLayout, QPushButton, QComboBox, \
    QLabel, QHBoxLayout, QVBoxLayout, QMessageBox, QPlainTextEdit, QFileDialog, \
    QStackedLayout

import lib.utils.pyqt_utils as utils
import lib.utils.vs_constants as c
from lib.utils.vs_utils import checkScript
from lib.utils.vs_evaluate_options import evaluateVapourSynthOptions
from lib.layouts.script_layout import OPENING_DEFAULT_SCRIPT
from lib.widgets.denoise_options import DenoiseOptionKNLM, DenoiseOptionBM3D

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
WORK_DIR = os.path.join(SCRIPT_DIR, '../../work')

NO_VIDEO_LOADED_SCRIPT = 'A video must be loaded before the script can be generated and validated'
TMP_FILENAME = f"{WORK_DIR}/tmp.vpy"

class VSPanelLayout(QVBoxLayout):
    """
    Main base layout for application
    """
    def __init__(self, scriptEditor, parent=None):
        """ Initializer """
        super().__init__()
        self._parent = parent
        self._scriptEditor = scriptEditor
        self._data = {
            'plugins': {}
        }
        
        self._generateVapourSynthOptions()
        self._generateWidgets()
        self._generateLayout()

    def _generateVapourSynthOptions(self):
        """ Generate VapourSynth options """
        self._preprocessor = QComboBox()
        for item in c.PREPROCESSOR_CONFIG.keys():
            self._preprocessor.addItem(item)
        self._preprocessor.activated[str].connect(
            lambda text: self._addVapourSynthOption(text, 'preprocessor', c.PREPROCESSOR_PLUGINS, c.PREPROCESSOR_CONFIG))

        self._denoiseFilters = QComboBox()
        for item in c.DENOISE_CONFIG.keys():
            self._denoiseFilters.addItem(item)
        self._denoiseFilters.activated[str].connect(
            lambda text: self._addVapourSynthOption(text, 'denoise', c.DENOISE_PLUGINS, c.DENOISE_CONFIG, self._setDenoiseLayout))

        self._knlmOptions = DenoiseOptionKNLM()
        self._bm3dOptions = DenoiseOptionBM3D()

    def _addVapourSynthOption(self, text, key, vsPlugin, vsConfig, otherFuncToExecute=None):
        """ Add vapoursynth option data """
        if text == 'None':
            self._data[key] = None
            for plugin in vsPlugin.keys():
                self._data['plugins'].pop(plugin, None)
        else:
            self._data[key] = {'type': text, 'args': vsConfig[text]}
            self._data['plugins'].update(vsPlugin)

        if otherFuncToExecute:
            otherFuncToExecute(text)

    def _setDenoiseLayout(self, text):
        """ Set stack """
        self._knlmOptions.save(ignoreErrors=True)
        self._bm3dOptions.save(ignoreErrors=True)
        if text == 'None':
            self._denoise.hide()
        else:
            self._denoise.show()
            self._denoiseStack.setCurrentWidget(self._knlmOptions) if text == 'KNLM' \
                else self._denoiseStack.setCurrentWidget(self._bm3dOptions)

    def _generateWidgets(self):
        """ Generate other widgets """
        self._generateScriptButton = QPushButton("Generate Script")
        self._generateScriptButton.clicked.connect(self._generateScript)

        self._checkScriptButton = QPushButton("Check Script")
        self._checkScriptButton.clicked.connect(self._checkScript)

        self._scriptToFileButton = QPushButton("Save script to file")
        self._scriptToFileButton.clicked.connect(self._saveScriptToFile)

        self._renderButton = QPushButton('Render video')
        self._renderButton.clicked.connect(self._renderVideo)

        self._checkScriptOutput = QPlainTextEdit()
        self._checkScriptOutput.setReadOnly(True)
        self._checkScriptOutput.setMaximumWidth(300)

    def _generateLayout(self):
        """ Generate layout """
        self.addLayout(utils.generateRow("Preprocessor:", self._preprocessor))
        self.addLayout(utils.generateRow('Denoise', self._denoiseFilters))

        # stack denoise options
        self._denoise = QWidget()
        self._denoiseStack = QStackedLayout()
        self._denoiseStack.addWidget(self._knlmOptions)
        self._denoiseStack.addWidget(self._bm3dOptions)
        self._denoise.setLayout(self._denoiseStack)
        self._denoise.setMaximumWidth(300)
        self._denoise.setMaximumHeight(50)
        self.addWidget(self._denoise)
        self._denoise.hide()

        self.addLayout(utils.generateRow(self._generateScriptButton, self._checkScriptButton))
        self.addLayout(utils.generateRow(self._scriptToFileButton, self._renderButton))
        self.addWidget(self._checkScriptOutput)

    def setVideo(self, filename, duration):
        """ Set video path """
        self._data['video'] = {
            'filename': filename,
            'trimStart': 0,
            'trimEnd': duration
        }

    def _generateScript(self):
        """ Generate script and fill the editor box """
        script = self.toScript()
        if script is None:
            return

        old_script = self._scriptEditor.toPlainText()

        if script == NO_VIDEO_LOADED_SCRIPT:
            utils.clearAndSetText(self._checkScriptOutput, script)
            return

        canOverwrite = True
        if script != old_script and old_script != OPENING_DEFAULT_SCRIPT:
            msgBox = utils.generateMessageBox(message="This will override the current script. Continue?",
                                              windowTitle="Hold on!", icon=QMessageBox.Warning,
                                              buttons=(QMessageBox.Ok | QMessageBox.Cancel))
            canOverwrite = msgBox.exec() == QMessageBox.Ok

        if canOverwrite:
            utils.clearAndSetText(self._scriptEditor, script, clear=True, setTimestamp=False)
            utils.clearAndSetText(self._checkScriptOutput, "Generated script")

    def _checkScript(self):
        """ Check script is valid """
        if self.scriptToFile(TMP_FILENAME):
            result, text = checkScript(TMP_FILENAME)
            utils.clearAndSetText(self._checkScriptOutput, text)
            os.remove(TMP_FILENAME)

    def _saveScriptToFile(self):
        """ Save script to specified file """
        filename, _ = QFileDialog.getSaveFileName(self._parent, 'Save Script', "", "VapourSynth script (*.vpy)")
        if filename:
            self.scriptToFile(filename)
            utils.clearAndSetText(self._checkScriptOutput, f"Script saved to {filename}")

    def _renderVideo(self):
        """ Render video """
        pass

    def scriptToFile(self, filename=TMP_FILENAME):
        """ Generate script and save to file  """
        script = self._scriptEditor.toPlainText()
        if script == OPENING_DEFAULT_SCRIPT:
            self._generateScript()
            script = self._scriptEditor.toPlainText()
            if script == OPENING_DEFAULT_SCRIPT:
                return False

        with open(filename, 'w') as fh:
            fh.write(script)

        return True

    def toScript(self):
        """ Convert data to executable python script """
        # if video has not been loaded, no script to make
        if 'video' not in self._data:
            return NO_VIDEO_LOADED_SCRIPT

        # overwrite data with fields from values
        if self._denoise.isVisible():
            curWidget = self._denoiseStack.currentWidget()
            if not curWidget.save():
                return None
            self._data['denoise']['type'] = str(self._denoiseFilters.currentText())
            self._data['denoise']['args'] = curWidget.args
        else:
            self._data['denoise'] = None

        # add stuff that will always be there + plugins
        videoData = self._data['video']
        plugins = '\n'.join(self._data['plugins'].values())

        script = f"""#!./bin/python.exe
import sys
sys.path.append('../bin/scripts64')

import vapoursynth as vs
{plugins}

core = vs.get_core()
#core.max_cache_size = 1000 #Use this command to limit the RAM usage (1000 is equivalent to 1GB of RAM)

video = core.lsmas.LWLibavSource(source=r"{videoData['filename']}")

# trim video
#video = core.std.Trim(video, {videoData['trimStart']}, {videoData['trimEnd']})
"""
        # add options
        script += evaluateVapourSynthOptions(self._data)

        # add output information
        script += f"""
video = core.fmtc.bitdepth(video, bits=16)
video.set_output()
"""     
        return script
