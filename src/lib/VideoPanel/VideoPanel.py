#!./bin/python.exe
"""
Layout containing two videos
"""
from PyQt5.Qt import QMargins
from PyQt5.QtWidgets import QGridLayout, QFrame
from .VideoPlayerWidget import VideoPlayerWidget


class DualVideoFrame(QFrame):
    """ Dual video layout """
    def __init__(self, parent=None, filename=None, style=None):
        """ Initializer """
        super().__init__()
        self._style = style
        self._originalFilename = filename
        self._renderFilename = None
        self._generateWidgets()
        self._generateLayout()

    def _generateWidgets(self):
        """ Generate subwidgets """
        self._originalVideo = VideoPlayerWidget(filename=self._originalFilename, style=self._style)
        self._renderVideo = VideoPlayerWidget(style=self._style)

    def _generateLayout(self):
        """ Generate layout """
        layout = QGridLayout(self)
        layout.addWidget(self._originalVideo, 0, 0)
        layout.addWidget(self._renderVideo, 0, 1)

        self.setLayout(layout)
        self.setFrameShape(QFrame.StyledPanel)

    def loadVideoFile(self, filename, videoType=None, forceLoad=False):
        """ Load video file """
        if videoType not in [None, 'original', 'render']:
            raise ValueError(f'Unrecognized videoType {videoType}')

        self.clearVideo(videoType)

        if (not videoType or videoType == 'original') and (self._originalVideo.isVisible() or forceLoad):
            self._originalVideo.loadVideoFile(filename)
        if (not videoType or videoType == 'render') and (self._renderVideo.isVisible() or forceLoad):
            self._renderVideo.loadVideoFile(filename)

    def clearVideo(self, videoType=None):
        """ Clear video """
        if videoType not in [None, 'original', 'render']:
            raise ValueError(f'Unrecognized videoType {videoType}')

        if (not videoType or videoType == 'original'):
            self._originalVideo.clearVideo()
        if (not videoType or videoType == 'render'):
            self._renderVideo.clearVideo()

    def toggleVideo(self, videoType, forceClose=False, forceOpen=False):
        """ Toggle video to be visible or not """
        if forceClose and forceOpen:
            raise ValueError('Both forceClose and forceOpen cannot be set to True')

        if videoType not in ['original', 'render']:
            raise ValueError(f'Unrecognized videoType {videoType}')

        if videoType == 'original':
            video = self._originalVideo
            filename = self._originalFilename
        else:
            video = self._renderVideo
            filename = self._renderFilename

        if video.isVisible() or forceClose:
            video.hide()
        elif not video.isVisible() or forceOpen:
            video.show()
            video.loadVideoFile(filename)
