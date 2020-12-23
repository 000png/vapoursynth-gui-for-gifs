#!./bin/python.exe
"""
Layout containing original video cut
"""
from PyQt5.QtCore import QDir, Qt, QUrl
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QGridLayout, QPushButton, QSlider, QStyle, QLabel, QSizePolicy, QHBoxLayout
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtGui import QIcon

class DualVideoLayout(QGridLayout):

    def __init__(self, parent):
        super().__init__()
        self._parent = parent
        self._buttons = []

        self._generateWidgets()
        self._generateLayout()

    def _generatePushButton(self, style):
        """ Generate push button """
        button = QPushButton()
        button.setCheckable(True)
        button.setEnabled(False)
        if style:
            button.setIcon(style)

        self._buttons.append(button)
        return button

    def _generateWidgets(self):
        """ Generate widgets """
        self._playButton = self._generatePushButton(self._parent.style().standardIcon(QStyle.SP_MediaPlay))
        self._playButton.clicked.connect(self._toggleVideo)

        self._slider = QSlider(Qt.Horizontal)
        self._slider.setRange(0, 0)
        self._slider.setTickPosition(QSlider.TicksBothSides)
        self._slider.sliderMoved.connect(self._setPosition)

        # sync slider with first video
        self._originalVideoLayout = VideoLayout(self._slider)
        self._previewVideoLayout = VideoLayout()

    def _generateLayout(self):
        """ Generate layout """
        controlPanel = QHBoxLayout()
        controlPanel.addWidget(self._playButton)
        controlPanel.addWidget(self._slider)

        self.addLayout(self._originalVideoLayout, 0, 0)
        self.addLayout(self._previewVideoLayout, 0, 1)
        self.addLayout(controlPanel, 1, 0, 1, 0)

    def _toggleVideo(self):
        self._originalVideoLayout.toggleVideo()
        self._previewVideoLayout.toggleVideo()

        if self._playButton.isChecked():
            self._playButton.setIcon(self._parent.style().standardIcon(QStyle.SP_MediaPause))
        else:
            self._playButton.setIcon(self._parent.style().standardIcon(QStyle.SP_MediaPlay))

    def _pauseIfPlaying(self):
        if self._playButton.isChecked():
            self._playButton.toggle()
            self._toggleVideo()

    def _setPosition(self, position):
        self._pauseIfPlaying()
        self._slider.setValue(position)
        self._originalVideoLayout.setPosition(position)
        self._previewVideoLayout.setPosition(position)

    def loadVideoFile(self, filename):
        """ Load the video file """
        for button in self._buttons:
            button.setEnabled(True)
        self._playButton.toggle()
        self._playButton.setIcon(self._parent.style().standardIcon(QStyle.SP_MediaPause))

        self._originalVideoLayout.loadVideoFile(filename)
        self._previewVideoLayout.loadVideoFile(filename)

class VideoLayout(QVBoxLayout):

    def __init__(self, slider=None):
        super().__init__()

        self._videoPaused = True
        self._slider = slider
        self._start = 0
        self._end = 0
        self._duration = 0
        self._position = 0
        self._generateLayout()

    def _generateLayout(self):
        """
        Make widgets used in this layout
        """
        # the video widget
        self._videoWidget = QVideoWidget()
        self._videoWidget.resize(300, 300)
        self._videoWidget.show()
        self.addWidget(self._videoWidget)

        # media player
        self._mediaPlayer = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        self._mediaPlayer.setVideoOutput(self._videoWidget)
        self._mediaPlayer.stateChanged.connect(self._mediaStateChanged)

        # if slider exists, sync video with slider
        if self._slider:
            self._mediaPlayer.setNotifyInterval(10)
            self._mediaPlayer.positionChanged.connect(self._positionChanged)
            self._mediaPlayer.durationChanged.connect(self._durationChanged)

    def _mediaStateChanged(self, state):
        if not self._videoPaused and self._mediaPlayer.state() != QMediaPlayer.PlayingState:
            self._mediaPlayer.play()

    def _positionChanged(self, position):
        if position >= self._end:
            position = self._start
            self._mediaPlayer.setPosition(position)

        self._position = position
        self._slider.setValue(position)

    def _durationChanged(self, duration):
        self._duration = duration
        self._start = 0
        self._end = duration
        self._slider.setRange(0, duration)
        self._slider.setTickInterval(duration / 20)

    def loadVideoFile(self, filename):
        """
        Load the video file
        """
        self._mediaPlayer.setMedia(QMediaContent(QUrl.fromLocalFile(filename)))
        self.toggleVideo()

    def toggleVideo(self):
        """ Toggle video """
        self._videoPaused = not self._videoPaused
        self._mediaPlayer.pause() if self._videoPaused else self._mediaPlayer.play()

    def setPosition(self, position):
        self._mediaPlayer.setPosition(position)

    def setStart(self, start):
        if start >= self._end:
            raise ValueError("Specified start position cannot be greater than end position")
        self._start = 0 if start < 0 else start

    def setEnd(self, end):
        if end <= self._start:
            raise ValueError("Specified end position cannot be greater than start position")
        self._end = self._duration if end > self._duration else end
