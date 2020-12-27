#!./bin/python.exe
"""
General widget utils shared by everything
"""
from datetime import datetime
from PyQt5.QtWidgets import QMessageBox, QHBoxLayout, QLabel

def generateMessageBox(message, icon=QMessageBox.Information, windowTitle="Info",
                       buttons=QMessageBox.Ok):
    """ Generate message box """
    msgBox = QMessageBox()
    msgBox.setIcon(icon)
    msgBox.setText(message)
    msgBox.setWindowTitle(windowTitle)
    msgBox.setStandardButtons(buttons)

    return msgBox


def generateRow(label, widget):
    """ Generate horizontal layout composed of two widgets """
    if isinstance(label, str):
        label = QLabel(label)
    
    layout = QHBoxLayout()
    layout.addWidget(label)
    layout.addWidget(widget)

    return layout


def clearAndSetText(textWidget, text, clear=False, setTimestamp=True):
    """ Clear and set text widget """
    if setTimestamp:
        text = f"{datetime.now().time()} {text}"

    if clear:
        textWidget.clear()

    textWidget.insertPlainText(f"{text}\n\n")
