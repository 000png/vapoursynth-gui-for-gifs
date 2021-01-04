#!./bin/python.exe
"""
Helps with managing QProcesses for VSPanelLayout
"""
from PyQt5.QtCore import QProcess
from lib.utils.PyQtUtils import clearAndSetText


class SubprocessManager():
    """ Class to help with QProcessses """
    def __init__(self, loadingScreen, outputTerminal):
        """ Initializer """
        self._loadingScreen = loadingScreen
        self._loadingScreen.setAbortFunction(self.onAbort)
        self._outputTerminal = outputTerminal

    def setSubprocess(self, cmd, onFinish, nextCmd=None):
        """ Set subprocess """
        if onFinish is None and nextCmd is None:
            raise ValueError("Need either onFinish or nextCmd")

        self._loadingScreen.show()
        self._p = QProcess()

        if not onFinish:
            self._p.finished.connect(lambda: self.setSubprocess(**nextCmd))
        else:
            self._p.finished.connect(lambda: self._prepOnFinish(onFinish))

        self._p.readyReadStandardError.connect(self.onReadyReadStandardError)
        self._p.readyReadStandardOutput.connect(self.onReadyReadStandardOutput)
        clearAndSetText(self._outputTerminal, f"EXECUTING CMD:\n{cmd}", clear=False, setTimestamp=True)
        self._p.start(cmd)

    def getFinishedSubprocessResults(self):
        """ Get finished subprocess results """
        return self._p.exitCode(), self._p.readAllStandardOutput().data().decode(), self._p.readAllStandardError().data().decode()

    def onReadyReadStandardError(self):
        """ Stream stderr """
        error = self._p.readAllStandardError().data().decode()
        clearAndSetText(self._outputTerminal, error, clear=False, setTimestamp=True)

    def onReadyReadStandardOutput(self):
        """ Stream stdout """
        out = self._p.readAllStandardOutput().data().decode()
        clearAndSetText(self._outputTerminal, '\n' + out, clear=False, setTimestamp=True)

    def onAbort(self):
        """ On abort """
        if self._p.state() != QProcess.NotRunning:
            self._p.kill()
            clearAndSetText(self._outputTerminal, 'Process aborted', clear=False, setTimestamp=True)

    def _prepOnFinish(self, onFinish):
        """ Stop loading screen and execute function """
        self._loadingScreen.hide()
        onFinish()
