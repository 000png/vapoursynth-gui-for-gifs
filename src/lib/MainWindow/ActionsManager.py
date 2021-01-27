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

    def _makeGenericAction(self, connect, title, icon, statusTip=None, shortcut=None, actionName=None):
        """ Make generic action """
        action = QAction(icon, title, self.mainWindow)
        action.triggered.connect(connect)

        if shortcut:
            action.setShortcut(shortcut)
        if statusTip:
            action.setStatusTip(statusTip)
        if actionName:
            self._toggles[actionName] = action

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
        elif actionName == 'toggle_original_video':
            return self._makeGenericAction(connect, '&Toggle original video', self._icons['toggled'],
                                       'Toggle showing the original video in the editor',
                                       actionName=actionName)
        elif actionName == 'toggle_render_video':
            return self._makeGenericAction(connect, '&Toggle render video', self._icons['toggled'],
                                       'Toggle showing the render video in the editor',
                                       actionName=actionName)
        elif actionName == 'toggle_browser_resizer':
            return self._makeGenericAction(connect, '&Use browser for resizer', self._icons['toggled'],
                                       'Open up the resizer in the default browser',
                                       actionName=actionName)
        else:
            raise ValueError(f"Unrecognized action name {actionName}")

    def setToggleIcon(self, actionName, result):
        """ Toggle icon on action """
        if actionName not in self._toggles:
            raise ValueError(f"Action {actionName} not found; may need to create action first")

        iconKey = 'toggled' if result else 'notToggled'
        self._toggles[actionName].setIcon(self._icons[iconKey])
