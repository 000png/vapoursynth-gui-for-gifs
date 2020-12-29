#!./bin/python.exe
"""
General widget utils shared by everything
"""
from datetime import datetime
from PyQt5.QtWidgets import QMessageBox, QHBoxLayout, QLabel, QWidget, QStackedLayout

def generateMessageBox(message, icon=QMessageBox.Information, windowTitle="Info",
                       buttons=QMessageBox.Ok):
    """ Generate message box """
    msgBox = QMessageBox()
    msgBox.setIcon(icon)
    msgBox.setText(message)
    msgBox.setWindowTitle(windowTitle)
    msgBox.setStandardButtons(buttons)

    return msgBox


def generateRow(label, widgets, setZeroMargins=True):
    """ Generate horizontal layout composed of two widgets """
    if isinstance(label, str):
        label = QLabel(label)
    
    layout = QHBoxLayout()
    layout.addWidget(label)

    if not isinstance(widgets, list):
        widgets = [widgets]
    for item in widgets:
        layout.addWidget(item)

    if setZeroMargins:
        layout.setContentsMargins(0, 0, 0, 0)

    return layout


def clearAndSetText(textWidget, text, clear=True, setTimestamp=False):
    """ Clear and set text widget """
    if setTimestamp:
        text = f"{datetime.now().time()} {text}"

    if clear:
        textWidget.clear()

    textWidget.insertPlainText(f"{text}\n\n")


def generateStackedWidget(widgets, maxWidth=None, maxHeight=None):
    """ Generate stacked widget """
    w = QWidget()
    stack = QStackedLayout()
    for item in widgets:
        stack.addWidget(item)

    w.setLayout(stack)

    if maxWidth is not None and maxWidth > 0:
        w.setMaximumWidth(maxWidth)

    if maxHeight is not None and maxHeight > 0:
        w.setMaximumHeight(maxHeight)

    return w, stack