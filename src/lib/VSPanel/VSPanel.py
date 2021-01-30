#!./bin/python.exe
"""
Layout containing options for Vapoursynth
"""
import os
import re
import posixpath
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QPushButton, QComboBox, QLabel, QVBoxLayout, QMessageBox, \
    QPlainTextEdit, QFileDialog, QStackedLayout, QStyle, QFrame

import lib.utils.PyQtUtils as utils
from lib.Resizer.ResizerWindow import ResizerWindow
from lib.utils.SubprocessManager import SubprocessManager
from lib.utils.SubprocessUtils import checkVSScript, renderVSVideo, trimVideo, TRIMMED_FILENAME

from . import VSConstants as c
from .PresetManager import PresetManager
from .OptionsVS import DenoiseOptionKNLM, DenoiseOptionBM3D, FineSharpOptions, TrimOptions

CWD = os.getcwd()
SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
WORK_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, '../../../work'))
TMP_VS_SCRIPT = os.path.join(WORK_DIR, 'tmp.vpy')

NO_VIDEO_LOADED_SCRIPT = 'A video must be loaded before the script can be generated and validated'


class VSPanelFrame(QFrame):
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
        self._presetManager = PresetManager(self)

    def setSubprocessManager(self, loadingScreen):
        """ Set the subprocess manager """
        self._subprocessManager = SubprocessManager(loadingScreen, self._outputTerminal)

    def _generateComboBox(self, option, config, plugins, index=0, otherFuncToExecute=None):
        """ Generate VSOptions dropdown combobox """
        comboBox = QComboBox()
        for item in config.keys():
            comboBox.addItem(item)

        comboBox.activated[str].connect(
            lambda text: self._addVapourSynthOption(text, option, plugins, config, otherFuncToExecute))
        comboBox.setCurrentIndex(index)

        return comboBox

    def _generateVapourSynthOptions(self):
        """ Generate VapourSynth options """
        # denoising
        self._knlmOptions = DenoiseOptionKNLM()
        self._bm3dOptions = DenoiseOptionBM3D()

        # sharpening
        self._fineSharpOptions = FineSharpOptions()

        # trimming; this is actually to preprocess trimming with ffmpeg beforehand or not
        self._vsTrimOption = TrimOptions()

        self._dropdowns = {
            'preprocessor': self._generateComboBox('preprocessor', c.PREPROCESSOR_CONFIG, c.PREPROCESSOR_PLUGINS, index=1),
            'denoise': self._generateComboBox('denoise', c.DENOISE_CONFIG, c.DENOISE_PLUGINS, otherFuncToExecute=self._setLayout),
            'sharpen': self._generateComboBox('sharpen', c.SHARPEN_CONFIG, c.SHARPEN_PLUGINS, otherFuncToExecute=self._setLayout),
            'trim': self._generateComboBox('trim', c.TRIM_CONFIG, c.TRIM_PLUGINS, otherFuncToExecute=self._setLayout)
        }

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
            otherFuncToExecute(text, key)

    def _setLayout(self, text, key):
        """ Set denoise layout, switch on stack """
        if key == 'denoise':
            self._knlmOptions.save(ignoreErrors=True)
            self._bm3dOptions.save(ignoreErrors=True)
            options = self._denoiseOptions
        elif key == 'sharpen':
            self._fineSharpOptions.save(ignoreErrors=True)
            options = self._sharpenOptions
        elif key == 'trim':
            self._vsTrimOption.save(ignoreErrors=True)
            options = self._trimOptions
        else:
            raise ValueError(f"Unrecognized key {key}")

        if text == 'None':
            options.hide()
        else:
            options.show()
            if key == 'denoise':
                self._stacks['denoise'].setCurrentWidget(self._knlmOptions) if text == 'KNLM' \
                    else self._stacks['denoise'].setCurrentWidget(self._bm3dOptions)

    def _openOutputFileDialogue(self):
        """ Open file dialogue """
        filename, _ = QFileDialog.getSaveFileName(self._parent, 'Video Output Location', "", ';;'.join(self._outputFormats))
        if filename:
            utils.clearAndSetText(self._outputFileText, filename, setToBottom=False)

    def _generateWidgets(self):
        """ Generate other widgets """
        self._outputFileText = utils.generateTextEntry(os.path.join(CWD, 'output.mov'), oneLiner=True)
        self._outputFileButton = QPushButton()
        self._outputFileButton.setIcon(self._parent.style().standardIcon(QStyle.SP_DirIcon))
        self._outputFileButton.setMaximumWidth(50)
        self._outputFileButton.clicked.connect(self._openOutputFileDialogue)

        self._resizeCropButton = QPushButton("Resize And Crop")
        self._resizeCropButton.clicked.connect(self.openResizer)

        self._resizeCropText = QPlainTextEdit()
        self._resizeCropText.setPlaceholderText("copy & paste output from the resize/crop window here")
        self._resizeCropText.setMaximumHeight(75)

        self._generateScriptButton = QPushButton("Generate Script")
        self._generateScriptButton.clicked.connect(self._generateScript)

        self._checkVSScriptButton = QPushButton("Check Script")
        self._checkVSScriptButton.clicked.connect(self._checkScriptOkay)

        self._renderAutoButton = QPushButton("Render (auto)")
        self._renderAutoButton.clicked.connect(lambda: self.renderVideo(regenerateScript=True))

        self._renderButton = QPushButton('Render (custom script)')
        self._renderButton.clicked.connect(lambda: self.renderVideo(regenerateScript=False))

        self._outputTerminal = QPlainTextEdit()
        self._outputTerminal.setReadOnly(True)

    def _generateLayout(self):
        """ Generate layout """
        layout = QVBoxLayout(self)

        outputRow = QWidget()
        outputRow.setLayout(utils.generateRow('Output:', [self._outputFileText, self._outputFileButton]))
        layout.addWidget(outputRow)

        # stack trim options
        layout.addLayout(utils.generateRow('Apply trimming:', self._dropdowns['trim']))
        self._trimOptions, trimStack = utils.generateStackedWidget([self._vsTrimOption])
        layout.addWidget(self._trimOptions)
        self._trimOptions.hide()

        layout.addWidget(self._resizeCropButton)
        layout.addWidget(self._resizeCropText)
        layout.addLayout(utils.generateRow("Preprocessor:", self._dropdowns['preprocessor']))

        # stack denoise options
        layout.addLayout(utils.generateRow('Denoise', self._dropdowns['denoise']))
        self._denoiseOptions, denoiseStack = utils.generateStackedWidget(
            [self._knlmOptions, self._bm3dOptions])
        layout.addWidget(self._denoiseOptions)
        self._denoiseOptions.hide()

        # stack sharpen options
        layout.addLayout(utils.generateRow("Sharpen", self._dropdowns['sharpen']))
        self._sharpenOptions, sharpenStack = utils.generateStackedWidget(
            [self._fineSharpOptions])
        layout.addWidget(self._sharpenOptions)
        self._sharpenOptions.hide()

        self._stacks = {
            'denoise': denoiseStack,
            'sharpen': sharpenStack,
            'trim': trimStack
        }

        layout.addLayout(utils.generateRow(self._checkVSScriptButton, self._generateScriptButton))
        layout.addLayout(utils.generateRow(self._renderButton, self._renderAutoButton))
        layout.addWidget(self._outputTerminal)

        self.setLayout(layout)
        self.setFrameShape(QFrame.StyledPanel)

    def _finishedOpenCropWindow(self, useBrowserForResize = False):
        """ On finished rendering webm for html window """
        if not useBrowserForResize:
            result, out, err = self._subprocessManager.getFinishedSubprocessResults()
            if result == 0:
                self._resizeWindow = ResizerWindow(self._parent)
                self._resizeWindow.show()
        else:
            ResizerWindow.openInBrowser(self._data['video']['filename'])

    def openResizer(self):
        """ Open resize crop window """
        if 'video' not in self._data:
            utils.clearAndSetText(self._outputTerminal, "A video must be loaded in order to crop/resize it", clear=False, setTimestamp=True)
            return

        videoData = self._data['video']
        if videoData['stateChanged'] and not self._parent._useBrowserForResizer:
            self._subprocessManager.setSubprocess(trimVideo(videoData['filename'], '00:00:00', '00:01:00',
                trimFilename=os.path.abspath(os.path.join(WORK_DIR, 'resizer.webm')),
                trimArgs="-vcodec libvpx -acodec libvorbis -preset ultrafast"),
                self._finishedOpenCropWindow)
            videoData['stateChanged'] = False
        else:
            self._finishedOpenCropWindow(self._parent._useBrowserForResizer)

    def _finishedCheckScriptOkay(self):
        """ On finished calling VSPipe to check if script is okay """
        result, _, _ = self._subprocessManager.getFinishedSubprocessResults()
        if result != 0:
            msgBox = utils.generateMessageBox(message="Script was invalid, check terminal output for logs",
                                              windowTitle="Script invalid", icon=QMessageBox.Warning)
            msgBox.exec()

    def _checkScriptOkay(self):
        """ Check script is valid """
        if self.scriptToFile(TMP_VS_SCRIPT, regenerateScript=self._scriptEditor.toPlainText() == ""):
            self._subprocessManager.setSubprocess(checkVSScript(TMP_VS_SCRIPT), self._finishedCheckScriptOkay)

    def _generateScript(self):
        """ Generate script and fill the editor box """
        script = self.toScript()
        if not script:
            return False

        script = script.strip()
        old_script = self._scriptEditor.toPlainText().strip()

        if script == NO_VIDEO_LOADED_SCRIPT:
            utils.clearAndSetText(self._outputTerminal, NO_VIDEO_LOADED_SCRIPT, clear=False, setTimestamp=True)
            return False

        canOverwrite = True
        if script != old_script and old_script:
            msgBox = utils.generateMessageBox(message="This will override the current script. Continue?",
                                              windowTitle="Hold on!", icon=QMessageBox.Warning,
                                              buttons=(QMessageBox.Ok | QMessageBox.Cancel))
            canOverwrite = msgBox.exec() == QMessageBox.Ok

        if canOverwrite:
            utils.clearAndSetText(self._scriptEditor, script)
            utils.clearAndSetText(self._outputTerminal, "Generated script", clear=False, setTimestamp=True)

        return canOverwrite

    def scriptToFile(self, filename=TMP_VS_SCRIPT, regenerateScript=True):
        """ Generate script and save to file  """
        if not regenerateScript or self._generateScript():
            script = self._scriptEditor.toPlainText()
            if not script:
                return False
            with open(filename, 'w') as fh:
                fh.write(script)
            return True

        return False

    def saveScriptToFile(self):
        """ Save script to specified file """
        if 'video' not in self._data:
            utils.clearAndSetText(self._outputTerminal, "A video must be loaded in order to generate and save a script", clear=False, setTimestamp=True)
            return

        filename, _ = QFileDialog.getSaveFileName(self._parent, 'Save Script', "", "VapourSynth script (*.vpy)")
        if filename:
            filename = filename.strip()
            self.scriptToFile(filename, regenerateScript=False)
            utils.clearAndSetText(self._outputTerminal, f"Script saved to {filename}", clear=False, setTimestamp=True)

    def _finishedRender(self):
        """ On finish rendering through VapourSynth """
        result, out, err = self._subprocessManager.getFinishedSubprocessResults()
        utils.clearAndSetText(self._outputTerminal, err, clear=False, setTimestamp=True)

        if result != 0:
            msgBox = utils.generateMessageBox(f"Rendering failed; check terminal output for logs", icon=QMessageBox.Critical,
                                              windowTitle="Invalid argument")
            msgBox.exec()
        else:
            # set new video in render panel
            self._parent.setVideos(self._outputFileText.text().strip(), videoType='render')

    def renderVideo(self, regenerateScript=True):
        """ Render video """
        if 'video' not in self._data:
            utils.clearAndSetText(self._outputTerminal, "A video must be loaded in order to render it", clear=False, setTimestamp=True)
            return

        fullFilePath = self._outputFileText.text()
        fullFilePath = fullFilePath.strip()
        filename, extension = os.path.splitext(fullFilePath)
        # reformat for png sequence
        if extension == '.png':
            filename += f"%%05d{extension}"
            fullFilePath = os.path.join(os.path.dirname(fullFilePath), filename)

        if self.scriptToFile(TMP_VS_SCRIPT, regenerateScript=regenerateScript):
            cmd = renderVSVideo(TMP_VS_SCRIPT, self._data['video']['filename'], fullFilePath, extension)
            self._subprocessManager.setSubprocess(cmd, self._finishedRender)
        else:
            utils.clearAndSetText(self._outputTerminal, f'Failed to render video; make sure script is correct', clear=False, setTimestamp=True)

    def _checkCanSaveOption(self, key, pWidget, ignoreErrors):
        """ Check if the option can be saved """
        stack = self._stacks[key]
        dropdown = self._dropdowns[key]

        if pWidget.isVisible():
            curWidget = stack.currentWidget()
            if not curWidget.save(ignoreErrors=ignoreErrors):
                return False

            self._data[key]['type'] = str(dropdown.currentText())
            self._data[key]['args'] = curWidget.args
        else:
            self._data[key] = None

        return True

    def _saveValues(self, ignoreErrors=False):
        """ Save all fields """
        self._data['output'] = self._outputFileText.text().strip()

        orgData = self._resizeCropText.toPlainText().strip()
        resizeData = re.sub(r'\n\s*\n', '\n', orgData)
        resizeData = resizeData.split('\n')
        for item in resizeData:
            if 'descale.' in item:
                self._data['descale'] = item
                self._data['plugins'].update(c.DESCALE_PLUGINS)
            elif 'core.std.CropRel' in item:
                self._data['crop'] = item

        if 'descale.' not in orgData:
            self._data['descale'] = None
            self._data['plugins'].pop('descale', None)
        if 'core.std.CropRel' not in orgData:
            self._data['crop'] = None

        return self._checkCanSaveOption('denoise', self._denoiseOptions, ignoreErrors) and \
            self._checkCanSaveOption('sharpen', self._sharpenOptions, ignoreErrors) and \
            self._checkCanSaveOption('trim', self._trimOptions, ignoreErrors)

    def clearTerminal(self):
        """ Clear script output terminal """
        self._outputTerminal.clear()

    def setVideo(self, filename):
        """ Set video path """
        self._data['video'] = {
            'filename': filename,
            'stateChanged': True
        }

    def toScript(self):
        """ Convert data to executable python script """
        # if video has not been loaded, no script to make
        if 'video' not in self._data:
            return NO_VIDEO_LOADED_SCRIPT

        if not self._saveValues():
            return False

        return self._scriptEditor.toScript(self._data)

    def repopulateFields(self, newData):
        """ Update data object """
        self._data.update(newData)

        # None is always the 0th index
        for item in ['preprocessor', 'denoise', 'sharpen', 'trim']:
            value = self._data.get(item, 'None')
            if value is None:
                value = 'None'

            index = self._dropdowns[item].findText(value['type']) if value != 'None' else 0
            if index >= 0:
                self._dropdowns[item].setCurrentIndex(index)
                if index > 0:
                    if item != 'preprocessor':
                        self._setLayout(value['type'], item)
                    if item == 'denoise':
                        options = self._knlmOptions if value['type'] == 'KNLM' else self._bm3dOptions
                        options.loadArgs(value['args'])
                    elif item == 'sharpen':
                        self._fineSharpOptions.loadArgs(value['args'])
                    elif item == 'trim':
                        self._vsTrimOption.loadArgs(value['args'])

        if 'video' in self._data:
            filename = self._data['video'].get('filename', None)
            if filename and os.path.isfile(filename):
                self._parent.setVideos(filename)
                self._data['video']['stateChanged'] = True
            else:
                self._data.pop('video', None)

        if 'output' in self._data:
            utils.clearAndSetText(self._outputFileText, self._data['output'], setToBottom=False)

        resizeCropText = ''
        if self._data.get('descale', None):
            resizeCropText += self._data['descale'] + '\n'

        if self._data.get('crop', None):
            resizeCropText += self._data['crop']
        
        if resizeCropText:
            utils.clearAndSetText(self._resizeCropText, resizeCropText, setToBottom=False)

    def savePreset(self, isHistory=False):
        """ Save history """
        save = isHistory
        filename = None
        if not isHistory:
            filename, _ = QFileDialog.getSaveFileName(self._parent, 'Video Output Location', "", ';;'.join(['*.json']))
            if filename:
                save = True

        if save:
            self._saveValues(ignoreErrors=isHistory)
            self._presetManager.savePreset(self._data, filename=filename, isHistory=isHistory)

    def loadPreset(self):
        """ Load preset """
        filename, _ = QFileDialog.getOpenFileName(self._parent, 'Video Output Location', "", ';;'.join(['*.json']))
        if filename:
            self._presetManager.loadPreset(preset=filename)
