#!./bin/python.exe
"""
Layout containing options for Vapoursynth
"""
import os
import json
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QGridLayout, QPushButton, QComboBox, \
    QLabel, QHBoxLayout, QVBoxLayout, QMessageBox, QPlainTextEdit, QFileDialog, \
    QStackedLayout, QStyle

import lib.utils.pyqt_utils as utils
import lib.utils.vs_constants as c
from lib.utils.subprocess_utils import checkVSScript, renderVSVideo
from lib.utils.vs_evaluate_options import evaluateVapourSynthOptions
from lib.layouts.script_layout import OPENING_DEFAULT_SCRIPT
from lib.widgets.options_denoise_sharpen import DenoiseOptionKNLM, DenoiseOptionBM3D, FineSharpOptions

CWD = os.getcwd()
SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
WORK_DIR = os.path.join(SCRIPT_DIR, '../../work')

NO_VIDEO_LOADED_SCRIPT = 'A video must be loaded before the script can be generated and validated'
TMP_FILENAME = f"{WORK_DIR}/tmp.vpy"

PANEL_WIDTH = 300
ROW_HEIGHT = 50

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

        self._outputFormats = []
        for extension, out in c.OUTPUT_FORMATS.items():
            self._outputFormats.append(f'{out} (*{extension})')
        
        self._generateVapourSynthOptions()
        self._generateWidgets()
        self._generateLayout()

    def _generateVapourSynthOptions(self):
        """ Generate VapourSynth options """
        # preprocessing
        self._preprocessor = QComboBox()
        for item in c.PREPROCESSOR_CONFIG.keys():
            self._preprocessor.addItem(item)
        self._preprocessor.activated[str].connect(
            lambda text: self._addVapourSynthOption(text, 'preprocessor', c.PREPROCESSOR_PLUGINS, c.PREPROCESSOR_CONFIG))

        # denoising
        self._denoiseFilters = QComboBox()
        for item in c.DENOISE_CONFIG.keys():
            self._denoiseFilters.addItem(item)
        self._denoiseFilters.activated[str].connect(
            lambda text: self._addVapourSynthOption(text, 'denoise', c.DENOISE_PLUGINS, c.DENOISE_CONFIG, self._setDenoiseLayout))

        self._knlmOptions = DenoiseOptionKNLM()
        self._bm3dOptions = DenoiseOptionBM3D()

        # sharpening
        self._sharpenFilters = QComboBox()
        for item in c.SHARPEN_CONFIG.keys():
            self._sharpenFilters.addItem(item)
        self._sharpenFilters.activated[str].connect(
            lambda text: self._addVapourSynthOption(text, 'sharpen', c.SHARPEN_PLUGINS, c.SHARPEN_CONFIG, self._setSharpenLayout))

        self._fineSharpOptions = FineSharpOptions()

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

    def _setSharpenLayout(self, text):
        self._fineSharpOptions.save(ignoreErrors=True)
        if text == 'None':
            self._sharpen.hide()
        else:
            self._sharpen.show()

    def _openOutputFileDialogue(self):
        """ Open file dialogue """
        filename, _ = QFileDialog.getSaveFileName(self._parent, 'Video Output Location', "", ';;'.join(self._outputFormats))
        utils.clearAndSetText(self._outputFileText, filename)

    def _generateWidgets(self):
        """ Generate other widgets """
        self._outputFileText = QPlainTextEdit(os.path.join(CWD, 'output.mov'))
        self._outputFileText.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self._outputFileText.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self._outputFileText.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
        self._outputFileText.setMaximumHeight(ROW_HEIGHT / 2)
        self._outputFileButton = QPushButton()
        self._outputFileButton.setIcon(self._parent.style().standardIcon(QStyle.SP_DirIcon))
        self._outputFileButton.setMaximumWidth(ROW_HEIGHT)
        self._outputFileButton.clicked.connect(self._openOutputFileDialogue)

        self._generateScriptButton = QPushButton("Generate Script")
        self._generateScriptButton.clicked.connect(self._generateScript)

        self._checkVSScriptButton = QPushButton("Check Script")
        self._checkVSScriptButton.clicked.connect(self._checkScriptOkay)

        self._scriptToFileButton = QPushButton("Save script to file")
        self._scriptToFileButton.clicked.connect(self.saveScriptToFile)

        self._renderButton = QPushButton('Render video')
        self._renderButton.clicked.connect(self.renderVideo)

        self._outputTerminal = QPlainTextEdit()
        self._outputTerminal.setReadOnly(True)
        self._outputTerminal.setMaximumWidth(PANEL_WIDTH)

    def _generateLayout(self):
        """ Generate layout """
        outputRow = QWidget()
        outputRow.setLayout(utils.generateRow('Output:',
            [self._outputFileText, self._outputFileButton]))
        outputRow.setMaximumWidth(PANEL_WIDTH)
        outputRow.setMaximumHeight(ROW_HEIGHT / 2)
        self.addWidget(outputRow)

        self.addLayout(utils.generateRow("Preprocessor:", self._preprocessor))

        # stack denoise options
        self.addLayout(utils.generateRow('Denoise', self._denoiseFilters))
        self._denoise, self._denoiseStack = utils.generateStackedWidget(
            [self._knlmOptions, self._bm3dOptions], PANEL_WIDTH, ROW_HEIGHT)
        self.addWidget(self._denoise)
        self._denoise.hide()

        # stack sharpen options
        self.addLayout(utils.generateRow("Sharpen", self._sharpenFilters))
        self._sharpen, self._sharpenStack = utils.generateStackedWidget(
            [self._fineSharpOptions], PANEL_WIDTH, ROW_HEIGHT)
        self.addWidget(self._sharpen)
        self._sharpen.hide()

        self.addLayout(utils.generateRow(self._generateScriptButton, self._checkVSScriptButton))
        self.addLayout(utils.generateRow(self._scriptToFileButton, self._renderButton))
        self.addWidget(self._outputTerminal)

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
        if not script:
            return

        old_script = self._scriptEditor.toPlainText()

        if script == NO_VIDEO_LOADED_SCRIPT:
            utils.clearAndSetText(self._outputTerminal, NO_VIDEO_LOADED_SCRIPT, clear=False, setTimestamp=True)
            return

        canOverwrite = True
        if script != old_script and old_script != OPENING_DEFAULT_SCRIPT:
            msgBox = utils.generateMessageBox(message="This will override the current script. Continue?",
                                              windowTitle="Hold on!", icon=QMessageBox.Warning,
                                              buttons=(QMessageBox.Ok | QMessageBox.Cancel))
            canOverwrite = msgBox.exec() == QMessageBox.Ok

        if canOverwrite:
            utils.clearAndSetText(self._scriptEditor, script)
            utils.clearAndSetText(self._outputTerminal, "Generated script", clear=False, setTimestamp=True)

    def _checkScriptOkay(self):
        """ Check script is valid """
        if self.scriptToFile(TMP_FILENAME):
            result, text = checkVSScript(TMP_FILENAME)
            utils.clearAndSetText(self._outputTerminal, text, clear=False, setTimestamp=True)
            os.remove(TMP_FILENAME)

    def saveScriptToFile(self):
        """ Save script to specified file """
        if 'video' not in self._data:
            utils.clearAndSetText(self._outputTerminal, "A video must be loaded in order to generate and save a script", clear=False, setTimestamp=True)
            return

        filename, _ = QFileDialog.getSaveFileName(self._parent, 'Save Script', "", "VapourSynth script (*.vpy)")
        if filename:
            self.scriptToFile(filename)
            utils.clearAndSetText(self._outputTerminal, f"Script saved to {filename}", clear=False, setTimestamp=True)

    def renderVideo(self):
        """ Render video """
        if 'video' not in self._data:
            utils.clearAndSetText(self._outputTerminal, "A video must be loaded in order to render it", clear=False, setTimestamp=True)
            return

        fullFilePath = self._outputFileText.toPlainText()
        fullFilePath = fullFilePath.strip()
        filename, extension = os.path.splitext(fullFilePath)
        # reformat for png sequence
        if extension == '.png':
            filename += f"%05d{extension}"
            fullFilePath = os.path.join(os.path.dirname(fullFilePath), filename)

        renderVSVideo(fullFilePath, extension)
        utils.clearAndSetText(self._outputTerminal, f'Wrote to {fullFilePath}', clear=False, setTimestamp=True)

    def _checkCanSaveOption(self, key, pWidget, stack, filterWidget, ignoreErrors):
        """ Check if the option can be saved """
        if pWidget.isVisible():
            curWidget = stack.currentWidget()
            if not curWidget.save(ignoreErrors=ignoreErrors):
                print("can't save")
                return False

            self._data[key]['type'] = str(filterWidget.currentText())
            self._data[key]['args'] = curWidget.args
        else:
            self._data[key] = None

        return True

    def _saveValues(self, ignoreErrors=False):
        """ Save all fields """
        return self._checkCanSaveOption('denoise', self._denoise, self._denoiseStack, self._denoiseFilters, ignoreErrors) and \
            self._checkCanSaveOption('sharpen', self._sharpen, self._sharpenStack, self._sharpenFilters, ignoreErrors)

    def clearTerminal(self):
        """ Clear script output terminal """
        self._outputTerminal.clear()

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

        if not self._saveValues():
            return False

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
