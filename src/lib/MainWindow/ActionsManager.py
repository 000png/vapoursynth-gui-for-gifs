#!./bin/python.exe
"""
Actions/menu manager for the MainWindow's menu bar.
"""
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QAction, QStyle


class ActionsManager():
    """ Actions manager class """
    def __init__(self, mainWindow):
        """ Initializer """
        self.mainWindow = mainWindow
        style = self.mainWindow.style()

        self._icons = {
            'toggled': QIcon(style.standardIcon(QStyle.SP_DialogApplyButton)),
            'notToggled': QIcon(style.standardIcon(QStyle.SP_DialogCancelButton)),
            'open': QIcon(style.standardIcon(QStyle.SP_DirIcon)),
            'save': QIcon(style.standardIcon(QStyle.SP_DialogSaveButton)),
            'exit': QIcon('exit.png')
        }
        self._toggles = {}

    def _makeGenericAction(self, connect, title, icon, statusTip=None, shortcut=None, toggleActionName=None):
        """ Make generic action """
        action = QAction(icon, title, self.mainWindow)
        action.triggered.connect(connect)

        if shortcut:
            action.setShortcut(shortcut)
        if statusTip:
            action.setStatusTip(statusTip)

        return action

    def _makeToggleAction(self, connect, title, icon, toggleActioName, statusTip=None, shortcut=None, startTriggered=True):
        """ Make toggle action """
        action = self._makeGenericAction(connect, title, icon, statusTip, shortcut)
        action.setCheckable(True)
        action.setChecked(startTriggered)

        self._toggles[toggleActioName] = action
        return action

    def makeAction(self, actionName, connect):
        """ Make actions """
        if actionName == 'open_video':
            return self._makeGenericAction(connect, '&Open', self._icons['open'], 'Open video', 'Ctrl+O')
        elif actionName == 'save_preset':
            return self._makeGenericAction(connect, '&Save preset', self._icons['save'], 'Save current editor state as preset')
        elif actionName == 'load_preset':
            return self._makeGenericAction(connect, '&Load preset', self._icons['open'], 'Load preset into editor')
        elif actionName == 'save_script':
            return self._makeGenericAction(connect, '&Save script', self._icons['save'], 'Save script')
        elif actionName == 'exit':
            return self._makeGenericAction(connect, '&Exit', self._icons['exit'], 'Exit application', 'Ctrl+Q')
        elif actionName == 'resizer':
            return self._makeGenericAction(connect, '&Resize and crop', self._icons['open'], 'Resize and crop video', 'Ctrl+R')
        elif actionName == 'ffmpeg_settings':
            return self._makeGenericAction(connect, '&FFMPEG Settings', self._icons['exit'], 'FFMPEG settings')
        elif actionName == 'toggle_original_video':
            return self._makeToggleAction(connect, '&Show original video', self._icons['toggled'], actionName,
                                          'Toggle showing the original video in the editor')
        elif actionName == 'toggle_render_video':
            return self._makeToggleAction(connect, '&Show render video', self._icons['toggled'], actionName,
                                          'Toggle showing the render video in the editor')
        elif actionName == 'toggle_browser_resizer':
            return self._makeToggleAction(connect, '&Open resizer in browser', self._icons['toggled'], actionName,
                                          'Open up the resizer in the default browser')
        else:
            raise ValueError(f"Unrecognized action name {actionName}")

    def toggleAction(self, actionName):
        """ Toggle icon on action """
        if actionName not in self._toggles:
            raise ValueError(f"Action {actionName} not found; may need to create action first")

        toggle = self._toggles[actionName]
        iconKey = 'toggled' if toggle.isChecked() else 'notToggled'
        toggle.setIcon(self._icons[iconKey])

        return toggle.isChecked()

    def isActionToggled(self, actionName):
        """ Returns whether or not an action is toggled """
        if actionName not in self._toggles:
            raise ValueError(f"Action {actionName} not found; may need to create action first")
        return self._toggles[actionName].isChecked()
