#!./bin/python.exe
"""
Layout containing options for Vapoursynth
"""
from PyQt5.QtWidgets import QWidget, QGridLayout, QPushButton

# vapoursynth plugins/libraries available for use in the default; if the user
# wishes to use any others they'll need to download the plugin themselves and apply
# it to the script frame
EMBEDDED_PLUGINS = []

class VSOptionsLayout(QGridLayout):
    """
    Main base layout for application
    """
    def __init__(self):
        super().__init__()
        
        self.addWidget(QPushButton("VS Options Layout"), 0, 0)

