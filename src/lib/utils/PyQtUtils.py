#!./bin/python.exe
"""
General widget utils shared by everything
"""
from datetime import datetime
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMessageBox, QHBoxLayout, QLabel, QWidget, \
    QStackedLayout, QPlainTextEdit, QPushButton, QLineEdit

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


def clearAndSetText(textWidget, text, clear=True, setTimestamp=False, setToBottom=True):
    """ Clear and set text widget """
    oneLiner = isinstance(textWidget, QLineEdit)

    if clear:
        textWidget.clear()

    if not oneLiner:
        if setTimestamp:
            text = f"{datetime.now().time()} {text}"

        if setToBottom:
            text = f"{text}\n\n"
            textWidget.verticalScrollBar().setValue(textWidget.verticalScrollBar().maximum());

        textWidget.insertPlainText(text)
    else:
        textWidget.insert(text)


def generateStackedWidget(widgets, maxWidth=None, maxHeight=None):
    """ Generate stacked widget """
    w = QWidget()
    stack = QStackedLayout()
    for item in widgets:
        stack.addWidget(item)

    w.setLayout(stack)

    if maxWidth is not None and maxWidth > 0:
        w.setMaximumWidth(maxWidth)
    else:
        w.setMaximumWidth(widgets[0].frameGeometry().width())

    if maxHeight is not None and maxHeight > 0:
        w.setMaximumHeight(maxHeight)
    else:
        w.setMaximumHeight(widgets[0].frameGeometry().height())

    return w, stack


def generateTextEntry(text='', oneLiner=False):
    """ Generate text box with presets """
    if oneLiner:
        tb = QLineEdit(text)
    else:
        tb = QPlainTextEdit(text)
        tb.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        tb.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        tb.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)

    return tb


def findAndSetIndex(combo, value, comboBoxName=None, errMsg=None):
    """ Set combobox to specified value """
    index = combo.findText(value)
    if index >= 0:
        combo.setCurrentIndex(index)
    
    return index >= 0
