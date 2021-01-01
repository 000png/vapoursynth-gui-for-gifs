#!./bin/python.exe
"""
Layout containing options for Vapoursynth
"""
import os
import re
import time
import posixpath
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QPushButton, QComboBox, QLabel, QVBoxLayout, QMessageBox, \
    QPlainTextEdit, QFileDialog, QStackedLayout, QStyle

import lib.utils.PyQtUtils as utils
import lib.utils.VSConstants as c
from lib.utils.SubprocessUtils import checkVSScript, renderVSVideo, trimVideo, TRIMMED_FILENAME
from lib.widgets.OptionsDenoiseSharpen import DenoiseOptionKNLM, DenoiseOptionBM3D, FineSharpOptions
from lib.layouts.ResizeCropWindow import ResizeCropWindow
from lib.helpers.SubprocessManager import SubprocessManager
from lib.helpers.PresetManager import PresetManager

CWD = os.getcwd()
SCRIPT_DIR = os.path.abspath(os.path.dirname(os.path.realpath(__file__))).replace(os.sep, posixpath.sep)
WORK_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, '..\\..\\..\\work')).replace(os.sep, posixpath.sep)
TMP_VS_SCRIPT = os.path.abspath(os.path.join(WORK_DIR, 'tmp.vpy')).replace(os.sep, posixpath.sep)

NO_VIDEO_LOADED_SCRIPT = 'A video must be loaded before the script can be generated and validated'

PANEL_WIDTH = 350
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
        self._presetManager = PresetManager(self)

    def setSubprocessManager(self, loadingScreen):
        self._subprocessManager = SubprocessManager(loadingScreen, self._outputTerminal)

    def _generateVapourSynthOptions(self):
        """ Generate VapourSynth options """
        # preprocessing
        preprocessor = QComboBox()
        for item in c.PREPROCESSOR_CONFIG.keys():
            preprocessor.addItem(item)
        preprocessor.activated[str].connect(
            lambda text: self._addVapourSynthOption(text, 'preprocessor', c.PREPROCESSOR_PLUGINS, c.PREPROCESSOR_CONFIG))
        preprocessor.setCurrentIndex(1)

        # denoising
        denoise = QComboBox()
        for item in c.DENOISE_CONFIG.keys():
            denoise.addItem(item)
        denoise.activated[str].connect(
            lambda text: self._addVapourSynthOption(text, 'denoise', c.DENOISE_PLUGINS, c.DENOISE_CONFIG, self._setDenoiseLayout))

        self._knlmOptions = DenoiseOptionKNLM()
        self._bm3dOptions = DenoiseOptionBM3D()

        # sharpening
        sharpen = QComboBox()
        for item in c.SHARPEN_CONFIG.keys():
            sharpen.addItem(item)
        sharpen.activated[str].connect(
            lambda text: self._addVapourSynthOption(text, 'sharpen', c.SHARPEN_PLUGINS, c.SHARPEN_CONFIG, self._setSharpenLayout))

        self._fineSharpOptions = FineSharpOptions()

        self._dropdowns = {
            'preprocessor': preprocessor,
            'denoise': denoise,
            'sharpen': sharpen
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
            otherFuncToExecute(text)

    def _setDenoiseLayout(self, text):
        """ Set stack """
        self._knlmOptions.save(ignoreErrors=True)
        self._bm3dOptions.save(ignoreErrors=True)
        if text == 'None':
            self._denoiseOptions.hide()
        else:
            self._denoiseOptions.show()
            self._stacks['denoise'].setCurrentWidget(self._knlmOptions) if text == 'KNLM' \
                else self._stacks['denoise'].setCurrentWidget(self._bm3dOptions)

    def _setSharpenLayout(self, text):
        self._fineSharpOptions.save(ignoreErrors=True)
        if text == 'None':
            self._sharpenOptions.hide()
        else:
            self._sharpenOptions.show()

    def _openOutputFileDialogue(self):
        """ Open file dialogue """
        filename, _ = QFileDialog.getSaveFileName(self._parent, 'Video Output Location', "", ';;'.join(self._outputFormats))
        if filename:
            utils.clearAndSetText(self._outputFileText, filename, setToBottom=False)

    def _generateWidgets(self):
        """ Generate other widgets """
        self._outputFileText = utils.generateTextEntry(os.path.join(CWD, 'output.mov'))
        self._outputFileButton = QPushButton()
        self._outputFileButton.setIcon(self._parent.style().standardIcon(QStyle.SP_DirIcon))
        self._outputFileButton.setMaximumWidth(ROW_HEIGHT)
        self._outputFileButton.clicked.connect(self._openOutputFileDialogue)

        self._trimStart = utils.generateTextEntry("00:00:00")
        self._trimEnd = utils.generateTextEntry("00:00:05")
        for item in [self._outputFileText, self._trimStart, self._trimEnd]:
            item.setMaximumHeight(ROW_HEIGHT / 2)

        self._resizeCropButton = QPushButton("Resize And Crop")
        self._resizeCropButton.clicked.connect(self.openResizeCropWindow)

        self._resizeCropText = QPlainTextEdit()
        self._resizeCropText.setPlaceholderText("copy & paste output from the resize/crop window here")
        self._resizeCropText.setMaximumWidth(PANEL_WIDTH)
        self._resizeCropText.setMaximumHeight(ROW_HEIGHT)

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
        self._outputTerminal.setMaximumWidth(PANEL_WIDTH)

    def _generateLayout(self):
        """ Generate layout """
        outputRow = QWidget()
        outputRow.setLayout(utils.generateRow('Output:', [self._outputFileText, self._outputFileButton]))

        trimRow = QWidget()
        trimRow.setLayout(utils.generateRow('Trim (HH:MM:SS):', [self._trimStart, QLabel(':'), self._trimEnd]))

        for item in [outputRow, trimRow]:
            item.setMaximumWidth(PANEL_WIDTH)
            item.setMaximumHeight(ROW_HEIGHT / 2)
            self.addWidget(item)

        self.addWidget(self._resizeCropButton)
        self.addWidget(self._resizeCropText)
        self.addLayout(utils.generateRow("Preprocessor:", self._dropdowns['preprocessor']))

        # stack denoise options
        self.addLayout(utils.generateRow('Denoise', self._dropdowns['denoise']))
        self._denoiseOptions, denoiseStack = utils.generateStackedWidget(
            [self._knlmOptions, self._bm3dOptions], PANEL_WIDTH, ROW_HEIGHT)
        self.addWidget(self._denoiseOptions)
        self._denoiseOptions.hide()

        # stack sharpen options
        self.addLayout(utils.generateRow("Sharpen", self._dropdowns['sharpen']))
        self._sharpenOptions, sharpenStack = utils.generateStackedWidget(
            [self._fineSharpOptions], PANEL_WIDTH, ROW_HEIGHT)
        self.addWidget(self._sharpenOptions)
        self._sharpenOptions.hide()

        self._stacks = {
            'denoise': denoiseStack,
            'sharpen': sharpenStack
        }

        self.addLayout(utils.generateRow(self._checkVSScriptButton, self._generateScriptButton))
        self.addLayout(utils.generateRow(self._renderButton, self._renderAutoButton))
        self.addWidget(self._outputTerminal)

    def _finishedOpenCropWindow(self):
        result, out, err = self._subprocessManager.getFinishedSubprocessResults()
        if result == 0:
            self._resizeWindow = ResizeCropWindow(self._parent)
            self._resizeWindow.show()

    def setTrimValues(self):
        """ Set trim values """
        start = self._trimStart.toPlainText().strip()
        end = self._trimEnd.toPlainText().strip()
        videoData = self._data['video']

        if videoData['stateChanged'] or (start != videoData['start']) or (end != videoData['end']):
            videoData['start'] = start
            videoData['end'] = end
            videoData['stateChanged'] = True
        else:
            videoData['stateChanged'] = False

        return start, end

    def openResizeCropWindow(self):
        """ Open resize crop window """
        if 'video' not in self._data:
            utils.clearAndSetText(self._outputTerminal, "A video must be loaded in order to crop/resize it", clear=False, setTimestamp=True)
            return

        start, end = self.setTrimValues()
        videoData = self._data['video']

        if videoData['stateChanged']:
            self._subprocessManager.setSubprocess(trimVideo(videoData['filename'], start, end,
                trimFilename=os.path.abspath(os.path.join(WORK_DIR, 'resizer.webm')),
                trimArgs="-vcodec libvpx -acodec libvorbis -preset ultrafast"),
                self._finishedOpenCropWindow)
            videoData['stateChanged'] = False
        else:
            self._finishedOpenCropWindow()

    def _finishedCheckScriptOkay(self):
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
        result, out, err = self._subprocessManager.getFinishedSubprocessResults()
        utils.clearAndSetText(self._outputTerminal, err, clear=False, setTimestamp=True)

        if result != 0:
            msgBox = utils.generateMessageBox(f"Rendering failed; check terminal output for logs", icon=QMessageBox.Critical,
                                              windowTitle="Invalid argument")
            msgBox.exec()
        else:
            # set new video in render panel
            self._parent.setVideos(self._outputFileText.toPlainText().strip(), videoType='render')

    def renderVideo(self, regenerateScript=True):
        """ Render video """
        if 'video' not in self._data:
            utils.clearAndSetText(self._outputTerminal, "A video must be loaded in order to render it", clear=False, setTimestamp=True)
            return

        fullFilePath = self._outputFileText.toPlainText()
        fullFilePath = fullFilePath.strip()
        filename, extension = os.path.splitext(fullFilePath)
        # reformat for png sequence
        if extension == '.png':
            filename += f"%%05d{extension}"
            fullFilePath = os.path.join(os.path.dirname(fullFilePath), filename)

        if self.scriptToFile(TMP_VS_SCRIPT, regenerateScript=regenerateScript):
            start = self._trimStart.toPlainText().strip()
            end = self._trimEnd.toPlainText().strip()
            cmds = renderVSVideo(TMP_VS_SCRIPT, self._data['video']['filename'], fullFilePath, extension, start, end)
            self._subprocessManager.setSubprocess(cmds[0], None, nextCmd={'cmd': cmds[1], 'onFinish': self._finishedRender})
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
        self._data['output'] = self._outputFileText.toPlainText().strip()
        if 'video' in self._data:
            self._data['video']['start'] = self._trimStart.toPlainText().strip()
            self._data['video']['end'] = self._trimEnd.toPlainText().strip()

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
            self._checkCanSaveOption('sharpen', self._sharpenOptions, ignoreErrors)

    def clearTerminal(self):
        """ Clear script output terminal """
        self._outputTerminal.clear()

    def setVideo(self, filename):
        """ Set video path """
        self._data['video'] = {
            'filename': filename,
            'trimmedFilename': TRIMMED_FILENAME,
            'start': "00:00:00",
            'end': "00:00:05",
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
        for item in ['preprocessor', 'denoise', 'sharpen']:
            value = self._data.get(item, 'None')
            if value is None:
                value = 'None'

            index = self._dropdowns[item].findText(value['type']) if value != 'None' else 0
            if index >= 0:
                self._dropdowns[item].setCurrentIndex(index)
                if index > 0:
                    if item == 'denoise':
                        self._setDenoiseLayout(value['type'])
                        options = self._knlmOptions if value['type'] == 'KNLM' else self._bm3dOptions
                        options.loadArgs(value['args'])
                    elif item == 'sharpen':
                        self._setSharpenLayout(value['type'])
                        self._fineSharpOptions.loadArgs(value['args'])

        if 'video' in self._data:
            filename = self._data['video'].get('filename', None)
            if filename and os.path.isfile(filename):
                self._parent.setVideos(filename)
                self._data['video']['stateChanged'] = True

            utils.clearAndSetText(self._trimStart, self._data['video'].get('start', '00:00:00'), setToBottom=False)
            utils.clearAndSetText(self._trimEnd, self._data['video'].get('end', '00:00:05'), setToBottom=False)

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
        if not isHistory:
            filename, _ = QFileDialog.getSaveFileName(self._parent, 'Video Output Location', "", ';;'.join(['*.json']))
            if filename:
                save = True
        else:
            filename = None

        if save:
            self._saveValues(ignoreErrors=isHistory)
            self._presetManager.savePreset(self._data, filename=filename, isHistory=isHistory)

    def loadPreset(self):
        filename, _ = QFileDialog.getOpenFileName(self._parent, 'Video Output Location', "", ';;'.join(['*.json']))
        if filename:
            self._presetManager.loadPreset(preset=filename)
