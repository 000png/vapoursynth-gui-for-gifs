#!./bin/python.exe
"""
Video player widget; along with the video itself, contains the pause/play button
and slider.
"""
from PyQt5.QtCore import QDir, Qt, QUrl
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QSlider, QStyle, \
    QLabel
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtGui import QIcon


class VideoPlayerWidget(QWidget):
    """ Video widget class """
    def __init__(self, parent=None, style=None, filename=None):
        """ Initializer """
        super().__init__(parent)
        self._style = style
        self._filename = filename

        self._videoPaused = True
        self._start = 0
        self._end = 0
        self._position = 0
        self._duration = 0

        self._generateWidgets()
        self._generateLayout()

        if filename:
            self.loadVideoFile(filename)

    def hide(self):
        """ Override to pause video """
        self._pauseIfPlaying()
        super().hide()

    def _generatePushButton(self, style=None):
        """ Generate push button """
        button = QPushButton()
        button.setCheckable(True)
        button.setEnabled(False)
        if style:
            button.setIcon(style)

        return button

    def _generateWidgets(self):
        """ Generate subwidgets """
        # videoWidget
        self._videoWidget = QVideoWidget()

        # play button
        self._playButton = self._generatePushButton(self._style.standardIcon(QStyle.SP_MediaPlay))
        self._playButton.clicked.connect(self.toggleVideo)

        # slider
        self._slider = QSlider(Qt.Horizontal)
        self._slider.setRange(0, 0)
        self._slider.setTickPosition(QSlider.TicksBothSides)
        self._slider.sliderMoved.connect(self._positionChanged)

        # media player
        self._mediaPlayer = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        self._mediaPlayer.setVideoOutput(self._videoWidget)
        self._mediaPlayer.stateChanged.connect(self._mediaStateChanged)
        self._mediaPlayer.setMuted(True)

        # media player settings
        self._mediaPlayer.setNotifyInterval(10)
        self._mediaPlayer.positionChanged.connect(self._positionChanged)
        self._mediaPlayer.durationChanged.connect(self._durationChanged)

    def _generateLayout(self):
        """ Generate layout """
        # control panel
        controlPanelLayout = QHBoxLayout()
        controlPanelLayout.addWidget(self._playButton)
        controlPanelLayout.addWidget(self._slider)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._videoWidget)
        layout.addLayout(controlPanelLayout)

        self.setLayout(layout)

    def _mediaStateChanged(self, state):
        """ On media state changed """
        if not self._videoPaused and self._mediaPlayer.state() != QMediaPlayer.PlayingState:
            self._mediaPlayer.play()

    def _positionChanged(self, position):
        """ On position changed """
        if position >= self._end:
            position = self._start
            self._mediaPlayer.setPosition(position)

        self._position = position
        self._slider.setValue(position)

    def _durationChanged(self, duration):
        """ On duration changed """
        self._duration = duration
        self._start = 0
        self._end = duration
        self._slider.setRange(0, duration)
        self._slider.setTickInterval(duration / 20)

    def _pauseIfPlaying(self):
        if self._playButton.isChecked():
            self._playButton.toggle()
            self.toggleVideo()

    def loadVideoFile(self, filename):
        """ Load the video file """
        if not filename:
            return

        self._pauseIfPlaying()
        self._playButton.setEnabled(True)
        self._playButton.toggle()
        self._filename = filename
        self._mediaPlayer.setMedia(QMediaContent(QUrl.fromLocalFile(filename)))
        self.toggleVideo()

    def toggleVideo(self):
        """ Toggle video """
        if self._playButton.isChecked():
            self._playButton.setIcon(self._style.standardIcon(QStyle.SP_MediaPause))
        else:
            self._playButton.setIcon(self._style.standardIcon(QStyle.SP_MediaPlay))

        self._videoPaused = not self._videoPaused
        self._mediaPlayer.pause() if self._videoPaused else self._mediaPlayer.play()

    def clearVideo(self):
        """ Clear video """
        self._mediaPlayer.setVideoOutput(None)
